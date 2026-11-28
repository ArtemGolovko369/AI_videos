// ================= ЧАСТЬ 6 · «Журнал приказывает» =================
const ICON_FIRE = `<g transform="translate(0 20)"><path d="M0 -110 Q70 -30 60 40 Q50 100 0 100 Q-50 100 -60 40 Q-70 -20 -20 -70 Q-10 -20 10 -10 Q20 -60 0 -110Z" fill="#ff7a1a" stroke="${ST}" stroke-width="6"/><path d="M0 -10 Q30 30 22 64 Q14 90 0 90 Q-14 90 -22 64 Q-28 34 0 -10Z" fill="#ffd23f"/></g>`;
const ICON_PEN = `<g transform="translate(0 20) rotate(-40)"><rect x="-22" y="-110" width="44" height="170" rx="8" fill="#3d7be0" stroke="${ST}" stroke-width="6"/><path d="M-22 60 L0 110 L22 60Z" fill="#f3efe3" stroke="${ST}" stroke-width="6"/><path d="M-6 96 L0 110 L6 96Z" fill="#0d1018"/></g>`;
const ICON_TORN = `<g transform="translate(0 20)"><path d="M-80 -100 L60 -100 L60 -20 L40 -6 L58 12 L36 30 L56 50 L40 70 L60 100 L-80 100Z" fill="#f3efe3" stroke="${ST}" stroke-width="6"/><path d="M-60 -60 h90 M-60 -30 h80 M-60 0 h70 M-60 30 h76" stroke="#9fb8d8" stroke-width="5"/><path d="M80 -40 L110 -16 L90 6 L112 30" fill="none" stroke="#e9edf5" stroke-width="5" stroke-dasharray="8 6"/></g>`;
function uniform(x, y, sc = 1, o = {}) { // форма охранника на вешалке (y — крючок)
  let s = `<g transform="translate(${x} ${y}) scale(${sc})" stroke="${ST}" stroke-width="6" stroke-linejoin="round">`;
  s += `<path d="M0 -30 q0 -30 22 -30 q22 0 22 22" fill="none" stroke="#9aa3b6" stroke-width="8"/><path d="M-150 40 L0 -10 L150 40" fill="none" stroke="#9aa3b6" stroke-width="10"/>`;
  s += `<path d="M-150 40 Q-170 60 -175 120 L-185 420 L-130 420 L-120 160 L-110 520 L110 520 L120 160 L130 420 L185 420 L175 120 Q170 60 150 40 L40 20 L0 70 L-40 20Z" fill="#1d2433"/>`;
  s += `<path d="M-40 20 L0 70 L40 20 L20 10 L0 40 L-20 10Z" fill="#cfd6e4"/><path d="M0 70 L0 520" fill="none" stroke-width="4" opacity=".6"/>`;
  for (let i = 0; i < 5; i++) s += `<circle cx="14" cy="${110 + i * 80}" r="9" fill="#c0c6d2" stroke-width="3"/>`;
  s += `<rect x="-160" y="70" width="44" height="26" rx="6" fill="#ffd23f" stroke-width="3"/><rect x="116" y="70" width="44" height="26" rx="6" fill="#ffd23f" stroke-width="3"/>`;
  s += `<rect x="-100" y="300" width="70" height="50" rx="4" fill="#232b3c" stroke-width="4"/>`;
  if (o.badge) s += `<g transform="translate(-70 170) rotate(-4) scale(.22)">${badge(0, 0, 1)}</g>`;
  return s + '</g>';
}
function journalPage(t, lines, o = {}) { // одна страница журнала крупно, lines: [[text, t0, t1, col]]
  let s = rect(-400, -400, 1880, 2800, '#1a1712') + `<ellipse cx="540" cy="1000" rx="620" ry="520" fill="url(#warmBlob)" opacity=".3"/>`;
  s += rect(110, 560, 860, 860, '#efe8d6', `rx="8" stroke="${ST}" stroke-width="6"`);
  for (let i = 0; i < 12; i++) s += `<line x1="140" y1="${660 + i * 62}" x2="940" y2="${660 + i * 62}" stroke="#c9bfa5" stroke-width="2"/>`;
  s += mono(150, 620, o.head || 'ЖУРНАЛ ОБХОДА', 24, '#7a6a4a');
  lines.forEach(([tx, t0, t1, col, y]) => s += inkLine(150, y, tx, 34, col || '#1d2f6b', t1 < 0 ? 1 : seg(t, t0, t1)));
  return s;
}
function penHand(x, y, op = 1) {
  return `<g transform="translate(${f(x)} ${f(y)})" opacity="${f(op)}"><g transform="rotate(-35)"><rect x="-10" y="-160" width="20" height="160" rx="6" fill="#3d7be0" stroke="${ST}" stroke-width="4"/><path d="M-10 0 L0 24 L10 0Z" fill="#f3efe3" stroke="${ST}" stroke-width="4"/></g><ellipse cx="60" cy="-60" rx="70" ry="50" fill="#e3c3a3" stroke="${ST}" stroke-width="5"/><rect x="100" y="-90" width="300" height="70" fill="#2c3e63" stroke="${ST}" stroke-width="5"/></g>`;
}
function writing(t, x0, y, text, t0, t1, size = 40) { // ручка движется за текстом
  const k = seg(t, t0, t1), n = Math.round(text.length * k);
  const w = n * size * .52;
  return inkLine(x0, y, text, size, '#1d2f6b', k) + (k > 0 && k < 1 ? penHand(x0 + w, y - 4) : '');
}

// 0. Итог голосования части 5
add(0, S(1) - .15, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0d12');
  const tb = Wt(0, 'ДОПИСАТЬ');
  const dk = seg(t, .3, tb - .1), win = eout(seg(t, tb - .2, tb + .3));
  s += choiceCard(t, lerp(285, 180, win), 900, '1', 'СЖЕЧЬ|ЖУРНАЛ', ICON_FIRE, -1, '#56627c', dk, 1 - .25 * win);
  s += choiceCard(t, lerp(795, 610, win), lerp(900, 860, win), '2', 'ДОПИСАТЬ|СТРАНИЦУ', ICON_PEN, -1, '#ffd23f', 0, 1 + .25 * win);
  const sk = seg(t, tb, tb + .14);
  if (sk > 0) s += `<g transform="translate(540 1290) rotate(-4) scale(${f(lerp(1.6, 1, eout(sk)))})" opacity="${f(sk)}">${rect(-400, -56, 800, 112, '#e0322f', `rx="14" stroke="${ST}" stroke-width="6"`)}${txt(0, 18, 'ВЫ ВЫБРАЛИ: ДОПИСАТЬ', 54, '#fff')}</g>`;
  return cam(s, 1, 540, 960, sk > 0 && sk < 1 ? Math.sin(t * 60) * .8 : 0);
}, .2);
HUDOFF.push([0, P(3, 0) - .1]);

// 1. Ручка над журналом: почерк ложится, будто писал всегда
add(S(1) - .15, S(2) - .25, t => {
  const old = [];
  for (let i = 0; i < 5; i++) old.push([`${10 + i}-й д. — манекенов — 13`, -1, -1, '#1d2f6b', 690 + i * 62]);
  let s = journalPage(t, old);
  const tw = P(1, 1);
  s += writing(t, 150, 1032, 'Пишу. День 30.', tw, tw + 2.2);
  const k = eio(seg(t, S(1), E(1)));
  return cam(s, lerp(1.0, 1.4, k), lerp(540, 420, k), lerp(980, 960, k));
}, .25);

// 2. Заставка
add(S(2) - .25, P(3, 0) - .05, t => {
  let s = mallFloors(.8) + exitSign(860, 640, .8) + dust(t, 60, 9, 0, 0, 1080, 1920, '#cfe0ff', .45, 2.6) + darkness(.45);
  return cam(s, lerp(1.12, 1.04, eout(seg(t, S(2), S(2) + 5))), 540, 960);
}, .4);

// 3. Ночь 30: чистые страницы → схема «запись → завтра → ?»
add(P(3, 0) - .05, S(5) - .2, t => {
  if (t < P(3, 1) - .1) {
    let s = journalSpread(t, '', '');
    const q = (seg(t, P(3, 0), P(3, 1)) * 6) % 1, w = 430 * Math.cos(q * Math.PI);
    s += `<path d="M540 620 L${f(540 + w)} ${f(620 - 30 * Math.sin(q * Math.PI))} L${f(540 + w)} ${f(1340 - 30 * Math.sin(q * Math.PI))} L540 1340Z" fill="#f3eddc" stroke="${ST}" stroke-width="3"/>`;
    return cam(s, 1.0, 540, 980);
  }
  let s = blueprint(t, 'СХЕМА №12 · ЖУРНАЛ');
  const a = popScale(t, P(3, 1)), b = popScale(t, Wt(3, 'ЗАВТРА') + .1), c = popScale(t, Wt(3, 'РЕШАЕТ'));
  if (a > 0) s += `<g transform="translate(220 940) scale(${f(a)})">${rect(-110, -70, 220, 140, 'none', 'rx="12" stroke="#fff" stroke-width="5"')}${mono(0, 12, 'ЗАПИСЬ', 32, '#fff', 'middle')}</g>`;
  if (b > 0) s += parrow(340, 940, 430, 940, seg(t, Wt(3, 'ЗАВТРА'), Wt(3, 'ЗАВТРА') + .3)) + `<g transform="translate(560 940) scale(${f(b)})">${rect(-110, -70, 220, 140, 'none', 'rx="12" stroke="#fff" stroke-width="5"')}${mono(0, 12, 'ЗАВТРА', 32, '#fff', 'middle')}</g>`;
  if (c > 0) s += parrow(680, 940, 770, 940, seg(t, Wt(3, 'РЕШАЕТ') - .1, Wt(3, 'РЕШАЕТ') + .2), '#ff4040') + `<g transform="translate(880 940) scale(${f(c)})"><circle r="80" fill="none" stroke="#ff4040" stroke-width="6"/>${txt(0, 30, '?', 90, '#ff4040')}</g>`;
  const mk = seg(t, S(4), S(4) + .6);
  if (mk > 0) s += `<g opacity="${f(mk)}">${rect(260, 1110, 560, 70, 'none', 'rx="10" stroke="#ffd23f" stroke-width="5" stroke-dasharray="14 10"')}${mono(540, 1158, 'ПРОВЕРКА НА МЕЛОЧИ', 32, '#ffd23f', 'middle')}</g>`;
  const pk = seg(t, P(4, 1), P(4, 1) + .8);
  for (let i = 0; i < 12; i++) { const k = seg(pk, i / 14, i / 14 + .2); if (k > 0) s += rect(130 + i * 70, 1250, 54, 72, '#f3efe3', `rx="4" stroke="${ST}" stroke-width="3" opacity="${f(k)}"`); }
  if (pk > 0) s += mono(540, 1380, typeText('12 ЧИСТЫХ СТРАНИЦ', pk), 28, '#fff', 'middle');
  return cam(s, 1.02, 540, 1080);
}, .3);

// 4. Пишу строку про автомат
add(S(5) - .2, S(6) - .25, t => {
  const old = [['Пишу. День 30.', -1, -1, '#1d2f6b', 690]];
  let s = journalPage(t, old);
  const tw = P(5, 1) - .1;
  s += writing(t, 150, 790, 'Торговый автомат на фудкорте —', tw, tw + 2.2, 36);
  s += writing(t, 150, 852, 'горит.', tw + 2.2, tw + 2.7, 36);
  return cam(s, 1.25, 500, 820);
}, .3);

// 5. День 31: автомат светится на экране фудкорта
add(S(6) - .25, S(7) - .2, t => {
  const tz = P(6, 1), tl = Wt(6, 'СВЕТИЛСЯ');
  let s = monitors(t, { on: i => i === 4 ? 1 : .55 });
  const [x, y] = monPos(4);
  const g = seg(t, tl - .2, tl + .3);
  s += `<ellipse cx="${x + 45}" cy="${y + 70}" rx="${f(70 + 40 * g)}" ry="${f(60 + 30 * g)}" fill="url(#warmBlob)" opacity="${f(.4 + .6 * g)}"/>`;
  if (g > 0) s += rect(x - 8, y - 8, MG.w + 16, MG.h + 16, 'none', `rx="10" stroke="#ffb347" stroke-width="7" opacity="${f(g)}"`);
  if (t > P(6, 3)) s += mono(x + MG.w / 2, y - 20, 'ПОГАС НА 7-Й ДЕНЬ', 18, '#ffb347', 'middle');
  const zk = eio(seg(t, tz - .2, tz + .8));
  return cam(s, lerp(1, 2.6, zk), lerp(540, x + MG.w / 2, zk), lerp(900, y + MG.h / 2, zk));
}, .3);

// 6. Правило № 4
add(S(7) - .2, S(8) - .25, t => {
  const t1 = P(7, 1);
  return cam(notebook(t, [
    ['1. СЧЁТ ДОЛЖЕН СХОДИТЬСЯ', -1, 0, 740, 36],
    ['2. ОН ХОДИТ ТАМ, ГДЕ ТЕМНО', -1, 0, 800, 36],
    ['3. СЧИТАЕТСЯ ВСЁ', -1, 0, 860, 36],
    ['4. ЖУРНАЛ ПРИКАЗЫВАЕТ', t1 - .1, t1 + .7, 960, 54, '#c0392b'],
  ], 'ПРАВИЛО № 4', t1 + .7), lerp(1.0, 1.05, seg(t, S(7), S(8))), 540, 990);
}, .3);

// 7. День 32: медленно, слово за словом
add(S(8) - .25, S(10) - .25, t => {
  const old = [['Пишу. День 30.', -1, -1, '#1d2f6b', 690], ['Торговый автомат на фудкорте — горит.', -1, -1, '#1d2f6b', 752]];
  let s = journalPage(t, old);
  const w1 = P(9, 0) - .1, w2 = P(9, 1) - .1;
  s += writing(t, 150, 852, 'Манекенов — двенадцать.', w1, PE(9, 0) + .1, 38);
  s += writing(t, 150, 914, 'Охранник — ушёл.', w2, PE(9, 1) + .1, 38);
  return cam(s, lerp(1.1, 1.3, seg(t, S(8), E(9))), 500, 840);
}, .3);

// 8. День 33: на экране 12, места 13-го нет
add(S(10) - .25, S(11) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#05070b');
  const id = 'gs' + gid++;
  let inner = rect(60, 600, 960, 680, '#2a2a2a');
  for (let i = 0; i < 12; i++) inner += mannequin(150 + i * 70, 1160, 300, { sw: 2.5 });
  s += `<filter id="${id}"><feColorMatrix type="saturate" values="0"/></filter><g filter="url(#${id})">${inner}</g>`;
  for (let k = 0; k < 680; k += 5) s += `<line x1="60" y1="${600 + k}" x2="1020" y2="${600 + k}" stroke="#000" stroke-width="2" opacity=".2"/>`;
  s += mono(80, 640, 'CAM 04 · ОДЕЖДА', 26, '#fff') + rect(40, 580, 1000, 720, 'none', `rx="14" stroke="#2a3142" stroke-width="22"`);
  const t12 = Wt(10, 'ДВЕНАДЦАТЬ');
  for (let i = 0; i < 12; i++) { const pk = popScale(t, lerp(P(10, 1), t12, i / 11), .15); if (pk > 0) s += `<g transform="translate(${150 + i * 70} 820) scale(${f(pk)})"><circle r="22" fill="#3ddc84" stroke="${ST}" stroke-width="3"/>${txt(0, 9, i + 1, 24, '#0d1018')}</g>`; }
  const nk = seg(t, P(10, 3), P(10, 3) + .4);
  if (nk > 0) s += `<g opacity="${f(nk)}">${rect(150 + 12 * 70 - 40, 900, 80, 280, 'none', 'rx="10" stroke="#ffd23f" stroke-width="5" stroke-dasharray="12 8"')}${txt(150 + 12 * 70, 880, '—', 40, '#ffd23f')}</g>`;
  return cam(s, lerp(1.0, 1.06, seg(t, S(10), S(11))), 540, 960);
}, .3);

// 9. Ночь: 02:00 → 03:00, тишина
add(S(11) - .2, S(12) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#0c140f');
  s += rect(330, 560, 420, 780, '#3a4a3e', `stroke="${ST}" stroke-width="7"`) + rect(-400, 1330, 1880, 900, '#0a110c');
  s += `<ellipse cx="540" cy="700" rx="600" ry="300" fill="url(#greenBlob)" opacity=".45"/>`;
  s += hero(540, 1470, 560, 'front');
  const steps = [[S(11), '02:00'], [P(11, 1), '02:30'], [P(11, 2), '03:00']];
  let clock = steps[0][1]; steps.forEach(([tt, v]) => { if (t >= tt) clock = v; });
  s += rect(400, 600, 280, 100, '#07090d', `rx="14" stroke="#3a4560" stroke-width="5"`) + mono(540, 672, clock, 66, '#ff5a4a', 'middle');
  s += `<rect x="330" y="1334" width="420" height="10" fill="#000"/>`;
  return cam(s, lerp(1.0, 1.1, seg(t, S(11), S(12))), 540, 1000);
}, .3);
DRONE.push([0, .3], [S(1), .55], [S(2), .5], [S(3), .55], [S(6), .5], [S(8), .45], [S(11), .6], [P(11, 1), .3], [P(11, 2) - .2, 0], [S(12) - .1, 0], [S(12) + .6, .55]);

// 10. День 34: форма на крючке, моего размера
add(S(12) - .25, S(13) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#11151d') + rect(-400, 1400, 1880, 900, '#0d1016');
  s += `<ellipse cx="540" cy="900" rx="700" ry="500" fill="#3d7be0" opacity=".14"/>` + rect(470, 520, 140, 30, '#5a6273', `rx="6" stroke="${ST}" stroke-width="4"`);
  const tr = Wt(12, 'МОЕГО');
  const k = eout(seg(t, tr - .4, tr + .2));
  if (k < 1) s += uniform(540, 560, 1.15);
  if (t > tr - .4) {
    s += `<g opacity="${f(k)}">${hero(540, 1560, 900, 'front')}</g>`;
    s += `<g opacity="${f(k)}">${uniform(540, lerp(560, 640, k), 1.12)}</g>`;
    s += txt(540, 480, '= МОЙ РАЗМЕР', 44, '#ff4040', `opacity="${f(seg(t, tr, tr + .3))}" stroke="${ST}" stroke-width="8" paint-order="stroke"`);
  }
  const nk = seg(t, P(12, 5) - .1, P(12, 5) + .3);
  if (nk > 0) s += mono(540, 1500, 'ВЧЕРА КРЮЧОК БЫЛ ПУСТ', 30, '#ffd23f', 'middle', `opacity="${f(nk)}"`);
  return cam(s, lerp(1.0, 1.06, seg(t, S(12), S(13))), 540, 1000);
}, .3);

// 11. Схема: форма в кольце присыпки
add(S(13) - .2, S(14) - .25, t => {
  let s = blueprint(t, 'СХЕМА №13 · КОЛЬЦО ПРИСЫПКИ');
  s += rect(120, 820, 840, 600, 'none', 'stroke="#fff" stroke-width="4"') + mono(140, 860, 'СКЛАД (ВИД СВЕРХУ)', 22, '#a9cbf5');
  const fk = popScale(t, S(13) + .2);
  if (fk > 0) s += `<g transform="translate(540 1120) scale(${f(fk * .7)})"><path d="M-150 -200 L150 -200 L190 200 L-190 200Z" fill="rgba(29,36,51,.6)" stroke="#fff" stroke-width="6"/><path d="M-40 -200 L0 -150 L40 -200" fill="none" stroke="#fff" stroke-width="5"/></g>`;
  const rk = seg(t, P(13, 1), P(13, 1) + 1.2);
  if (rk > 0) {
    const C = 2 * Math.PI * 230;
    s += `<circle cx="540" cy="1120" r="230" fill="none" stroke="#e9e7e1" stroke-width="34" opacity=".55" stroke-dasharray="${f(C * rk)} ${f(C)}" transform="rotate(-90 540 1120)"/>`;
    s += mono(540, 860 + 20, typeText('КОЛЬЦО ПРИСЫПКИ', rk), 28, '#ffd23f', 'middle');
  }
  const tk = seg(t, P(13, 2), P(13, 2) + .6);
  if (tk > 0) s += mono(540, 1470, typeText('ТРОНУТ = СЛЕД', tk), 36, '#3ddc84', 'middle');
  return cam(s, 1.02, 540, 1100);
}, .3);

// 12. День 36: кольцо цело → форма снова на крючке
add(S(14) - .25, S(15) - .15, t => {
  const tb = P(14, 3) - .1;
  if (t < tb) {
    let s = rect(-400, -400, 1880, 2800, '#14110c') + `<ellipse cx="540" cy="1100" rx="600" ry="400" fill="url(#warmBlob)" opacity=".2"/>`;
    s += `<ellipse cx="540" cy="1120" rx="330" ry="150" fill="none" stroke="#e9e7e1" stroke-width="40" opacity=".8"/>`;
    for (let i = 0; i < 60; i++) { const a = i / 60 * 6.283; s += `<circle cx="${f(540 + Math.cos(a) * (330 + Math.sin(i * 7) * 18))}" cy="${f(1120 + Math.sin(a) * (150 + Math.cos(i * 5) * 8))}" r="${f(4 + (i % 4))}" fill="#fff" opacity=".6"/>`; }
    const ek = seg(t, P(14, 1), P(14, 1) + .3);
    if (ek > 0) s += txt(540, 1140, 'ПУСТО', 54, '#ffd23f', `opacity="${f(ek)}"`);
    const nk = seg(t, P(14, 2), P(14, 2) + .3);
    if (nk > 0) s += txt(540, 860, '0 СЛЕДОВ', 48, '#3ddc84', `opacity="${f(nk)}" stroke="${ST}" stroke-width="8" paint-order="stroke"`);
    return cam(s, lerp(1.0, 1.1, seg(t, S(14), tb)), 540, 1060);
  }
  let s = rect(-400, -400, 1880, 2800, '#11151d') + rect(-400, 1400, 1880, 900, '#0d1016') + `<ellipse cx="540" cy="900" rx="700" ry="500" fill="#3d7be0" opacity=".14"/>`;
  s += rect(470, 520, 140, 30, '#5a6273', `rx="6" stroke="${ST}" stroke-width="4"`) + uniform(540, 560, 1.15, { badge: false });
  return cam(s, lerp(1.15, 1.0, eout(seg(t, tb, tb + .6))), 540, 1000, t < tb + .1 ? Math.sin(t * 60) * .6 : 0);
}, .1);

// 13. На груди — мой бейдж; пустой карман
add(S(15) - .15, S(16) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#11151d') + `<ellipse cx="540" cy="900" rx="700" ry="500" fill="#3d7be0" opacity=".14"/>`;
  const bk = popScale(t, Wt(15, 'БЕЙДЖ') - .2);
  s += rect(470, 520, 140, 30, '#5a6273', `rx="6" stroke="${ST}" stroke-width="4"`) + uniform(540, 560, 1.15, { badge: bk > 0 });
  const zk = eio(seg(t, S(15), PE(15, 0) + .2)), zk2 = eio(seg(t, P(15, 1), P(15, 1) + .6));
  if (zk2 > 0) {
    s += `<g opacity="${f(zk2)}">${rect(-400, -400, 1880, 2800, '#11151d')}${rect(240, 700, 600, 700, '#2c3e63', `rx="30" stroke="${ST}" stroke-width="7"`)}${rect(380, 900, 320, 260, '#223154', `rx="16" stroke="${ST}" stroke-width="6"`)}
      <g transform="translate(${f(540 + Math.sin(t * 10) * 20)} ${f(1000 + Math.abs(Math.sin(t * 10)) * 20)})"><ellipse rx="100" ry="70" fill="#e3c3a3" stroke="${ST}" stroke-width="6"/></g>
      ${txt(540, 1290, 'ПУСТО', 54, '#ff4040', `stroke="${ST}" stroke-width="8" paint-order="stroke"`)}</g>`;
  }
  const cx = lerp(540, 540 - 80, zk) , cy = lerp(1000, 560 + 1.15 * 170, zk);
  return cam(s, lerp(1, 2.4, zk) * (1 - zk2) + zk2, lerp(cx, 540, zk2), lerp(cy, 1000, zk2));
}, .25);

// 14. Журнал: третья строка проступает сама
add(S(16) - .2, S(18) - .2, t => {
  const old = [['Пишу. День 30.', -1, -1, '#1d2f6b', 690], ['Торговый автомат на фудкорте — горит.', -1, -1, '#1d2f6b', 752], ['Манекенов — двенадцать.', -1, -1, '#1d2f6b', 852], ['Охранник — ушёл.', -1, -1, '#1d2f6b', 914]];
  let s = journalPage(t, old);
  const tn = P(16, 1), tv = S(17);
  const k = seg(t, tn, tv + 1.2);
  const glow = seg(t, tv - .1, tv + .4);
  if (glow > 0) s += rect(140, 966, 700, 64, '#ff4040', `opacity="${f(.18 * glow)}" rx="8"`);
  s += inkLine(150, 1014, 'Охранник вернулся.', 44, glow > 0 ? '#c0392b' : '#1d2f6b', k);
  if (t > P(16, 3) - .1) s += `<path d="M120 690 L120 930" stroke="#3ddc84" stroke-width="6"/>` + mono(110, 820, 'Я', 28, '#3ddc84', 'end') + `<path d="M120 970 L120 1030" stroke="#ff4040" stroke-width="6"/>` + mono(110, 1010, '?', 34, '#ff4040', 'end');
  return cam(s, lerp(1.15, 1.45, seg(t, S(16), tv + 1)), 520, lerp(860, 960, seg(t, S(16), tv)));
}, .25);
DRONE.push([S(12), .55], [S(14), .6], [P(14, 3), .8], [S(16), .5], [P(16, 1), .2], [S(17), .9], [E(17) + .3, 0], [S(18) + .5, .45]);

// 15. Экран выбора
add(S(18) - .2, DUR + 1, t => {
  let s = rect(-400, -400, 1880, 2800, '#11151d') + uniform(300, 600, .9, { badge: true });
  s = `<g opacity=".3">${s}</g>` + rect(-10, -10, 1100, 1940, '#000', 'opacity=".3"');
  const ICON_UNI = `<g transform="translate(0 -60) scale(.42)">${uniform(0, 0, 1)}</g>`;
  s += choiceCard(t, 285, 900, '1', 'НАДЕТЬ|ФОРМУ', ICON_UNI, Wt(18, 'НАДЕТЬ'), '#ffd23f');
  s += choiceCard(t, 795, 900, '2', 'ВЫРВАТЬ|СТРАНИЦУ', ICON_TORN, Wt(18, 'ВЫРВАТЬ'), '#ffd23f');
  const ok = seg(t, Wt(18, 'ВЫРВАТЬ'), Wt(18, 'ВЫРВАТЬ') + .3);
  if (ok > 0) s += `<g opacity="${f(ok)}"><circle cx="540" cy="900" r="52" fill="#0d1018" stroke="#9aa6bd" stroke-width="5"/>${txt(540, 914, 'ИЛИ', 34, '#e9edf5')}</g>`;
  const pk = popScale(t, P(18, 2));
  const pul = 1 + .03 * Math.sin(t * 6);
  if (pk > 0) s += `<g transform="translate(540 1250) scale(${(pk * pul).toFixed(3)})">${rect(-440, -48, 880, 96, '#e0322f', `rx="16" stroke="${ST}" stroke-width="5"`)}${txt(0, 16, 'ПИШИ 1 ИЛИ 2 — РЕШАЕТ БОЛЬШИНСТВО', 40, '#fff')}</g>`;
  if (pk > 0) s += mono(540, 1660, 'ЧАСТЬ 7 — ДЕНЬ 37', 34, '#9aa6bd', 'middle', `opacity="${f(seg(t, P(18, 2) + .4, P(18, 2) + .9))}"`);
  return s;
}, .3);

// ---------- HUD ----------
const DAYS = [[P(3, 0), 30], [S(6), 31], [S(8), 32], [S(10), 33], [S(12), 34], [S(14), 36]];
DAYS.slice(1).forEach(([t]) => sfx(t, 'page', .9));
function dayAt(t) { let d = null, t0 = 0; for (const [tt, n] of DAYS) if (t >= tt) { d = n; t0 = tt; } return [d, t0]; }
function keyf(t, kf) {
  if (t <= kf[0][0]) return kf[0][1];
  for (let i = 1; i < kf.length; i++) if (t < kf[i][0]) return lerp(kf[i - 1][1], kf[i][1], eio(seg(t, kf[i - 1][0], kf[i][0])));
  return kf[kf.length - 1][1];
}
const FOOD = [[0, 36], [S(6), 34], [Wt(6, 'СВЕТИЛСЯ'), 34], [Wt(6, 'СВЕТИЛСЯ') + 1.5, 70], [S(12), 64], [S(14), 58]];
const SLEEP = [[0, 55], [S(11), 55], [E(11), 85], [S(14), 70], [P(16, 1), 70], [P(16, 1) + .6, 25]];
const WATER = [[0, 34], [S(6), 32], [Wt(6, 'СВЕТИЛСЯ') + .3, 32], [Wt(6, 'СВЕТИЛСЯ') + 1.5, 70], [S(14), 62]];
const PAGES = [[0, 12], [P(5, 1) + 2.2, 11], [PE(9, 1), 10], [P(16, 1) + .3, 9]];
function pagesAt(t) { let v = 12, tt = -9; PAGES.forEach(([a, b]) => { if (t >= a) { v = b; tt = a; } }); return [v, tt]; }
const t12 = Wt(10, 'ДВЕНАДЦАТЬ');
const DROPS = [P(16, 1) + .3];
const PLATES = [
  [P(3, 1), 'p', 'ЧТО ПИСАТЬ?', S(6) - .3],
  [S(4), 's', 'ПРОВЕРИТЬ НА МЕЛОЧИ', S(6) - .3],
  [P(12, 1), 'p', 'ФОРМА ИЗ НИОТКУДА', S(14) - .3],
  [P(13, 1), 's', 'КОЛЬЦО ПРИСЫПКИ', S(14) - .3],
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
  elZ.textContent = 'ЗОНА: ВНЕ МАРШРУТА'; elZ.style.background = '#22b45e'; elZ.style.transform = 'none';
  const vals = [keyf(t, FOOD), 100, keyf(t, SLEEP), keyf(t, WATER)];
  vals.forEach((v, i) => {
    elB[i].style.width = v.toFixed(1) + '%';
    let col = v < 20 ? '#ff4040' : v < 45 ? '#ffd23f' : (i === 3 ? '#6cc0ff' : '#e9edf5');
    if (i === 1) col = '#3ddc84';
    elB[i].style.background = col;
    elV[i].textContent = i === 1 ? 'ОТ СЕТИ' : Math.round(v) + '%';
    if (i === 1) elV[i].style.color = '#3ddc84';
  });
  const n = t >= t12 ? 12 : 13;
  const [pg, tp] = pagesAt(t);
  const dk = t - tp < 1.2 && tp > 0 ? 1 - (t - tp) / 1.2 : 0;
  const auto = tp === PAGES[3][0];
  elMC.innerHTML = `МАНЕКЕНЫ: <b style="color:${n === 12 ? '#3ddc84' : '#fff'}">${n}</b> · 📖 СТРАНИЦЫ: <b style="color:${auto && dk > 0 ? '#ff4040' : '#fff'}">${pg}</b>` + (dk > 0 ? ` <b style="color:#ff4040;opacity:${f(dk)}">−1</b>` : '');
  let h = '';
  PLATES.forEach(([tp2, ty, tx, tEnd]) => {
    if (t < tp2 || t > tEnd) return;
    const k = seg(t, tp2, tp2 + .14); const sc = lerp(1.6, 1, eout(k)); const o = k * (1 - seg(t, tEnd - .25, tEnd));
    const sh = t - tp2 < .25 ? Math.sin((t - tp2) * 80) * 4 * (1 - (t - tp2) / .25) : 0;
    h += `<div class="plate ${ty}" style="transform:translateX(${sh.toFixed(1)}px) scale(${sc.toFixed(3)}) rotate(${ty === 'p' ? -2 : 2}deg);opacity:${o.toFixed(2)}"><span>${ty === 'p' ? 'ПРОБЛЕМА:' : 'РЕШЕНИЕ:'}</span>${tx}</div>`;
  });
  elPl.innerHTML = on > 0 ? h : '';
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
  if (t > DUR - .6) black = Math.max(black, seg(t, DUR - .6, DUR));
  document.getElementById('flash').style.opacity = black.toFixed(2);
}

// ---------- звуки ----------
(function () {
  sfx(Wt(0, 'ДОПИСАТЬ'), 'stamp', 1.1);
  sfx(P(1, 1), 'pencil', .55, { d: 2.2 });
  sfx(S(2) - .1, 'boom', 1);
  for (let i = 0; i < 6; i++) sfx(P(3, 0) + i * .25, 'page', .35);
  sfx(P(3, 1), 'pencil', .55, { d: 3 });
  sfx(P(5, 1) - .1, 'pencil', .5, { d: 2.7 });
  sfx(P(6, 1), 'static', .3, { d: .4 }); sfx(Wt(6, 'СВЕТИЛСЯ') - .2, 'hum', .6, { d: 2.5 });
  sfx(P(7, 1) + .7, 'stamp', 1.1);
  sfx(P(9, 0) - .1, 'pencil', .5, { d: PE(9, 0) - P(9, 0) + .2 }); sfx(P(9, 1) - .1, 'pencil', .5, { d: PE(9, 1) - P(9, 1) + .2 });
  for (let i = 0; i < 12; i++) sfx(lerp(P(10, 1), Wt(10, 'ДВЕНАДЦАТЬ'), i / 11), 'tick', .45);
  for (let i = 0; i < 8; i++) sfx(S(11) + i * .6, 'tick', .4 - i * .04);
  sfx(Wt(12, 'ФОРМА'), 'sand', .4, { d: .8 }); sfx(Wt(12, 'МОЕГО') - .3, 'whoosh', .5);
  sfx(S(13), 'pencil', .55, { d: 3 }); sfx(P(13, 1), 'sand', .7, { d: 1.6 });
  sfx(P(14, 3) - .1, 'boom', .8);
  sfx(Wt(15, 'БЕЙДЖ') - .2, 'pop', .5); for (let i = 0; i < 3; i++) sfx(P(15, 1) + .1 + i * .3, 'knock', .35);
  sfx(P(16, 1), 'pencil', .55, { d: 3.5 });
  sfx(S(17), 'tone', .9, { d: 3 }); sfx(E(17) - .2, 'keys', .35, { pan: .7 });
  for (let i = 0; i < 14; i++) sfx(S(18) + .4 + i * .5, 'tick', .45);
  sfx(Wt(18, 'НАДЕТЬ'), 'pop', .6); sfx(Wt(18, 'ВЫРВАТЬ'), 'pop', .6); sfx(P(18, 2), 'stamp', .9);
  DRONE.sort((a, b) => a[0] - b[0]).forEach(([t, v]) => sfx(t, 'drone_kf', v));
  sfx(DUR - 2.5, 'drone_kf', .4); sfx(DUR, 'drone_kf', 0);
})();

// обложка: журнал, последняя строка красным, форма на заднем плане
window.COVER = function () {
  let s = rect(-400, -400, 1880, 2800, '#11151d') + `<g opacity=".55">${uniform(820, 420, .9, { badge: true })}</g>`;
  s += `<g transform="rotate(-5 540 1150)">` + rect(130, 760, 820, 760, '#efe8d6', `rx="8" stroke="${ST}" stroke-width="6"`);
  for (let i = 0; i < 10; i++) s += `<line x1="160" y1="${860 + i * 62}" x2="920" y2="${860 + i * 62}" stroke="#c9bfa5" stroke-width="2"/>`;
  s += inkLine(170, 900, 'Манекенов — двенадцать.', 40) + inkLine(170, 962, 'Охранник — ушёл.', 40);
  s += rect(160, 1000, 640, 70, '#ff4040', 'opacity=".2" rx="8"') + inkLine(170, 1050, 'Охранник вернулся.', 50, '#c0392b') + '</g>';
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="url(#vig)"/>`;
  return s;
};
