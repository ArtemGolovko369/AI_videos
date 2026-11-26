// ---------- сцены части 4 ----------
const ICON_HAND = `<g transform="translate(0 20)" fill="#e3c3a3" stroke="${ST}" stroke-width="6" stroke-linejoin="round"><path d="M-60 90 L-60 -10 Q-60 -30 -44 -30 Q-28 -30 -28 -10 L-28 -70 Q-28 -92 -10 -92 Q8 -92 8 -70 L8 -80 Q8 -100 26 -100 Q44 -100 44 -80 L44 -60 Q44 -80 62 -80 Q80 -80 80 -60 L80 40 Q80 90 30 100 L-30 100 Q-60 96 -60 90Z"/></g>`;
const ICON_DOOR = `<g transform="translate(0 20)"><rect x="-70" y="-100" width="140" height="200" rx="6" fill="#5d6677" stroke="#e9edf5" stroke-width="7"/><circle cx="40" cy="6" r="9" fill="#e9edf5"/><rect x="-100" y="96" width="200" height="10" fill="#e9edf5"/></g>`;
function headlamp(x, y, tx, ty, w, op = 1) { return beam(x, y, tx, ty, w, op); }
function darkness(op) { return `<rect x="-400" y="-400" width="2800" height="2800" fill="#000" opacity="${f(op)}"/>`; }
function breakerPanel(t, leverK, smoke = 0) { // щиток с рубильником, leverK: 0 вверх, 1 вниз
  let s = rect(-400, -400, 1880, 2800, '#1d1c1a');
  s += rect(230, 520, 620, 900, '#6c7586', `rx="18" stroke="${ST}" stroke-width="8"`) + rect(260, 550, 560, 840, '#596274', 'rx="10"');
  for (let i = 0; i < 6; i++) s += rect(300 + (i % 3) * 170, 600 + Math.floor(i / 3) * 140, 130, 100, '#2a3142', `rx="8" stroke="${ST}" stroke-width="4"`) + rect(345 + (i % 3) * 170, 625 + Math.floor(i / 3) * 140, 40, 50, '#e9edf5', 'rx="4"');
  // рубильник
  s += rect(440, 930, 200, 330, '#2a3142', `rx="14" stroke="${ST}" stroke-width="6"`);
  const ang = lerp(-35, 35, leverK);
  s += `<g transform="rotate(${f(ang)} 540 1095)"><rect x="525" y="930" width="30" height="170" fill="#c0c6d2" stroke="${ST}" stroke-width="5"/><rect x="490" y="900" width="100" height="44" rx="12" fill="#e0322f" stroke="${ST}" stroke-width="5"/></g>`;
  s += txt(540, 1300, leverK > .5 ? 'OFF' : 'ON', 40, leverK > .5 ? '#ff4040' : '#3ddc84');
  if (smoke > 0) for (let i = 0; i < 6; i++) { const d = ((t * .6 + i / 6) % 1); s += `<circle cx="${f(380 + i * 18 + Math.sin(t * 2 + i) * 30)}" cy="${f(620 - d * 380)}" r="${f(30 + d * 60)}" fill="#9aa3b6" opacity="${f(smoke * .35 * (1 - d))}"/>`; }
  return s;
}
function notebook(t, lines, stampTxt, tStamp) { // листок блокнота с правилом
  let s = rect(-400, -400, 1880, 2800, '#0d1018');
  s += `<g transform="rotate(-3 540 1000)">` + rect(150, 640, 780, 700, '#f3efe3', `rx="10" stroke="${ST}" stroke-width="6"`);
  for (let i = 0; i < 12; i++) s += `<line x1="170" y1="${720 + i * 52}" x2="910" y2="${720 + i * 52}" stroke="#9fb8d8" stroke-width="2"/>`;
  s += `<line x1="240" y1="640" x2="240" y2="1340" stroke="#e08a8a" stroke-width="3"/>`;
  for (let i = 0; i < 7; i++) s += `<circle cx="${210 + i * 110}" cy="640" r="14" fill="#0d1018"/>`;
  lines.forEach(([txt0, t0, t1, y, size, col]) => s += `<text x="270" y="${y}" font-family="Inter" font-style="italic" font-weight="900" font-size="${size}" fill="${col || '#1d2f6b'}">${typeText(txt0, seg(t, t0, t1))}</text>`);
  s += '</g>';
  const k = seg(t, tStamp, tStamp + .12);
  if (k > 0) s += `<g transform="translate(700 1250) rotate(-10) scale(${f(lerp(1.5, 1, k))})" opacity="${f(k * .92)}"><rect x="-230" y="-60" width="460" height="120" rx="14" fill="none" stroke="#e0322f" stroke-width="10"/>${txt(0, 18, stampTxt, 54, '#e0322f')}</g>`;
  return s;
}
function lightFloors(t, kOn, order = 'down') { // атриум, этажи гаснут/загораются
  let s = mallFloors(1);
  const fl = [560, 930, 1300];
  fl.forEach((fy, i) => {
    const idx = order === 'down' ? i : 2 - i; // какой этаж в очереди
    const on = clamp(kOn * 3 - idx);
    s += rect(-400, fy - 380, 1880, 380, '#000', `opacity="${f(.85 * (1 - on))}"`);
    if (on > 0) s += `<ellipse cx="540" cy="${fy - 150}" rx="600" ry="150" fill="url(#warmBlob)" opacity="${f(.35 * on)}"/>`;
  });
  return s;
}

function packOn(x, base, h, op = 1) { // рюкзак надет на манекена (анфас): мешок за спиной, лямки спереди
  const y = v => f(base - h * v);
  return {
    back: `<path d="M${f(x - h * .16)} ${y(.8)} Q${f(x - h * .2)} ${y(.5)} ${f(x - h * .15)} ${y(.42)} L${f(x + h * .15)} ${y(.42)} Q${f(x + h * .2)} ${y(.5)} ${f(x + h * .16)} ${y(.8)} Q${f(x)} ${y(.86)} ${f(x - h * .16)} ${y(.8)}Z" fill="#ff7a1a" stroke="${ST}" stroke-width="4" opacity="${f(op)}"/>`,
    front: `<path d="M${f(x - h * .075)} ${y(.82)} L${f(x - h * .06)} ${y(.5)} M${f(x + h * .075)} ${y(.82)} L${f(x + h * .06)} ${y(.5)}" stroke="#ff7a1a" stroke-width="${f(h * .022)}" stroke-linecap="round" opacity="${f(op)}"/>`,
  };
}

// 0. Итог голосования части 3
add(0, S(1) - .15, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0d12');
  const tb = Wt(0, 'ВЫКЛЮЧИТЬ');
  const dk = seg(t, .3, tb - .1), win = eout(seg(t, tb - .2, tb + .3));
  s += choiceCard(t, lerp(795, 900, win), 900, '2', 'СМОТРЕТЬ|ДАЛЬШЕ', ICON_EYE, -1, '#56627c', dk, 1 - .25 * win);
  s += choiceCard(t, lerp(285, 470, win), lerp(900, 860, win), '1', 'ВЫКЛЮЧИТЬ|КАМЕРЫ', ICON_SWITCH, -1, '#ffd23f', 0, 1 + .25 * win);
  const sk = seg(t, tb, tb + .14);
  if (sk > 0) s += `<g transform="translate(540 1290) rotate(-4) scale(${f(lerp(1.6, 1, eout(sk)))})" opacity="${f(sk)}">${rect(-420, -56, 840, 112, '#e0322f', `rx="14" stroke="${ST}" stroke-width="6"`)}${txt(0, 18, 'ВЫ ВЫБРАЛИ: ВЫКЛЮЧИТЬ', 54, '#fff')}</g>`;
  return cam(s, 1, 540, 960, sk > 0 && sk < 1 ? Math.sin(t * 60) * .8 : 0);
}, .2);
HUDOFF.push([0, S(1) - .2]);

// 1. Рубильник вниз → экраны гаснут → этажи гаснут
add(S(1) - .15, S(2) - .25, t => {
  const tl = Wt(1, 'ОПУСТИЛ'), tE = P(1, 1), tC = P(1, 2);
  if (t < tE - .05) {
    let s = breakerPanel(t, eout(seg(t, tl + .1, tl + .45)));
    s += `<g transform="translate(${f(lerp(600, 560, seg(t, tl, tl + .45)))} ${f(lerp(880, 1040, eout(seg(t, tl + .1, tl + .45))))})"><ellipse cx="0" cy="0" rx="80" ry="60" fill="#e3c3a3" stroke="${ST}" stroke-width="5"/><rect x="40" y="-30" width="300" height="70" fill="#2c3e63" stroke="${ST}" stroke-width="5"/></g>`;
    return cam(s, 1.15, 540, 1050, t > tl + .4 && t < tl + .6 ? Math.sin(t * 70) * 1 : 0);
  }
  if (t < tC - .1) {
    const k = seg(t, tE, tC - .2);
    return cam(monitors(t, { on: i => 1 - seg(k, i / 16, i / 16 + .06) }), 1.0, 540, 900);
  }
  const k = seg(t, tC, E(1) + .3);
  return cam(lightFloors(t, 1 - k, 'up'), 1.0, 540, 960);
}, .2);

// 2. Заставка (в темноте)
add(S(2) - .25, P(3, 0) - .05, t => {
  let s = mallFloors(.5) + dust(t, 50, 9, 0, 0, 1080, 1920, '#cfe0ff', .35, 2.4) + darkness(.7);
  return cam(s, lerp(1.12, 1.04, eout(seg(t, S(2), S(2) + 5))), 540, 960);
}, .4);
HUDOFF.push([S(2) - .3, P(3, 0) - .1]);

// 3. Тёмный коридор: «ВЫХОД» гаснет последней
add(P(3, 0) - .05, S(4) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0b0a');
  s += `<path d="M-400 1500 L380 1000 L700 1000 L1480 1500" fill="#11110f" stroke="#1a1a17" stroke-width="5"/>`;
  s += rect(380, 700, 320, 300, '#070707', `stroke="#1a1a17" stroke-width="5"`);
  const toff = Wt(3, 'ВЫХОД');
  const on = t < toff ? (Math.sin(t * 30) > -.3 ? 1 : .3) : (t < toff + .3 ? (Math.sin(t * 50) > 0 ? .5 : 0) : 0);
  s += exitSign(540, 620, 1.2, on);
  if (on > 0) s += `<ellipse cx="540" cy="900" rx="300" ry="200" fill="url(#greenBlob)" opacity="${f(.5 * on)}"/>`;
  return cam(s, lerp(1.0, 1.1, seg(t, S(3), S(4))), 540, 900);
}, .3);

// 4. На складе между коробок; луч под дверью проходит мимо
add(S(4) - .2, S(6) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#060606');
  // дверь со щелью внизу
  s += rect(360, 560, 360, 760, '#0d0d0d', `stroke="#1c1c1c" stroke-width="6"`);
  const ts = S(5), te = PE(5, 0);
  const bx = lerp(-200, 1300, seg(t, ts, te + .4));
  const near = clamp(1 - Math.abs(bx - 540) / 500);
  if (t > ts - .2) {
    s += `<rect x="360" y="1314" width="360" height="10" fill="#fffbe6" opacity="${f(.15 + .85 * near)}"/>`;
    s += `<ellipse cx="${f(clamp(bx, 360, 720))}" cy="1350" rx="${f(200 * near)}" ry="40" fill="url(#spot)" opacity="${f(.6 * near)}"/>`;
  }
  // коробки и герой в щели
  const box = (x, y, w, h) => rect(x, y, w, h, '#2b241a', `stroke="#3a3124" stroke-width="5"`) + `<line x1="${x}" y1="${y + h / 2}" x2="${x + w}" y2="${y + h / 2}" stroke="#3a3124" stroke-width="4"/>`;
  s += box(-60, 900, 300, 420) + box(-40, 560, 260, 340) + box(820, 820, 320, 500) + box(840, 520, 280, 300);
  s += `<g opacity="${f(.35 + .5 * near)}">${hero(300, 1330, 520, 'front')}</g>`;
  // ключи: волны справа налево
  if (t > Wt(4, 'КЛЮЧИ') - .1 && t < te + .5) { const wk = (t * 1.8) % 1; s += `<circle cx="${f(clamp(bx, 0, 1080))}" cy="1260" r="${f(30 + wk * 160)}" fill="none" stroke="#ffd23f" stroke-width="4" opacity="${f(.6 * (1 - wk))}"/>`; }
  return cam(s, 1.0 + .08 * near, 520, 1000);
}, .3);

// 5. Правило № 2
add(S(6) - .2, S(7) - .25, t => {
  const t1 = P(6, 1);
  return cam(notebook(t, [['ОН ХОДИТ', t1, t1 + .5, 830, 76], ['ТАМ, ГДЕ ТЕМНО', t1 + .4, t1 + 1.1, 930, 76, '#c0392b']], 'ПРАВИЛО № 2', t1 + 1.2), lerp(1.0, 1.05, seg(t, S(6), S(7))), 540, 990);
}, .3);

// 6. День 19: рубильник не поднимается, дым
add(S(7) - .25, S(8) - .2, t => {
  const tr = Wt(7, 'НЕ');
  const jerk = t > tr - .3 && t < tr + .6 ? Math.abs(Math.sin((t - tr) * 18)) * .25 : 0;
  let s = breakerPanel(t, 1 - jerk, seg(t, P(7, 2) - .3, P(7, 2) + .3));
  const fk = seg(t, Wt(7, 'ПРЕДОХРАНИТЕЛИ') - .1, Wt(7, 'ПРЕДОХРАНИТЕЛИ') + .3);
  if (fk > 0) for (let i = 0; i < 6; i++) { const x = 365 + (i % 3) * 170, y = 650 + Math.floor(i / 3) * 140; s += `<path d="M${x - 30} ${y - 30} l60 60 M${x + 30} ${y - 30} l-60 60" stroke="#ff4040" stroke-width="10" stroke-linecap="round" opacity="${f(fk)}"/>`; }
  s += darkness(.25) + headlamp(540, 1700, 540, 950, 380, .8);
  return cam(s, 1.0, 540, 980, jerk > 0 ? Math.sin(t * 60) * .6 : 0);
}, .3);

// 7. Схема: своя «табличка»
add(S(8) - .2, S(9) - .15, t => {
  let s = blueprint(t, 'СХЕМА №9 · СВОЯ ТАБЛИЧКА');
  const items = [
    [Wt(8, 'НАЛОБНЫЕ'), 230, 'ФОНАРЬ', `<circle cx="0" cy="0" r="56" fill="none" stroke="#fff" stroke-width="6"/><circle cx="0" cy="0" r="26" fill="#ffd23f"/><path d="M-90 0 h-40 M90 0 h40" stroke="#fff" stroke-width="10" stroke-linecap="round"/>`],
    [Wt(8, 'ПАУЭРБАНКИ'), 540, 'ПАУЭРБАНК', `<rect x="-70" y="-36" width="140" height="72" rx="14" fill="none" stroke="#fff" stroke-width="6"/><rect x="-50" y="-10" width="70" height="20" rx="4" fill="#3ddc84"/>`],
    [Wt(8, 'ПАКЕТЫ'), 850, 'ЗЕЛЁНЫЙ ПАКЕТ', `<path d="M-60 -50 L60 -50 L70 60 L-70 60Z" fill="rgba(61,220,132,.35)" stroke="#3ddc84" stroke-width="6"/><path d="M-30 -50 q30 -40 60 0" fill="none" stroke="#3ddc84" stroke-width="5"/>`],
  ];
  items.forEach(([tt, x, lb, ic], i) => {
    const k = popScale(t, tt - .1); if (k <= 0) return;
    s += `<g transform="translate(${x} 960) scale(${f(k)})">${ic}</g>` + mono(x, 1080, lb, 26, '#fff', 'middle');
    if (i < 2) s += txt(x + 155, 980, '+', 70, '#fff', `opacity="${f(seg(t, items[i + 1][0] - .2, items[i + 1][0]))}"`);
  });
  const ek = seg(t, PE(8, 3) - .2, PE(8, 3) + .4);
  if (ek > 0) {
    s += txt(540, 1200, '=', 80, '#fff', `opacity="${f(ek)}"`);
    s += `<g transform="translate(540 1320) scale(${f(back(ek))})"><ellipse cx="0" cy="0" rx="220" ry="90" fill="url(#greenBlob)"/>${rect(-110, -34, 220, 68, '#2fd27a', `rx="8" stroke="${ST}" stroke-width="4"`)}${txt(0, 12, 'ВЫХОД', 36, '#06180e')}</g>`;
  }
  return cam(s, lerp(1.0, 1.04, seg(t, S(8), S(9))), 540, 1050);
}, .3);

// 8. План коридора: шесть точек света
add(S(9) - .15, S(10) - .2, t => {
  let s = blueprint(t, 'СХЕМА №10 · КОРИДОР');
  s += rect(140, 900, 800, 260, 'none', 'stroke="#fff" stroke-width="5"');
  [['ЩИТОК', 260], ['СКЛАД', 540], ['ОХРАНА', 820]].forEach(([n, x]) => s += rect(x - 90, 900, 180, 60, 'none', 'stroke="#fff" stroke-width="3"') + mono(x, 940, n, 22, '#a9cbf5', 'middle'));
  s += rect(140, 1080, 40, 80, '#fff', 'opacity=".6"') + mono(160, 1200, 'ВХОД', 22, '#a9cbf5', 'middle');
  for (let i = 0; i < 6; i++) {
    const k = popScale(t, S(9) + .2 + i * .25); if (k <= 0) continue;
    const x = 220 + i * 130;
    s += `<g transform="translate(${x} 1040) scale(${f(k)})"><circle r="70" fill="url(#greenBlob)"/><circle r="16" fill="#3ddc84" stroke="${ST}" stroke-width="3"/></g>`;
  }
  s += mono(540, 1300, typeText('6 ФОНАРЕЙ ПО ВСЕМУ КОРИДОРУ', seg(t, S(9) + .3, S(9) + 1.6)), 28, '#ffd23f', 'middle');
  return cam(s, 1.02, 540, 1060);
}, .3);

// 9. Коридор в зелёном свете → луч под дверью замирает и сворачивает
add(S(10) - .2, S(11) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#0c140f');
  s += `<path d="M-400 1500 L380 1000 L700 1000 L1480 1500" fill="#101a13" stroke="#1d2b21" stroke-width="5"/>`;
  s += rect(380, 640, 320, 360, '#0a0e0b', `stroke="#2a3a2e" stroke-width="6"`);
  for (let i = 0; i < 6; i++) { const q = i / 5, x = i % 2 ? lerp(700, 1300, q) : lerp(380, -220, q), y = lerp(760, 560, q); s += `<ellipse cx="${f(x)}" cy="${f(y + 60)}" rx="${f(120 + 120 * q)}" ry="${f(90 + 60 * q)}" fill="url(#greenBlob)"/>` + rect(x - 30 - 20 * q, y, 60 + 40 * q, 24 + 10 * q, '#2fd27a', `rx="4" stroke="${ST}" stroke-width="3"`); }
  // луч под дверью
  const tA = Wt(10, 'ДОШЛИ'), tStay = Wt(10, 'ПОСТОЯЛИ'), tGo = Wt(10, 'СВЕРНУЛИ');
  let bx = lerp(200, 540, eout(seg(t, tA - .6, tA + .4)));
  if (t > tGo - .1) bx = lerp(540, 1000, eio(seg(t, tGo - .1, tGo + .8)));
  const op = seg(t, tA - .8, tA - .4) * (1 - seg(t, tGo + .3, tGo + .9));
  s += `<rect x="380" y="994" width="320" height="8" fill="#fffbe6" opacity="${f(op * clamp(1 - Math.abs(bx - 540) / 300))}"/>`;
  s += `<ellipse cx="${f(clamp(bx, 380, 700))}" cy="1020" rx="160" ry="22" fill="url(#spot)" opacity="${f(op * clamp(1 - Math.abs(bx - 540) / 400))}"/>`;
  s += hero(540, 1560, 480, 'back');
  return cam(s, lerp(1.0, 1.08, seg(t, S(10), S(11))), 540, 1060);
}, .3);
DRONE.push([0, .3], [S(1), .8], [P(1, 2), .9], [E(1) + .3, .1], [S(2), .5], [S(3), .6], [Wt(4, 'ЗДЕСЬ'), .9], [S(5), .9], [PE(5, 1), .3], [S(7), .55], [S(10), .7], [Wt(10, 'ПОСТОЯЛИ'), .9], [Wt(10, 'СВЕРНУЛИ') + .5, .4], [S(11), .55]);

// 10. День 22: пауэрбанки, один гаснет; инфографика
add(S(11) - .25, S(12) - .15, t => {
  let s = room(1340) + darkness(.2);
  for (let i = 0; i < 30; i++) {
    const x = 120 + (i % 10) * 92, y = 1100 + Math.floor(i / 10) * 80;
    const dead = i === 29 && t > Wt(11, 'ОДИН');
    s += rect(x - 40, y - 24, 80, 48, '#2b3242', `rx="10" stroke="${ST}" stroke-width="4"`) + rect(x - 30, y - 7, 36, 12, dead ? '#3a2020' : '#3ddc84', 'rx="3"');
    if (dead && t < Wt(11, 'ОДИН') + .4) s += `<circle cx="${x}" cy="${y}" r="50" fill="none" stroke="#ff4040" stroke-width="5"/>`;
  }
  const ik = seg(t, P(11, 2), P(11, 2) + .4);
  if (ik > 0) s += `<g opacity="${f(ik)}">${rect(120, 720, 840, 200, '#123a6b', `rx="18" stroke="#fff" stroke-width="5"`)}${mono(540, 800, '6 ФОНАРЕЙ', 44, '#ffd23f', 'middle')}${mono(540, 870, '= 1 ПАУЭРБАНК / НОЧЬ', 40, '#fff', 'middle')}</g>`;
  return cam(s, lerp(1.0, 1.06, seg(t, S(11), S(12))), 540, 1000);
}, .3);

// 11. «Осталось 29 — меньше месяца»
add(S(12) - .15, S(13) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#0d1018');
  const tc = Wt(12, 'ДВАДЦАТЬ');
  const n = Math.round(lerp(30, 29, seg(t, tc - .2, tc + .3)));
  s += txt(540, 860, String(n), 300, '#ff4040', `stroke="${ST}" stroke-width="12" paint-order="stroke"`) + txt(540, 950, 'НОЧЕЙ ЗАРЯДА', 50, '#e9edf5');
  // месяц: 31 клетка, 29 закрашено
  const mk = seg(t, Wt(12, 'МЕНЬШЕ') - .3, Wt(12, 'МЕНЬШЕ') + .3);
  for (let i = 0; i < 31; i++) {
    const x = 160 + (i % 7) * 110, y = 1040 + Math.floor(i / 7) * 60;
    const fill = i < 29 ? '#3ddc84' : '#3a2020';
    s += rect(x, y, 96, 48, mk > 0 ? fill : '#1b2131', `rx="8" stroke="${i >= 29 && mk > 0 ? '#ff4040' : '#2a3142'}" stroke-width="4" opacity="${f(.35 + .65 * mk)}"`);
  }
  const fk = seg(t, P(12, 2), P(12, 2) + .3);
  if (fk > 0) s += `<g opacity="${f(fk)}">${rect(290, 1360, 500, 80, '#e0322f', `rx="12" stroke="${ST}" stroke-width="5"`)}${txt(540, 1414, 'НУЖНЫ ПРЕДОХРАНИТЕЛИ', 36, '#fff')}</g>`;
  return cam(s, 1.0, 540, 1050);
}, .3);

// 12. Журнал: заметка на полях и подпись
add(S(13) - .2, S(14) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#0c0a08');
  s += headlamp(540, 1900, 540, 1000, 520, .9);
  s += rect(110, 640, 860, 660, '#4a3a28', `rx="14" stroke="${ST}" stroke-width="6"`) + rect(140, 660, 400, 620, '#efe8d6', `stroke="${ST}" stroke-width="4"`) + rect(540, 660, 400, 620, '#f3eddc', `stroke="${ST}" stroke-width="4"`);
  const ink = '#1d2f6b';
  for (let i = 0; i < 8; i++) s += `<text x="164" y="${720 + i * 66}" font-family="Inter" font-style="italic" font-weight="800" font-size="24" fill="${ink}" opacity=".75">${String(i + 10).padStart(2, '0')}.11 — манекенов — 12</text>`;
  const tn = P(13, 2);
  const note = 'Предохр. — склад,';
  const note2 = '3-я полка';
  s += `<g transform="rotate(-8 760 800)"><text x="600" y="780" font-family="Inter" font-style="italic" font-weight="900" font-size="34" fill="#c0392b">${typeText(note, seg(t, tn - .3, tn + .9))}</text><text x="600" y="830" font-family="Inter" font-style="italic" font-weight="900" font-size="34" fill="#c0392b">${typeText(note2, seg(t, tn + .7, tn + 1.4))}</text></g>`;
  const sk = seg(t, Wt(13, 'ПОДПИСЬ') - .2, Wt(13, 'ПОДПИСЬ') + .2);
  s += `<text x="900" y="1240" text-anchor="end" font-family="Inter" font-style="italic" font-weight="900" font-size="54" fill="#1d2f6b" opacity="${f(sk)}">${INITIALS}</text>`;
  // лупа
  const lk = seg(t, P(13, 1) - .3, P(13, 1));
  const lx = t < Wt(13, 'ПОДПИСЬ') - .2 ? 760 : lerp(760, 830, seg(t, Wt(13, 'ПОДПИСЬ') - .2, Wt(13, 'ПОДПИСЬ') + .2));
  const ly = t < Wt(13, 'ПОДПИСЬ') - .2 ? 800 : lerp(800, 1220, seg(t, Wt(13, 'ПОДПИСЬ') - .2, Wt(13, 'ПОДПИСЬ') + .2));
  if (lk > 0) s += `<circle cx="${f(lx)}" cy="${f(ly)}" r="150" fill="rgba(255,255,255,.08)" stroke="#e9edf5" stroke-width="12" opacity="${f(lk)}"/><path d="M${f(lx + 106)} ${f(ly + 106)} l90 90" stroke="#e9edf5" stroke-width="26" stroke-linecap="round" opacity="${f(lk)}"/>`;
  return cam(s, lerp(1.0, 1.15, seg(t, S(13), E(13))), lerp(540, 700, seg(t, S(13), E(13))), lerp(960, 1000, seg(t, S(13), E(13))));
}, .3);

// 13. Сплит: журнал ↔ блокнот, линии между буквами → «Это мой почерк»
add(S(14) - .2, S(16) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#0d1018');
  const ink = '#1d2f6b';
  const pk = eout(seg(t, Wt(14, 'БЛОКНОТ') - .3, Wt(14, 'БЛОКНОТ') + .3));
  // слева журнал
  s += rect(40, 640, 480, 640, '#efe8d6', `rx="10" stroke="${ST}" stroke-width="5"`) + mono(70, 690, 'ЖУРНАЛ ОБХОДА', 24, '#7a6a4a');
  s += `<text x="70" y="820" font-family="Inter" font-style="italic" font-weight="900" font-size="54" fill="${ink}">сходиться</text>`;
  s += `<text x="70" y="1180" font-family="Inter" font-style="italic" font-weight="900" font-size="54" fill="${ink}">${INITIALS}</text>`;
  // справа блокнот (из части 2)
  s += `<g transform="translate(${f(lerp(700, 0, pk))} 0)">` + rect(560, 640, 480, 640, '#f3efe3', `rx="10" stroke="${ST}" stroke-width="5"`) + mono(590, 690, 'МОЙ БЛОКНОТ', 24, '#7a6a4a');
  for (let i = 0; i < 10; i++) s += `<line x1="570" y1="${740 + i * 52}" x2="1030" y2="${740 + i * 52}" stroke="#9fb8d8" stroke-width="2"/>`;
  s += `<text x="590" y="820" font-family="Inter" font-style="italic" font-weight="900" font-size="54" fill="${ink}">сходиться</text>`;
  s += `<text x="590" y="1180" font-family="Inter" font-style="italic" font-weight="900" font-size="54" fill="${ink}">${INITIALS}</text></g>`;
  // пунктиры между одинаковыми буквами
  const lk = seg(t, Wt(14, 'БУКВЫ') - .2, Wt(14, 'НАКЛОН') + .3);
  for (let i = 0; i < 6; i++) { const x1 = 90 + i * 40, x2 = 610 + i * 40; s += pline(x1, 830, x2, 830, seg(lk, i / 7, i / 7 + .3), '#ffd23f', 4, '10 8'); }
  s += pline(170, 1190, 690, 1190, seg(lk, .6, 1), '#ffd23f', 4, '10 8');
  const mk = seg(t, S(15) - .1, S(15) + .2);
  if (mk > 0) {
    s += rect(30, 630, 1020, 660, 'none', `rx="14" stroke="#ff4040" stroke-width="${f(10 * mk)}"`);
    s += darkness(.25 * mk);
  }
  return cam(s, 1.0 + .06 * mk, 540, 960);
}, .3);
DRONE.push([S(13), .6], [S(15) - .2, .3], [S(15), .0], [S(16), .0], [S(16) + .6, .5]);

// 14. День 25: луч по полкам → коробка → рубильник вверх
add(S(16) - .25, S(17) - .15, t => {
  const tUp = Wt(16, 'ПОДНЯЛ');
  if (t < P(16, 3) - .1) {
    let s = rect(-400, -400, 1880, 2800, '#060606');
    for (let j = 0; j < 4; j++) {
      s += rect(60, 640 + j * 200, 960, 16, '#3a3124');
      for (let i = 0; i < 6; i++) { const hi = j === 2 && i === 3; s += rect(90 + i * 155, 640 + j * 200 - 110, 130, 110, hi ? '#6b5a3a' : '#2b241a', `stroke="${hi ? '#ffd23f' : '#3a3124'}" stroke-width="${hi ? 6 : 4}"`); if (hi) s += txt(90 + i * 155 + 65, 640 + j * 200 - 50, 'ПРЕДОХР.', 22, '#ffd23f'); }
    }
    s += mono(1000, 1050, '3', 40, '#ffd23f', 'end');
    const tk = seg(t, S(16), Wt(16, 'КОРОБКА'));
    const bx = lerp(200, 90 + 3 * 155 + 65, eio(tk)), by = lerp(600, 640 + 2 * 200 - 55, eio(tk));
    s = `<g>${s}</g>` + darkness(.55) + headlamp(540, 1900, bx, by, 170, 1);
    return cam(s, lerp(1.0, 1.15, seg(t, Wt(16, 'КОРОБКА'), P(16, 3))), lerp(540, bx, seg(t, Wt(16, 'КОРОБКА'), P(16, 3))), 960);
  }
  let s = breakerPanel(t, 1 - eout(seg(t, tUp, tUp + .35)));
  s += `<g transform="translate(${f(560)} ${f(lerp(1040, 880, eout(seg(t, tUp, tUp + .35))))})"><ellipse cx="0" cy="0" rx="80" ry="60" fill="#e3c3a3" stroke="${ST}" stroke-width="5"/><rect x="40" y="-30" width="300" height="70" fill="#2c3e63" stroke="${ST}" stroke-width="5"/></g>`;
  s += darkness(.35 * (1 - seg(t, tUp + .3, tUp + .6)));
  return cam(s, 1.15, 540, 1050, t > tUp + .3 && t < tUp + .5 ? Math.sin(t * 70) : 0);
}, .25);

// 15. Свет вернулся → экраны → камера 16 пустая
add(S(17) - .15, S(18) - .2, t => {
  const tS = P(17, 1), t16 = P(17, 2);
  if (t < tS - .1) return cam(lightFloors(t, seg(t, S(17), PE(17, 0) + .2), 'down'), 1.0, 540, 960);
  if (t < t16 - .1) return monitors(t, { on: i => seg(t, tS + i * .05, tS + i * .05 + .1) });
  let s = rect(-400, -400, 1880, 2800, '#05070b') + cctvFrame(t, cctv(t, 0, 820, 300), 0);
  const nk = seg(t, Wt(17, 'НИКОГО') - .2, Wt(17, 'НИКОГО') + .3);
  if (nk > 0) s += rect(700, 860, 260, 400, 'none', `rx="12" stroke="#3ddc84" stroke-width="6" stroke-dasharray="16 10" opacity="${f(nk)}"`);
  return cam(s, 1.0, 540, 900);
}, .2);

// 16. Камера с манекенами: 13-й с оранжевым рюкзаком (единственное цветное пятно)
add(S(18) - .2, S(19) - .1, t => {
  let s = rect(-400, -400, 1880, 2800, '#05070b');
  const id = 'gs' + gid++;
  let inner = rect(60, 600, 960, 680, '#2a2a2a');
  const N = 13, gap = 70, x0 = 120;
  const bk0 = seg(t, Wt(18, 'ОРАНЖЕВЫЙ') - .3, Wt(18, 'ОРАНЖЕВЫЙ'));
  const pk13 = packOn(x0 + 12 * gap, 1160, 300, .25 + .75 * bk0);
  for (let i = 0; i < N; i++) inner += mannequin(x0 + i * gap, 1160, 300, { sw: 2.5 });
  s += `<filter id="${id}"><feColorMatrix type="saturate" values="0"/></filter>`;
  s += `<g filter="url(#${id})">${inner.split('<!--13-->')[0]}</g>`;
  for (let k = 0; k < 680; k += 5) s += `<line x1="60" y1="${600 + k}" x2="1020" y2="${600 + k}" stroke="#000" stroke-width="2" opacity=".2"/>`;
  s += mono(80, 640, 'CAM 04 · ОДЕЖДА', 26, '#fff') + rect(40, 580, 1000, 720, 'none', `rx="14" stroke="#2a3142" stroke-width="22"`);
  const xb = x0 + 12 * gap;
  // рюкзак на 13-м — в цвете: мешок за спиной, 13-й поверх (ч/б), лямки спереди
  const id2 = 'gs' + gid++;
  s += pk13.back + `<filter id="${id2}"><feColorMatrix type="saturate" values="0"/></filter><g filter="url(#${id2})">${mannequin(x0 + 12 * gap, 1160, 300, { sw: 2.5 })}</g>` + pk13.front;
  // номера 1..13
  const t13 = Wt(18, 'ТРИНАДЦАТЬ');
  for (let i = 0; i < N; i++) {
    const pk = popScale(t, lerp(P(18, 0) + .5, t13, i / 12), .15); if (pk <= 0) continue;
    s += `<g transform="translate(${x0 + i * gap} 820) scale(${f(pk)})"><circle r="22" fill="${i === 12 ? '#e0322f' : '#e9edf5'}" stroke="${ST}" stroke-width="3"/>${txt(0, 9, i + 1, 24, i === 12 ? '#fff' : '#0d1018')}</g>`;
  }
  const zk = eio(seg(t, P(18, 2) - .2, P(18, 2) + .8));
  return cam(s, lerp(1, 2.4, zk), lerp(540, xb, zk), lerp(960, 1000, zk));
}, .25);

// 17. Стул, где висел рюкзак, — пустой
add(S(19) - .1, S(20) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#11151d') + rect(-400, 1330, 1880, 900, '#0d1016');
  s += `<ellipse cx="540" cy="900" rx="700" ry="500" fill="#3d7be0" opacity=".14"/>`;
  // стул
  s += `<g stroke="${ST}" stroke-width="7" stroke-linejoin="round">${rect(380, 1000, 320, 40, '#3a4560')}${rect(390, 700, 300, 300, '#2a3142')}<path d="M400 1040 L380 1330 M680 1040 L700 1330 M420 1040 L440 1290 M660 1040 L640 1290" fill="none"/></g>`;
  const tn = Wt(19, 'НЕТ');
  if (t < P(19, 1)) s += `<g opacity="${f(1 - seg(t, P(19, 1) - .3, P(19, 1)))}">${backpack(540, 1000, 300)}</g>`;
  if (t > tn - .1) s += txt(540, 640, '?', 120, '#ff4040', `opacity="${f(seg(t, tn - .1, tn + .2))}"`);
  return cam(s, lerp(1.1, 1.25, seg(t, S(19), E(19))), 540, 1000, t > tn && t < tn + .2 ? Math.sin(t * 60) : 0);
}, .08);
DRONE.push([S(17), .5], [S(18), .7], [P(19, 1) - .3, .8], [P(19, 1), 0], [S(20) + .5, .45]);

// 18. Экран выбора
add(S(20) - .2, DUR + 1, t => {
  let s = rect(-400, -400, 1880, 2800, '#05070b');
  for (let i = 0; i < 13; i++) s += mannequin(120 + i * 70, 1160, 300, { sw: 2.5, dim: .5 });
  { const pk = packOn(120 + 12 * 70, 1160, 300); s += pk.back + mannequin(120 + 12 * 70, 1160, 300, { sw: 2.5, dim: .5 }) + pk.front; }
  s = `<g opacity=".3">${s}</g>` + rect(-10, -10, 1100, 1940, '#000', 'opacity=".3"');
  s += choiceCard(t, 285, 900, '1', 'ЗАБРАТЬ', ICON_HAND, Wt(20, 'ЗАБРАТЬ'), '#ffd23f');
  s += choiceCard(t, 795, 900, '2', 'ОСТАВИТЬ', ICON_DOOR, Wt(20, 'ОСТАВИТЬ'), '#ffd23f');
  const ok = seg(t, Wt(20, 'ОСТАВИТЬ'), Wt(20, 'ОСТАВИТЬ') + .3);
  if (ok > 0) s += `<g opacity="${f(ok)}"><circle cx="540" cy="900" r="52" fill="#0d1018" stroke="#9aa6bd" stroke-width="5"/>${txt(540, 914, 'ИЛИ', 34, '#e9edf5')}</g>`;
  const pk = popScale(t, P(20, 2));
  const pul = 1 + .03 * Math.sin(t * 6);
  if (pk > 0) s += `<g transform="translate(540 1250) scale(${(pk * pul).toFixed(3)})">${rect(-440, -48, 880, 96, '#e0322f', `rx="16" stroke="${ST}" stroke-width="5"`)}${txt(0, 16, 'ПИШИ 1 ИЛИ 2 — РЕШАЕТ БОЛЬШИНСТВО', 40, '#fff')}</g>`;
  if (pk > 0) s += mono(540, 1660, 'ЧАСТЬ 5 — ДЕНЬ 26', 34, '#9aa6bd', 'middle', `opacity="${f(seg(t, P(20, 2) + .4, P(20, 2) + .9))}"`);
  return s;
}, .3);

// ---------- HUD ----------
const DAYS = [[S(1), 18], [S(7), 19], [S(11), 22], [S(16), 25]];
DAYS.slice(1).forEach(([t]) => sfx(t, 'page', .9));
function dayAt(t) { let d = null, t0 = 0; for (const [tt, n] of DAYS) if (t >= tt) { d = n; t0 = tt; } return [d, t0]; }
function keyf(t, kf) {
  if (t <= kf[0][0]) return kf[0][1];
  for (let i = 1; i < kf.length; i++) if (t < kf[i][0]) return lerp(kf[i - 1][1], kf[i][1], eio(seg(t, kf[i - 1][0], kf[i][0])));
  return kf[kf.length - 1][1];
}
const tRed = P(4, 3), tGreen = Wt(10, 'СВЕРНУЛИ'), tFuse = Wt(16, 'ПОДНЯЛ');
const FOOD = [[0, 62], [S(7), 58], [S(11), 52], [S(16), 46]];
const NIGHTS = [[0, 30], [S(9), 30], [S(11), 30], [Wt(11, 'ОДИН'), 30], [Wt(12, 'ДВАДЦАТЬ') + .3, 29]];
const SLEEP = [[0, 68], [Wt(4, 'КЛЮЧИ'), 68], [Wt(4, 'КЛЮЧИ') + .6, 30], [S(11), 45], [S(16), 50]];
const WATER = [[0, 58], [S(7), 54], [S(11), 48], [S(16), 42]];
const DROPS = [Wt(4, 'КЛЮЧИ'), Wt(12, 'МЕНЬШЕ')];
const PLATES = [
  [P(7, 2), 'p', 'НЕТ СВЕТА', S(11) - .3],
  [S(9), 's', 'СВОИ ТАБЛИЧКИ', S(11) - .3],
  [P(12, 1), 'p', 'ЗАРЯД ТАЕТ', S(16) - .3],
  [tFuse, 's', 'ПРЕДОХРАНИТЕЛИ', S(18) - .3],
];
PLATES.forEach(([t]) => sfx(t, 'stamp', .8));
DROPS.forEach(t => sfx(t, 'alarm', .5));
const ONLYCOUNT = [S(18) - .2, S(20) - .2]; // без HUD, только счётчик манекенов

const elDay = document.getElementById('day'), elHud = document.getElementById('hud'), elPl = document.getElementById('plates');
const elB = [0, 1, 2, 3].map(i => document.getElementById('b' + i)), elV = [0, 1, 2, 3].map(i => document.getElementById('v' + i));
const elMC = document.getElementById('mcount'), elZ = document.getElementById('zone'), elBars = document.getElementById('bars');
function renderHUD(t) {
  const [d, t0] = dayAt(t);
  let on = d !== null ? clamp((t - S(1)) / .3) : 0;
  HUDOFF.forEach(([a, b]) => { if (t > a && t < b) on = 0; });
  const only = t > ONLYCOUNT[0] && t < ONLYCOUNT[1];
  elHud.style.opacity = on;
  elDay.style.visibility = elBars.style.visibility = elZ.style.visibility = only ? 'hidden' : 'visible';
  if (d !== null) {
    const fk = seg(t, t0, t0 + .35); const sy = fk < .5 ? 1 - fk * 2 : (fk - .5) * 2;
    const idx = DAYS.findIndex(x => x[1] === d); const shown = fk < .5 && idx > 0 ? DAYS[idx - 1][1] : d;
    elDay.innerHTML = `ДЕНЬ ${shown} <small>/ 365</small>`;
    elDay.style.transform = `scaleY(${Math.max(.02, sy).toFixed(3)})`;
  }
  // зона: вне маршрута → на маршруте (тьма) → вне маршрута (свои таблички)
  const red = t >= tRed && t < tGreen;
  const zt = red ? tRed : (t >= tGreen ? tGreen : -9);
  const zk = seg(t, zt, zt + .2);
  elZ.textContent = red ? 'ЗОНА: НА МАРШРУТЕ' : 'ЗОНА: ВНЕ МАРШРУТА';
  elZ.style.background = red ? '#e0322f' : '#22b45e';
  elZ.style.transform = `scale(${f(zt > 0 && zk < 1 ? lerp(1.5, 1, eout(zk)) : 1)})`;
  const nights = Math.round(keyf(t, NIGHTS));
  const fused = t >= tFuse + .3;
  const vals = [keyf(t, FOOD), fused ? 100 : nights / 30 * 100, keyf(t, SLEEP), keyf(t, WATER)];
  vals.forEach((v, i) => {
    elB[i].style.width = v.toFixed(1) + '%';
    let col = v < 20 ? '#ff4040' : v < 45 ? '#ffd23f' : (i === 3 ? '#6cc0ff' : '#e9edf5');
    if (i === 1) col = fused ? '#3ddc84' : (t > Wt(12, 'ДВАДЦАТЬ') ? '#ff4040' : '#e9edf5');
    elB[i].style.background = col;
    elV[i].textContent = i === 1 ? `≈ ${nights} НОЧЕЙ` : Math.round(v) + '%';
    if (i === 1) elV[i].style.color = col === '#e9edf5' ? '' : col;
  });
  elMC.innerHTML = `МАНЕКЕНЫ: <b style="color:${only ? '#ff4040' : '#fff'}">13</b>`;
  elMC.style.opacity = only ? (Math.sin(t * 12) > 0 ? 1 : .35) : 1;
  let h = '';
  PLATES.forEach(([tp, ty, tx, tEnd]) => {
    if (t < tp || t > tEnd) return;
    const k = seg(t, tp, tp + .14); const sc = lerp(1.6, 1, eout(k)); const o = k * (1 - seg(t, tEnd - .25, tEnd));
    const sh = t - tp < .25 ? Math.sin((t - tp) * 80) * 4 * (1 - (t - tp) / .25) : 0;
    h += `<div class="plate ${ty}" style="transform:translateX(${sh.toFixed(1)}px) scale(${sc.toFixed(3)}) rotate(${ty === 'p' ? -2 : 2}deg);opacity:${o.toFixed(2)}"><span>${ty === 'p' ? 'ПРОБЛЕМА:' : 'РЕШЕНИЕ:'}</span>${tx}</div>`;
  });
  elPl.innerHTML = on > 0 && !only ? h : '';
  let rf = 0; DROPS.forEach(td => { const q = t - td; if (q > 0 && q < .7) rf = Math.max(rf, (1 - q / .7) * (Math.sin(q * 30) * .3 + .7)); });
  document.getElementById('redflash').style.opacity = rf.toFixed(2);
}

const elTitle = document.getElementById('title');
function renderOverlays(t) {
  const a = S(2) - .1, b = P(3, 0) - .15;
  elTitle.style.opacity = (seg(t, a, a + .5) * (1 - seg(t, b - .4, b))).toFixed(2);
  elTitle.style.transform = `scale(${lerp(1.08, 1, eout(seg(t, a, a + 1.5))).toFixed(3)})`;
  let black = 0;
  if (t < .35) black = 1 - t / .35;
  black = Math.max(black, seg(t, E(1) + .2, E(1) + .5) * (1 - seg(t, S(2) - .1, S(2) + .3)));
  const tz = Wt(3, 'ЗАМЕР'); black = Math.max(black, seg(t, tz - .1, tz + .2) * (1 - seg(t, S(4) - .3, S(4))));
  if (t > DUR - .6) black = Math.max(black, seg(t, DUR - .6, DUR));
  document.getElementById('flash').style.opacity = black.toFixed(2);
}

// ---------- звуки ----------
(function () {
  sfx(Wt(0, 'ВЫКЛЮЧИТЬ'), 'stamp', 1.1);
  sfx(Wt(1, 'ОПУСТИЛ') + .4, 'slam', .9);
  for (let i = 0; i < 16; i++) sfx(P(1, 1) + i * .09, 'click', .35);
  sfx(P(1, 2), 'powerdown', .8);
  sfx(S(2) - .1, 'boom', 1);
  sfx(Wt(3, 'ВЫХОД'), 'buzz', .4); sfx(Wt(3, 'ВЫХОД') + .3, 'click', .7);
  sfx(Wt(4, 'КЛЮЧИ'), 'keys', .9, { pan: -.7 }); sfx(P(4, 3), 'keys', 1, { pan: 0 });
  sfx(S(4), 'breath', .4, { d: 6 });
  for (let i = 0; i < 8; i++) sfx(S(5) - .3 + i * .45, 'step', .6, { pan: -1 + i / 7 * 2 });
  sfx(PE(5, 1), 'keys', .4, { pan: 1 });
  sfx(P(6, 1) + 1.2, 'stamp', 1.1); sfx(P(6, 1), 'pencil', .5, { d: 1.2 });
  for (let i = 0; i < 4; i++) sfx(Wt(7, 'НЕ') - .2 + i * .17, 'clack', .7);
  sfx(P(7, 2) - .3, 'hiss', .5, { d: 2 });
  sfx(S(8), 'pencil', .6, { d: 3 });
  ['НАЛОБНЫЕ', 'ПАУЭРБАНКИ', 'ПАКЕТЫ'].forEach(w => sfx(Wt(8, w) - .1, 'pop', .55));
  sfx(Wt(8, 'ПАКЕТЫ'), 'sand', .5, { d: .8 });
  for (let i = 0; i < 6; i++) sfx(S(9) + .2 + i * .25, 'click', .55);
  sfx(Wt(10, 'ДОШЛИ') - .6, 'keys', .7); for (let i = 0; i < 4; i++) sfx(Wt(10, 'ДОШЛИ') - .6 + i * .4, 'step', .5);
  sfx(Wt(10, 'СВЕРНУЛИ'), 'keys', .4, { pan: .8 });
  sfx(Wt(11, 'ОДИН'), 'powerdown', .5);
  for (let i = 0; i < 6; i++) sfx(S(11) + .4 + i * .3, 'tick', .4);
  sfx(Wt(12, 'ДВАДЦАТЬ'), 'tick', .7);
  sfx(S(13), 'page', .6); sfx(P(13, 2), 'pencil', .4, { d: 1.5 });
  sfx(Wt(14, 'БЛОКНОТ'), 'whoosh', .5); sfx(Wt(14, 'БУКВЫ'), 'pencil', .4, { d: 1.5 });
  sfx(S(15), 'tone', .9, { d: 3 });
  sfx(S(16), 'step', .4); sfx(Wt(16, 'КОРОБКА'), 'scrape', .6);
  sfx(Wt(16, 'ПОДНЯЛ') + .3, 'slam', 1);
  sfx(S(17), 'hum', .7, { d: 3 });
  for (let i = 0; i < 16; i++) sfx(P(17, 1) + i * .05, 'click', .3);
  for (let i = 0; i < 13; i++) sfx(lerp(P(18, 0) + .5, Wt(18, 'ТРИНАДЦАТЬ'), i / 12), 'tick', .5);
  sfx(Wt(19, 'НЕТ'), 'boom', 1.1);
  for (let i = 0; i < 14; i++) sfx(S(20) + .4 + i * .5, 'tick', .45);
  sfx(Wt(20, 'ЗАБРАТЬ'), 'pop', .6); sfx(Wt(20, 'ОСТАВИТЬ'), 'pop', .6); sfx(P(20, 2), 'stamp', .9);
  DRONE.sort((a, b) => a[0] - b[0]).forEach(([t, v]) => sfx(t, 'drone_kf', v));
  sfx(DUR - 2.5, 'drone_kf', .4); sfx(DUR, 'drone_kf', 0);
})();

// обложка: ч/б ряд манекенов, на одном оранжевый рюкзак
window.COVER = function () {
  const id = 'gsc';
  let inner = rect(-400, -400, 1880, 2800, '#1e1e1e') + rect(-400, 1300, 1880, 900, '#141414');
  [80, 230, 385, 540, 700, 855, 1005].forEach(x => inner += mannequin(x, 1300, 640, {}));
  let s = `<filter id="${id}"><feColorMatrix type="saturate" values="0"/></filter><g filter="url(#${id})">${inner}</g>`;
  const pk = packOn(540, 1300, 640);
  s += pk.back + `<g filter="url(#${id})">${mannequin(540, 1300, 640, {})}</g>` + pk.front;
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="url(#vig)"/>`;
  return s;
};
