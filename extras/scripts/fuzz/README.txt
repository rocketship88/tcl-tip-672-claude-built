Random-garbage tests for the "$(" / "$((" body scanner

1. structure differential (harness.c + fuzz.py)
   200,000 random inputs per spelling (400,000 total): mostly random strings over the alphabet
   ( ) [ ] { } " \ space $ a b 1 + * ; newline, raw NUL, UTF-8 e-acute and euro; 15% built from nested
   pieces such as {)} "(" [set x )] \) . Each is parsed by Tcl_ParseVarName from an exactly-sized heap
   block under AddressSanitizer. An independent reference scanner (fuzz.py, written from the spec, not
   from the C code) predicts: success and exact consumed length, "incomplete", or a syntax error.
   Result: 0 mismatches, 0 ASan reports.  Sanity: with the reference deliberately broken (no backslash
   handling / braces not protecting parens) the same run reports ~1,600 mismatches per 20,000 cases.
   Build:  gcc -fsanitize=address -fsanitize-recover=address ... harness.c tclParse.o libtcl.a
   Run:    python3 fuzz.py 2 200000 7     (arg1 = 1 or 2 for the spelling, then count, seed)

2. value differential (sem.tcl)
   3 seeds x 60,000 random expression bodies built from atoms containing ")" "]" {)} \) nested
   brackets etc.: [subst {$((body))}] must equal [expr body], including whether it errors.
   Result: 180,000 compared, 0 different (about 20,000 per seed are successful values, the rest are
   errors on both sides). Also 60,000 on the $( build, 0 different.
