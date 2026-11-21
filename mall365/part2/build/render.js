// node build/render.js stills 1.5,10,20   |  node build/render.js full [workers]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const TL = JSON.parse(fs.readFileSync(path.join(ROOT, 'build/timeline.json'), 'utf8'));
const FPS = 30;
async function page(browser) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.addInitScript(tl => { window.TL = tl; }, TL);
  const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.join(ROOT, 'scene/index.html'));
  await p.evaluate(() => document.fonts.ready);
  if (errs.length) throw new Error(errs.join('\n'));
  return p;
}
(async () => {
  const mode = process.argv[2];
  const browser = await chromium.launch();
  if (mode === 'stills') {
    const p = await page(browser);
    const out = path.join(ROOT, 'build/stills'); fs.mkdirSync(out, { recursive: true });
    for (const t of process.argv[3].split(',').map(Number)) {
      await p.evaluate(t => window.renderAt(t), t);
      await p.screenshot({ path: path.join(out, `t${t.toFixed(2).padStart(7, '0')}.jpg`), type: 'jpeg', quality: 80 });
    }
    fs.writeFileSync(path.join(ROOT, 'build/sfx.json'), JSON.stringify(await p.evaluate(() => window.SFX), null, 0));
  } else {
    const W = +(process.argv[3] || 4);
    const N = Math.ceil(TL.duration * FPS);
    const out = path.join(ROOT, 'build/frames'); fs.mkdirSync(out, { recursive: true });
    let next = 0, done = 0; const t0 = Date.now();
    await Promise.all([...Array(W)].map(async () => {
      const p = await page(browser);
      while (true) {
        const i = next++; if (i >= N) break;
        const fn = path.join(out, `f${String(i).padStart(5, '0')}.jpg`);
        if (fs.existsSync(fn)) { done++; continue; }
        await p.evaluate(t => window.renderAt(t), i / FPS);
        await p.screenshot({ path: fn, type: 'jpeg', quality: 92 });
        if (++done % 300 === 0) console.log(done, '/', N, ((Date.now() - t0) / 1000).toFixed(0) + 's');
      }
    }));
    fs.writeFileSync(path.join(ROOT, 'build/sfx.json'), JSON.stringify(await (await page(browser)).evaluate(() => window.SFX)));
    console.log('frames', N);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
