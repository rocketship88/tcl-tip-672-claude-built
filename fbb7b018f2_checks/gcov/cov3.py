import subprocess,re,os,collections
BASE='6a9f9e9402'; R='/root/gh672'
FILES=['tcl.h','tclCmdMZ.c','tclCompCmdsSZ.c','tclCompExpr.c','tclCompile.c','tclParse.c','tclTest.c']
def added(f):
    d=subprocess.check_output(['git','-C',R,'diff','-U0',BASE,'fbb7','--','generic/'+f],text=True)
    s=set();cur=None
    for l in d.splitlines():
        m=re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@',l)
        if m: cur=int(m.group(1)); continue
        if cur is not None and l.startswith('+') and not l.startswith('+++'): s.add(cur);cur+=1
    return s
for mode in (1,2):
    d=f'/root/cov-fbb{mode}'; tot=collections.Counter(); notrun=[]
    for f in FILES:
        if f=='tcl.h': continue
        subprocess.run(['gcov','-b','-o',d+'/'+('' ),'/root/jv/generic/'+f],cwd=d,capture_output=True)
        g=d+'/'+f+'.gcov'
        if not os.path.exists(g): print('missing',g); continue
        want=added(f); br_t=br_k=0
        cur=None
        for ln in open(g,errors='replace'):
            m=re.match(r'\s*([^:]+):\s*(\d+):',ln)
            if m:
                c=m.group(1).strip(); n=int(m.group(2)); cur=n if n in want else None
                if cur and c!='-':
                    if c in('#####','====='):
                        tot['exec']+=1; notrun.append((f,n,ln.rstrip()[:110]))
                    else: tot['exec']+=1; tot['run']+=1
                continue
            b=re.match(r'branch\s+\d+ (taken (\d+)|never executed)',ln)
            if b and cur:
                tot['br']+=1
                if b.group(2) and int(b.group(2))>0: tot['brtaken']+=1
    print(f'mode {mode}: lines run {tot["run"]} of {tot["exec"]} executable new/changed ({100*tot["run"]/tot["exec"]:.1f}%); branches taken {tot["brtaken"]} of {tot["br"]}')
    for x in notrun: print('   not run:',x)
