// Снимает отдельные кадры для проверки: node tools/preview.js out_dir t1 t2 ...
const { chromium } = require('playwright'); const fs=require('fs'), path=require('path');
(async()=>{
  const [out,...ts]=process.argv.slice(2); fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
  const errs=[]; p.on('console',m=>{if(m.type()!=='log')errs.push(m.text())}); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('file://'+path.resolve(__dirname,'render.html'));
  const tl=JSON.parse(fs.readFileSync(path.resolve(__dirname,'timeline.json')));
  await p.evaluate(tl=>window.init(tl),tl);
  for(const t of ts){ await p.evaluate(t=>frame(+t),t); await p.screenshot({path:`${out}/t${(+t).toFixed(1).padStart(6,'0')}.jpg`,type:'jpeg',quality:80}); }
  console.log(errs.slice(0,10).join('\n')); await b.close();
})();
