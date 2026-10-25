nulsweep.c - over-read sweep for the "$(" / "$((" scanner (run under AddressSanitizer)

For each string in a corpus of 24 inputs, for every prefix length n, and for every
position z < n where a raw 0 byte is injected (plus the no-NUL case), it calls
  mode 0: Tcl_ParseVarName(NULL, buf, n, &p, 0)  with buf malloc'd to EXACTLY n bytes
  mode 1: Tcl_ParseCommand(NULL, buf, n, 0, &p)  with buf n+1 bytes (terminator, per core's contract)
Total 3084 calls per spelling.  tclParse.c is compiled with -fsanitize-recover=address so
all reports are listed, then sorted by fault site.

Result (both spellings): zero reports in code we added or changed.
The only reports are two existing core reads one byte past the length, reached through the
array-index path (Tcl_ParseCommand tclParse.c:294 and Tcl_ParseQuotedString :2148), which
rely on Tcl strings always being NUL terminated.  git blame: initial import, not our lines.
Note: a Tcl-level string can never hold a raw 0 byte (it is stored as C0 80), so this
test has to be done from C.
