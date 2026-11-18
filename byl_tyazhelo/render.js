// node render.js <outdir> [t1,t2,...]  — без списка рендерит все кадры 30 fps
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
  const list = process.argv[3] ? process.argv[3].split(',').map(Number) : null;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(__dirname, 'index.html'));
  await p.evaluate(() => document.fonts.ready);
  const times = list || Array.from({ length: Math.ceil(14.13 * 30) }, (_, i) => i / 30);
  for (let i = 0; i < times.length; i++) {
    await p.evaluate(t => window.render(t), times[i]);
    const f = list ? `t_${times[i].toFixed(2)}.png` : `f_${String(i).padStart(4, '0')}.jpg`;
    await p.screenshot({ path: path.join(out, f), type: list ? 'png' : 'jpeg', ...(list ? {} : { quality: 93 }) });
  }
  if (errs.length) console.log('ERRORS', errs);
  await b.close();
})();
