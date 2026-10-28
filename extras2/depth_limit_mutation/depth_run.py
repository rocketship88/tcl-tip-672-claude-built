import json,subprocess,sys,os,re,time
mode=sys.argv[1]; root='/root/mut'; here=f'{root}/depth'
src=f'{root}/src{mode}'; b=f'{root}/b{mode}'
muts=json.load(open(f'{here}/mutants_depth.json'))
resf=f'{here}/results{mode}.jsonl'; basef=f'{here}/baseline{mode}.json'
TESTS='parse.test parseOld.test parseExpr.test compile.test subst.test'
pr=open(f'{here}/pristine_tclParse.c',encoding='utf-8').read()
TARGET=f'{src}/generic/tclParse.c'
def put(text): open(TARGET,'w',encoding='utf-8').write(text)
def build():
    r=subprocess.run(['make','tcltest'],cwd=b,capture_output=True,text=True,timeout=900,stdin=subprocess.DEVNULL)
    return r.returncode==0
def runtests():
    try:
        r=subprocess.run(['./tcltest',f'{src}/tests/all.tcl','-testdir',f'{src}/tests','-file',TESTS],cwd=b,
            capture_output=True,text=True,timeout=60,stdin=subprocess.DEVNULL,errors='replace',env=dict(os.environ,TCL_TEST_EXPR_SUBST_PARENS=mode))
    except subprocess.TimeoutExpired:
        return dict(status='killed-timeout')
    out=r.stdout+r.stderr
    m=re.search(r'all\.tcl:\s+Total\s+(\d+)\s+Passed\s+(\d+)\s+Skipped\s+(\d+)\s+Failed\s+(\d+)',out)
    if not m: return dict(status='killed-crash',rc=r.returncode,tail=out[-200:])
    total,passed,skipped,failed=map(int,m.groups())
    names=re.findall(r'^==== (\S+) .*FAILED',out,re.M)
    abort='Test files exiting with errors' in out
    return dict(total=total,passed=passed,failed=failed,names=sorted(set(names))[:6],abort=abort,rc=r.returncode)
if not os.path.exists(basef):
    put(pr); assert build(), 'baseline build failed'
    base=runtests(); print('baseline',base,flush=True)
    assert base.get('failed')==0 and not base.get('abort'), base
    json.dump(base,open(basef,'w'))
base=json.load(open(basef))
done=set()
if os.path.exists(resf):
    for l in open(resf):
        try: done.add(json.loads(l)['id'])
        except Exception: pass
for m in muts:
    if m['id'] in done: continue
    lines=pr.split('\n'); i=m['line']-1
    assert m['old'] in lines[i]
    lines[i]=lines[i].replace(m['old'],m['new'],1)
    put('\n'.join(lines)); t0=time.time()
    try: ok=build()
    except subprocess.TimeoutExpired: ok=False
    if not ok: res=dict(status='buildfail')
    else:
        res=runtests()
        if 'status' not in res:
            if res['failed']>0: res['status']='killed-fail'
            elif res['abort']: res['status']='killed-abort'
            elif res['total']!=base['total']: res['status']='killed-count'
            else: res['status']='survived'
    res.update(id=m['id'],line=m['line'],desc=m['desc'],secs=round(time.time()-t0,1))
    open(resf,'a').write(json.dumps(res)+'\n')
put(pr); build()
open(f'{here}/DONE{mode}','w').write('done\n')
