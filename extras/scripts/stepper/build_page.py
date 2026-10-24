import json,re,sys,html
G='/root/tcl-trunk/generic/'
def lines(f,a,b):
    L=open(G+f).read().split('\n')
    return [(n,L[n-1]) for n in range(a,b+1)]
# (name,title,file,a,b)
SN=[('pvn','Tcl_ParseVarName: start','tclParse.c',1578,1593),
    ('hook','Tcl_ParseVarName: the new branch','tclParse.c',1655,1709),
    ('fin','Tcl_ParseVarName: finish','tclParse.c',1775,1778),
    ('scan','SkipExprSubstScan','tclParse.c',1345,1429),
    ('arr','Tcl_ParseVarName: ordinary name path','tclParse.c',1710,1716),
    ('arr2','Tcl_ParseVarName: array index','tclParse.c',1737,1753),
    ('comp','TclCompileTokens','tclCompile.c',2876,2897),
    ('run','TclSubstTokens','tclParse.c',2523,2588)]
snips={}
for n,t,f,a,b in SN:
    snips[n]={'title':t,'file':f,'lines':[[x,y] for x,y in lines(f,a,b)]}
    if n=='pvn': snips[n]['note']='unchanged: the start for every $'
# sanity checks on the line numbers the JS trace uses
chk={('scan',1353):'while (src < end)',('scan',1354):'switch',('scan',1355):"case '\\\\'",('scan',1361):"case '{'",
 ('scan',1365):'while (src < end)',('scan',1370):"'{'",('scan',1372):"'}'",('scan',1378):'return NULL',('scan',1382):"case '\"'",
 ('scan',1384):'*src != \'"\'',('scan',1389):"'['",('scan',1390):'SkipExprSubstScan',('scan',1401):"case '['",('scan',1402):'SkipExprSubstScan',
 ('scan',1407):"case '('",('scan',1409):'depth++',('scan',1412):"case ')'",('scan',1414):'depth == 0',('scan',1415):'return src',('scan',1417):'depth--',
 ('scan',1420):"case ']'",('scan',1422):'return src',('scan',1426):'src++',('scan',1428):'return NULL',
 ('hook',1672):'skip',('hook',1673):'FindExprSubstEnd',('hook',1675):'bodyEnd',('hook',1681):'TCL_PARSE_SYNTAX',('hook',1678):'ExprSubstSyntaxError',('hook',1685):'bodyEnd == NULL',('hook',1705):'EXPR_SUBST',('hook',1706):'start',('hook',1707):'size',('hook',1708):'numTokens',('hook',1709):'bodyEnd + skip',('pvn',1581):'TCL_TOKEN_VARIABLE',('pvn',1586):'src++',
 
 ('fin',1776):'size',('fin',1777):'numComponents',('arr',1711):'TCL_TOKEN_TEXT',('arr2',1737):'array =',('arr2',1750):'ParseTokens',
 ('comp',2876):'EXPR_SUBST',('comp',2889):'envPtr->line',('comp',2890):'TclCompileExpr',('run',2558):'EXPR_SUBST',('run',2564):'Tcl_NewStringObj',('run',2569):'Tcl_ExprObj'}
for (n,l),sub in chk.items():
    txt=dict((a,b) for a,b in snips[n]['lines']).get(l)
    assert txt is not None and sub in txt,(n,l,txt,sub)
def extract(f,name):
    L=open(G+f).read().split('\n')
    i=next(n for n,l in enumerate(L) if re.match(r'^'+name+r'\(',l))
    a=i-1
    k=a-1
    if L[k].strip()=='' : k-=1
    if L[k].rstrip().endswith('*/'):
        while not L[k].startswith('/*'): k-=1
        a=k
    e=i
    while L[e]!='}': e+=1
    return {'a':a+1,'file':f,'lines':L[a:e+1]}
FUNCS={}
for f,n in [('tclParse.c','Tcl_ParseVarName'),('tclParse.c','SkipExprSubstScan'),('tclParse.c','FindExprSubstEnd'),('tclParse.c','TclSubstTokens'),('tclCompile.c','TclCompileTokens'),('tclCompExpr.c','TclCompileExpr'),('tclCompCmds.c','TclCompileExprCmd'),('tclCompile.c','TclCompileExprWords'),('tclCmdMZ.c','TclSubstOptions'),('tclCmdMZ.c','TclNRSubstObjCmd'),('tclParse.c','ParseTokens')]:
    FUNCS[n]=extract(f,n)
LN={}
def find(fn,sub,nth=0):
    hits=[(FUNCS[fn]['a']+k) for k,l in enumerate(FUNCS[fn]['lines']) if sub in l]
    assert hits,(fn,sub)
    return hits[nth]
LN['parseexpr']=find('TclCompileExpr','code = ParseExpr(')
LN['compiletree']=find('TclCompileExpr','CompileExprTree(')
LN['exprwords']=find('TclCompileExprCmd','TclCompileExprWords(')
LN['simpleword']=find('TclCompileExprWords','TCL_TOKEN_SIMPLE_WORD')
LN['direct']=find('TclCompileExprWords','TclCompileExpr(interp, tokenPtr[1]')
LN['cmdcase']=find('TclSubstTokens','case TCL_TOKEN_COMMAND:')
LN['exprstk']=find('TclCompileExprWords','EXPR_STK')
for k,v in [('s_objc',('TclNRSubstObjCmd','if (objc < 2)')),('s_call',('TclNRSubstObjCmd','TclSubstOptions(interp')),('s_nr',('TclNRSubstObjCmd','Tcl_NRSubstObj(')),
  ('o_init',('TclSubstOptions','int flags = numOpts')),('o_or',('TclSubstOptions','flags |= optionFlags')),('o_neg',('TclSubstOptions','if (flags >> 16)')),
  ('o_mask',('TclSubstOptions','flags = TCL_SUBST_ALL & ~')),('o_clearif',('TclSubstOptions','if ((flags & (TCL_SUBST_VARIABLES')),('o_clear',('TclSubstOptions','flags &= ~TCL_SUBST_EXPRESSIONS')),
  ('p_dollar',('ParseTokens',"} else if (*src == '$') {")),('p_exprsyn',('ParseTokens','int exprSyntax')),('p_gate',('ParseTokens','if (exprSyntax ?')),('p_lit',('ParseTokens','Substitution of this kind is disabled')),
  ('p_call',('ParseTokens','Tcl_ParseVarName(parsePtr->interp')),('p_brack',('ParseTokens',"} else if (*src == '[') {")),('p_cgate',('ParseTokens','if (!(flags & TCL_SUBST_COMMANDS))'))]:
    LN[k]=find(*v)
for n,k,a,z in (('subc','TclNRSubstObjCmd',0,None),('subo','TclSubstOptions',0,None)):
    snips[n]={'title':k,'file':FUNCS[k]['file'],'lines':[[FUNCS[k]['a']+x,y] for x,y in enumerate(FUNCS[k]['lines'])]}
LN['p_lit']+=3   # the TEXT token line after the comment
assert 'TCL_TOKEN_TEXT' in lines('tclParse.c',LN['p_lit'],LN['p_lit'])[0][1]
pd=LN['p_dollar']; pb=LN['p_cgate']
snips['ptok']={'title':'ParseTokens: the $ and [ cases','file':'tclParse.c','lines':[[x,y] for x,y in lines('tclParse.c',pd,pb+3)]}
for n,k in (('cexpr','TclCompileExpr'),('cexcmd','TclCompileExprCmd'),('cexw','TclCompileExprWords')):
    snips[n]={'title':k,'file':FUNCS[k]['file'],'lines':[[FUNCS[k]['a']+x,y] for x,y in enumerate(FUNCS[k]['lines'])]}
print(LN)
LP=open(G+'tclParse.c').read().split('\n')
FUNCS['TCL_EXPR_SUBST_PARENS']={'a':118,'file':'tclParse.c','lines':LP[117:149]}
assert 'TCL_EXPR_SUBST_PARENS selects' in FUNCS['TCL_EXPR_SUBST_PARENS']['lines'][1]
for n,v in FUNCS.items(): print(n,v['file'],v['a'],len(v['lines']))
TCLH=open(G+'tcl.h').read()
assert '</script' not in TCLH.lower()
import subprocess
sys.path.insert(0,'.')
from review_notes import NOTES,QUESTIONS,QHUNKS
raw=subprocess.run(['git','diff','-U3','--','generic/'],cwd='/root/tcl-trunk',capture_output=True,text=True).stdout
hunks=[];cf=None;cnt={}
for l in raw.split('\n'):
    if l.startswith('diff --git'): cf=l.split(' b/')[1].strip(); cnt[cf]=0; continue
    if cf is None or l.startswith(('index ','--- ','+++ ','new file','deleted file')): continue
    if l.startswith('@@'):
        cnt[cf]+=1
        m=re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@ ?(.*)',l)
        n=NOTES[(cf,cnt[cf])]
        hunks.append(dict(file=cf,idx=cnt[cf],hdr=l,newStart=int(m.group(3)),ctx=m.group(5),lines=[],**n)); continue
    if hunks and (l[:1] in ' +-\\'): hunks[-1]['lines'].append(l)
assert len(hunks)==len(NOTES),(len(hunks),len(NOTES))
REVIEW={'hunks':hunks,'questions':QUESTIONS,'qhunks':QHUNKS}
d1=json.load(open('data1.json')); d2=json.load(open('data2.json'))
FILESD={n:open(G+n).read().replace('\r\n','\n') for n in ['tclParse.c','tclCompile.c','tclCompCmdsSZ.c','tclCompExpr.c','tclCmdMZ.c','tclCompCmds.c','tclTest.c','tcl.h']}
import re as _re
_raw=subprocess.run(['git','diff','-U0','--','generic/'],cwd='/root/tcl-trunk',capture_output=True,text=True).stdout
_add=set();_del=set()
for _l in _raw.split('\n'):
    if _l[:3] in ('+++','---'): continue
    for _set,_p in ((_add,'+'),(_del,'-')):
        if _l.startswith(_p):
            _m=_re.match(r'.[ \t]*#[ \t]*define[ \t]+(\w+)',_l) or _re.match(r'.([A-Za-z_]\w*)\($',_l)
            if _m: _set.add(_m.group(1))
NEWDEFS=sorted(_add-_del)
print('NEWDEFS',NEWDEFS)
tpl=open('template.html').read()
out=tpl.replace('__SNIPS__',json.dumps(snips)).replace('__FUNCS__',json.dumps(FUNCS)).replace('__LN__',json.dumps(LN)).replace('__REVIEW__',json.dumps(REVIEW)).replace('__NEWDEFS__',json.dumps(NEWDEFS)).replace('__FILES__',json.dumps(FILESD).replace('</','<\\/')).replace('__DATA1__',json.dumps(d1)).replace('__DATA2__',json.dumps(d2))
open(sys.argv[1],'w').write(out)
print('ok',len(out))
