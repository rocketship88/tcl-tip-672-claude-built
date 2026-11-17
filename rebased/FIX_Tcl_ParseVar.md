# The Tcl_ParseVar / Tcl_ParseVarName fix (Nov 16 to 17, 2026)

Fossil check-in `fbb7b018f2` on `tip-672-v2` ("Fix Tcl_ParseVarName(), so it never returns the new token. patch provided by Eric Taylor"),
committed by Jan Nijtmans, 2026-11-17 09:27 UTC. The patch is `fix-fbb7b018f2.patch` in this folder (6 files, Fossil format).
`tip-672-full.patch` already contains it.

## What was wrong (reported by Florent Merlet on the TIP forum, during the vote)

`Tcl_ParseVar` returns a `const char *` that callers assume is the value of a variable, valid like any variable value (for example, call
it twice and use both strings, or pass the string to `Tcl_AppendResult`). The first version of this feature let `Tcl_ParseVarName`
(and so `Tcl_ParseVar`) return the new `TCL_TOKEN_EXPR_SUBST` token, so `Tcl_ParseVar("$((1000+1))", ...)` evaluated the expression.
The value of an expression is held by nobody except the interpreter result, so the returned pointer stayed valid only until the interp
result next changed. A later `Tcl_ParseVar` call, or `Tcl_AppendResult`, invalidated it. The API documentation also says `Tcl_ParseVarName`
parses a variable reference, and the new token broke that contract for C callers.

Reproduction: `repro/parsevar_repro.c` (build against a static libtcl of the tree under test: `cc parsevar_repro.c -I generic -I unix libtcl9.1.a -lm -lz -ldl -lpthread`; this was run on Linux).
Output before the fix (wrong, and the two expression values should differ):

    vars : a=<10> b=<20>
    exprs: a=<2002> b=<2002>
    var : value is 10 (ok)
    expr: 1001value is 1001 (ok)

Output after the fix, and also what a stock Tcl 9.0/9.1 build prints:

    vars : a=<10> b=<20>
    exprs: a=<(null)> b=<(null)>
    var : value is 10 (ok)
    expr: invalid character in array indexvalue is (null) (ok)

(`$((` is not an expression for these two functions any more. It is parsed as in stock Tcl, as an array element with the empty name, and
the "(" in the index is the error "invalid character in array index".)

## Lineage (why the code looked the way it did)

1. Original design: `Tcl_ParseVarName` produced the expression token; `Tcl_ParseVar` evaluated it with `TclSubstTokens`.
2. AddressSanitizer found a use-after-free in that: `Tcl_ParseVar` reset the interp result before returning its string. A first fix
   (an `isExprSubst` flag in `Tcl_ParseVar`, keep the result alive, test `parse-22.5`) made the string valid until the interp result next changes.
   This is the "real bug in Tcl_ParseVar" in extras/mutation_testing.md. It was not enough: "until the result next changes" is not a
   guarantee callers of `Tcl_ParseVar` can use.
3. Florent's report (Nov 16, forum posts 18 to 20) pointed at the contract itself.
4. The fix (this document): the public functions never produce the token.

## The fix

* `generic/tclParse.c`: the body of `Tcl_ParseVarName` moved into a new internal function
  `TclParseVarName(interp, start, numBytes, parsePtr, append, exprSubst)`. The `$(` / `$((` branch now starts `exprSubst && ...`.
  The public `Tcl_ParseVarName` is one line: `return TclParseVarName(interp, start, numBytes, parsePtr, append, 0);`.
  `ParseTokens` calls `TclParseVarName(..., 1, 1)`. `Tcl_ParseVar` is back to the stock code (the `isExprSubst` flag and its comment are gone).
* `generic/tclInt.h`: `MODULE_SCOPE` declaration of `TclParseVarName`.
* `generic/tclCompExpr.c`: `ParseExpr` calls `TclParseVarName(NULL, start, numBytes, parsePtr, 1, 1)` (the expression parser still needs the token).
* `generic/tclTest.c`: `testparsevar varName ?varName2?` can hold two `Tcl_ParseVar` results at once.
* `doc/ParseCmd.3`: says which functions can return `TCL_TOKEN_EXPR_SUBST` (`Tcl_ParseCommand`, `Tcl_ParseExpr`, and the others that parse a
  whole word or expression) and that `Tcl_ParseVarName` and `Tcl_ParseVar` never do.
* `tests/parse.test`: `parse-22.4` and `22.5` now expect the stock error `invalid character in array index`; new `22.5.1` to `22.5.3`
  (two values stay valid together, array elements, interp result reset after a variable); `22.93` (no truncated prefix is accepted)
  uses `testparser`; the memory test `22.80` uses `catch` for the now-failing call.
* Size: about 26 net core lines (tclParse.c +22/-3, tclInt.h +3, tclCompExpr.c +1/-1), tests +30, doc +5. No behaviour of
  `$((expr))` in scripts, `subst` or the compiler changes. Only C callers of the two public functions are affected, and they get exactly the
  Tcl 9.0 behaviour back. The TIP text was changed by Jan to say so (he edited the TIP, no new vote was needed, per his forum post 21).

## Checks

* Full suite on the tree with the fix (Jan's rebase 715e7cce27 plus the six files): 509601 tests, 0 failed, both spellings
  (the cmdAH timestamp test is environmental).
* Mutation testing of only the lines the fix changed (`extras2/fbb7b018f2_checks/mutation_fix_only/`): 6 of 6 mutants killed in both builds.
  The mutants: wrapper flag 0 to 1, drop `exprSubst &&`, negate it, `&&` to `||`, `ParseTokens` caller flag 1 to 0, `ParseExpr` caller flag 1 to 0.
* gcov of all new or changed lines on this tree: 98.3 percent on the default build (`extras2/fbb7b018f2_checks/gcov/`).
* Stepper v2 (extras2/parser_stepper_v2.html) shows the change as hunks 5 (wrapper and internal function) and 7 to 8, and as reviewer question 7.

## Alternatives that were considered

* Keep the old behaviour and document that the returned string is valid only until the interp result changes: rejected, callers of
  `Tcl_ParseVar` cannot know when that is.
* Make `Tcl_ParseVar` return a string that lives longer (copy it into the interpreter or an object kept alive): changes the API contract and leaks or
  needs a new free rule.
* Florent's separate TIP 759 approach (read from his branch `tip-759a-tcl91-subst`): a `[(` form, found by running the expression parser in a
  parse-only mode, reusing `TCL_TOKEN_SUB_EXPR`. It leaves `Tcl_ParseVarName` and `Tcl_ParseVar` untouched, which is the property the fix gives here.
