# Expression substitution `$((expr))` / `$(expr)`: design decisions and results

Base: Tcl trunk 77ac0bb (9.1). Everything below was measured on Linux (gcc, x86-64); Windows (MSVC, static, Win10 1903) was verified by you for both spellings before the last bug fix.

## 1. Design decisions

1. **A real parser feature, not text rewriting.** `Tcl_ParseVarName` recognises the construct and emits a new token, so nothing is pushed back into the input stream.
2. **New token `TCL_TOKEN_EXPR_SUBST` (512).** `numComponents` = 1, followed by one TEXT token holding the unparsed body. The parser never substitutes inside the body; `expr` sees it as one braced word, so there is no double substitution. Outputs of the parser tools show it as `exprsubst`.
3. **One implementation, two spellings.** Build switch `TCL_EXPR_SUBST_PARENS`: 2 (default) triggers on `$((`; 1 triggers on `$(`. Any other value is an `#error`. `$((` is the default because `$(` conflicts with the array whose name is the empty string (`$()`, `set () x`).
4. **Same body rule in both spellings.** The body is the text between the matching outer parentheses of `$(`. So `$((a)*b)` is valid in both builds, and `$((expr))` stays valid if `$(` is adopted later (the extra parentheses just group the expression). This is why `$(` is purely a superset.
5. **Scanner.** `SkipExprSubstScan` / `FindExprSubstEnd` find the closing parenthesis, skipping braces, double quotes, backslash escapes and `[...]` commands, so a `)` inside those does not end the body. An unterminated construct reports `missing )` (`TCL_PARSE_MISSING_PAREN`, `incomplete` set, so `info complete` and interactive shells keep reading).
6. **Compiled path.** `TclCompileTokens` and `TclSubstCompile` call `TclCompileExpr` on the body. The bytecode is identical to `[expr {(body)}]` (checked with `tcl::unsupported::disassemble` and `getbytecode`); only the `commands` list differs (one entry instead of two). Constant folding still happens.
7. **Uncompiled path.** `TclSubstTokens` calls `Tcl_ExprObj` on a fresh object holding the body. Non-OK return codes (`return -code error ...`, `break` and so on) are handled like `[command]` substitution (this was the bug found by mutation testing, section 3).
8. **Error messages.** They match `[expr {(body)}]`, so the parentheses are visible in expression errors, e.g. `in expression "(1+_@_)"`. This is deliberate: it keeps the two forms indistinguishable.
9. **`Tcl_ParseVar`.** The value of an expression substitution exists only as the interpreter result, so `Tcl_ParseVar` returns that string without resetting the result (a use-after-free found by AddressSanitizer before the fix).
10. **Expression lexer.** The VARIABLE lexeme in `tclCompExpr.c` accepts the new token, so `expr {$((1+1))*2}` works.
11. **Known cosmetic point.** `envPtr->line += adjust` / `-= adjust` around the compile call mirrors the `[command]` case; no test could tell whether it matters. Candidate to remove in review.
12. **Tests adapt to the build** with constraint `exprSubstSingleParen`; env var `TCL_TEST_EXPR_SUBST_PARENS=1|2` lets `parse-22.99` verify the build really uses that spelling. `parse-18.12` and `parseOld-5.12` (which tested `$(`-as-array behaviour) are conditional.

## 2. Verification results

| Check | Result |
|---|---|
| Full suite (`all.tcl`), both builds | `$((`: 509,471 tests, 0 failed; `$(`: 508,717 tests, 0 failed (`binary.test` was killed by the system in that run, about 750 tests; it is also killed in some runs on untouched trunk). The `cmdAH-24.9` abort is environmental, identical on untouched trunk |
| New tests | 107 new tests: `parse.test` 83, `subst.test` 13, `compile.test` 10, `parseOld.test` 1 (counted by running the four files on untouched trunk and on this tree: 271 to 354, 71 to 84, 171 to 181, 158 to 159) |
| AddressSanitizer + `-DPURIFY` (final code, both builds) | parse, parseOld, parseExpr, subst, compile (1,064 tests each build): no errors. Only report: a 48-byte leak in `TclArgumentBCEnter` (core Tcl, `tclBasic.c`), which also appears when running `info.test`, a file that never touches this feature |
| Memory-debug build (`--enable-symbols=mem`, final code, both builds) | the same five files, 1,064 tests, 0 failed, no guard-byte errors. Leak-growth test (`scripts/valgrind_asan_mem/leak*.tcl`): each construct run 20,000 to 80,000 times; live blocks stay flat, with a one-off growth of 36 blocks for plain `$((...))` that stops after the first two rounds of 20,000 (object pools), versus none for `[expr {...}]` |
| Valgrind (memcheck, full leak check, `-DPURIFY`, final code) | both builds, the same five files: no invalid reads or writes; the same one 48-byte core leak as above. Logs in `valgrind/` (`final_*.txt`; the older per-file logs are from before the last changes) |
| Windows static build, both spellings | passed (only `encoding-31.2` fails, a Win10 1903 issue in the trunk test, unrelated) |

## 3. Mutation testing

See `mutation_testing.md`. Second pass, on the final code: 235 mutants compile per build. Kill rate 69.4% (`$(`) and 88.1% (`$((`, the default). The `$(` build is lower because the look-ahead and the message builder are not compiled into it, so mutants there are dead code. Every survivor is classified in `mutation_testing.md`; none points to a missing behaviour test. The earlier first pass (186 mutants) found one real bug (non-OK return codes lost on the uncompiled path), fixed. The second pass added tests `parse-22.100` to `22.109`.

## 4. Performance

Wall-clock timing was too noisy (about +/-5% run to run), so everything below is instruction counts (callgrind, `Ir`), which are deterministic. Optimized builds (`-O2`, no symbols), original trunk vs modified, both spellings. Scripts are in `performance/`.

| Workload | Original | New `$((` | New `$(` | Change |
|---|---:|---:|---:|---:|
| Ordinary scripts (parse, compile and `subst` with `$x`, `$a(k)`, `${x}`, `$::g(i)`, `[cmd]`, 10 rounds of 200 statements) | 659,946,882 | 660,193,064 | 660,193,049 | **+0.04%** |

The 0.04% is 246 thousand instructions over the whole run, about a quarter of a percent of the startup cost, and is code layout / one extra comparison in the `$(` branch. The ordinary `$name` path takes no new work: the new test is only reached when `(` directly follows `$`.

The new feature itself (10 rounds of 200 statements, startup of about 30.8M instructions included in each figure):

| Workload | `[expr {(...)}]` | `$((...))` | Change |
|---|---:|---:|---:|
| Run via `eval` (uncompiled-script path, parse and compile) | 47,791,074 | 46,450,240 | -2.8% |
| Compiled in a `proc` | 41,176,468 | 39,441,060 | -4.2% |

Expression substitution is slightly cheaper than the form it replaces, because it involves one command instead of two. The `$(` build gives the same numbers within about 1,200 instructions.

Run time of an already compiled loop (`loop.tcl`; the bytecode is identical): `[expr {...}]` 13,352 us vs `$((...))` 13,472 us per 200,000 iterations, within the noise.

Scaling of the scanner (body length 2,000 / 4,000 / 8,000 terms, plus unterminated and deeply nested bodies): added instructions over startup 4.1M / 8.1M / 15.5M, so linear and no quadratic behaviour.

**Conclusion: no performance bottleneck introduced.**

## 5. Parser stepper (version 1.3: whole-file code view, subst script, clickable steps, shortcuts box)

`parser_stepper.html` is an interactive page (also published as an artifact) that steps through the parser for `$((expr))` in seven scripts and both builds: real C code with colour, folding and double-click definitions, the scanner's call stack, the token array growing, and the real bytecode and result. Its scanner trace is checked against the real parser for every scenario. The last steps show how `expr` parses the body and put `$((expr))` side by side with the `[expr {expr}]` it stands for (real tokens, bytecode and results for both): same body text, same instructions and result; the bracket form is parsed twice and looks up the command `expr`, which `$((expr))` does not (a redefined `expr` or a trace on it affects only the bracket form).

## 6. `subst` options: `-expressions` / `-noexpressions`

Finding that led to it: `subst -nocommands {$(([string length abc]+1))}` returned 4, because the body of an expression substitution can contain `[commands]`. Code that uses `subst -nocommands` to make text safe would have let commands through the new syntax.

What was added:

- New flag `TCL_SUBST_EXPRESSIONS` (010) in `tcl.h`; `TCL_SUBST_ALL` is now 017, so existing callers that pass the macro get the new syntax. `Tcl_SubstObj` callers that compiled in a literal 7 do not.
- `subst` accepts `-expressions` and `-noexpressions` (`TclSubstOptions` in `tclCmdMZ.c`; usage and error messages updated). Positive and negated options still cannot be combined.
- `ParseTokens` (the `$` case): the expression form (`$((`, or `$(` in the other build) is substituted only if the flag is set; otherwise the `$` is literal text and the scanner is not run, so unbalanced parentheses are not an error. `-expressions` works without `-variables`.
- `-novariables` and `-nocommands` also clear the expressions bit (an expression body can run commands, and `$((` is `$` syntax). So existing scripts that use those options for safety behave as before. `-nobackslashes` leaves expressions on. The positive `-expressions` is an explicit opt-in (commands in the body then run).
- Docs: `subst.n`, `SubstObj.3`. Tests: `subst-expr-1.1` to `1.13` in `tests/subst.test`; the usage and bad-option messages in `subst-1.1`, `1.2`, `7.1`, `7.x` updated.

Open points for reviewers: the option names; changing the value of `TCL_SUBST_ALL`; and whether `-nocommands` should rather keep doing the arithmetic while refusing commands in the body.

## 7. Files

`new/` and `orig/` hold the 15 changed files (11 for the syntax, plus 4 for the subst options); `extras/expr-subst.patch` applies to pristine 77ac0bb; `changes_made.md` has line counts; `NOTES.txt` has build instructions (including the Windows `EXPRSUBST` variable); `mutation/`, `performance/`, `valgrind/` hold the harnesses and raw results.

## 8. `$((expr))` requires the closing `))` (look-ahead)

First version: `$((` consumed only the first `(`, so the second `(` was part of the body and the substitution ended at the first balancing `)`. `$((1+2)*3)` was accepted (9), and the typo `$((  1+2)*3  ))` for `$((  (1+2)*3  ))` was accepted too and left a stray `)` (`9)`).

Now (default build only): the trigger is `$((`, the body is the text up to the first `)` that balances the parentheses inside it, and the next character must be a second `)`. Otherwise it is a syntax error (type TCL_PARSE_SYNTAX, not incomplete) with an expr-style message, e.g. for `$((1+2)*3)`: `missing second ")" at _@_` / `in expression substitution "$((1+2)_@_*3)"`. Long text is shortened with `...` (60 bytes before the marker, 20 after, never inside a UTF-8 character; tests parse-22.98, 22.98a). If the text ends right after the first `)`, it is "missing )" and incomplete, so interactive shells keep reading. The body is now `X` for `$((X))` (it was `(X)`), so error messages quote `1+` like `[expr {1+}]`. The single-paren build is unchanged (body `(X)` for `$((X))`, no look-ahead).

Results: `$((1+2)*3)` error; `$((  1+2)*3  ))` error; `$((  (1+2)*3  ))` 9; `$(( 1+2 ))` 3; `$((1+2) )` error. Tests parse-22.90 to 22.97; parse-22.1 to 22.6, 22.32, 22.33, 22.40, 22.53, 22.68, 22.74, 22.75 now compute the expected parentheses from the build.

What the unchanged Tcl 9.1.1 does (probe: `scripts/probes/pristine_array_index_probe.tcl`): an array index stops at an unescaped `(`, `)`, `"` or `{`, and anything other than `)` there is "invalid character in array index". So `$((`, `$( (` (a space does not help), `$(x*(2+3))`, `$({a})` and `$("a")` are already errors; `$(` followed by text without those characters and then `)` is a legal empty-name array (`$(a)`, `$(1+2)`, `$( 1+2)`, `$(a b)`); `$(\()` works (index `(`). `$(` with no `)` is "missing )". So `$((` is free syntax. A space after the first `(` (`$( (`) is therefore not the trigger and stays the same error as before (parse-22.96).

Open: the core team has not decided between `$((` and `$(`. Results with this change: full suite 509,459 (mode 1) and 508,705 (mode 2) tests, 0 failed (the cmdAH abort is environmental); Valgrind clean on parse.test and subst.test; mutation testing was not rerun for the new look-ahead branch.

## 9. Final test results for this round

Code frozen at `tclParse.c` md5 7d9e28c9543e3d739b3ea5a4ed696489.

* Full Linux suites: 509,471 tests (`$((`) and 508,717 (`$(`), 0 failed. `cmdAH-24.9` aborts on untouched trunk too. `binary.test` is killed by the system in some runs (the totals differ by about 750 tests for that reason).
* Windows (earlier code, same behaviour): `test 1|2 release full` 526,603 tests each, 1 failure (`encoding-31.2`, environmental).
* Memory checks on the final code: Valgrind, AddressSanitizer and the Tcl memory-debug build, both builds, no errors; the one 48-byte leak reported is in core Tcl and appears without this feature (see section 2). Linux results are enough for the memory checks: the new code is plain C with no operating-system calls.
* Mutation testing: see section 3. The two remaining `envPtr->line += adjust` / `-= adjust` survivors in `tclCompile.c` are equivalent: `adjust` is never non-zero on the paths the tests reach, and the same mutation of the existing core line (`tclCompile.c` 2852) also survives Tcl's own `info`, `eval`, `compile` and `basic` tests. Test `parse-22.109` still checks that a command inside `$((...))` reports the same line as inside `[expr {...}]` after a continuation line.
