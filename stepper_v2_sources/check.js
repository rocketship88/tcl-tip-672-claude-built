const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1200,height:1000}});
 const errs=[]; pg.on('pageerror',e=>errs.push(String(e))); pg.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await pg.goto('file://'+process.argv[2]);
 const r=await pg.evaluate(()=>window.__stepper.all());
 console.log(JSON.stringify(r,null,0)); console.log('ERRS',errs.slice(0,5));
 await b.close();
})();
