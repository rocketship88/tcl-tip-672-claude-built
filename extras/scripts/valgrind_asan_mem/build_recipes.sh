#!/bin/bash
# Recipes (not a turnkey script): run each in its own empty build directory.
SRC=$HOME/tcl-trunk/unix
# Normal builds: default ($((), and single-paren ($()
#   $SRC/configure                                   && make
#   CFLAGS="-DTCL_EXPR_SUBST_PARENS=1" $SRC/configure && make
# AddressSanitizer (PURIFY makes Tcl_Obj use plain malloc so ASan sees it)
#   $SRC/configure --disable-shared 'CFLAGS=-g -O1 -DPURIFY=1 -fsanitize=address -fno-omit-frame-pointer' LDFLAGS=-fsanitize=address
#   ulimit -s unlimited; ASAN_OPTIONS=detect_leaks=1:detect_stack_use_after_return=0 ./tcltest ../tests/parse.test
# Memory-debug build (parse-22.80 leak test needs the 'memory' constraint)
#   $SRC/configure --disable-shared --enable-symbols=mem && make tcltest
# Valgrind
#   CFLAGS="-g -O0 -DPURIFY=1" $SRC/configure --enable-symbols && make tcltest
#   valgrind -q --leak-check=full --error-exitcode=9 ./tcltest parse.test -verbose ""
# Optimized builds for instruction counts (orig = pristine worktree)
#   $HOME/tcl-orig/unix/configure --disable-symbols; $SRC/configure --disable-symbols
#   valgrind --tool=callgrind ./tclsh ../performance/shared.tcl 10
# Full suite
#   make test    (or: TCL_TEST_EXPR_SUBST_PARENS=1 make test  for the $( build)
