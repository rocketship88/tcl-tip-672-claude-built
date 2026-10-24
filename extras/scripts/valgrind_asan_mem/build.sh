#!/bin/bash
set -x
cd ~
for d in tcl-build-vg tcl-build-vg1 tcl-build-asan; do (cd $d && make -j2 tcltest 2>&1 | tail -2); done
mk() { # dir mode extra
  mkdir -p ~/$1 && cd ~/$1 && [ -f Makefile ] || /root/tcl-trunk/unix/configure --disable-shared "${@:3}" >/dev/null 2>&1
  make -j2 tcltest 2>&1 | tail -2
}
mk tcl-build-mem2 2 --enable-symbols=mem 'CFLAGS=-g -O0'
mk tcl-build-mem1 1 --enable-symbols=mem 'CFLAGS=-g -O0 -DTCL_EXPR_SUBST_PARENS=1'
mk tcl-build-asan1 1 'CFLAGS=-g -O1 -fsanitize=address -fno-omit-frame-pointer -DTCL_EXPR_SUBST_PARENS=1' LDFLAGS=-fsanitize=address
echo BUILD-DONE
