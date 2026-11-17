Mutation testing of the scanner depth limit (Oct 27, 2026)

Source under test: generic/tclParse.c of this package (md5 e30bfbd51c776f130e07c783902f4bdc),
which has EXPR_SUBST_MAX_SCAN_DEPTH = 1000. 26 hand-picked mutants of the depth-limit code
(mutants_depth.json: line, old text, new text, description). Each mutant was built and run in both
builds ($( = mode 1, $(( = mode 2) against parse.test parseOld.test parseExpr.test compile.test
subst.test (1,073 tests; baseline 0 failed in both).

depth_run.py    the runner (modelled on extras/mutation/run.py; paths are those of the machine it ran on)
results1.jsonl  $( build, one line per mutant (status killed-fail / killed-abort / killed-timeout / survived)
results2.jsonl  $(( build
baseline1.json, baseline2.json   the unmutated runs

Result: 23 killed, 3 survived, the same in both builds. See extras/mutation_testing.md, section
"Third pass: the depth limit".
