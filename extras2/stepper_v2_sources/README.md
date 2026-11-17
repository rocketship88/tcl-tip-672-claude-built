# Stepper v2 (version 3.0) sources

Rebuilt for the tip-672-v2 branch, check-in fbb7b018f2. The page is extras2/parser_stepper_v2.html; v1 (extras/parser_stepper.html) is the pre-rebase version.

Rebuild: run gen.tcl and gen_substall.tcl with a tcltest binary of each build (the $( and $(( spellings) to make data1.json / data2.json and substall1.json / substall2.json
(TCL_LIBRARY must point at the Tcl library directory), then python3 build_page.py out.html. build_page.py reads the C files from G= and the diff from a git
checkout of the trunk base with the branch files copied over it (edit G= and the two cwd= paths; they are /root/rb in the build that made this copy).
check.js (Playwright) runs all 530 scenario/option traces in both builds and checks the JavaScript scanner against the real parser.
review_notes.py holds the 20 hunk notes and the 7 reviewer questions.
Changes from v1: all line numbers moved to the new tclParse.c / tclCompile.c; hunk list is now 20 hunks (Jan Nijtmans' restructuring of the subst
options means the "clear the EXPRESSIONS bit" step is gone, the no-options carry the bit in the table); the walkthrough calls the internal TclParseVarName;
new reviewer question 7 about Tcl_ParseVar. The codeview and fold features are unchanged.
