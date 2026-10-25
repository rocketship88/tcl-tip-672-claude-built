# Finishing the job: what is left (plan agreed Oct 2026)

Base of our work: Tcl trunk check-in 77ac0bb. The patch is `expr-subst.patch` (git diff, 15 files; `patch -p1`).
The mode switch `TCL_EXPR_SUBST_PARENS` (2 = `$((`, default; 1 = `$(`) lives only in generic/tclParse.c.

## A. Engineering, before anything is published
1. Freeze the code (no more behaviour changes after this point).
2. Mutation testing, both builds (new mutants for: FindExprSubstEnd / SkipExprSubstScan look-ahead,
   ExprSubstSyntaxError message builder, the -expressions gating in TclSubstOptions and ParseTokens).
3. Valgrind and ASan runs on the frozen code (parse.test, subst.test, compile.test at least).
4. Full suites in both modes on Windows (test.bat 1 and 2 run only parse*.test and compile.test so far;
   also run subst.test and a full all.tcl once per mode).
5. Put the final numbers into design_and_results.md section 9.

## B. Fossil branch for TIP 672 (needs the fossil repo on your computer; I cannot reach it from my session)
1. `fossil pull` / `fossil update trunk`, note the new trunk tip. Check it against 77ac0bb:
   `fossil diff --brief --from 77ac0bb --to trunk` (or timeline). Pay attention to generic/tclParse.c,
   generic/tcl.h, generic/tclCmdMZ.c, tclCompile.c, tests/parse.test, tests/subst.test, doc/*.
2. If trunk moved only in unrelated files: apply the patch to a clean trunk checkout.
   If it touched our files: merge by hand (Beyond Compare), then rebuild.
3. Create the branch (check the exact syntax with `fossil help branch`):
   `fossil branch new expr-subst trunk` then `fossil update expr-subst`.
4. Apply the patch (`patch -p1 < expr-subst.patch`) or copy new/ files over, `fossil changes`, build both modes,
   run the suites in both modes (test.bat 1 and 2).
5. `fossil commit -m "..."` on the branch, then `fossil push`.
6. Check on the web UI that the branch shows with all 15 files.

## C. Update TIP 672 (you own it)
Text to bring in line with the implementation:
- Spelling: `$((expr))` default, `$(expr)` as a build option; `$((expr))` valid in both.
- Strict rule for `$((`: body ends at the first balancing `)`, which must be followed by a second `)`.
  Error: `missing second ")" at _@_` plus the quoted text (expr-style).
- `$(` + anything that is not `$((` stays an empty-name array element (unchanged Tcl 9 behaviour); in `$(` mode
  that spelling is taken (the `$(index)` array with empty name can be written `[set (index)]`).
- `subst -expressions` / `-noexpressions`; `-nocommands` and `-novariables` also turn expressions off.
- C API: `TCL_TOKEN_EXPR_SUBST` (512), `TCL_SUBST_EXPRESSIONS` (010), `TCL_SUBST_ALL` question (7 vs 15).
- No double substitution: the body is compiled as `expr {body}`.
- Build switch and how the core team can flip the default.
Commit the TIP in the TIP repository and push.

## D. Mailing-list message to the core team (tcl-core)
Points to cover: link to the TIP and the fossil branch; what it does in two lines; the two spellings and your
preference for `$(`; the one incompatibility (`$(index)` empty-name arrays) and its workaround;
the new subst option and why (safety for untrusted input); test results (both modes, mutation, valgrind/ASan);
the open questions for them (decision `$((` vs `$(`, option names, TCL_SUBST_ALL value,
whether -nocommands should keep disabling the arithmetic). I will draft it when A to C are done.

## E. Open decisions for the core team
`$((` vs `$(`; option names; `TCL_SUBST_ALL` 7 or 15; behaviour of -nocommands.

## Conditional to-do (only if the core team reacts positively)

- Add two tests to tests/parse.test to reach 100% line coverage of the new code on the default
  (`$((`) build: (1) a stray "]" in the body, e.g. `subst {$((1 ] 2))}` (line 1424 of tclParse.c);
  (2) the syntax error with no interpreter, e.g. `info complete {puts $((1+2)x)}` (the
  `parsePtr->interp != NULL` branch). Both were confirmed in a scratch run to hit those spots.
  Doing it means a new check-in on tip-672-v2, a GitHub commit and a new zip, so do it only if
  there is real interest in the feature. Do not do it before then.
- Optional, same condition: prototype replacing the `{`, `"` and `[` cases of SkipExprSubstScan with
  Tcl_ParseBraces / Tcl_ParseQuotedString / Tcl_ParseCommand (see design_and_results.md section 10),
  checking it with extras/scripts/fuzz and measuring the cost.
