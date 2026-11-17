# Notes for a fresh Claude

You were given this repo (usually as a zip) so that you can answer questions about the TIP 672 change or write patches
for it. Read in this order: README.md, rebased/README.md, extras/NOTES.txt (newest section first), extras/design_and_results.md.

* The current code is in rebased/ (Fossil branch tip-672-v2, check-in fbb7b018f2). orig/ and new/ at the top level are the
  older, pre-rebase files; results in extras/ were measured on those.
* Key design: the parser finds the end of $((body)) (a scanner, SkipExprSubstScan in tclParse.c), makes a
  TCL_TOKEN_EXPR_SUBST token (512) holding the body, and the compiler / TclSubstTokens treat the body as if it had been braced
  in [expr {...}]. expr itself is not changed.
* Public API: Tcl_ParseVarName and Tcl_ParseVar behave exactly as in Tcl 9.0 and never return the new token. The internal
  TclParseVarName(..., exprSubst) is what ParseTokens and tclCompExpr.c call with exprSubst = 1. (This came from Florent
  Merlet's report during the vote: Tcl_ParseVar could return a pointer into the interp result.)
* Build: unix/configure --disable-shared; add CFLAGS=-DTCL_EXPR_SUBST_PARENS=1 for the $( spelling. Tests: parse.test,
  parseOld.test, subst.test, compile.test. Tests adapt to the build's spelling.
* Rules the author wants kept: never write one-line ifs (always braces and separate lines, so gcov sees each action); every
  change gets tests; no curly quotes in text meant for email.
* Do not push or edit the TIP while a vote is open; the TIP text is edited by the TIP editors, the code through Fossil.

## Questions you will probably be asked, and where the answer is

* "What was the Tcl_ParseVar defect and what did you fix?" Read rebased/FIX_Tcl_ParseVar.md (defect, repro with before/after output,
  lineage, the exact code changes, tests, mutation and coverage results, alternatives). The patch is rebased/fix-fbb7b018f2.patch.
* "How big is the change, how was it tested?" extras/NOTES.txt (top section) and extras2/fbb7b018f2_checks/.
* "Show me the code" extras2/parser_stepper_v2.html (review of the 20 hunks and a step-through).
* To reproduce the defect on an old tree: rebased/repro/parsevar_repro.c.
