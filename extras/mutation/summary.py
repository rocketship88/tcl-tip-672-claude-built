import json,os,collections
root='/root/mut'
muts=json.load(open(f'{root}/mutants.json'))
print('total mutants',len(muts))
for m in (1,2):
    f=f'{root}/results{m}.jsonl'; rs=[]
    if os.path.exists(f):
        for l in open(f):
            try: rs.append(json.loads(l))
            except Exception: pass
    c=collections.Counter(r['status'] for r in rs)
    kill=sum(v for k,v in c.items() if k.startswith('killed'))
    valid=len(rs)-c['buildfail']
    print(f'mode {m}: done {len(rs)}/{len(muts)}  valid {valid}  killed {kill}  survived {c["survived"]}  buildfail {c["buildfail"]}  ',dict(c),('FINISHED' if os.path.exists(f'{root}/DONE{m}') else ''))
    if valid: print(f'   kill rate so far: {100*kill/valid:.1f}%')
