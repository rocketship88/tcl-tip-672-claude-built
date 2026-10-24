#!/bin/bash
T="parse.test parseOld.test parseExpr.test subst.test compile.test"
for spec in "mem2 2 1" "mem1 1 1"; do
  set -- $spec
  d=~/tcl-build-$1
  [ $1 = mem2 -o $1 = mem1 -o $1 = asan -o $1 = asan1 ] || continue
  echo "=== $1 mode $2 start $(date +%T)"
  (cd $d && TCL_TEST_EXPR_SUBST_PARENS=$2 ASAN_OPTIONS=detect_leaks=1 ./tcltest ~/memchk/wrap.tcl $3 $T > ~/memchk/out-$1.log 2>&1; echo rc=$? >> ~/memchk/out-$1.log)
  grep -E "Total|MEMACTIVE|ERROR|rc=" ~/memchk/out-$1.log | head -6
done
echo A-DONE
