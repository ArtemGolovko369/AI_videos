// node tools/render.js preview t1 t2 ...   -> build/preview_<t>.png
// node tools/render.js all [fps]          -> build/frames/%05d.jpg
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
(async () => {
  const mode = process.argv[2];
  const tm = JSON.parse(fs.readFileSync(path.join(ROOT, 'build/timing.json')));
  const browser = await chromium.launch();
  const N = mode === 'all' ? 4 : 1;
  const fps = 30, dur = tm.lines.at(-1).s + tm.lines.at(-1).d + 2.2;
  const total = Math.ceil(dur * fps);
  const frames = mode === 'all' ? [...Array(total).keys()] : process.argv.slice(3).map(Number);
  if (mode === 'all') fs.mkdirSync(path.join(ROOT, 'build/frames'), { recursive: true });
  const work = async (k) => {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    await page.goto('file://' + path.join(ROOT, 'tools/scene.html'));
    await page.evaluate((t) => window.setup(t), tm);
    await page.evaluate(() => document.fonts.ready);
    for (let i = k; i < frames.length; i += N) {
      const t = mode === 'all' ? frames[i] / fps : frames[i];
      await page.evaluate((t) => window.render(t), t);
      const out = mode === 'all' ? `build/frames/${String(frames[i]).padStart(5, '0')}.jpg` : `build/preview_${t}.png`;
      await page.screenshot({ path: path.join(ROOT, out), type: mode === 'all' ? 'jpeg' : 'png', quality: mode === 'all' ? 92 : undefined });
      if (mode === 'all' && i % 300 === 0) console.log('frame', i, '/', total);
    }
  };
  await Promise.all([...Array(N).keys()].map(work));
  await browser.close();
  console.log('done', frames.length, 'frames, dur', dur.toFixed(2));
})();
