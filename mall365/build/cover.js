const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..'); const TL = JSON.parse(fs.readFileSync(ROOT + '/build/timeline.json'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(tl => { window.TL = tl; }, TL); await p.goto('file://' + ROOT + '/scene/index.html'); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { window.renderAt(4.6); document.getElementById('subs').innerHTML = ''; document.getElementById('flash').style.opacity = 0;
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;left:0;right:0;top:250px;text-align:center';
    d.innerHTML = '<div style="font:900 150px/0.95 Inter;color:#fff;-webkit-text-stroke:14px #07080c;paint-order:stroke fill">365 ДНЕЙ<br>В ТЦ</div><div style="position:absolute;left:50%;top:1170px;margin-left:-330px;white-space:nowrap;background:#e0322f;color:#fff;font:900 96px/1 Inter;padding:18px 34px;border-radius:18px;border:6px solid #07080c;transform:rotate(-3deg)">13-Й МАНЕКЕН</div>';
    document.querySelector('.ui').appendChild(d); });
  await p.screenshot({ path: ROOT + '/cover.jpg', type: 'jpeg', quality: 92 }); await b.close(); })();
