# TIP 672: Extend $ substitution to include expressions as $(expression)

	Author:		Eric Taylor
	State:		Draft
	Type:		Project
	Created:	2023-06-06
	Tcl-Version:	9.1
	Tcl-Branch:	tip-672-v2
-----

# Abstract

This TIP extends the $ substitution to include expressions as
$(expression).

The expression is parsed once, by the Tcl parser itself, as if it were the
braced argument of `expr`, so it is never substituted twice. The reference
implementation can also be built to use the spelling `$((expression))`,
which changes no existing script; see the Specification and the open
questions at the end.

# Rationale and Discussion

The current method for expressions using the `[expr]` command has 2
problems. First, it is difficult to BOTH read and write. Some, as in
TIP 282, go so far as to say it is ugly.

Secondly, as indicated in TIP 526, expressions should be braced, or
there can be problems with both security and performance.

Consider the following computation (from TIP 282):
```
  set x [expr {5*$y + 6*$z}]
  set w [expr {$x**2 + $y**2}]
  set v [expr {$w**2 + $y**2}]
```
The `[expr {...}]` constructs make the code considerably harder to
read. This TIP would propose that there be a shorthand as such:
```
  set x $(5*$y + 6*$z)
  set w $($x**2 + $y**2)
  set v $($w**2 + $y**2)
```
The implementation of this should also eliminate the requirement for
the braces from above, as braces would be assumed and code would be
compiled as though the parentheses were braces.

Since this is a `$` substitution, it would continue to work inside
double quotes with the expected result.

There would also be an advantage in some text editors, which already have 
parenthesis balancing and syntax coloring features.

Another Tcl implementation, JimTcl uses this `$(...)` substitution and it 
seems to work without problems.

# Version and Incompatibility

This TIP would apply to version 9. of Tcl. Since 9.* would be a major
release, it should allow for some incompatibilities.

One incompatibility is that it would require that the use of the null string `""` 
or `{}` as an array name would require a change from using $ substituion to using 
the 2 argument form of the set command. (This applies only to the `$(expression)`
spelling. With the `$((expression))` spelling there is no such incompatibility: 
an unescaped `(` inside an array index is already an error in Tcl 9.1, so `$((`
cannot occur in a script that works today.)

Thus, to assign the variable `""` to a value, would still work for both scalars 
and array variables, as in:
```
  set {} foobar             ;# scalar variable
  set (index) "array value" ;# array variable
```
But the use of `$(index)` would have to change by using the set command:

```
  set var [set (index)]
```

One other possible incompatibility would be with the use of the `subst` command.
The issue here is whether `$(...)` would be a command or variable substitution
that subst has options to suppress. The reference implementation solves this
with two new options of the `subst` command, `-expressions` and
`-noexpressions` (the shorter `-expr` and `-noexpr` work as unique
abbreviations). Because the body of an expression can contain `[commands]`
and `$variables`, `-nocommands` and `-novariables` also turn expression
substitution off. Code that uses them to make text safe therefore behaves as
before.

## Migration

The `$((expression))` spelling is also a safe way to start using the new
substitution today. If Tcl later changes to the `$(expression)` spelling, and
deprecates the use of an array with no name, scripts that already use
`$((expression))` continue to work with the same value: the `$(` spelling
accepts `$((expression))` as `$(` followed by a parenthesised expression.
The test suite runs `$((...))` in both builds. Only scripts that use the empty
array name, as in `$(index)`, would need the change described above.

# Examples

The examples use the proposed `$(expression)` spelling.

```
  % lassign {3.0 4.0} a b
  % set c $( sqrt($a**2 + $b**2) ) ;# 3 4 5 triangle
  5.0

  % lassign {1000 3} total number
  % puts "ave = $( double($total)/$number )" ;# demo usage inside quotes
  ave = 333.333333333

  .canvas addtag enclosed $($x - 20)  $($x + 20)  $($y - 20)  $($y + 20) 

```

With the alternative spelling, the first example reads:

```
  % set c $(( sqrt($a**2 + $b**2) ))
  5.0
```

Inside `subst`:

```
  % set n 4
  % subst {n squared is $($n**2)}
  n squared is 16
  % subst -noexpressions {n squared is $($n**2)}
  n squared is $(4**2)
```

With `-noexpressions` the `$(` is left as ordinary text, and the `$n` inside it is
still substituted as a variable.

Inside an expression, including a braced one such as the condition of `if`
or `while`:

```
  % set x 5
  % expr {1 + $($x*2)}
  11
  % if {$($x*2) > 9} {puts big}
  big
  % expr {$($x + $(2*3))}   ;# nested
  11
```

This works because the expression parser uses the same `$` substitution
parsing as the script parser. No new code was needed in `expr` itself beyond
accepting the new token as an operand (a one-line change in
`generic/tclCompExpr.c`).

# Specification

## Syntax

The new substitution is recognised wherever `$` substitution is: in words,
inside double quotes, in `subst`, in `Tcl_ParseVar`, and inside expressions
(for example `expr {1 + $(2*3)}` or the condition of an `if`), where it can
also be nested.
It has the value of `[expr {body}]`, evaluated in the current scope, with the
same result and the same error and return-code behaviour (including `return`,
`break` and `error` inside a `[command]` in the body).

There are two spellings, chosen when Tcl is built (see Build switch):

 * `$(body)`. The proposed spelling.
 * `$((body))`. Valid in both builds. The two outer parentheses play the
   role of the braces in `[expr {body}]`, which makes the body easy to see.

The body ends at the first `)` that is not nested inside parentheses opened
in the body, a braced word, a double-quoted string, or a `[command]`. A
backslash protects the next character. In the `$((` spelling the closing `)`
must be followed immediately by a second `)`, otherwise the text is a syntax
error with the message `missing second ")"`. If the input ends right there,
the command is incomplete, so an interactive tclsh waits for more input.

The body is passed to the expression compiler exactly as the argument of a
braced `expr` would be. The word parser does not substitute anything in it,
so nothing is substituted twice.

## The subst command

`subst` gets `-expressions` and `-noexpressions`. `-nocommands` and
`-novariables` also switch expression substitution off (see above).

The `subst` command in current trunk (TIP 712) also has positive forms:
`-backslashes`, `-commands`, `-variables` and `-expressions` turn on only the
substitutions named and leave every other kind off. For example,
`subst -variables $s` substitutes variables and nothing else. This makes
`-expressions` an explicit opt-in: a list of positive options that does not
name it does not substitute expressions. Positive and negative options cannot
be mixed in one call; `subst -expressions -novariables $s` is the error
`cannot combine positive and negative options`. With no options at all,
everything is substituted, including expressions, as before.

## C interface

`Tcl_ParseVarName` (and so `Tcl_ParseCommand` and `Tcl_ParseVar`) can
return a token of a new type, `TCL_TOKEN_EXPR_SUBST` (value 512). It spans the text from the `$` through the closing parenthesis,
`numComponents` is 1, and the one component is a `TCL_TOKEN_TEXT` holding the
body, which is not parsed further. A new flag, `TCL_SUBST_EXPRESSIONS`, is
used by `Tcl_SubstObj`. `TCL_SUBST_ALL` grows from 7 to
15 so that existing callers passing `TCL_SUBST_ALL` get the new
substitution. Code that walks the tokens of a parse with a `switch` and no
`default` case needs a new case. In the default build only text containing
`$((` can produce the new token, so a script that does not contain it is
unaffected.

## Build switch

`TCL_EXPR_SUBST_PARENS` is a compile-time constant: 2 (the default) means the
trigger is `$((`, 1 means `$(`. Only one source file, `tclParse.c`, depends
on it. The core team can choose the spelling by changing one number.

# Open Questions

 1. Which spelling: `$(expression)` or `$((expression))`. The first is
    shorter and is what this TIP proposes; the second changes no existing
    script. A script written with `$((...))` works under both.
 2. The option names (`-expressions`/`-noexpressions`).
 3. Whether `TCL_SUBST_ALL` should change from 7 to 15 in `tcl.h`.
 4. Whether `-nocommands` and `-novariables` should also turn expression
    substitution off, or only the explicit `-noexpressions`.
 5. The new public token type, `TCL_TOKEN_EXPR_SUBST`.

# Implementation

See branch [`tip-672-v2`](https://core.tcl-lang.org/tcl/timeline?r=tip-672-v2)

The shortcut is implemented in the parser (`Tcl_ParseVarName` in
`generic/tclParse.c`, with the compile-time and run-time handling in
`tclCompile.c` and `TclSubstTokens`), not by rewriting text. For a constant
expression `$(1+2)` compiles to the same bytecode as `[expr {1+2}]`. In
instructions executed, running through `eval` is about 3% cheaper and
compiling in a proc about 4% cheaper.

The change comes with documentation (`Tcl.n`, `subst.n`, `ParseCmd.3`,
`SubstObj.3`) and 107 new tests in `parse.test`, `subst.test`,
`compile.test` and `parseOld.test`. The full test suite passes in both
spellings on Linux and Windows. The new code was also run under Valgrind,
AddressSanitizer and the Tcl memory-debug build with no errors, and checked
by mutation testing.

# Copyright

This document has been placed in the public domain.

