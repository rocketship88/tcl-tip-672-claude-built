#!/bin/bash
for spec in "asanP2 2" "asanP1 1"; do
  set -- $spec
  mkdir -p ~/tcl-build-$1 && cd ~/tcl-build-$1
  /root/tcl-trunk/unix/configure --disable-shared "CFLAGS=-g -O1 -DPURIFY=1 -fsanitize=address -fno-omit-frame-pointer -DTCL_EXPR_SUBST_PARENS=$2" LDFLAGS=-fsanitize=address >/dev/null 2>&1
  make -j2 tcltest 2>&1 | tail -1
done
echo P-DONE
