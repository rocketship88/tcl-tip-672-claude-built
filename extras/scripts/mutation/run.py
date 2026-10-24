import json,subprocess,sys,os,re,time
mode=sys.argv[1]; root='/root/mut'
src=f'{root}/src{mode}'; b=f'{root}/b{mode}'
muts=json.load(open(f'{root}/mutants.json'))
resf=f'{root}/results{mode}.jsonl'; basef=f'{root}/baseline{mode}.json'
TESTS='parse.test parseOld.test parseExpr.test compile.test'
def log_progress(msg):
    open(f'{root}/progress{mode}.txt','w').write(f'{time.strftime("%H:%M:%S")} {msg}\n')
def pristine(f): return open(f'{root}/pristine/{f}',encoding='utf-8').read()
def put(f,text):
    open(f'{src}/{f}','w',encoding='utf-8').write(text)
def build():
    r=subprocess.run(['make','tcltest'],cwd=b,capture_output=True,text=True,timeout=600,stdin=subprocess.DEVNULL)
    return r.returncode==0
def runtests():
    try:
        r=subprocess.run(['./tcltest',f'{src}/tests/all.tcl','-testdir',f'{src}/tests','-file',TESTS],cwd=b,
            capture_output=True,text=True,timeout=30,stdin=subprocess.DEVNULL,errors='replace',env=dict(os.environ,TCL_TEST_EXPR_SUBST_PARENS=mode))
    except subprocess.TimeoutExpired:
        return dict(status='killed-timeout')
    out=r.stdout+r.stderr
    m=re.search(r'all\.tcl:\s+Total\s+(\d+)\s+Passed\s+(\d+)\s+Skipped\s+(\d+)\s+Failed\s+(\d+)',out)
    if not m: return dict(status='killed-crash',rc=r.returncode,tail=out[-300:])
    total,passed,skipped,failed=map(int,m.groups())
    names=re.findall(r'^==== (\S+) .*FAILED',out,re.M)
    abort='Test files exiting with errors' in out
    return dict(total=total,passed=passed,failed=failed,names=names[:6],abort=abort,rc=r.returncode)
if not os.path.exists(basef):
    log_progress('baseline')
    for f in ['generic/tclParse.c']: put(f,pristine(f))
    assert build()
    base=runtests(); print('baseline',base)
    assert base.get('failed')==0 and not base.get('abort'), base
    json.dump(base,open(basef,'w'))
base=json.load(open(basef))
done=set()
if os.path.exists(resf):
    for l in open(resf):
        try: done.add(json.loads(l)['id'])
        except Exception: pass
last=None
for m in muts:
    if m['id'] in done: continue
    log_progress(f"mutant {m['id']}/{len(muts)} {m['file']}:{m['line']}")
    f=m['file']
    if last and last!=f: put(last,pristine(last))
    last=f
    lines=pristine(f).split('\n')
    assert lines[m['line']-1]==m['orig']
    lines[m['line']-1]=m['new']
    put(f,'\n'.join(lines))
    t0=time.time()
    try:
        ok=build()
    except subprocess.TimeoutExpired:
        ok=False
    if not ok: res=dict(status='buildfail')
    else:
        res=runtests()
        if 'status' not in res:
            if res['failed']>0: res['status']='killed-fail'
            elif res['abort']: res['status']='killed-abort'
            elif res['total']!=base['total']: res['status']='killed-count'
            else: res['status']='survived'
    res.update(id=m['id'],file=f,line=m['line'],op=m['op'],secs=round(time.time()-t0,1))
    open(resf,'a').write(json.dumps(res)+'\n')
if last: put(last,pristine(last)); build()
open(f'{root}/DONE{mode}','w').write('done\n')
log_progress('DONE')
