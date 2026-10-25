#!/bin/bash
cd ~
for m in 1 2; do
  d=tcl-build-cov$m
  mkdir -p $d && cd $d
  if [ $m = 1 ]; then F="-DTCL_EXPR_SUBST_PARENS=1"; else F=""; fi
  /root/tcl-trunk/unix/configure --disable-shared "CFLAGS=-g -O0 --coverage $F" LDFLAGS=--coverage >/dev/null 2>&1
  make -j4 tcltest 2>&1 | tail -2
  cd ~
done
echo COV-BUILD-DONE
