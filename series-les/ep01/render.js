// Рендер кадров через Chromium (Playwright) → ffmpeg.
// node render.js stills 0.5,10,30     — отдельные кадры в PNG
// node render.js video out.mp4 [from] [to] — видео без звука
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const DATA = {
  words: JSON.parse(fs.readFileSync(path.join(DIR, 'words.json'))).words,
  amp: JSON.parse(fs.readFileSync(path.join(DIR, 'amp.json'))).amp,
};

(async () => {
  const [mode, a1, a2, a3] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.setContent('<html><body style="margin:0;background:#000"><div id="r"></div></body></html>');
  await page.evaluate(d => { window.DATA = d; }, DATA);
  await page.addScriptTag({ path: path.join(DIR, '../art/art.js') });
  await page.addScriptTag({ path: path.join(DIR, 'timeline.js') });
  const total = await page.evaluate(() => TOTAL);
  const draw = t => page.evaluate(t => { document.getElementById('r').innerHTML = frame(t); }, t);

  if (mode === 'stills') {
    fs.mkdirSync(path.join(DIR, 'stills'), { recursive: true });
    for (const t of a1.split(',').map(Number)) {
      await draw(t);
      await page.screenshot({ path: path.join(DIR, 'stills', `t${t.toFixed(2)}.png`) });
    }
    console.log('total', total);
  } else {
    const from = +(a2 || 0), to = Math.min(+(a3 || total), total);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', '30', '-i', '-',
      '-vf', 'noise=alls=6,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', a1], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n0 = Math.round(from * 30), n1 = Math.round(to * 30);
    const t0 = Date.now();
    for (let n = n0; n < n1; n++) {
      await draw(n / 30);
      const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (n % 150 === 0) console.log(`кадр ${n}/${n1}  ${((Date.now() - t0) / 1000).toFixed(0)}с`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('готово', a1, 'длительность', ((n1 - n0) / 30).toFixed(2));
  }
  await browser.close();
})();
