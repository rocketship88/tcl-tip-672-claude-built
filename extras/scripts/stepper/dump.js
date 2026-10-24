const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const b=await chromium.launch();const pg=await b.newPage();
pg.on('pageerror',e=>console.log('ERR',String(e)));
await pg.goto('file:///root/stepper/parser_stepper_new.html');
const scs=['basic','missing','nested','braces','var','runtime','unterm','single','typo'];
const sop=['d','ne','e','nc','nv','nb'];
let out='';
async function one(bld,s,o){
  const r=await pg.evaluate(([b,s,o])=>window.__stepper.dump(b,s,o),[bld,s,o]);
  out+=`\n######## build ${bld}  script ${s}${o?' option '+o:''}  src=${JSON.stringify(r.src)}\n`;
  for(const x of r.steps){
    out+=`\n[${x.k}] ${x.sn}:${x.ln}  ${x.h}\n  line: ${x.line}\n  pos=${x.pos} reg=${x.reg} frames=${x.frames}\n  kv=${JSON.stringify(x.kv)}\n  tokens: ${x.tokens}\n  text: ${x.p}\n`;
    if(x.res) out+=`  res: ${x.res}\n`; if(x.check) out+=`  check: ${x.check}\n`;
  }
}
for(const bld of [1,2]){ for(const s of scs){ try{await one(bld,s,null);}catch(e){out+=`\n#### build ${bld} ${s}: ${e.message.slice(0,200)}\n`;} }
  for(const o of sop){ try{await one(bld,'subst',o);}catch(e){out+=`\n#### build ${bld} subst ${o}: ${e.message.slice(0,200)}\n`;} } }
fs.writeFileSync('audit_dump.txt',out); console.log(out.length);
await b.close();})();
