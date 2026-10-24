#!/bin/bash
T="parse.test parseOld.test parseExpr.test subst.test compile.test"
for spec in "asanP2 2" "asanP1 1"; do
  set -- $spec
  (cd ~/tcl-build-$1 && TCL_TEST_EXPR_SUBST_PARENS=$2 ASAN_OPTIONS=detect_leaks=1:detect_stack_use_after_return=0 ./tcltest ~/memchk/wrap.tcl 0 $T > ~/memchk/out-$1.log 2>&1; echo rc=$? >> ~/memchk/out-$1.log)
  echo "$1: $(grep -E 'all.tcl:.*Total' ~/memchk/out-$1.log) | asan errors: $(grep -c 'ERROR: AddressSanitizer' ~/memchk/out-$1.log) | $(grep rc= ~/memchk/out-$1.log)"
done
echo C-DONE
