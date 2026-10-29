# Changes made

Here are the lines I added, per file, against trunk 77ac0bb (final code and tests, after the mutation-testing round). Source and test files are split into code, comment and blank lines. I counted comments from the full new file, so lines inside a multi-line `/* ... */` block count as comments, and a line with code plus a trailing comment counts as code.

| File | Code | Comment | Blank | Total added | Removed |
|---|---:|---:|---:|---:|---:|
| `generic/tclParse.c` | 137 | 81 | 16 | 234 | 0 |
| `generic/tclCompile.c` | 14 | 5 | 3 | 22 | 0 |
| `generic/tcl.h` | 1 | 12 | 0 | 13 | 0 |
| `generic/tclCompCmdsSZ.c` | 5 | 0 | 0 | 5 | 0 |
| `generic/tclTest.c` | 3 | 0 | 0 | 3 | 0 |
| `generic/tclCompExpr.c` | 2 | 0 | 0 | 2 | 1 |
| **Source subtotal** | **162** | **98** | **19** | **279** | **1** |
| `tests/parse.test` | 302 | 30 | 18 | 350 | 1 |
| `tests/compile.test` | 126 | 3 | 1 | 130 | 0 |
| `tests/parseOld.test` | 6 | 2 | 0 | 8 | 1 |
| **Test subtotal** | **434** | **35** | **19** | **488** | **2** |
| `doc/Tcl.n` | 34 | n/a | 0 | 34 | 4 |
| `doc/ParseCmd.3` | 12 | n/a | 0 | 12 | 0 |
| **Doc subtotal** | **46** | **n/a** | **0** | **46** | **4** |
| **Total** | **642** | **133** | **38** | **813** | **7** |

- **Doc files:** they are nroff, so I counted every text line under "code" and didn't try to separate comments.
- **Removed lines:** the 3 removals are existing lines that I edited in place, not deleted code. They are one condition in `tclCompExpr.c` and the headers of `parse-18.12` and `parseOld-5.12`. Each also appears in the added column as its replacement.
- **Biggest part:** `tclParse.c` is about 84% of the source change (234 of 279 lines). Most of it is the body scanner (`SkipExprSubstScan` and `FindExprSubstEnd`) and its comments, and the mode-selection comment near the top accounts for much of the rest.
- **Why `tcl.h` has so many comments:** it's one new `#define` and 12 lines of documentation for the new token type.
- **Why the test files grew:** the mutation-testing round added about 220 lines of tests (scanner details, the uncompiled paths, truncated input, a memory-leak test and `getbytecode` checks). See `mutation_testing.md`.

## Addendum: `subst` options (lines added / removed, `git diff --numstat`)

| File | Added | Removed |
|---|---:|---:|
| `generic/tclCmdMZ.c` | 19 | 3 |
| `generic/tcl.h` (flag, in addition to the earlier token change; totals now 15 / 1) | 2 | 0 |
| `generic/tclParse.c` (`ParseTokens` gate, in addition to the earlier change; totals now 244 / 1) | 10 | 0 |
| `doc/subst.n` | 20 | 6 |
| `doc/SubstObj.3` | 8 | 3 |
| `tests/subst.test` | 54 | 5 |
