// Рендер листа персонажей и листа локаций в PNG через Playwright.
const A = require('./art.js');
const { chromium } = require('playwright');
const fs = require('fs');

const bgTxt = '#e9e2d0', sub = '#9aa3b8';

function svgWrap(w, h, inner) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><defs>${A.defs()}</defs>${inner}</svg>`;
}
function scene(inner, extras = '') {
  return `<svg viewBox="0 0 1080 1920" width="100%" height="100%"><defs>${A.defs()}</defs>${inner}${extras}${A.vignette(1080, 1920)}${A.grain(1080, 1920)}</svg>`;
}
function label(x, y, t, s = 44, c = bgTxt, w = 'bold') {
  return `<text x="${x}" y="${y}" text-anchor="middle" font-family="DejaVu Sans" font-weight="${w}" font-size="${s}" fill="${c}">${t}</text>`;
}

// ---------- лист персонажей ----------
function charSheet() {
  const W = 2100, H = 2350;
  let s = `<rect width="${W}" height="${H}" fill="#0f1220"/>`;
  s += label(W / 2, 90, 'ВЫЖИВАНИЕ В ЛЕСУ — ПЕРСОНАЖИ', 60);
  const cols = [
    { x: 350, f: A.sveta, name: 'СВЕТА, 38', d1: 'курьер · рассказчица', d2: 'тёплый цвет: оранжевая куртка', o: { emo: 'smile' } },
    { x: 1050, f: A.marina, name: 'МАРИНА', d1: 'одноклассница · полицейская', d2: 'холодный цвет: тёмно-синий', o: { emo: 'serious', torch: true } },
    { x: 1750, f: A.owner, name: 'СТАРЫЙ ХОЗЯИН', d1: 'бывший хозяин дома', d2: 'лицо в тени — только глаза и улыбка', o: { smile: 1 } },
  ];
  for (const c of cols) {
    s += `<ellipse cx="${c.x}" cy="1240" rx="260" ry="34" fill="#000" opacity=".4"/>`;
    s += `<g transform="translate(${c.x - 200 * 1.4} ${1240 - 760 * 1.4}) scale(1.4)">${c.f(c.o)}</g>`;
    s += label(c.x, 1330, c.name, 52) + label(c.x, 1385, c.d1, 32, sub, 'normal') + label(c.x, 1430, c.d2, 28, sub, 'normal');
  }
  // эмоции
  s += label(W / 2, 1540, 'ЭМОЦИИ И ПОЗЫ РТА (для липсинка и моргания)', 38, sub);
  const heads = [
    [A.sveta, { emo: 'neutral' }, 'спокойна'], [A.sveta, { emo: 'scared' }, 'страх'], [A.sveta, { emo: 'smirk' }, 'нервная шутка'], [A.sveta, { emo: 'scared', mouth: 2 }, 'рот: открыт'], [A.sveta, { blink: 1 }, 'моргание'],
    [A.marina, { emo: 'serious' }, 'серьёзна'], [A.marina, { emo: 'scared' }, 'страх'], [A.marina, { emo: 'serious', look: -1 }, 'слушает'],
    [A.owner, { smile: 0, face: true }, 'лицо (воспоминание)'], [A.owner, { smile: 1, silhouette: true }, 'силуэт'],
  ];
  heads.forEach(([f, o, t], i) => {
    const col = i % 5, row = Math.floor(i / 5);
    const x = 110 + col * 390, y = 1600 + row * 360;
    s += `<rect x="${x}" y="${y}" width="320" height="300" rx="24" fill="#171b2c"/>`;
    s += `<svg x="${x}" y="${y}" width="320" height="260" viewBox="${f === A.owner ? '125 95 190 190' : '110 90 180 190'}">${f(o)}</svg>`;
    s += label(x + 160, y + 285, t, 26, sub, 'normal');
  });
  return svgWrap(W, H, s);
}

// ---------- лист локаций ----------
function locSheet() {
  const tw = 480, th = 853, gap = 36, W = 4 * tw + 5 * gap, H = 2 * th + 3 * gap + 260 + 520;
  const t = 1.2;
  const locs = [
    ['1. ИЗБА: ЗАПИСКА', A.bgInterior({ t }) + A.darkness(1080, 1920, [{ x: 330, y: 1060, r: 520 }], 0.9, 'd1') + A.warmLight(330, 1050, 500)],
    ['2. ЛЕС, ФУРГОН', A.bgForest({ t }) + A.snowStreaks(1080, 1920, 140, 4, t, 0.55)],
    ['3. ДОМ СНАРУЖИ', A.bgHouseExt({ t }) + A.snowStreaks(1080, 1920, 110, 9, t, 0.45)],
    ['4. ИЗБА: ПЕЧЬ, ЛЮК', A.bgInterior({ t, fire: 1, hatch: 'ajar' }) + A.darkness(1080, 1920, [{ x: 920, y: 1050, r: 1000 }], 0.75, 'd4')],
    ['5. ПОДВАЛ', A.bgCellar({ t }) + A.darkness(1080, 1920, [{ x: 700, y: 1200, r: 800 }], 0.8, 'd5') + A.warmLight(700, 1150, 700, .8)],
    ['6. ВОСПОМИНАНИЕ: ВЫСЕЛЕНИЕ', A.bgEviction()],
    ['7. ФИНАЛ: ЛЮК СНИЗУ', A.bgHatchFromBelow({ t }) + A.darkness(1080, 1920, [{ x: 540, y: 820, r: 700 }], 0.6, 'd7') + A.warmLight(540, 1100, 600, .9)],
    ['8. ЗАСТАВКА', A.titleCard({ t })],
  ];
  let s = `<rect width="${W}" height="${H}" fill="#0f1220"/>` + label(W / 2, 90, 'ЛОКАЦИИ И РЕКВИЗИТ', 60);
  locs.forEach(([name, inner], i) => {
    const col = i % 4, row = Math.floor(i / 4);
    const x = gap + col * (tw + gap), y = 150 + row * (th + gap + 70);
    s += `<svg x="${x}" y="${y}" width="${tw}" height="${th}" viewBox="0 0 1080 1920" preserveAspectRatio="xMidYMid slice"><defs>${A.defs()}</defs>${inner}${i === 0 || i === 3 ? A.hud(i === 0 ? '23:47' : '00:04', i === 0 ? 12 : 3) : ''}${A.vignette(1080, 1920)}${A.grain(1080, 1920)}</svg>`;
    s += label(x + tw / 2, y + th + 48, name, 30, bgTxt);
  });
  // реквизит
  const py = 150 + 2 * (th + gap + 70) + 40;
  s += label(W / 2, py, 'РЕКВИЗИТ', 38, sub);
  const props = [
    [A.note(0, 0, 1.3), 'записка'], [A.matchbox(0, 0, 1.2, 3), 'коробок: 3 спички'], [A.photo(0, 0, 1.2), 'фото дома'], [A.mug(0, 30, 1.6, 0.4), 'кружка: тёплая'],
    [`<g transform="scale(0.85)">${A.hud('00:00', 3).replace('translate(540 150)', 'translate(0 -10)')}</g>`, 'HUD: время + спички'],
  ];
  props.forEach(([g, name], i) => {
    const x = gap + i * ((W - 2 * gap) / 5) + 40, w = (W - 2 * gap) / 5 - 80;
    s += `<rect x="${x}" y="${py + 30}" width="${w}" height="380" rx="24" fill="#171b2c"/>`;
    s += `<g transform="translate(${x + w / 2} ${py + 210})">${g}</g>`;
    s += label(x + w / 2, py + 460, name, 28, sub, 'normal');
  });
  return svgWrap(W, H, s);
}

(async () => {
  const out = process.argv[2] || '.';
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [name, svg] of [['characters', charSheet()], ['locations', locSheet()]]) {
    fs.writeFileSync(`${out}/${name}.svg`, svg);
    const m = svg.match(/width="(\d+)" height="(\d+)"/);
    await page.setViewportSize({ width: +m[1], height: +m[2] });
    await page.setContent(`<html><body style="margin:0;background:#000">${svg}</body></html>`);
    await page.screenshot({ path: `${out}/${name}.png` });
    console.log('ok', name);
  }
  await browser.close();
})();
