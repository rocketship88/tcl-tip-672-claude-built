# Checks on fbb7b018f2 (Nov 17, 2026)

* gcov/: coverage of the lines added or changed by the whole change (compared with trunk 6a9f9e9402 on the GitHub mirror = Fossil 6e7c8299c5),
  tests parse, parseOld, subst, compile, both builds. gcov_results.txt has the result (default build: 176 of 179 executable lines ran, 98.3 percent;
  single-paren build: 148 of 178, the rest is the "missing second )" path that spelling cannot reach). Scripts are for the paths used on the day (/root/jv = the tree).
* mutation_fix_only/: mutation testing of only the lines the fix (check-in fbb7b018f2) changed. 6 mutants per build, all killed in both builds
  (run.py harness, adapted from extras/scripts/mutation; results1.jsonl = $( build, results2.jsonl = $(( build).
  The older whole-feature mutation result (86 to 88 percent killed, extras/mutation_testing.md) was measured on the pre-rebase code and was not rerun.
* examples_check.tcl: the TIP672-examples.html procedures that use $(( ))), run against the default build; the plain and $((...)) versions give equal results.
* Full test suite on this tree: 509601 tests, 0 failed (the cmdAH timestamp test is environmental).
