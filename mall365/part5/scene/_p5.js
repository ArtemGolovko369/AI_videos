// ================= ЧАСТЬ 5 · «Охранник на месте» =================
const ICON_FIRE = `<g transform="translate(0 20)"><path d="M0 -110 Q70 -30 60 40 Q50 100 0 100 Q-50 100 -60 40 Q-70 -20 -20 -70 Q-10 -20 10 -10 Q20 -60 0 -110Z" fill="#ff7a1a" stroke="${ST}" stroke-width="6"/><path d="M0 -10 Q30 30 22 64 Q14 90 0 90 Q-14 90 -22 64 Q-28 34 0 -10Z" fill="#ffd23f"/></g>`;
const ICON_PEN = `<g transform="translate(0 20) rotate(-40)"><rect x="-22" y="-110" width="44" height="170" rx="8" fill="#3d7be0" stroke="${ST}" stroke-width="6"/><path d="M-22 60 L0 110 L22 60Z" fill="#f3efe3" stroke="${ST}" stroke-width="6"/><path d="M-6 96 L0 110 L6 96Z" fill="#0d1018"/></g>`;
const ICON_SWITCH_OFF = '';
const TODAY = 'ДЕНЬ 30';
// бейдж охраны с фото героя
function badge(cx, cy, sc = 1, year = '2018') {
  return `<g transform="translate(${cx} ${cy}) scale(${sc})">
    <rect x="-300" y="-190" width="600" height="380" rx="28" fill="#f4f2ec" stroke="${ST}" stroke-width="8"/>
    <rect x="-300" y="-190" width="600" height="86" rx="28" fill="#1d2f6b"/><rect x="-300" y="-130" width="600" height="26" fill="#1d2f6b"/>
    ${txt(0, -130, 'СЛУЖБА ОХРАНЫ', 44, '#fff')}
    <rect x="-260" y="-80" width="200" height="240" rx="10" fill="#cfd6e4" stroke="${ST}" stroke-width="5"/>
    <clipPath id="photoClip"><rect x="-260" y="-80" width="200" height="240" rx="10"/></clipPath>
    <g clip-path="url(#photoClip)">${hero(-160, 378, 420, 'front')}</g>
    <rect x="-30" y="-50" width="300" height="20" rx="6" fill="#9aa6bd"/><rect x="-30" y="-10" width="220" height="20" rx="6" fill="#9aa6bd"/>
    ${mono(-30, 70, 'ДЕЖУРНЫЙ: ' + INITIALS, 30, '#0d1018')}
    ${mono(-30, 120, 'ВЫДАН: ' + year, 30, '#e0322f')}
    <rect x="-40" y="-200" width="80" height="30" rx="10" fill="#c0c6d2" stroke="${ST}" stroke-width="5"/></g>`;
}
function clothesRow(t, o = {}) { // магазин одежды, 13 манекенов (последний — 13-й)
  let s = room(1340) + rackRail(560, -400, 2400);
  const N = 13, gap = 150, x0 = 140;
  for (let i = 0; i < N; i++) {
    const x = x0 + i * gap;
    if (i === 12) {
      const wob = o.wob || 0;
      let m = '';
      if (o.pack) { const pk = packOn(x, 1330, 640, 1, o.packCol); m += pk.back + mannequin(x, 1330, 640, {}) + pk.front; }
      else m += mannequin(x, 1330, 640, {});
      s += `<g transform="rotate(${f(wob)} ${x} 1330)">${m}</g>`;
    } else s += mannequin(x, 1330, 640, {});
  }
  return s;
}
// packOn с цветом (двойник: синий низ под оранжевой плёнкой)
const _packOn = packOn;
packOn = function (x, base, h, op = 1, col) {
  const r = _packOn(x, base, h, op);
  if (col === 'fake') {
    r.back = r.back.replace('#ff7a1a', '#ff8f3a') + `<path d="M${f(x - h * .16)} ${f(base - h * .62)} L${f(x + h * .16)} ${f(base - h * .62)} M${f(x - h * .17)} ${f(base - h * .5)} L${f(x + h * .17)} ${f(base - h * .5)}" stroke="#0d1018" stroke-width="${f(h * .008)}" stroke-dasharray="${f(h * .01)} ${f(h * .01)}"/>`;
  }
  return r;
};
function journalSpread(t, left, right, o = {}) {
  let s = rect(-400, -400, 1880, 2800, '#1a1712') + `<ellipse cx="540" cy="1000" rx="620" ry="460" fill="url(#warmBlob)" opacity=".3"/>`;
  s += rect(80, 600, 920, 760, '#4a3a28', `rx="14" stroke="${ST}" stroke-width="6"`) + rect(110, 620, 430, 720, '#efe8d6', `stroke="${ST}" stroke-width="4"`) + rect(540, 620, 430, 720, '#f3eddc', `stroke="${ST}" stroke-width="4"`);
  return s + left + right;
}
function inkLine(x, y, s, size = 34, col = '#1d2f6b', k = 1) {
  return `<text x="${x}" y="${y}" font-family="Inter" font-style="italic" font-weight="900" font-size="${size}" fill="${col}">${typeText(s, k)}</text>`;
}

// 0. Итог голосования части 4
add(0, S(1) - .15, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0d12');
  const tb = Wt(0, 'ЗАБРАТЬ');
  const dk = seg(t, .3, tb - .1), win = eout(seg(t, tb - .2, tb + .3));
  s += choiceCard(t, lerp(795, 900, win), 900, '2', 'ОСТАВИТЬ', ICON_DOOR, -1, '#56627c', dk, 1 - .25 * win);
  s += choiceCard(t, lerp(285, 470, win), lerp(900, 860, win), '1', 'ЗАБРАТЬ', ICON_HAND, -1, '#ffd23f', 0, 1 + .25 * win);
  const sk = seg(t, tb, tb + .14);
  if (sk > 0) s += `<g transform="translate(540 1290) rotate(-4) scale(${f(lerp(1.6, 1, eout(sk)))})" opacity="${f(sk)}">${rect(-380, -56, 760, 112, '#e0322f', `rx="14" stroke="${ST}" stroke-width="6"`)}${txt(0, 18, 'ВЫ ВЫБРАЛИ: ЗАБРАТЬ', 54, '#fff')}</g>`;
  return cam(s, 1, 540, 960, sk > 0 && sk < 1 ? Math.sin(t * 60) * .8 : 0);
}, .2);
HUDOFF.push([0, P(4, 0) - .1]);

// 1. Руки расстёгивают рюкзак → бейдж
add(S(1) - .15, S(3) - .25, t => {
  if (t < S(2) - .15) {
    let s = rect(-400, -400, 1880, 2800, '#14171e');
    const zk = eio(seg(t, S(1) + .2, P(1, 1)));
    s += `<g transform="translate(540 1000) scale(3.2)">` + backpack(0, 160, 330) + `</g>`;
    const zx = lerp(320, 760, zk);
    s += `<path d="M320 760 Q540 ${f(760 - 40 * zk)} ${f(zx)} 760" stroke="#0d1018" stroke-width="${f(10 + 30 * zk)}" fill="none"/>`;
    s += `<g transform="translate(${f(zx)} 740)"><rect x="-20" y="-10" width="40" height="70" rx="8" fill="#c0c6d2" stroke="${ST}" stroke-width="5"/></g>`;
    s += `<g transform="translate(${f(zx + 70)} 700)"><ellipse rx="80" ry="60" fill="#e3c3a3" stroke="${ST}" stroke-width="5"/></g><g transform="translate(220 780)"><ellipse rx="80" ry="60" fill="#e3c3a3" stroke="${ST}" stroke-width="5"/></g>`;
    return cam(s, 1.0, 540, 960);
  }
  let s = rect(-400, -400, 1880, 2800, '#0d1018') + `<ellipse cx="540" cy="960" rx="600" ry="500" fill="url(#warmBlob)" opacity=".25"/>`;
  s += badge(540, 960, 1.4);
  const fk = eio(seg(t, P(2, 1) - .1, PE(2, 2) + .5));
  const yk = seg(t, P(2, 2), P(2, 2) + .4);
  if (yk > 0) s += `<rect x="${540 - 42 + 1.4 * -30}" y="${960 + 1.4 * 88}" width="${f(1.4 * 260 * yk)}" height="${1.4 * 46}" fill="none" stroke="#e0322f" stroke-width="6" rx="8"/>`;
  return cam(s, lerp(1.0, 1.6, fk), lerp(540, 540 - 1.4 * 160, fk), lerp(960, 960 + 1.4 * 40, fk));
}, .25);

// 2. Заставка
add(S(3) - .25, P(4, 0) - .05, t => {
  let s = mallFloors(.8) + exitSign(860, 640, .8) + dust(t, 60, 9, 0, 0, 1080, 1920, '#cfe0ff', .45, 2.6) + darkness(.45);
  return cam(s, lerp(1.12, 1.04, eout(seg(t, S(3), S(3) + 5))), 540, 960);
}, .4);

// 3. День 26: мониторы, 14:00, все на месте
add(P(4, 0) - .05, S(5) - .15, t => {
  const tok = P(4, 3);
  let s = monitors(t, { hi: t > tok ? 3 : -1, hiCol: '#3ddc84' });
  s += rect(400, 1180, 280, 90, '#07090d', `rx="14" stroke="#3a4560" stroke-width="5"`) + mono(540, 1246, '14:00', 60, '#ffd23f', 'middle');
  if (t > tok) s += txt(monPos(3)[0] + MG.w / 2, monPos(3)[1] - 18, '✓ 13 НА МЕСТЕ', 26, '#3ddc84');
  // крошечный герой идёт по экрану одежды
  if (t > P(4, 1)) { const [x, y] = monPos(12); s += `<circle cx="${f(x + 30 + seg(t, P(4, 1), E(4)) * 140)}" cy="${y + 60}" r="7" fill="#ff7a1a"/>`; }
  return cam(s, 1.0, 540, 950);
}, .3);

// 4. Рюкзак снялся слишком легко, манекен качнулся
add(S(5) - .15, S(6) - .25, t => {
  const tl = Wt(5, 'СНЯЛСЯ') - .2;
  const k = eout(seg(t, tl, tl + .5));
  const wob = t > tl + .3 ? Math.sin((t - tl - .3) * 9) * 4 * Math.exp(-(t - tl - .3) * 1.5) : 0;
  let s = clothesRow(t, { pack: k < .2, wob });
  const x13 = 140 + 12 * 150;
  if (k >= .2) s += `<g transform="translate(${f(x13 - 220 * k)} ${f(1330 - 640 * .44 + 260 * k)}) rotate(${f(-20 * k)})">${backpack(0, 0, 200)}</g>`;
  s += hero(x13 - 280, 1340, 600, 'front', k > .2 ? 'read' : 'stand');
  return cam(s, 1.25, x13 - 160, 1000);
}, .3);

// 5. Ночь: полоска луча под дверью не уходит
add(S(6) - .25, S(7) - .15, t => {
  let s = rect(-400, -400, 1880, 2800, '#0c140f');
  s += `<path d="M-400 1500 L380 1000 L700 1000 L1480 1500" fill="#101a13" stroke="#1d2b21" stroke-width="5"/>`;
  s += rect(380, 640, 320, 360, '#0a0e0b', `stroke="#2a3a2e" stroke-width="6"`);
  for (let i = 0; i < 6; i++) { const q = i / 5, x = i % 2 ? lerp(700, 1300, q) : lerp(380, -220, q), y = lerp(760, 560, q); s += `<ellipse cx="${f(x)}" cy="${f(y + 60)}" rx="${f(120 + 120 * q)}" ry="${f(90 + 60 * q)}" fill="url(#greenBlob)"/>` + rect(x - 30 - 20 * q, y, 60 + 40 * q, 24 + 10 * q, '#2fd27a', `rx="4" stroke="${ST}" stroke-width="3"`); }
  const tA = P(6, 1);
  const bx = lerp(150, 540, eout(seg(t, tA - .3, tA + 1.2)));
  const op = seg(t, tA - .5, tA);
  s += `<rect x="380" y="994" width="320" height="8" fill="#fffbe6" opacity="${f(op * clamp(1 - Math.abs(bx - 540) / 300))}"/><ellipse cx="${f(clamp(bx, 380, 700))}" cy="1020" rx="160" ry="22" fill="url(#spot)" opacity="${f(op * clamp(1 - Math.abs(bx - 540) / 400))}"/>`;
  s += hero(540, 1560, 480, 'back');
  return cam(s, lerp(1.0, 1.12, seg(t, S(6), S(7))), 540, 1060);
}, .3);

// 6. Экран: 13-й без рюкзака, пунктир на месте рюкзака
add(S(7) - .15, S(8) - .15, t => {
  let s = rect(-400, -400, 1880, 2800, '#05070b');
  const id = 'gs' + gid++;
  let inner = rect(60, 600, 960, 680, '#2a2a2a');
  for (let i = 0; i < 13; i++) inner += mannequin(120 + i * 70, 1160, 300, { sw: 2.5 });
  s += `<filter id="${id}"><feColorMatrix type="saturate" values="0"/></filter><g filter="url(#${id})">${inner}</g>`;
  for (let k = 0; k < 680; k += 5) s += `<line x1="60" y1="${600 + k}" x2="1020" y2="${600 + k}" stroke="#000" stroke-width="2" opacity=".2"/>`;
  s += mono(80, 640, 'CAM 04 · ОДЕЖДА · 02:07', 26, '#fff') + rect(40, 580, 1000, 720, 'none', `rx="14" stroke="#2a3142" stroke-width="22"`);
  const xb = 120 + 12 * 70, h = 300;
  const dk = seg(t, Wt(7, 'БЕЗ') - .2, Wt(7, 'БЕЗ') + .3);
  if (dk > 0) s += `<path d="M${f(xb - h * .16)} ${f(1160 - h * .8)} Q${f(xb - h * .2)} ${f(1160 - h * .5)} ${f(xb - h * .15)} ${f(1160 - h * .42)} L${f(xb + h * .15)} ${f(1160 - h * .42)} Q${f(xb + h * .2)} ${f(1160 - h * .5)} ${f(xb + h * .16)} ${f(1160 - h * .8)}Z" fill="rgba(255,64,64,.12)" stroke="#ff4040" stroke-width="5" stroke-dasharray="12 8" opacity="${f(dk * (.6 + .4 * Math.sin(t * 8)))}"/>`;
  const zk = eio(seg(t, P(7, 2) - .2, P(7, 2) + .8));
  return cam(s, lerp(1, 2.3, zk), lerp(540, xb, zk), lerp(960, 1000, zk));
}, .25);

// 7. Сидит спиной к двери до утра: часы 02:00 → 06:00
add(S(8) - .15, S(9) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#0c140f');
  s += rect(330, 560, 420, 780, '#3a4a3e', `stroke="${ST}" stroke-width="7"`) + rect(-400, 1330, 1880, 900, '#0a110c');
  s += `<ellipse cx="540" cy="700" rx="600" ry="300" fill="url(#greenBlob)" opacity=".5"/>`;
  s += hero(540, 1470, 560, 'front');
  const ta = P(8, 2), tb = E(8) + .2;
  const k = Math.pow(seg(t, ta, tb), 1.8);
  const mins = Math.floor(lerp(120, 360, k)), hh = Math.floor(mins / 60), mm = mins % 60;
  s += rect(400, 600, 280, 100, '#07090d', `rx="14" stroke="#3a4560" stroke-width="5"`) + mono(540, 672, `0${hh}:${String(mm).padStart(2, '0')}`, 66, k > .98 ? '#3ddc84' : '#ff5a4a', 'middle');
  const op = 1 - seg(t, tb - .2, tb + .2);
  s += `<rect x="330" y="1334" width="420" height="10" fill="#fffbe6" opacity="${f(op * (.7 + .3 * Math.sin(t * 3)))}"/>`;
  if (k > .98) s += `<rect x="-400" y="-400" width="2800" height="2800" fill="#ffd8a0" opacity="${f(.12 * seg(t, tb, tb + .5))}"/>`;
  return cam(s, lerp(1.0, 1.06, seg(t, S(8), S(9))), 540, 980);
}, .3);
DRONE.push([0, .3], [S(1), .6], [P(2, 1), .2], [S(3), .5], [S(4), .5], [S(5), .65], [S(6), .7], [P(6, 1), .95], [S(8), .9], [E(8), .4], [S(9), .5]);

// 8. Правило № 3 под правилами 1 и 2
add(S(9) - .25, S(10) - .25, t => {
  const t1 = P(9, 1), t2 = P(9, 2);
  return cam(notebook(t, [
    ['1. СЧЁТ ДОЛЖЕН СХОДИТЬСЯ', -1, 0, 760, 40],
    ['2. ОН ХОДИТ ТАМ, ГДЕ ТЕМНО', -1, 0, 830, 40],
    ['3. СЧИТАЕТСЯ ВСЁ', t1, t1 + .6, 940, 64, '#c0392b'],
    ['даже то, что надето', t2, t2 + 1, 1010, 40],
  ], 'ПРАВИЛО № 3', t1 + .7), lerp(1.0, 1.05, seg(t, S(9), S(10))), 540, 990);
}, .3);

// 9. День 27: полка спорттоваров — синий рюкзак и оранжевый дождевик
add(S(10) - .25, S(11) - .2, t => {
  let s = room(1340) + rect(-400, 520, 1880, 30, '#1b2131') + txt(540, 600, 'СПОРТТОВАРЫ', 40, '#7e889c', 'letter-spacing="6"');
  for (let i = 0; i < 6; i++) { const x = 140 + i * 160; s += `<path d="M${x} 680 v40" stroke="#9aa3b6" stroke-width="6"/><circle cx="${x}" cy="680" r="8" fill="#9aa3b6"/>`; }
  const tn = Wt(10, 'НЕТ');
  if (t > tn - .2) for (let i = 0; i < 3; i++) s += txt(140 + i * 160, 800, '✕', 60, '#ff4040', `opacity="${f(seg(t, tn - .2, tn + .2))}"`);
  const tb = Wt(10, 'СИНИЙ');
  const bk = popScale(t, tb - .2);
  if (bk > 0) s += `<g transform="translate(620 1000) scale(${f(bk)})">${backpack(0, 0, 300).replace(/#ff7a1a/g, '#3d7be0').replace(/#e3600a/g, '#2b5bb0')}</g>`;
  const tr = Wt(10, 'ДОЖДЕВИК');
  const rk = popScale(t, tr - .3);
  if (rk > 0) s += `<g transform="translate(880 1000) scale(${f(rk)})"><path d="M-110 -300 Q0 -340 110 -300 L150 0 L-150 0Z" fill="#ff8f3a" stroke="${ST}" stroke-width="6"/><path d="M-40 -320 Q0 -380 40 -320" fill="none" stroke="${ST}" stroke-width="6"/><path d="M0 -300 L0 0" stroke="${ST}" stroke-width="3" opacity=".5"/></g>`;
  s += hero(250, 1340, 600, 'front');
  return cam(s, lerp(1.0, 1.06, seg(t, S(10), S(11))), 600, 980);
}, .3);

// 10. Схема: двойник рюкзака → вешаю на 13-го
add(S(11) - .2, S(12) - .2, t => {
  const tHang = P(11, 3) - .1;
  if (t >= tHang) {
    const k = eout(seg(t, tHang, tHang + .8));
    let s = clothesRow(t, { pack: k >= 1, packCol: 'fake' });
    const x13 = 140 + 12 * 150;
    if (k < 1) s += `<g transform="translate(${f(lerp(x13 - 220, x13, k))} ${f(lerp(1100, 1330 - 640 * .44, k))})">${backpack(0, 0, 200)}</g>`;
    s += hero(x13 - 280, 1340, 600, 'front', k < 1 ? 'read' : 'stand');
    return cam(s, 1.25, x13 - 160, 1000);
  }
  let s = blueprint(t, 'СХЕМА №11 · ДВОЙНИК РЮКЗАКА');
  const items = [
    [Wt(11, 'ОБТЯНУЛ'), 200, 'СИНИЙ РЮКЗАК', `<path d="M-60 60 Q-70 -60 0 -70 Q70 -60 60 60Z" fill="rgba(61,123,224,.4)" stroke="#fff" stroke-width="6"/>`],
    [Wt(11, 'ДОЖДЕВИКОМ'), 440, 'ДОЖДЕВИК', `<path d="M-60 -60 Q0 -80 60 -60 L80 60 L-80 60Z" fill="rgba(255,143,58,.45)" stroke="#fff" stroke-width="6"/>`],
    [Wt(11, 'СТЯЖКАМИ'), 680, 'СТЯЖКИ', `<path d="M-60 -30 h120 M-60 0 h120 M-60 30 h120" stroke="#fff" stroke-width="6" stroke-dasharray="10 6"/>`],
    [Wt(11, 'ГАЗЕТАМИ'), 900, 'ГАЗЕТЫ', `<rect x="-60" y="-50" width="120" height="100" fill="none" stroke="#fff" stroke-width="6"/><path d="M-44 -26 h88 M-44 0 h88 M-44 26 h60" stroke="#fff" stroke-width="4"/>`],
  ];
  items.forEach(([tt, x, lb, ic], i) => {
    const k = popScale(t, tt - .1); if (k <= 0) return;
    s += `<g transform="translate(${x} 960) scale(${f(k)})">${ic}</g>` + mono(x, 1070, lb, 24, '#fff', 'middle');
    if (i < 3) s += txt(x + 120, 980, '+', 60, '#fff', `opacity="${f(seg(t, items[i + 1][0] - .2, items[i + 1][0]))}"`);
  });
  const ek = seg(t, Wt(11, 'ВЕСИЛ') - .2, Wt(11, 'ВЕСИЛ') + .3);
  if (ek > 0) {
    s += txt(540, 1190, '=', 70, '#fff', `opacity="${f(ek)}"`);
    s += `<g transform="translate(540 1330) scale(${f(back(ek))})">${backpack(0, 60, 160).replace('#ff7a1a', '#ff8f3a')}</g>` + mono(540, 1450, 'ДВОЙНИК РЮКЗАКА', 32, '#ffd23f', 'middle', `opacity="${f(ek)}"`);
    s += mono(760, 1330, typeText('ВЕС КАК У ОРИГИНАЛА', seg(t, Wt(11, 'ВЕСИЛ'), Wt(11, 'ВЕСИЛ') + .8)), 24, '#a9cbf5');
  }
  return cam(s, 1.02, 540, 1080);
}, .3);

// 11. Ночь на экране: луч проходит мимо ряда
add(S(12) - .2, S(13) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#05070b');
  const id = 'gs' + gid++;
  let inner = rect(60, 600, 960, 680, '#2a2a2a');
  for (let i = 0; i < 13; i++) inner += mannequin(120 + i * 70, 1160, 300, { sw: 2.5 });
  s += `<filter id="${id}"><feColorMatrix type="saturate" values="0"/></filter><g filter="url(#${id})">${inner}</g>`;
  const pk = packOn(120 + 12 * 70, 1160, 300, 1, 'fake'); s += pk.back + `<g filter="url(#${id})">${mannequin(120 + 12 * 70, 1160, 300, { sw: 2.5 })}</g>` + pk.front;
  const bx = lerp(-200, 1400, seg(t, S(12) + .3, E(12) + .2));
  s += `<g clip-path="inset(0)">${beam(bx - 300, 400, bx, 1200, 90, .7)}</g>`;
  for (let k = 0; k < 680; k += 5) s += `<line x1="60" y1="${600 + k}" x2="1020" y2="${600 + k}" stroke="#000" stroke-width="2" opacity=".2"/>`;
  s += mono(80, 640, 'CAM 04 · ОДЕЖДА · 02:11', 26, '#fff') + rect(40, 580, 1000, 720, 'none', `rx="14" stroke="#2a3142" stroke-width="22"`);
  const mk = seg(t, Wt(12, 'МИМО') - .1, Wt(12, 'МИМО') + .3);
  if (mk > 0) s += `<g opacity="${f(mk)}">${rect(380, 1330, 320, 80, '#22b45e', `rx="12" stroke="${ST}" stroke-width="5"`)}${txt(540, 1384, 'МИМО ✓', 42, '#fff')}</g>`;
  return cam(s, 1.0, 540, 960);
}, .3);
DRONE.push([S(10), .55], [S(12), .7], [Wt(12, 'МИМО') + .5, .4], [S(13), .55]);

// 12. День 30: журнал с первой страницы
add(S(13) - .25, S(14) - .2, t => {
  const pg = P(13, 2);
  let L1 = inkLine(140, 700, 'ДЕНЬ 1', 34, '#7a3a2a', seg(t, pg - .2, pg + .3));
  ['День первый.', 'Десять вечера.', 'Я задержался', 'в книжном.'].forEach((w, i) => L1 += inkLine(150, 790 + i * 66, w, 34, '#1d2f6b', seg(t, pg + .2 + i * .25, pg + .6 + i * .25)));
  const s = journalSpread(t, L1 + mono(500, 1320, '— 1 —', 22, '#7a6a4a', 'middle'), '', {});
  const k = eio(seg(t, S(13), P(13, 1) + .5));
  return cam(s, lerp(1.0, 1.15, k), lerp(540, 380, k), lerp(980, 900, k));
}, .3);

// 13. Сплит: журнал ↔ блокнот, совпадения подсвечиваются → «восемь лет назад»
add(S(14) - .2, S(16) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#0d1018');
  s += rect(40, 600, 480, 720, '#efe8d6', `rx="10" stroke="${ST}" stroke-width="5"`) + mono(70, 650, 'ЖУРНАЛ ОБХОДА · с. 1', 22, '#7a6a4a');
  s += rect(560, 600, 480, 720, '#f3efe3', `rx="10" stroke="${ST}" stroke-width="5"`) + mono(590, 650, 'МОЙ БЛОКНОТ', 22, '#7a6a4a');
  for (let i = 0; i < 11; i++) s += `<line x1="570" y1="${700 + i * 54}" x2="1030" y2="${700 + i * 54}" stroke="#9fb8d8" stroke-width="2"/>`;
  const rows = [['День первый.', 760, P(14, 0)], ['Десять вечера.', 840, P(14, 1)], ['Я задержался', 920, P(14, 2)], ['в книжном.', 990, P(14, 2) + .5]];
  rows.forEach(([w, y, tt]) => {
    const hk = seg(t, tt - .1, tt + .3);
    if (hk > 0) s += rect(60, y - 40, 440, 54, '#ffd23f', `opacity="${f(.45 * hk)}" rx="6"`) + rect(580, y - 40, 440, 54, '#ffd23f', `opacity="${f(.45 * hk)}" rx="6"`);
    s += inkLine(80, y, w, 40) + inkLine(600, y, w, 40);
  });
  const sk = seg(t, S(15), S(15) + .3);
  if (sk > 0) s += `<g opacity="${f(sk)}">${pline(280, 1060, 800, 1060, seg(t, S(15), S(15) + .8), '#ffd23f', 6, '14 10')}${txt(540, 1120, 'СЛОВО В СЛОВО', 44, '#ffd23f', `stroke="${ST}" stroke-width="8" paint-order="stroke"`)}</g>`;
  const yk = seg(t, P(15, 2), P(15, 2) + .2);
  if (yk > 0) s += `<g transform="translate(280 1240) rotate(-8) scale(${f(lerp(1.5, 1, yk))})" opacity="${f(yk)}">${rect(-150, -44, 300, 88, 'none', `rx="12" stroke="#e0322f" stroke-width="8"`)}${txt(0, 16, '2018', 54, '#e0322f')}</g>`;
  return cam(s, lerp(1.0, 1.04, seg(t, S(14), S(16))), 540, 960);
}, .3);

// 14. Пролистывание до конца → последняя запись завтрашним числом
add(S(16) - .2, S(18) - .2, t => {
  const tf = S(16), te = PE(16, 0) + .2;
  let s = journalSpread(t, '', '');
  if (t < te) {
    const q = (seg(t, tf, te) * 20) % 1, w = 430 * Math.cos(q * Math.PI);
    s += `<path d="M540 620 L${f(540 + w)} ${f(620 - 30 * Math.sin(q * Math.PI))} L${f(540 + w)} ${f(1340 - 30 * Math.sin(q * Math.PI))} L540 1340Z" fill="#e6dfca" stroke="${ST}" stroke-width="3"/>`;
    s += mono(540, 580, String(2018 + Math.min(8, Math.floor(seg(t, tf, te) * 9))), 44, '#ffd23f', 'middle');
  } else {
    for (let i = 0; i < 6; i++) s += inkLine(130, 700 + i * 64, `${23 + i}-й д. — манекенов — 13`, 26, '#1d2f6b', 1);
    const tdate = Wt(16, 'ЗАВТРАШНИМ');
    const dk = seg(t, tdate - .1, tdate + .3);
    s += `<g opacity="${f(dk)}">${mono(570, 720, 'ДЕНЬ 31', 30, '#e0322f')}<g transform="translate(860 700) rotate(-10)">${rect(-100, -30, 200, 60, 'none', `rx="8" stroke="#e0322f" stroke-width="6"`)}${txt(0, 12, 'ЗАВТРА', 32, '#e0322f')}</g></g>`;
    s += inkLine(570, 820, 'Манекенов — 13.', 40, '#1d2f6b', seg(t, P(17, 0) - .1, PE(17, 0)));
    s += inkLine(570, 900, 'Охранник —', 40, '#c0392b', seg(t, P(17, 1) - .1, P(17, 1) + .5));
    s += inkLine(570, 970, 'на месте.', 40, '#c0392b', seg(t, P(17, 1) + .4, PE(17, 1)));
    s += `<text x="940" y="1260" text-anchor="end" font-family="Inter" font-style="italic" font-weight="900" font-size="48" fill="#1d2f6b" opacity="${f(seg(t, PE(17, 1), PE(17, 1) + .3))}">${INITIALS}</text>`;
  }
  const zk = eio(seg(t, te, te + 1));
  return cam(s, lerp(1.0, 1.5, zk), lerp(540, 760, zk), lerp(980, 880, zk));
}, .25);
DRONE.push([S(13), .5], [S(16), .7], [P(17, 1) - .1, .9], [P(17, 1), 0], [S(18) + .5, .45]);

// 15. Экран выбора
add(S(18) - .2, DUR + 1, t => {
  let s = journalSpread(t, inkLine(570, 900, 'Охранник — на месте.', 34, '#c0392b', 1), '');
  s += `<g transform="translate(900 1500)">${rect(-70, -40, 140, 100, '#5a6273', `rx="12" stroke="${ST}" stroke-width="5"`)}${[0, 1, 2, 3].map(i => `<path d="M${-30 + i * 20} -40 q10 ${-40 - 10 * Math.sin(t * 20 + i)} 20 0Z" fill="#4da3ff"/>`).join('')}</g>`;
  s = `<g opacity=".3">${s}</g>` + rect(-10, -10, 1100, 1940, '#000', 'opacity=".3"');
  s += choiceCard(t, 285, 900, '1', 'СЖЕЧЬ|ЖУРНАЛ', ICON_FIRE, Wt(18, 'СЖЕЧЬ'), '#ffd23f');
  s += choiceCard(t, 795, 900, '2', 'ДОПИСАТЬ|СТРАНИЦУ', ICON_PEN, Wt(18, 'ДОПИСАТЬ'), '#ffd23f');
  const ok = seg(t, Wt(18, 'ДОПИСАТЬ'), Wt(18, 'ДОПИСАТЬ') + .3);
  if (ok > 0) s += `<g opacity="${f(ok)}"><circle cx="540" cy="900" r="52" fill="#0d1018" stroke="#9aa6bd" stroke-width="5"/>${txt(540, 914, 'ИЛИ', 34, '#e9edf5')}</g>`;
  const pk = popScale(t, P(18, 2));
  const pul = 1 + .03 * Math.sin(t * 6);
  if (pk > 0) s += `<g transform="translate(540 1250) scale(${(pk * pul).toFixed(3)})">${rect(-440, -48, 880, 96, '#e0322f', `rx="16" stroke="${ST}" stroke-width="5"`)}${txt(0, 16, 'ПИШИ 1 ИЛИ 2 — РЕШАЕТ БОЛЬШИНСТВО', 40, '#fff')}</g>`;
  if (pk > 0) s += mono(540, 1660, 'ЧАСТЬ 6 — ДЕНЬ 31', 34, '#9aa6bd', 'middle', `opacity="${f(seg(t, P(18, 2) + .4, P(18, 2) + .9))}"`);
  return s;
}, .3);

// ---------- HUD ----------
const DAYS = [[P(4, 0), 26], [S(10), 27], [S(13), 30]];
DAYS.slice(1).forEach(([t]) => sfx(t, 'page', .9));
function dayAt(t) { let d = null, t0 = 0; for (const [tt, n] of DAYS) if (t >= tt) { d = n; t0 = tt; } return [d, t0]; }
function keyf(t, kf) {
  if (t <= kf[0][0]) return kf[0][1];
  for (let i = 1; i < kf.length; i++) if (t < kf[i][0]) return lerp(kf[i - 1][1], kf[i][1], eio(seg(t, kf[i - 1][0], kf[i][0])));
  return kf[kf.length - 1][1];
}
const tRed = P(4, 1), tGreen = S(6);
const FOOD = [[0, 46], [S(10), 42], [S(13), 36]];
const SLEEP = [[0, 50], [P(6, 1), 50], [P(6, 1) + .6, 18], [S(10), 30], [Wt(12, 'МИМО'), 30], [Wt(12, 'МИМО') + 1, 55]];
const WATER = [[0, 42], [S(10), 38], [S(13), 34]];
const tMissing = Wt(7, 'БЕЗ'), tFixed = Wt(12, 'МИМО');
const DROPS = [P(6, 1), tMissing];
const PLATES = [
  [S(8), 'p', 'СЧЁТ НЕ СХОДИТСЯ', S(13) - .3],
  [P(11, 0), 's', 'ДВОЙНИК РЮКЗАКА', S(13) - .3],
];
PLATES.forEach(([t]) => sfx(t, 'stamp', .8));
DROPS.forEach(t => sfx(t, 'alarm', .5));

const elDay = document.getElementById('day'), elHud = document.getElementById('hud'), elPl = document.getElementById('plates');
const elB = [0, 1, 2, 3].map(i => document.getElementById('b' + i)), elV = [0, 1, 2, 3].map(i => document.getElementById('v' + i));
const elMC = document.getElementById('mcount'), elZ = document.getElementById('zone');
function renderHUD(t) {
  const [d, t0] = dayAt(t);
  let on = d !== null ? clamp((t - DAYS[0][0]) / .3) : 0;
  HUDOFF.forEach(([a, b]) => { if (t > a && t < b) on = 0; });
  elHud.style.opacity = on;
  if (d !== null) {
    const fk = seg(t, t0, t0 + .35); const sy = fk < .5 ? 1 - fk * 2 : (fk - .5) * 2;
    const idx = DAYS.findIndex(x => x[1] === d); const shown = fk < .5 && idx > 0 ? DAYS[idx - 1][1] : d;
    elDay.innerHTML = `ДЕНЬ ${shown} <small>/ 365</small>`;
    elDay.style.transform = `scaleY(${Math.max(.02, sy).toFixed(3)})`;
  }
  const red = t >= tRed && t < tGreen;
  const zt = red ? tRed : (t >= tGreen ? tGreen : -9), zk = seg(t, zt, zt + .2);
  elZ.textContent = red ? 'ЗОНА: НА МАРШРУТЕ' : 'ЗОНА: ВНЕ МАРШРУТА';
  elZ.style.background = red ? '#e0322f' : '#22b45e';
  elZ.style.transform = `scale(${f(zt > 0 && zk < 1 ? lerp(1.5, 1, eout(zk)) : 1)})`;
  const vals = [keyf(t, FOOD), 100, keyf(t, SLEEP), keyf(t, WATER)];
  vals.forEach((v, i) => {
    elB[i].style.width = v.toFixed(1) + '%';
    let col = v < 20 ? '#ff4040' : v < 45 ? '#ffd23f' : (i === 3 ? '#6cc0ff' : '#e9edf5');
    if (i === 1) col = '#3ddc84';
    elB[i].style.background = col;
    elV[i].textContent = i === 1 ? 'ОТ СЕТИ' : Math.round(v) + '%';
    if (i === 1) elV[i].style.color = '#3ddc84';
  });
  const miss = t >= tMissing && t < tFixed;
  const fixK = seg(t, tFixed, tFixed + .5);
  elMC.innerHTML = `МАНЕКЕНЫ: <b>13</b>` + (miss || (t >= tFixed && fixK < 1) ? ` <b style="color:#fff;background:#e0322f;border-radius:6px;padding:2px 8px;opacity:${miss ? (Math.sin(t * 10) > 0 ? 1 : .4) : 1 - fixK}">−1 ПРЕДМЕТ</b>` : '');
  let h = '';
  PLATES.forEach(([tp, ty, tx, tEnd]) => {
    if (t < tp || t > tEnd) return;
    const k = seg(t, tp, tp + .14); const sc = lerp(1.6, 1, eout(k)); const o = k * (1 - seg(t, tEnd - .25, tEnd));
    const sh = t - tp < .25 ? Math.sin((t - tp) * 80) * 4 * (1 - (t - tp) / .25) : 0;
    h += `<div class="plate ${ty}" style="transform:translateX(${sh.toFixed(1)}px) scale(${sc.toFixed(3)}) rotate(${ty === 'p' ? -2 : 2}deg);opacity:${o.toFixed(2)}"><span>${ty === 'p' ? 'ПРОБЛЕМА:' : 'РЕШЕНИЕ:'}</span>${tx}</div>`;
  });
  elPl.innerHTML = on > 0 ? h : '';
  let rf = 0; DROPS.forEach(td => { const q = t - td; if (q > 0 && q < .7) rf = Math.max(rf, (1 - q / .7) * (Math.sin(q * 30) * .3 + .7)); });
  document.getElementById('redflash').style.opacity = rf.toFixed(2);
}

const elTitle = document.getElementById('title');
function renderOverlays(t) {
  const a = S(3) - .1, b = P(4, 0) - .15;
  elTitle.style.opacity = (seg(t, a, a + .5) * (1 - seg(t, b - .4, b))).toFixed(2);
  elTitle.style.transform = `scale(${lerp(1.08, 1, eout(seg(t, a, a + 1.5))).toFixed(3)})`;
  let black = 0;
  if (t < .35) black = 1 - t / .35;
  black = Math.max(black, seg(t, E(2) + .2, E(2) + .5) * (1 - seg(t, S(3) - .1, S(3) + .3)));
  if (t > DUR - .6) black = Math.max(black, seg(t, DUR - .6, DUR));
  document.getElementById('flash').style.opacity = black.toFixed(2);
}

// ---------- звуки ----------
(function () {
  sfx(Wt(0, 'ЗАБРАТЬ'), 'stamp', 1.1);
  sfx(S(1) + .2, 'scrape', .6); sfx(S(1) + .5, 'sand', .5, { d: 1.2 });
  sfx(P(2, 1), 'tone', .9, { d: 3 });
  sfx(S(3) - .1, 'boom', 1);
  for (let i = 0; i < 8; i++) sfx(P(4, 1) + i * .5, 'step', .4);
  sfx(P(4, 3), 'chime', .4);
  sfx(Wt(5, 'СНЯЛСЯ'), 'clack', .6); sfx(Wt(5, 'СНЯЛСЯ') + .3, 'scrape', .5);
  sfx(S(6) + .2, 'keys', .8);
  for (let i = 0; i < 8; i++) sfx(P(6, 1) - .4 + i * .32, 'step', .5 + i * .05, { pan: -.8 + i * .1 });
  sfx(P(6, 2), 'keys', .6);
  sfx(S(7), 'static', .3, { d: .6 });
  sfx(S(8), 'breath', .35, { d: 4 });
  for (let i = 0; i < 18; i++) sfx(P(8, 2) + Math.pow(i / 18, .6) * (E(8) - P(8, 2)), 'tick', .4);
  sfx(P(9, 1) + .7, 'stamp', 1.1); sfx(P(9, 1), 'pencil', .5, { d: 1.2 });
  sfx(Wt(10, 'СИНИЙ') - .2, 'pop', .5); sfx(Wt(10, 'ДОЖДЕВИК') - .3, 'pop', .5);
  sfx(S(11), 'pencil', .6, { d: 3.5 });
  sfx(Wt(11, 'ДОЖДЕВИКОМ'), 'sand', .5, { d: .9 });
  for (let i = 0; i < 3; i++) sfx(Wt(11, 'СТЯЖКАМИ') + i * .12, 'ratchet', .35);
  sfx(Wt(11, 'ГАЗЕТАМИ'), 'page', .5);
  sfx(P(11, 3) + .6, 'clack', .6);
  sfx(S(12) + .3, 'keys', .35, { pan: -.6 }); sfx(E(12), 'keys', .25, { pan: .7 });
  sfx(S(13), 'page', .6);
  [P(14, 0), P(14, 1), P(14, 2)].forEach(tt => sfx(tt, 'chime', .3));
  sfx(S(15), 'chime', .5);
  for (let i = 0; i < 20; i++) sfx(S(16) + i * (PE(16, 0) + .2 - S(16)) / 20, 'page', .3);
  sfx(P(17, 1), 'boom', 1.1);
  for (let i = 0; i < 14; i++) sfx(S(18) + .4 + i * .5, 'tick', .45);
  sfx(Wt(18, 'СЖЕЧЬ'), 'pop', .6); sfx(Wt(18, 'ДОПИСАТЬ'), 'pop', .6); sfx(P(18, 2), 'stamp', .9);
  DRONE.sort((a, b) => a[0] - b[0]).forEach(([t, v]) => sfx(t, 'drone_kf', v));
  sfx(DUR - 2.5, 'drone_kf', .4); sfx(DUR, 'drone_kf', 0);
})();

// обложка: бейдж крупно, оранжевый рюкзак на заднем плане
window.COVER = function () {
  let s = rect(-400, -400, 1880, 2800, '#0d1018') + `<ellipse cx="540" cy="1000" rx="700" ry="600" fill="url(#warmBlob)" opacity=".25"/>`;
  s += `<g transform="translate(780 1420) rotate(12)">${backpack(0, 0, 520)}</g>`;
  s += `<g transform="rotate(-6 520 1000)">${badge(500, 1000, 1.35)}</g>`;
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="url(#vig)"/>`;
  return s;
};
