import re,sys
t=open('audit_dump.txt').read()
parts=re.split(r'\n(?=######## )',t)
match=sys.argv[1].split('|'); frm=int(sys.argv[2]); to=int(sys.argv[3]); tl=int(sys.argv[4]) if len(sys.argv)>4 else 330
for p in parts:
    h=p.split('\n')[0]
    if all(m in h for m in match):
        print(h)
        for blk in re.split(r'\n\n(?=\[)',p):
            m=re.match(r'\[(\d+)\] (.*)',blk)
            if not m: continue
            k=int(m.group(1))
            if frm<=k<=to:
                d={}
                for l in blk.split('\n')[1:]:
                    mm=re.match(r'\s+(\w+)[:=] ?(.*)',l)
                    if mm: d[mm.group(1)]=mm.group(2)
                print(f"[{k}] {m.group(2)}\n   line: {d.get('line','').strip()[:100]}  pos={d.get('pos','')[:30]} {d.get('kv','')[:110]}\n   text: {d.get('text','')[:tl]}"+(f"\n   res: {d['res']}" if 'res' in d else ''))
