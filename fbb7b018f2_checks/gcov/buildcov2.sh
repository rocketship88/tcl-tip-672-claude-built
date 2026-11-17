#!/bin/bash
for m in 1 2; do
  d=/root/cov-fbb$m; rm -rf $d; mkdir -p $d; cd $d
  if [ $m = 1 ]; then F="-DTCL_EXPR_SUBST_PARENS=1"; else F=""; fi
  /root/jv/unix/configure --disable-shared "CFLAGS=-g -O0 --coverage $F" LDFLAGS=--coverage >/dev/null 2>&1
  make -j2 tcltest 2>&1 | tail -2
done
echo COV-BUILD-DONE
