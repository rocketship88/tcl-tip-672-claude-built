# Status (Nov 17, 2026)

The Oct 2026 plan that was here (freeze, mutation testing, Valgrind/ASan, Windows runs) is done; its results are in
design_and_results.md, mutation_testing.md and the coverage/, valgrind/ and mutation/ folders (all measured on the
pre-rebase code, trunk 77ac0bb).

Current code: see ../rebased/README.md. Fossil branch tip-672-v2, leaf check-in fbb7b018f2.

Open items:
 - TIP 672 is in the vote. The code and the TIP text are now changed through Fossil and the TIP site, not here.
 - Rerun, on fbb7b018f2: gcov (both builds) and mutation testing of the lines the fix changed. Results will be
   added to NOTES.txt.
 - Two tests that would take the default build to 100 percent line coverage are still deferred.
 - Known typos in the TIP text were reported to the TIP editors; not changed here.
