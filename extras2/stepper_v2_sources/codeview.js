  /* ================= full code view: coloured, foldable, double-click to follow a name ================= */
  var FN = {pvn: 'Tcl_ParseVarName', hook: 'Tcl_ParseVarName', fin: 'Tcl_ParseVarName', arr: 'Tcl_ParseVarName', arr2: 'Tcl_ParseVarName',
            scan: 'SkipExprSubstScan', comp: 'TclCompileTokens', run: 'TclSubstTokens'};
  var BASE_TABS = ['Tcl_ParseVarName', 'FindExprSubstEnd', 'SkipExprSubstScan', 'TclCompileTokens', 'TclSubstTokens', 'TCL_EXPR_SUBST_PARENS'];
  var FUNCS = {}, HDR = new Map(), HDRL = [], KIND = new Map();
  Object.keys(FUNCS0).forEach(function (n) { FUNCS[n] = FUNCS0[n]; });
  var colorOn = true, foldOn = true, openFolds = new Set(), codeOpen = false, codeTab = null, codeStep = -1,
      codeExtra = [], codeWant = null, codeHit = null, codeMark = null, codeStack = [];
  window.__codeOpen = false;

  function indexTclHeader(text) {
    var L = text.replace(/\r\n/g, '\n').split('\n'), M = new Map();
    var comment = function (a) {
      if (a > 0 && /^\s*(\/\*|\*)/.test(L[a - 1]) && /\*\/\s*$/.test(L[a - 1])) { var d = a - 1; while (d > 0 && !/^\s*\/\*/.test(L[d]) && a - d < 40) d--; if (/^\s*\/\*/.test(L[d])) return d; }
      return a;
    };
    var put = function (name, a, b, rank, kind) { var o = M.get(name); if (!o || rank > o.rank) M.set(name, {a: a, b: b, rank: rank, kind: kind}); };
    var count = function (l) { var d = 0; l.replace(/\/\*.*?\*\//g, '').split('').forEach(function (ch) { if (ch === '{') d++; else if (ch === '}') d--; }); return d; };
    for (var i = 0; i < L.length; i++) {
      var l = L[i], m;
      if ((m = /^\s*#\s*define\s+(\w+)/.exec(l))) {
        var b = i; while (/\\\s*$/.test(L[b]) && b < L.length - 1) b++;
        put(m[1], comment(i), b, 2, /^[A-Z0-9_]+$/.test(m[1]) ? 'k-mac' : 'k-fn'); i = b; continue;
      }
      if ((m = /^\s*\}\s*(\w+)\s*;/.exec(l))) {
        var d = 0, j = i; for (; j >= 0; j--) { d += -count(L[j]); if (d <= 0 && /\{/.test(L[j])) break; }
        if (j >= 0) put(m[1], comment(j), i, 3, 'k-ty');
      }
      if ((m = /^\s*(?:typedef\s+)?(?:struct|union|enum)\s+(\w+)\s*\{/.exec(l))) {
        var d2 = 0, j2 = i; for (; j2 < L.length; j2++) { d2 += count(L[j2]); if (d2 <= 0) break; }
        put(m[1], comment(i), j2, 3, 'k-ty');
      }
      if (/^\s*typedef\b/.test(l) && !/\{/.test(l)) {
        var b2 = i; while (!/;\s*(\/\*.*\*\/)?\s*$/.test(L[b2]) && b2 < L.length - 1) b2++;
        var tt = L.slice(i, b2 + 1).join(' ').replace(/\/\*.*?\*\//g, '');
        var mm = /\(\s*\*?\s*(\w+)\s*\)\s*\(/.exec(tt) || /(\w+)\s*(?:\[[^\]]*\])?\s*;\s*$/.exec(tt);
        if (mm) put(mm[1], comment(i), b2, 1, 'k-ty');
        i = b2;
      }
    }
    HDRL = L; return M;
  }
  function tclDef(w) {
    var h = HDR.get(w);
    return h ? {a: h.a + 1, lines: HDRL.slice(h.a, h.b + 1), ext: 'tcl.h'} : null;
  }
  function buildKinds() {
    KIND = new Map();
    Object.keys(FUNCS0).forEach(function (n) { KIND.set(n, n === 'TCL_EXPR_SUBST_PARENS' ? 'k-mac' : 'k-fn'); });
    HDR.forEach(function (h, n) { if (!KIND.has(n)) KIND.set(n, h.kind); });
  }
  function lineHtml(l, st, mk, clickable) {
    var T = [], push = function (s, e, c) { if (e > s) T.push([s, e, c]); };
    var comm = function (s, e) {
      var re = /[A-Za-z_]\w*/g; re.lastIndex = s; var last = s, m;
      while ((m = re.exec(l)) && m.index < e) { var k = clickable && KIND.get(m[0]); if (k) { push(last, m.index, 'cm'); push(m.index, m.index + m[0].length, k); last = m.index + m[0].length; } }
      push(last, e, 'cm');
    };
    var n = l.length, i = 0, done = false;
    if (st.inBlock) { var j = l.indexOf('*/'); if (j < 0) { comm(0, n); done = true; } else { comm(0, j + 2); st.inBlock = false; i = j + 2; } }
    if (!done) {
      var re = /\/\*|\/\/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[A-Za-z_]\w*/g; re.lastIndex = i;
      var last2 = i, m2;
      while ((m2 = re.exec(l))) {
        var s = m2.index, t = m2[0], e = s + t.length;
        push(last2, s, '');
        if (t === '/*') { var j2 = l.indexOf('*/', s + 2); if (j2 < 0) { comm(s, n); st.inBlock = true; last2 = n; break; } comm(s, j2 + 2); last2 = j2 + 2; re.lastIndex = last2; continue; }
        if (t === '//') { comm(s, n); last2 = n; break; }
        if (t[0] === '"' || t[0] === "'") push(s, e, 'st'); else push(s, e, (clickable && KIND.get(t)) || '');
        last2 = e;
      }
      push(last2, n, '');
    }
    var out = '';
    T.forEach(function (x) {
      var s = x[0], e = x[1], c = x[2];
      var piece = function (a, b) { if (b <= a) return ''; var tx = esc(l.slice(a, b)); return c ? '<span class="' + c + '">' + tx + '</span>' : tx; };
      if (mk && mk.col < e && mk.col + mk.len > s) {
        var a = Math.max(s, mk.col), b = Math.min(e, mk.col + mk.len);
        out += piece(s, a) + '<mark class="clicked">' + piece(a, b) + '</mark>' + piece(b, e);
      } else out += piece(s, e);
    });
    return out;
  }
  function codeOnly(lines) {
    var inBlock = false;
    return lines.map(function (l) {
      var o = '', i = 0;
      while (i < l.length) {
        if (inBlock) { var j = l.indexOf('*/', i); if (j < 0) { i = l.length; break; } inBlock = false; i = j + 2; o += ' '; continue; }
        var c = l[i];
        if (c === '/' && l[i + 1] === '*') { inBlock = true; i += 2; continue; }
        if (c === '/' && l[i + 1] === '/') break;
        if (c === '"' || c === "'") { var k = i + 1; while (k < l.length && l[k] !== c) k += (l[k] === '\\') ? 2 : 1; o += c + ' '.repeat(Math.max(0, k - i - 1)) + c; i = k + 1; continue; }
        o += c; i++;
      }
      return o;
    });
  }
  function foldRegions(lines) {
    var S = codeOnly(lines), n = lines.length, D = [], d = 0, k, ch;
    for (k = 0; k < n; k++) { D[k] = d; for (var q = 0; q < S[k].length; q++) { ch = S[k][q]; if (ch === '{') d++; else if (ch === '}') d--; if (d < 0) return []; } }
    if (d !== 0) return [];
    var T = S.map(function (x) { return x.trim(); });
    var lead = function (k) { var c = 0; for (var q = 0; q < T[k].length; q++) { if (T[k][q] === '}') c++; else if (T[k][q] !== ' ') break; } return c; };
    var open = -1; for (k = 0; k < n; k++) if (T[k] === '{' && D[k] === 0) { open = k; break; }
    if (open < 0) return [];
    var R = [], endOf = function (r, depth) { for (var k2 = r + 1; k2 < n; k2++) if (D[k2] === depth && T[k2][0] === '}') return k2; return -1; };
    var add = function (s, e) { while (e >= s && T[e] === '') e--; if (e - s + 1 >= 2) R.push({s: s, e: e}); };
    for (var r = open + 1; r < n; r++) {
      if (!/\{$/.test(T[r]) || D[r] - lead(r) !== 1) continue;
      var head = T[r], h = r;
      while (h > open + 1 && (head.split(')').length - 1) > (head.split('(').length - 1) && r - h < 8) { h--; head = T[h] + ' ' + head; }
      if (/^(\}\s*)?(if\s*\(|else\s+if\s*\(|else\s*\{$)/.test(head)) {
        var c = endOf(r, 2); if (c > 0) add(r + 1, c - 1);
      } else if (/^switch\s*\(/.test(head)) {
        var c2 = endOf(r, 2); if (c2 < 0) continue;
        var labels = []; for (var k3 = r + 1; k3 < c2; k3++) if (D[k3] === 2 && /^(case\b|default\s*:)/.test(T[k3])) labels.push(k3);
        labels.forEach(function (k4, ii) { add(k4 + 1, (ii + 1 < labels.length ? labels[ii + 1] : c2) - 1); });
        r = c2;
      }
    }
    return R;
  }
  function stepTarget() {
    var s = steps[i];
    return {fn: FN[s.sn], k: s.ln - FUNCS[FN[s.sn]].a, s: s};
  }
  function renderCode() {
    var tg = stepTarget(), s = tg.s;
    var names = BASE_TABS.concat(codeExtra);
    if (codeStep !== i) { codeTab = tg.fn; codeStep = i; codeHit = null; codeMark = null; codeStack = []; codeExtra = []; names = BASE_TABS.slice(); }
    if (codeWant && names.indexOf(codeWant) >= 0) codeTab = codeWant; codeWant = null;
    var f = FUNCS[codeTab];
    $('code-h').textContent = 'Code for step ' + (i + 1) + ': ' + s.h;
    $('ctabs').innerHTML = names.map(function (n) { return '<button data-n="' + n + '" aria-pressed="' + (n === codeTab) + '">' + n + (n === tg.fn ? ' \u2022' : '') + '</button>'; }).join('');
    var hitK = (codeTab === tg.fn && !f.ext) ? tg.k : -1;
    if (codeHit && codeHit.tab === codeTab && codeHit.k >= 0) hitK = codeHit.k;
    var cst = {inBlock: false}, regs = (foldOn && !f.ext) ? foldRegions(f.lines) : [], regAt = [];
    regs.forEach(function (r) {
      var must = (hitK >= r.s && hitK <= r.e) || (codeMark && codeMark.tab === codeTab && codeMark.k >= r.s && codeMark.k <= r.e);
      r.open = must || openFolds.has(codeTab + ':' + r.s);
      for (var k = r.s; k <= r.e; k++) regAt[k] = r;
    });
    $('codepre').innerHTML = f.lines.map(function (l, k) {
      var rg = regAt[k], cls = 'ln', pre0 = '';
      if (rg && !rg.open) {
        if (k !== rg.s) { if (colorOn) lineHtml(l, cst, null, false); return ''; }
        return '<span class="ln fold" data-fs="' + rg.s + '" title="click to open"><i></i>\u25b8 \u2026 ' + (rg.e - rg.s + 1) + ' lines</span>';
      }
      if (rg && k === rg.s) pre0 = '<span class="ln fold open" data-fs="' + rg.s + '" title="click to close"><i></i>\u25be hide these ' + (rg.e - rg.s + 1) + ' lines</span>';
      if (k === hitK) cls += ' hit';
      var mk = codeMark && codeMark.tab === codeTab && codeMark.k === k ? codeMark : null;
      var body = colorOn ? lineHtml(l, cst, mk, !f.ext) : (mk ? esc(l.slice(0, mk.col)) + '<mark class="clicked">' + esc(l.slice(mk.col, mk.col + mk.len)) + '</mark>' + esc(l.slice(mk.col + mk.len)) : esc(l));
      return pre0 + '<span class="' + cls + '" data-k="' + k + '"><i>' + (f.a + k) + '</i>' + body + '</span>';
    }).join('');
    var pre = $('codepre'), mEl = pre.querySelector('mark.clicked');
    if (mEl) pre.scrollTop = Math.max(0, mEl.parentElement.offsetTop - pre.clientHeight / 3);
    else if (hitK > 14) { var el = pre.querySelector('[data-k="' + hitK + '"]'); if (el) pre.scrollTop = Math.max(0, el.offsetTop - 60); }
    else pre.scrollTop = 0;
    $('b-back').textContent = codeStack.length ? '\u2190 Back (' + codeStack.length + ')' : '\u2190 Back';
    $('cnote').innerHTML = f.ext ? 'This is the definition from ' + f.ext + ' (the modified trunk); names in it are not followed further. Back, or a double-click on blank space, returns.'
      : (colorOn ? 'Names you can double-click are bold: <span class="k-fn">functions</span>, <span class="k-mac">macros</span>, <span class="k-ty">types</span> (comments are <span class="cm">green</span>, strings <span class="st">red</span>). A double-click shows the definition; Back returns. ' : '')
        + 'The line for this step is highlighted. Fold hides the outer blocks of the function except the one holding that line; click a "\u2026 lines" row to open it.';
    $('codepre').parentNode.dataset.tab = codeTab;
  }
  function setCode(on) {
    codeOpen = on; window.__codeOpen = on;
    $('codeview').hidden = !on;
    document.querySelector('.panes').style.display = on ? 'none' : '';
    $('b-code').textContent = on ? 'Show panes' : 'Show code';
    if (on) { codeStep = -1; renderCode(); }
  }
  $('b-code').onclick = function () { setCode(!codeOpen); };
  $('codepre').addEventListener('mousedown', function (e) { if (e.detail > 1) e.preventDefault(); });
  function wordAt(x, y) {
    var node = null, off = 0;
    if (document.caretPositionFromPoint) { var c = document.caretPositionFromPoint(x, y); if (c) { node = c.offsetNode; off = c.offset; } }
    else if (document.caretRangeFromPoint) { var r = document.caretRangeFromPoint(x, y); if (r) { node = r.startContainer; off = r.startOffset; } }
    if (!node || node.nodeType !== 3) return null;
    if (node.parentElement && (node.parentElement.tagName === 'I' || node.parentElement.closest('.fold'))) return null;
    var ln = node.parentElement && node.parentElement.closest('.ln'); if (!ln) return null;
    var txt = node.data, a = off, b = off;
    while (a > 0 && /\w/.test(txt[a - 1])) a--;
    while (b < txt.length && /\w/.test(txt[b])) b++;
    if (a === b) return null;
    var rg = document.createRange(); rg.setStartAfter(ln.querySelector('i')); rg.setEnd(node, a);
    return {word: txt.slice(a, b), k: +ln.dataset.k, col: rg.toString().length, len: b - a};
  }
  $('codepre').addEventListener('click', function (e) {
    var r = e.target.closest('.fold'); if (!r) return;
    var key = codeTab + ':' + r.dataset.fs; if (openFolds.has(key)) openFolds.delete(key); else openFolds.add(key);
    var pre = $('codepre'), top = pre.scrollTop; renderCode(); pre.scrollTop = top;
  });
  $('codepre').addEventListener('dblclick', function (e) {
    if (e.target.closest('.fold')) return;
    var say = function (m) { $('cmsg').textContent = m; };
    var hit = wordAt(e.clientX, e.clientY);
    var sel = window.getSelection(); if (sel) sel.removeAllRanges();
    if (!hit) { say(''); $('b-back').click(); return; }
    var w = hit.word, f = FUNCS[codeTab];
    if (f.ext) { if (w === codeTab) { say(''); $('b-back').click(); } else say('This is the definition from ' + f.ext + '; definitions there are followed one level only. Back returns.'); return; }
    var tab = null;
    if (FUNCS0[w]) tab = w;
    else { var d = tclDef(w); if (d) { FUNCS[w] = d; tab = w; } }
    if (!tab) { say('"' + w + '" is not a function, macro or type that this page has the definition of (it is C, or a local name).'); return; }
    if (tab === codeTab) { say('"' + w + '" is the code shown here.'); return; }
    say('');
    codeStack.push({tab: codeTab, extra: codeExtra.slice(), mark: {tab: codeTab, k: hit.k, col: hit.col, len: hit.len}});
    if (BASE_TABS.indexOf(tab) < 0 && codeExtra.indexOf(tab) < 0) codeExtra.push(tab);
    codeWant = tab; codeMark = null; codeHit = null;
    renderCode();
  });
  $('codeview').addEventListener('dblclick', function (e) { if (e.target === $('codeview')) { $('cmsg').textContent = ''; $('b-back').click(); } });
  $('b-back').onclick = function () {
    var sn = codeStack.pop(); if (!sn) { setCode(false); return; }
    codeExtra = sn.extra; codeWant = sn.tab; codeMark = sn.mark; codeHit = null; renderCode();
  };
  $('ctabs').addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; codeWant = b.dataset.n; codeHit = null; codeMark = null; renderCode(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && codeOpen) setCode(false);
    if (e.key === 'Backspace' && codeOpen && e.target.tagName !== 'INPUT') { e.preventDefault(); $('b-back').click(); }
  });
  var applyColor = function () { colorOn = $('colorOn').checked; var pre = $('codepre'), top = pre.scrollTop; renderCode(); pre.scrollTop = top; };
  var applyFold = function () { foldOn = $('foldOn').checked; openFolds.clear(); renderCode(); };
  $('colorOn').addEventListener('change', applyColor); $('foldOn').addEventListener('change', applyFold);
  HDR = indexTclHeader($('tclh').textContent); buildKinds();
