const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..'); const TL = JSON.parse(fs.readFileSync(ROOT + '/build/timeline.json'));
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(tl => { window.TL = tl; }, TL); await p.goto('file://' + ROOT + '/scene/index.html'); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => { window.renderAt(30); document.getElementById('scA').innerHTML = window.COVER(); document.getElementById('hud').style.opacity = 0; document.getElementById('plates').innerHTML = ''; document.getElementById('subs').innerHTML = ''; document.getElementById('flash').style.opacity = 0;
    const d = document.createElement('div'); d.style.cssText = 'position:absolute;left:0;right:0;top:250px;text-align:center';
    d.innerHTML = '<div style="font:900 120px/1 Inter;color:#fff;-webkit-text-stroke:14px #07080c;paint-order:stroke fill">365 ДНЕЙ В ТЦ<br><span style="color:#ffd23f">· 4 ·</span></div><div style="position:absolute;left:50%;top:1440px;white-space:nowrap;background:#e0322f;color:#fff;font:900 84px/1 Inter;padding:18px 34px;border-radius:18px;border:6px solid #07080c;transform:translateX(-50%) rotate(-3deg)">ЭТО МОЙ ПОЧЕРК</div>';
    document.querySelector('.ui').appendChild(d); });
  await p.screenshot({ path: ROOT + '/cover.jpg', type: 'jpeg', quality: 92 }); await b.close(); })();
