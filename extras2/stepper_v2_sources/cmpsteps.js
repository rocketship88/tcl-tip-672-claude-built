    /* ---- how expr handles the body, and how the [expr {...}] form differs ---- */
    if (D.body) {
      var row = function (t) { return {type: t.type, text: t.text, nc: t.nc, cls: (t.type === 'command' || t.type === 'variable') ? 'hl' : ''}; };
      var treeT = (realTokens(D.tree) || []).map(row);
      var refT = (realTokens(D.refTok) || []).map(function (t) { return {type: t.type, text: t.text, nc: t.nc, cls: t.type === 'command' ? 'hl' : ''}; });
      var rs = D.refSrc, o1 = rs.indexOf('[expr {'), bs = o1 + 7, be = bs + D.body.length;
      var refReg = [reg(o1, bs, 'dollar'), reg(bs, be, 'body'), reg(be, be + 2, 'dollar')];
      var isRt = scen === 'runtime';
      E('cexpr', LN.parseexpr, 'expr parses the body as an expression',
        'The body text goes to TclCompileExpr (or Tcl_ExprObj when run uncompiled), which calls ParseExpr. This is expr\'s own parser, not the word parser: it builds an operator tree. Words that need substitution, a $variable or a [command], become their own nodes (highlighted) and are substituted once, when the expression is evaluated. That is why the body can safely be left unparsed by the word parser.',
        {pos: null, reg: bodyReg, tokens: treeT, tokNote: 'expr parse tree (testexprparser)'});
      var lblRef = isRt
        ? 'The outer parser sees one command token. Nothing inside it has been parsed yet. When the text is substituted, the command is evaluated as a script: the command expr is looked up by name, runs, and its C code (Tcl_ExprObjCmd) calls the same expression engine on the braced word. The braces mean no substitution happens before expr sees the text.'
        : 'The outer parser sees [ ... ] as one command token and does not look inside it. The compiler later parses that text as a command of its own: the word expr, then one braced word. The braces stop the word parser from substituting anything, which is the same protection $((...)) gets by never parsing its body. The command name expr has to be looked up, and the compiler routine for the core expr command, TclCompileExprCmd, runs.';
      E(isRt ? 'run' : 'cexcmd', isRt ? LN.cmdcase : LN.exprwords, 'The same text written as [expr {...}]', lblRef,
        {pos: null, srcText: rs, reg: refReg, tokens: refT, tokNote: 'real testparser output (reference form)'});
      if (!isRt) {
        E('cexw', LN.direct, 'A single braced word goes straight to TclCompileExpr',
          'TclCompileExprWords checks that the expression is a single word with no substitutions (a braced word is a "simple word"). It is, so it calls TclCompileExpr with the body, the same call the $((...)) code makes. If the word needed substitutions, as in expr $x*2 with no braces, the else branch would emit code to concatenate the words and call expr again at run time (the EXPR_STK instruction). That second round of substitution is the double substitution that $((...)) cannot trigger, because its body is never a word.',
          {pos: null, srcText: rs, reg: refReg, tokens: refT, tokNote: 'real testparser output (reference form)'});
      }
      var insns = function (d) { return d.split('\n').filter(function (l) { return /^\s+\(\d+\) /.test(l); }).map(function (l) { return l.replace(/^\s+\(\d+\)\s*/, '').replace(/\s+/g, ' ').trim(); }); };
      var cmds = function (d) { var m = /Cmds (\d+)/.exec(d); return m ? m[1] : '-'; };
      var sameI = !isRt && JSON.stringify(insns(D.dis)) === JSON.stringify(insns(D.refDis));
      var sameR = String(D.res) === String(D.refRes) && String(D.rc) === String(D.refRc);
      var cmp = {
        rt: isRt, sameI: sameI, sameR: sameR,
        a: {title: '$' + (build === 2 ? '((' : '(') + ' ... ' + (build === 2 ? '))' : ')') + ' form', script: D.src, route: isRt
              ? ['TclSubstTokens meets the EXPR_SUBST token', 'Tcl_ExprObj(body)']
              : ['Tcl_ParseVarName emits EXPR_SUBST + TEXT', 'TclCompileTokens', 'TclCompileExpr(body)'],
            ntok: String((realTokens(D.tokens) || []).length), cmds: isRt ? '-' : cmds(D.dis), dis: D.dis, res: D.res, rc: D.rc},
        b: {title: '[expr {...}] form', script: D.refSrc, route: isRt
              ? ['TclSubstTokens meets a COMMAND token', 'Tcl_EvalEx runs the script "expr {...}"', 'look up the command expr', 'Tcl_ExprObjCmd, then the expression engine']
              : ['word parser: one COMMAND token', 'compile the command expr: look up expr', 'TclCompileExprCmd', 'TclCompileExprWords', 'TclCompileExpr(body)'],
            ntok: String((realTokens(D.refTok) || []).length), cmds: isRt ? '-' : cmds(D.refDis), dis: D.refDis, res: D.refRes, rc: D.refRc}
      };
      E('cexpr', LN.compiletree, 'Side by side',
        isRt ? 'Both forms end in the same expression engine and give the same result. The $((...)) form skips the command lookup and the second parse of the script.'
             : 'Both forms hand the same body text to TclCompileExpr, so they produce the same instructions and the same value. The bracket form needs a second parse and a command lookup first; the $((...)) form goes there directly.',
        {pos: null, reg: bodyReg, tokens: realT ? realT.map(function (t) { return {type: t.type, text: t.text, nc: t.nc, cls: t.type === 'exprsubst' ? 'hl' : ''}; }) : [], tokNote: 'real testparser output',
         cmp: cmp});
    }
