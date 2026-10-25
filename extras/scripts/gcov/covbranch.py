import json,re
lf=json.load(open("/tmp/linefilter.json"))
want={}
for e in lf:
    s=set()
    for a,b in e["lines"]: s.update(range(a,b+1))
    want[e["name"]]=s
for mode in (1,2):
    d=f"/root/tcl-build-cov{mode}"
    print(f"\n######## build {mode}")
    for name in ["tclParse.c","tclCmdMZ.c","tclCompCmdsSZ.c","tclCompExpr.c","tclCompile.c"]:
        cur=None; src={}; br={}
        for ln in open(f"{d}/{name}.gcov",errors="replace"):
            m=re.match(r'\s*([^:]+):\s*(\d+):(.*)',ln)
            if m and int(m.group(2))>0:
                cur=int(m.group(2)); src[cur]=m.group(3).strip(); continue
            b=re.match(r'branch\s+(\d+) (taken (\d+)|never executed)',ln)
            if b and cur in want[name]:
                br.setdefault(cur,[]).append(0 if b.group(2).startswith('never') else int(b.group(3)))
        tot=sum(len(v) for v in br.values()); taken=sum(1 for v in br.values() for x in v if x>0)
        print(f"{name}: {taken}/{tot} branch outcomes taken on changed lines")
        if name=="tclParse.c" or tot-taken>0:
            for n in sorted(br):
                z=[i for i,x in enumerate(br[n]) if x==0]
                if z: print(f"   line {n}: {len(z)}/{len(br[n])} untaken  | {src[n][:70]}")
