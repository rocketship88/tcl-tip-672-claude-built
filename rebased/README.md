# rebased/ : the CURRENT state of the change

Source of truth: the Fossil branch `tip-672-v2` at https://core.tcl-lang.org/tcl , leaf check-in `fbb7b018f2`
(2026-11-17, jan.nijtmans, "Fix Tcl_ParseVarName(), so it never returns the new token. patch provided by Eric Taylor").
This folder is only a convenient copy of it.

| Path | Contents |
|---|---|
| `orig/` | the 16 changed files as they are in trunk, at the check-in `tip-672-v2` was rebased onto (Fossil `6e7c8299c5`, 2026-11-11) |
| `new/` | the same 16 files at `fbb7b018f2` (same relative paths as in the Tcl tree) |
| `tip-672-full.patch` | the whole feature: `orig/` to `new/`. 16 files, 1380 lines added, 48 removed. Apply to a tree at that trunk check-in with `patch -p1` or `git apply` |
| `fix-fbb7b018f2.patch` | only the last check-in (the Tcl_ParseVar fix, 6 files). Fossil format (`Index:` headers, no prefixes): apply with `patch -p0` to a tree at the rebase check-in `715e7cce27` |

The 16 files: doc/ParseCmd.3, doc/SubstObj.3, doc/Tcl.n, doc/subst.n, generic/tcl.h, generic/tclCmdMZ.c,
generic/tclCompCmdsSZ.c, generic/tclCompExpr.c, generic/tclCompile.c, generic/tclInt.h, generic/tclParse.c,
generic/tclTest.c, tests/compile.test, tests/parse.test, tests/parseOld.test, tests/subst.test.

Size of the whole change (added lines): core C and headers 508 (302 code, 172 comments, 34 blank); tests 765; docs 107.

The top-level `orig/`, `new/` and `extras/expr-subst.patch` are the PRE-rebase version (trunk 77ac0bb). They are kept
because the test, mutation, coverage, fuzz and Valgrind results in `extras/` were measured on them. Do not apply them.
