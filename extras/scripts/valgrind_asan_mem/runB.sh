#!/bin/bash
T="parse.test parseOld.test parseExpr.test subst.test compile.test"
for spec in "vg 2" "vg1 1"; do
  set -- $spec
  d=~/tcl-build-$1
  echo "=== $1 mode $2 start $(date +%T)"
  (cd $d && TCL_TEST_EXPR_SUBST_PARENS=$2 valgrind --error-exitcode=9 --leak-check=full --show-leak-kinds=definite,indirect --errors-for-leak-kinds=definite,indirect --num-callers=20 ./tcltest ~/memchk/wrap.tcl 0 $T > ~/memchk/out-$1.log 2>&1; echo rc=$? >> ~/memchk/out-$1.log)
  grep -E "Total|ERROR SUMMARY|definitely|indirectly|rc=" ~/memchk/out-$1.log | head -8
done
echo B-DONE
