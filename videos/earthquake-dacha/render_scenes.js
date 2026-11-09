// Render build/svg/*.svg to build/png/*.png at 1350x2400 (1.25x, headroom for camera moves).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2] || 'build';
  const svgs = fs.readdirSync(path.join(dir, 'svg')).filter(f => f.endsWith('.svg'));
  fs.mkdirSync(path.join(dir, 'png'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1.25 });
  for (const f of svgs) {
    const svg = fs.readFileSync(path.join(dir, 'svg', f), 'utf8');
    await page.setContent(`<html><body style="margin:0;background:#000">${svg}</body></html>`);
    await page.screenshot({ path: path.join(dir, 'png', f.replace('.svg', '.png')), clip: { x: 0, y: 0, width: 1080, height: 1920 } });
  }
  await browser.close();
  console.log('rendered', svgs.length);
})();
