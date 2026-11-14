// Растеризация frames/*.svg → *.png (1080×1920) через Playwright Chromium; SVG удаляются.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    await p.setContent(`<html><body style="margin:0">${fs.readFileSync(path.join(dir, f), 'utf8')}</body></html>`);
    await p.screenshot({ path: path.join(dir, f.replace('.svg', '.png')) });
    fs.unlinkSync(path.join(dir, f));
  }
  await b.close();
})();
