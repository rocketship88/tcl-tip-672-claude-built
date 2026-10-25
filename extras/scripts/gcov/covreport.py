import json,subprocess,re,sys,os
lf=json.load(open("/tmp/linefilter.json"))
want={}
for e in lf:
    s=set()
    for a,b in e["lines"]: s.update(range(a,b+1))
    want[e["name"]]=s
def parse_gcov(path):
    res={}
    cur=None
    for ln in open(path,errors="replace"):
        m=re.match(r'\s*([^:]+):\s*(\d+):(.*)',ln)
        if not m: continue
        c,n,src=m.group(1).strip(),int(m.group(2)),m.group(3)
        if n==0: continue
        res[n]=(c,src)
    return res
tot={}
for mode in (1,2):
    d=f"/root/tcl-build-cov{mode}"
    print(f"\n######## build {mode} ($ {'(' if mode==1 else '(('} trigger)")
    for name in ["tclParse.c","tclCmdMZ.c","tclCompCmdsSZ.c","tclCompExpr.c","tclCompile.c"]:
        subprocess.run(["gcov","-b","-c","-o",d,f"/root/tcl-trunk/generic/{name}"],cwd=d,capture_output=True)
        g=parse_gcov(f"{d}/{name}.gcov")
        ex=[n for n in sorted(want[name]) if n in g and g[n][0]!='-' ]
        # executable lines: count is number or #####
        hit=[n for n in ex if g[n][0] not in ('#####','=====')]
        miss=[n for n in ex if g[n][0] in ('#####','=====')]
        print(f"{name}: {len(ex)} executable changed lines, {len(hit)} hit, {len(miss)} never run")
        for n in miss: print(f"   MISS {n}: {g[n][1].strip()}")
