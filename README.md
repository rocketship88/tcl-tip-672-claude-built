# Tcl expression substitution: `$((expr))` / `$(expr)`

*Placeholder README, to be replaced.*

A proof-of-concept patch for Tcl (based on trunk 77ac0bb, Tcl 9.1.1) that adds a shortcut for `[expr {...}]`
in the real parser, usable wherever `$` substitution works:

    set x $((1 + 2 * 3))        ;# same as: set x [expr {1 + 2 * 3}]

This goes with TIP 672. A build switch, `TCL_EXPR_SUBST_PARENS`, chooses the trigger: `$((` (default) or `$(`.

## Layout

| Folder | Contents |
|---|---|
| `orig/` | the original Tcl files that were changed |
| `new/` | the changed files (source, docs, tests), same paths as in the Tcl tree |
| `extras/` | notes, the patch, test, mutation and gcov coverage results, fuzz/NUL-sweep and memory-check scripts and logs, and the interactive parser stepper (`extras/parser_stepper.html`) |

Start with `extras/NOTES.txt` and `extras/design_and_results.md`.

## Licence

The Tcl files carry the Tcl licence (`tcl_license.terms`). The rest is under the MIT licence (`LICENSE`).

Interactive review and step-by-step walkthrough of the parser changes (served by GitHub Pages):
https://rocketship88.github.io/tcl-tip-672-claude-built/extras/parser_stepper.html
