#!/bin/bash
# usage: run1.sh builddir script args...
d=$1; shift
LD_LIBRARY_PATH=$d TCL_LIBRARY=$HOME/tcl-trunk/library exec $d/tclsh "$@"
