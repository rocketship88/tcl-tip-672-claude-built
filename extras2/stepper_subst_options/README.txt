Extra stepper sources (stepper v1.8, "subst options": pick any combination of the eight options)

Put these three files next to build_page.py in extras/scripts/stepper/ (they are kept here only because extras/
is at the 100-file upload limit).

  gen_substall.tcl   run once per build:  TCL_LIBRARY=<tcl>/library tclsh gen_substall.tcl > substallN.json
                     (N = 1 for the "$(" build, 2 for the default "$((" build). It runs
                     subst <options> {$((1+2)) $x [set y 7]}  for all 256 combinations of the eight options,
                     with x = 5, and records the real result of each. 225 of them are the error
                     "cannot combine positive and negative options"; 31 are valid.
  substall1.json     the real results from the "$(" build
  substall2.json     the real results from the default "$((" build

build_page.py reads substall1.json / substall2.json from its own directory and adds them to the page data.
Check after any change: the page has window.__stepper.all(), which runs every trace (265 per build) and returns the
self-check of each; all must be "ok" (tested with Playwright, see extras/scripts/stepper/check.js).
