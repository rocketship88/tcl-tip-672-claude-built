# Reviewer notes, keyed by (file, hunk number in that file). Facts here were checked on the build; see design_and_results.md.
NOTES = {('generic/tcl.h', 1): {'title': 'New subst flag TCL_SUBST_EXPRESSIONS',
                        'what': 'One new bit (010) for Tcl_SubstObj and ParseTokens, and TCL_SUBST_ALL grows from 007 to 017 so existing callers that pass ALL get the new syntax.',
                        'check': 'Callers that compiled in the literal 7 (not the macro) will not get expression substitution; that is the safe direction. Is changing the value of TCL_SUBST_ALL '
                                 'acceptable for a public header?',
                        'tests': 'subst-expr-1.1 to 1.13'},
 ('generic/tcl.h', 2): {'title': 'Document the new token type',
                        'what': 'A comment block describing TCL_TOKEN_EXPR_SUBST: spans from the $ through the matching ), numComponents is always 1, the one following token is a TEXT token with the '
                                'raw body.',
                        'check': 'Tcl_Token is public API. Is the description of the token layout the one we want to commit to?',
                        'tests': 'parse-22.1 to 22.6 (token structure through testparser, testparsevarname, testparsevar)'},
 ('generic/tcl.h', 3): {'title': 'New token value 512',
                        'what': 'One #define, the next free bit after TCL_TOKEN_EXPAND_WORD (256).',
                        'check': 'Extensions that walk Tcl_Parse tokens with a switch and no default would not know this type. Only a script that contains the new syntax produces it (in the default '
                                 'build, only text containing "$((").',
                        'tests': 'parse-22.1 to 22.4'},
 ('generic/tclCompCmdsSZ.c', 1): {'title': 'Compile [subst] with a literal argument',
                                  'what': 'The second switch in TclSubstCompile (the one that emits code inside the catch range) compiles the body with TclCompileExpr, like the TEXT/VARIABLE cases '
                                          'next to it.',
                                  'check': 'Same call and arguments as the compiler uses for a braced [expr] word. The bytecode is identical to [expr {(body)}].',
                                  'tests': 'parse-22.23 (subst), 22.40 (compiled and uncompiled equivalence), compile-21.1 to 21.10 (disassemble and getbytecode)'},
 ('generic/tclCompile.c', 1): {'title': 'Compile the token in a word',
                               'what': 'New case in TclCompileTokens: flush pending literal text, check the nesting depth, compile the body with TclCompileExpr, count one more object to concatenate. '
                                       'The depth check is the same one TclCompileScript makes (numLevels against maxNestingDepth, with the 5/4 factor, error code TCL LIMIT STACK). It is needed '
                                       'because $((...)) nested inside $((...)) recurses through TclCompileExpr and TclCompileTokens without ever passing TclCompileScript: without it, about 20000 '
                                       'levels overflow the C stack. This check was found by reading this review.',
                               'check': 'The envPtr->line += adjust / -= adjust pair mirrors the COMMAND case. No test could tell whether it matters (two surviving mutants). Keep or drop?',
                               'tests': 'parse-22.10 to 22.13, 22.28, 22.29 (line numbers), parse-22.110 to 22.113 (nesting depth), compile-21.9 and 21.10 (error lines)'},
 ('generic/tclCmdMZ.c', 1): {'title': 'subst: option names, flags and the "no" masks',
                             'what': 'Changed by Jan Nijtmans in his rebase (Nov 12). The option table gets -expressions and -noexpressions, and the options are listed in alphabetical order (the '
                                     'flag table is in the same order). A positive option maps to its bit. A negated option maps to the bit shifted left by 16, and in the table -nocommands and '
                                     '-novariables also carry the EXPRESSIONS bit: (COMMANDS|EXPRESSIONS) << 16 and (VARIABLES|EXPRESSIONS) << 16. When the "no" options are applied (flags = ALL & '
                                     '~(flags >> 16)) they therefore turn expression substitution off too. The body of an expression can run commands, and $((...)) is "$" syntax, so scripts that use '
                                     'subst -nocommands or -novariables to make text safe keep doing so. The positive -expressions is an explicit opt-in.',
                             'check': 'This is the answer to the earlier -nocommands question. It is table-driven now: there is no separate "clear the expressions bit" step. Consequence: subst '
                                      '-nobackslashes keeps expressions, but there is no way to get "no commands but yes expressions" except -expressions -variables, where commands in the body run. '
                                      'Option names: unique prefixes still work, but "-no" was ambiguous before and still is.',
                             'tests': 'subst-1.2, subst-7.1, subst-expr-1.1 to 1.13'},
 ('generic/tclCmdMZ.c', 2): {'title': 'subst: usage message',
                             'what': 'Changed by Jan Nijtmans in his rebase (Nov 12). With no arguments the message lists the new options. It is built as two usage lines (positive options, then the '
                                     '"no" options) with the INTERP_ALTERNATE_WRONG_ARGS flag set between the two Tcl_WrongNumArgs calls, so the error reads as two alternatives.',
                             'check': 'Only the message text and its construction changed. Tests for the message were updated (subst-1.1).',
                             'tests': 'subst-1.1'},
 ('generic/tclCompExpr.c', 1): {'title': 'Expression parser: use the internal variable parser',
                                'what': 'Part of the fix for the Tcl_ParseVar report (patch by Eric Taylor, committed by Jan Nijtmans as fbb7b018f2). In ParseExpr the VARIABLE case now calls '
                                        'TclParseVarName(..., 1, 1) (append, exprSubst = 1) instead of the public Tcl_ParseVarName. The expression lexer needs the expression form so that $((...)) '
                                        'can be an operand, and the public function no longer provides it.',
                                'check': 'One-line change. With the last argument 0 the lexer would parse "$((" as a variable with the empty name, which is an error.',
                                'tests': 'parse-22.20, 22.24, 22.25 (mutation: killed)'},
 ('generic/tclCompExpr.c', 2): {'title': 'Let the expression lexer accept the token',
                                'what': 'In ParseExpr, the check that a substitution token is a VARIABLE (so it can be an operand) also accepts EXPR_SUBST. This is what makes expr {$((1+1))*2} work.',
                                'check': 'The only change to existing logic in the patch: one condition widened. Without it the lexer rejects the token.',
                                'tests': 'parse-22.24 (in an expression), 22.20 (nested)'},
 ('generic/tclInt.h', 1): {'title': 'Declare the internal variable parser',
                           'what': 'Part of the fix for the Tcl_ParseVar report (patch by Eric Taylor, committed by Jan Nijtmans as fbb7b018f2). TclParseVarName(interp, start, numBytes, parsePtr, '
                                   'append, exprSubst) is declared MODULE_SCOPE: the same arguments as Tcl_ParseVarName plus a flag that says whether an expression substitution is recognized.',
                           'check': 'Not public. The public Tcl_ParseVarName keeps its Tcl 9.0 signature and behaviour.',
                           'tests': 'used by every parse-22 test; parse-22.4 and 22.5 test the public side'},
 ('generic/tclParse.c', 1): {'title': 'Build switch, depth limit and prototype',
                             'what': 'TCL_EXPR_SUBST_PARENS: 2 (default) means the trigger is $((, 1 means $(. Anything else is an #error. The comment explains why: $() is an element of the array '
                                     'with the empty name. Also here: EXPR_SUBST_MAX_SCAN_DEPTH (1000, the same number as the default recursion limit), the most levels of nested [ that the scanner '
                                     'follows, and the object whose address (EXPR_SUBST_TOO_DEEP) the scanner returns when that is exceeded. Jan Nijtmans changed the default in his rebase: when '
                                     'TCL_NO_DEPRECATED is defined (it is not by default, on Unix or Windows) the default becomes 1, the $( spelling; a normal build still uses $((.',
                             'check': 'The default keeps every script that does not contain "$((" unchanged. With 1, every "$(" in existing scripts changes meaning. In both builds the body is the '
                                      'text between the outer parentheses, so $((expr)) means the same thing under either setting. The depth limit is a plain #define inside #ifndef, so the core team '
                                      'can change the number in one place or override it with -DEXPR_SUBST_MAX_SCAN_DEPTH=n; 1000 was chosen because it is the default for interp recursionlimit.',
                             'tests': 'parse-22.50 to 22.53 (spellings), parse-22.99 (checks the build with TCL_TEST_EXPR_SUBST_PARENS), parse-22.114 to 22.118 (the depth limit)'},
 ('generic/tclParse.c', 2): {'title': 'ParseTokens: honour the flag',
                             'what': 'In the "$" case, decide first whether the text is the expression form ("$((" or "$("); if so it is substituted only when TCL_SUBST_EXPRESSIONS is set, otherwise '
                                     '(and for ordinary variables, when TCL_SUBST_VARIABLES is clear) the "$" becomes a literal text token. This also lets -expressions work without -variables.',
                             'check': 'The test for the expression form looks at two or three bytes before TclParseVarName; the scanner is not involved when disabled, so unbalanced parentheses are '
                                      'not an error then.',
                             'tests': 'subst-expr-1.1, 1.2, 1.10'},
 ('generic/tclParse.c', 3): {'title': 'ParseTokens: call the internal parser',
                             'what': 'Part of the fix for the Tcl_ParseVar report (patch by Eric Taylor, committed by Jan Nijtmans as fbb7b018f2). The "$" case calls TclParseVarName(..., 1, 1) '
                                     'instead of Tcl_ParseVarName. ParseTokens is the one place in the parser that is allowed to produce the expression token, so it asks for it.',
                             'check': 'Pairs with the next-but-one hunks: the public function passes 0 and never returns the new token.',
                             'tests': 'parse-22.1 to 22.6, subst-expr-1.1'},
 ('generic/tclParse.c', 4): {'title': 'The scanner',
                             'what': 'SkipExprSubstScan finds the matching ")". It skips braced words, quoted strings, backslash pairs and [commands] (by calling itself), and counts nested '
                                     'parentheses. FindExprSubstEnd is a one-line wrapper. The function has a level argument: 0 from FindExprSubstEnd, plus one for every nested [ (and every [ inside '
                                     'a quoted string). The first thing it does is return EXPR_SUBST_TOO_DEEP if level is above EXPR_SUBST_MAX_SCAN_DEPTH (1000); the two recursive calls pass that '
                                     'sentinel up unchanged instead of turning it into NULL.',
                             'check': 'This duplicates, in small form, rules the word parser and the expression parser already have. If they disagree, the symptom is a wrong end position. Worth '
                                      'reading closely. Mutants of the scanner that survive are boundary checks at the end of the text, each protected by a second guard (classified as equivalent). '
                                      'DEPTH LIMIT (added Oct 27): before this change the scanner called itself once per nested [ with no limit. Measured on Linux with an 8 MB stack and an '
                                      'unterminated $((llength [list [list ... : fine at 200,000 levels, segfault at about 300,000 (the unmodified parser, on similar text without $((, already '
                                      'segfaults between 20,000 and 50,000 levels). With the limit the stack use of the scanner is bounded by about 1000 small frames: 5,000,000 nested [ now give the '
                                      'error "expression substitution nested too deeply" (error code TCL LIMIT STACK) instead of a crash. Not measured: the Windows build, whose stack is smaller; a '
                                      'frame holds a few pointers and ints, so 1000 of them should be far below 1 MB, but that is an estimate. The number is a plain choice (Eric T. set it to 1000) '
                                      'and can be changed in one place.',
                             'tests': 'parse-22.17 to 22.19, 22.30 to 22.33, 22.60 to 22.69 (scanner, unterminated, info complete), 22.86 to 22.94 (outer braces and quotes), 22.93 (no truncated '
                                      'prefix is ever accepted), 22.114 to 22.118 (depth limit: nested commands still work, exactly 1000 levels, 1001 levels, 2,000,000 levels, and inside a quoted '
                                      'string)'},
 ('generic/tclParse.c', 5): {'title': 'Tcl_ParseVarName is a wrapper; TclParseVarName does the work',
                             'what': 'Part of the fix for the Tcl_ParseVar report (patch by Eric Taylor, committed by Jan Nijtmans as fbb7b018f2). The old body moves, unchanged apart from the new '
                                     'condition, into the internal function TclParseVarName with one extra parameter, exprSubst. The public Tcl_ParseVarName becomes a one-line wrapper: return '
                                     'TclParseVarName(interp, start, numBytes, parsePtr, append, 0). The header comment says so. Tcl_ParseVar (the public function that returns a string) is back to '
                                     'stock, so it never evaluates an expression and the string it returns is always the value of a variable.',
                             'check': "This is the fix for Florent Merlet's report during the vote: Tcl_ParseVar returned a pointer into the interpreter result for an expression, which a later call "
                                      'could invalidate. Now the public functions behave exactly as in Tcl 9.0 ("$((" is parsed as an empty-name array and reports "invalid character in array '
                                      'index"). Is this the right place to draw the line between public and internal?',
                             'tests': 'parse-22.4, 22.5 (error as in stock Tcl), 22.5.1 to 22.5.3 (two values stay valid); mutation: 6 of 6 mutants of the changed lines killed in both builds'},
 ('generic/tclParse.c', 6): {'title': 'Hook in TclParseVarName',
                             'what': 'A new branch before the ordinary name path, taken only when exprSubst is non-zero (the internal function called by the parser and the expression parser; the '
                                     'public function passes 0): if the next character is "(" and the build switch allows it, scan for the first ")" that balances the parentheses inside the body, '
                                     'relabel the VARIABLE token as EXPR_SUBST, and make one TEXT token that points at the body. The body is never parsed here. In the default build the trigger is '
                                     '"$((", the body ends at that first balancing ")", and the next character must be a second ")" (look-ahead): otherwise it is a syntax error (missing second ")" '
                                     'at _@_, followed by the quoted text with the marker after the first ")"; not incomplete). So $((1+2)*3) and $((  1+2)*3  )) are errors, and $(((1+2)*3)) is the '
                                     'way to write it. In the single-paren build there is no look-ahead. If the scanner returns EXPR_SUBST_TOO_DEEP the code sets the error "expression substitution '
                                     'nested too deeply" with error code TCL LIMIT STACK, errorType TCL_PARSE_SYNTAX, and does not mark the parse incomplete (more input could not fix it). The '
                                     '"exprSubst &&" at the start of that condition is the part added by the Tcl_ParseVar fix (Eric Taylor, fbb7b018f2).',
                             'check': 'No closing ")" at all -> "missing )"; the first ")" found but the text ends before the second -> the same missing second ")" message; both with incomplete=1 so '
                                      'interactive shells keep reading; a wrong character -> TCL_PARSE_SYNTAX, not incomplete; more than 1000 levels of nested [ -> the same TCL_PARSE_SYNTAX class, '
                                      'with its own message and the error code TCL LIMIT STACK. The errorType values cannot be seen from a script (parse-22.97 checks the message). In Tcl 9.1 the '
                                      'index of "$(" already rejects an unescaped "(" ("invalid character in array index"), so "$((" and "$( (" were errors before; only "$(" with no "(", quote or '
                                      'brace before the ")" is a legal empty-name array today.',
                             'tests': 'parse-22.1 to 22.6, 22.30 to 22.32, 22.50 to 22.53, 22.90 to 22.98a, 22.115 to 22.118 (too deep)'},
 ('generic/tclParse.c', 7): {'title': 'Run time: TclSubstTokens',
                             'what': 'Evaluate the body with Tcl_ExprObj on a copy of the text. On TCL_OK substitute the value. On any other return code substitute the result, as the COMMAND case '
                                     'does, and let the code after the switch handle error, break and continue.',
                             'check': 'The else branch is the bug found by mutation testing: before it, [return -code error boom] inside the body lost its message on this path. Equivalence with '
                                      '[expr {...}] is tested for compiled and uncompiled code.',
                             'tests': 'parse-22.40, 22.70 to 22.75 (including subst $var and Tcl_EvalEx), parse-22.80 (leak test, needs a memory-debug build)'},
 ('generic/tclTest.c', 1): {'title': 'Name the token in testparser',
                            'what': 'Prints "exprsubst" for the new type in the test command that dumps tokens.',
                            'check': 'Test support only.',
                            'tests': 'all parse-22.1 to 22.6'},
 ('generic/tclTest.c', 2): {'title': 'testparsevar takes a second reference (declaration and argument check)',
                            'what': 'Part of the fix for the Tcl_ParseVar report (patch by Eric Taylor, committed by Jan Nijtmans as fbb7b018f2). testparsevar accepts an optional second variable '
                                    'reference and a local value2 to hold its result.',
                            'check': 'Test support only. It lets the tests hold two Tcl_ParseVar results at once, which is what a C caller may rely on.',
                            'tests': 'parse-22.5.1 to 22.5.3'},
 ('generic/tclTest.c', 3): {'title': 'testparsevar parses the second reference while holding the first',
                            'what': 'Part of the fix for the Tcl_ParseVar report (patch by Eric Taylor, committed by Jan Nijtmans as fbb7b018f2). Calls Tcl_ParseVar a second time before using either '
                                    'value, then appends both to the result.',
                            'check': 'Test support only. Before the fix the first pointer could be invalid after the second call for an expression.',
                            'tests': 'parse-22.5.1 to 22.5.3'}}
QUESTIONS = [
 ('subst -nocommands and the new -expressions / -noexpressions options',
  'The body of $((...)) can contain [commands], so subst -nocommands {$(([string length abc]+1))} would have returned 4. subst now has -expressions / -noexpressions, and -nocommands and -novariables also turn expression substitution off, so existing code that uses them to make text safe is unchanged (subst-expr-1.3, 1.12). Open points: the option names; changing TCL_SUBST_ALL from 7 to 15 in tcl.h; and whether -nocommands should instead leave the bracketed command text unsubstituted while still doing the arithmetic.'),
 ('Which spelling, and the empty-name array',
  'The patch supports $(( and $( from one code path (a build switch). The default $(( leaves every existing script without "$((" unchanged (in Tcl 9.1 an unescaped "(" in an array index is already an error, so "$((" and "$( (" are free syntax). $(( code stays valid if $( is adopted later. The default build now requires the closing "))" (look-ahead), so a forgotten "(" is an error; the single-paren build has no such ambiguity.'),
 ('A new public token type',
  'TCL_TOKEN_EXPR_SUBST changes what Tcl_ParseCommand, Tcl_ParseExpr and the other procedures that parse a whole word or expression can return. Tcl_ParseVarName and Tcl_ParseVar never return it (question 7). In the default build only text containing "$((" can produce it. TclCompileTokens panics on an unknown type, so an extension that builds its own token walkers needs to know about it.'),
 ('The scanner re-implements skipping rules',
  'Braces, quotes, backslashes and brackets are skipped by a separate function (SkipExprSubstScan) instead of by the word parser. That is deliberate (the body must not be parsed), but the rules have to agree with expr\'s own. Tests put ")" inside each construct, and a test checks that no truncated prefix of a valid substitution is accepted. The scanner follows at most 1000 levels of nested [ (a constant in tclParse.c); deeper nesting is an error, not a crash.'),
 ('Line-number adjustment in TclCompileTokens',
  'envPtr->line is adjusted around the compile call, as the COMMAND case does. Two mutants that remove it survive: no test can tell. Safe to remove, or keep for parity?'),
 ('Behaviour that differs from [expr {...}]',
  'The bytecode, value and error message are the same. The command list in the bytecode has one entry instead of two. [expr] looks up the command named expr, so redefining it or tracing it changes [expr {...}] but not $((...)). An error trace ends with the original text of the substitution rather than "expr {...}".'),
 ('Tcl_ParseVarName and Tcl_ParseVar do not return the new token',
  'Found by Florent Merlet during the vote: Tcl_ParseVar returns a const char * that callers treat like a variable value, but for an expression the value lived only in the interpreter result, so a later call could invalidate it. Fix (patch by Eric Taylor, committed by Jan Nijtmans as fbb7b018f2): the public Tcl_ParseVarName is a wrapper that never recognizes the expression form, and the parser and the expression parser call the internal TclParseVarName with exprSubst = 1. So only whole-word and expression parsing (Tcl_ParseCommand, Tcl_ParseExpr, the compiler, subst) can return the token. Open point: is that the right line between public and internal?'),
]

# Which hunks (1-20, in page order) each question is about.
QHUNKS = [[1,4,5],[11,12,16],[2,3],[14],[9],[14,17],[7,8,10,13,15,16,19,20]]
