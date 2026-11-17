import re,subprocess,json,sys
sys.path.insert(0,'/root/ghv/extras/scripts/mutation')
R='/root/mut2/pristine/'
def changed(f):
    d=subprocess.check_output(['git','-C','/root/jv','diff','-U0','HEAD~1','HEAD','--',f],text=True)
    add=[];cur=None
    for l in d.splitlines():
        m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',l)
        if m: cur=int(m.group(3)); continue
        if cur is None: continue
        if l.startswith('+') and not l.startswith('+++'): add.append(cur);cur+=1
    return add
manual={
 'generic/tclParse.c':[
  ('return TclParseVarName(interp, start, numBytes, parsePtr, append, 0);','return TclParseVarName(interp, start, numBytes, parsePtr, append, 1);','wrapper flag 0->1'),
  ('} else if (exprSubst && (*src == \'(\') && ((TCL_EXPR_SUBST_PARENS == 1)','} else if ((*src == \'(\') && ((TCL_EXPR_SUBST_PARENS == 1)','drop exprSubst &&'),
  ('} else if (exprSubst && (*src == \'(\') && ((TCL_EXPR_SUBST_PARENS == 1)','} else if (!exprSubst && (*src == \'(\') && ((TCL_EXPR_SUBST_PARENS == 1)','negate exprSubst'),
  ('} else if (exprSubst && (*src == \'(\') && ((TCL_EXPR_SUBST_PARENS == 1)','} else if (exprSubst || (*src == \'(\') && ((TCL_EXPR_SUBST_PARENS == 1)','exprSubst && -> ||'),
  ('\t\t    1, 1) != TCL_OK) {','\t\t    1, 0) != TCL_OK) {','ParseTokens caller flag 1->0'),
 ],
 'generic/tclCompExpr.c':[
  ('code = TclParseVarName(NULL, start, numBytes, parsePtr, 1, 1);','code = TclParseVarName(NULL, start, numBytes, parsePtr, 1, 0);','CompExpr caller flag 1->0'),
 ]}
muts=[];mid=0
for f,lst in manual.items():
    lines=open(R+f,encoding='utf-8').read().split('\n')
    for a,b,op in lst:
        idx=[i for i,l in enumerate(lines) if l.strip()==a.strip()]
        assert len(idx)==1,(f,a,idx)
        i=idx[0]; new=lines[i].replace(a.strip(),b.strip()) if a.strip() in lines[i] else None
        assert new and new!=lines[i],(a)
        mid+=1; muts.append(dict(id=mid,file=f,line=i+1,op=op,orig=lines[i],new=new))
json.dump(muts,open('/root/mut2/mutants.json','w'),indent=0)
print(len(muts),'mutants')
for m in muts: print(m['id'],m['file'],m['line'],m['op'])
