# Mutation testing

Mutants were generated only for lines this change added in `tclParse.c`, `tclCompile.c`, `tclCompCmdsSZ.c` and `tclCompExpr.c`:
swapped comparison and logic operators, `++`/`--`, `TCL_OK`/`TCL_ERROR`, `true`/`false`, character literals (`'('`, `'{'`, `'"'`, ...),
small integer constants, negated `if`/`while` conditions, and deleted statements. Each mutant was rebuilt and run against
`parse.test parseOld.test parseExpr.test compile.test`, in both builds (`$(` and `$((`). A mutant counts as killed if any test
fails, the run crashes or aborts, a test file stops early, or it times out (30 s; the unmutated run takes about 1 s).
Mutants that do not compile are not counted. The harness is in `mutation/` (`gen.py`, `run.py`, `start.sh`, `summary.py`;
`results1.jsonl` = `$(` build, `results2.jsonl` = `$((` build, `mutants.json` = the mutant list).

## Final result (186 mutants per build, 173 compile)

| Build | Killed | Survived | Kill rate |
|---|---:|---:|---:|
| `$(` | 149 | 24 | 86.1% |
| `$((` | 152 | 21 | 87.9% |

First pass (before the extra tests): 188 mutants, about 69% killed in both builds.

## What the mutation run found

* **A real bug.** My "uncompiled" tests had been compiled to bytecode, so the runtime path (`TclSubstTokens`: `subst $var`, `Tcl_EvalEx`)
  was barely exercised. A test on the real runtime path showed `$(([return -code error boom]))` returning an empty message where
  `[expr {...}]` returns `boom`. Fixed in `TclSubstTokens`; the test is `parse-22.75`.
* **A real bug in `Tcl_ParseVar`** (found earlier by AddressSanitizer): the value of an expression substitution lives only in the
  interpreter result, so resetting the result freed the string being returned. Fixed in `Tcl_ParseVar`; test `parse-22.5`.
* **Weak scanner tests.** Most brace/quote tests had been wrapped in `[...]`, where `)` is ignored. New tests put braces, quotes,
  escapes and brackets directly in the expression (`parse-22.60` to `22.94`), plus `parse-22.93`: no truncated prefix of a valid substitution
  is ever accepted.
* **Self-adapting tests cannot see a wrong spelling.** The tests adapt to whichever of `$(` / `$((` the build uses, so a mutant that
  flips the build's spelling went unnoticed. `parse-22.99` (optional): set `TCL_TEST_EXPR_SUBST_PARENS=1` or `2` in the environment
  and the test checks the build uses that spelling.

## The 24/21 survivors, classified

| Count | Why they survive |
|---:|---|
| 1 | Deleted function prototype (`FindExprSubstEnd`): equivalent, the function is defined before use. |
| 10 | Boundary mutants in the scanner (`<` vs `<=`, `>=` vs `>`, `src + 1` vs `src + 0`, at the end of the input). Equivalent: each loop bound has a second guard, and the skipped character is at the end of the string. |
| 1 | Deleted last `break` in a `switch` (falls out of the switch anyway): equivalent. |
| 7 | The mode test itself (`TCL_EXPR_SUBST_PARENS == 1 \|\| numBytes > 1 && src[1] == '('`): the half of the condition that is dead code in the other build (it is a compile-time constant), plus `numBytes > 1` vs `>= 1` / `> 0`, which only reads the string's NUL terminator. Each is killed in the build where it matters. |
| 1 | `Tcl_IncrRefCount(bodyObj)` deleted: equivalent, `Tcl_ExprObj` leaves the refcount alone and the object is still freed once. |
| 2 | `Tcl_DecrRefCount` deleted (a leak): not visible to the normal suite. Killed by `parse-22.80` in a memory-debug build (`--enable-symbols=mem`), and also by LeakSanitizer in a `-DPURIFY` AddressSanitizer build. |
| 1 | `parsePtr->errorType = TCL_PARSE_MISSING_PAREN`: observable only through the C API, not from Tcl scripts. |
| 2 | `envPtr->line += adjust` / `-= adjust` in `TclCompileTokens`: no difference in `-errorline` or `info frame` in any scenario tried. It mirrors the `[command]` case; unproven, a candidate to drop in review. |

## Second pass (final code, after the look-ahead and the message builder were added)

Mutants were regenerated from the added lines (257 generated, 235 compile per build) and run against `parse.test parseOld.test parseExpr.test compile.test subst.test`.

| Build | Compile | Killed (1st run) | Killed after tests `parse-22.100`-`22.108` | Survived |
|---|---:|---:|---:|---:|
| `$(` | 235 | 162 (68.9%) | 163 (69.4%) | 72 |
| `$((` | 235 | 198 (84.3%) | 207 (88.1%) | 28 |

Survivors on the final code:

* `$(` build, about 39 lines: the look-ahead (`FindExprSubstEnd`, `ExprSubstSyntaxError`, the missing-second-paren branch) is not compiled into that build, so mutants there are dead code.
* Boundary mutants in `SkipExprSubstScan` (`<` vs `<=`, `src + 1` vs `src + 0` at the end of the input): equivalent, each loop has a second guard.
* `parsePtr->errorType = ...` (two places): observable only through the C API.
* Reference-count lines around `Tcl_ExprObj` in `Tcl_ParseVar`: a deleted decrement is a leak, not visible to the normal suite; covered by the memory-debug, Valgrind and AddressSanitizer runs below.
* `envPtr->line += adjust` / `-= adjust` in `TclCompileTokens` (two): equivalent. `adjust` was zero on every path the tests reach (checked with a debug print: the backslash-newline branch that raises it is never entered for these words), and the same mutation of the existing core line 2852 also survives Tcl's `info`, `eval`, `compile` and `basic` tests. Test `parse-22.109` compares the reported line of a command inside `$((...))` with the same command in `[expr {...}]` after a continuation line; it passes in both builds.

## Other checks on the final code

* Full existing suite (`tests/all.tcl`): 509,471 tests (`$((`) and 508,717 (`$(`, with `binary.test` killed by the system), 0 failed. `cmdAH-24.9` aborts identically on untouched trunk.
* AddressSanitizer with `-DPURIFY=1 -fsanitize=address`, Valgrind (full leak check, `-DPURIFY`) and the Tcl memory-debug build (`--enable-symbols=mem`), both builds, on parse, parseOld, parseExpr, subst and compile (1,064 tests): no errors. The only report is one 48-byte leak in core Tcl (`TclArgumentBCEnter`), which also appears when running `info.test`. ASan needs `ASAN_OPTIONS=detect_stack_use_after_return=0` for Tcl's regexp engine (its stack-depth check breaks under ASan's fake stacks).
* Leak-growth test with the memory-debug build: see `scripts/valgrind_asan_mem/leak*.tcl`.
* Windows (static, MSVC, Windows 10 1903): see `NOTES.txt`.
