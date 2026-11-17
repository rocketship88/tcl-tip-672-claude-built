# Tcl expression substitution: `$((expr))` / `$(expr)`  (TIP 672)

A change to the Tcl parser that adds a shortcut for `[expr {...}]`, usable wherever `$` substitution works:

    set x $((1 + 2 * 3))        ;# same as: set x [expr {1 + 2 * 3}]

The syntax is optional: `expr` and `[expr {...}]` are unchanged, and `$((` cannot occur in a working script today.
A build switch, `TCL_EXPR_SUBST_PARENS`, chooses the trigger: `$((` (default) or `$(`.

The code was written by Claude (Anthropic) under the direction of Eric Taylor, rebased and committed by Jan Nijtmans.
The official source is the Fossil branch `tip-672-v2` at https://core.tcl-lang.org/tcl .

## Where to start

| What | Where |
|---|---|
| The current code (16 files), the full patch, the last fix | `rebased/` (read `rebased/README.md`) |
| Why it is designed this way, test results | `extras/design_and_results.md`, `extras/NOTES.txt` (newest section first) |
| Interactive review and step-through of the parser changes (current, version 3.0) | `extras2/parser_stepper_v2.html` |
| The same, first version (pre-rebase) | `extras/parser_stepper.html` |
| What the Florent Merlet defect (Tcl_ParseVar) was and how it was fixed | `rebased/FIX_Tcl_ParseVar.md` |
| How to use this repo with Claude | `claude_notes.md` |

## Layout

| Folder | Contents |
|---|---|
| `rebased/` | CURRENT: files at trunk and at `fbb7b018f2`, full patch, fix patch |
| `orig/`, `new/` | PRE-REBASE history (trunk 77ac0bb); the test, mutation, coverage and fuzz results were measured on these |
| `extras/`, `extras2/` | notes, patches, tests, mutation, coverage, fuzz and memory-check scripts and logs, the stepper |

## Licence

The Tcl files carry the Tcl licence (`tcl_license.terms`). The rest is under the MIT licence (`LICENSE`).
