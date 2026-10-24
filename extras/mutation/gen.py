import re,subprocess,json,sys
FILES=['generic/tclParse.c','generic/tclCompile.c','generic/tclCompCmdsSZ.c','generic/tclCompExpr.c']
def added(f):
    d=subprocess.check_output(['git','-C','/root/tcl-trunk','diff','-U0',f],text=True)
    add=[];cur=None
    for l in d.splitlines():
        m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',l)
        if m: cur=int(m.group(3)); continue
        if cur is None: continue
        if l.startswith('+') and not l.startswith('+++'): add.append(cur);cur+=1
    return add
def kinds(lines):
    out=[];inc=False
    for l in lines:
        s=l.strip();k='code'
        if not s:k='blank'
        elif inc:
            k='comment'
            if '*/' in s:
                inc=False
                if s.split('*/',1)[1].strip():k='code'
        elif s.startswith('//'):k='comment'
        elif s.startswith('/*'):
            k='comment'
            if '*/' in s:
                if s.split('*/',1)[1].strip():k='code'
            else: inc=True
        elif '/*' in s and '*/' not in s.split('/*',1)[1]: inc=True
        out.append(k)
    return out
SWAPS=[(' == ',' != '),(' != ',' == '),(' < ',' <= '),(' <= ',' < '),(' > ',' >= '),(' >= ',' > '),(' && ',' || '),(' || ',' && '),
       ('++','--'),('--','++'),('TCL_OK','TCL_ERROR'),('TCL_ERROR','TCL_OK'),('true','false'),('false','true')]
CHARS=[("'('","')'"),("')'","'('"),("'{'","'}'"),("'}'","'{'"),("'\"'","'x'"),("'['","']'"),("']'","'['"),("'\\\\'","'x'")]
def mutants_for(line):
    out=[]
    s=line.strip()
    for a,b in SWAPS:
        for m in re.finditer(re.escape(a),line):
            out.append(('swap '+a.strip()+'->'+b.strip(),line[:m.start()]+b+line[m.end():]))
    for a,b in CHARS:
        if a in line: out.append(('char '+a+'->'+b,line.replace(a,b,1)))
    m=re.match(r'^(\s*)((?:\} else )?)(if|while) \((.*)\) \{$',line)
    if m: out.append(('negate cond',f'{m.group(1)}{m.group(2)}{m.group(3)} (!({m.group(4)})) {{'))
    for m in re.finditer(r'(?<![\w\'"])([012])(?![\w\'"])',line):
        if re.search(r'(src|numBytes|size|Tokens|numTokens|numComponents|count|depth|braces|\[|\])',line) :
            d=str(1-int(m.group(1))) if m.group(1)!='2' else '1'
            out.append(('const '+m.group(1)+'->'+d,line[:m.start()]+d+line[m.end():]))
    if s.endswith(';') and not s.startswith(('return','case')) :
        out.append(('delete stmt',re.sub(r'\S.*',';',line,count=1) if False else line[:len(line)-len(line.lstrip())]+';'))
    return out
muts=[];mid=0
for f in FILES:
    lines=open('/root/mut/pristine/'+f,encoding='utf-8').read().split('\n')
    k=kinds(lines)
    for n in added(f):
        line=lines[n-1]
        if k[n-1]!='code' or line.strip().startswith('#') : continue
        seen=set()
        for op,new in mutants_for(line):
            if new==line or (op,new) in seen: continue
            seen.add((op,new))
            mid+=1
            muts.append(dict(id=mid,file=f,line=n,op=op,orig=line,new=new))
json.dump(muts,open('/root/mut/mutants.json','w'),indent=0)
from collections import Counter
print(len(muts),'mutants'); print(Counter(m['file'] for m in muts)); print(Counter(m['op'].split()[0] for m in muts))
