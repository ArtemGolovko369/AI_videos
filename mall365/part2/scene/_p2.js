// ================= ЧАСТЬ 2 · сцены =================
// босой след: x,y центр, sc масштаб (длина ~110*sc), rot градусы, left — левая нога
function bareFoot(x, y, sc, rot = 0, left = false, col = '#4a3a2c', op = 1) {
  const m = left ? -1 : 1;
  return `<g transform="translate(${f(x)} ${f(y)}) rotate(${f(rot)}) scale(${f(sc * m)} ${f(sc)})" fill="${col}" opacity="${op.toFixed(2)}">
    <path d="M-14 40 Q-20 10 -16 -14 Q-12 -38 6 -40 Q22 -38 22 -16 Q22 8 14 40 Q2 54 -14 40Z"/>
    <ellipse cx="-14" cy="-52" rx="8" ry="9"/><ellipse cx="0" cy="-58" rx="6.5" ry="7.5"/><ellipse cx="11" cy="-56" rx="5.5" ry="6.5"/>
    <ellipse cx="20" cy="-50" rx="5" ry="5.5"/><ellipse cx="27" cy="-42" rx="4.5" ry="5"/></g>`;
}
function powderField(x, y, w, h, seed, op = .9) {
  const r = rng(seed); let s = `<g opacity="${op}">`;
  s += `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#e9e7e1" rx="30"/>`;
  for (let i = 0; i < 260; i++) s += `<circle cx="${f(x + r() * w)}" cy="${f(y + r() * h)}" r="${f(1 + r() * 4)}" fill="${r() > .5 ? '#ffffff' : '#c9c5bc'}" opacity=".7"/>`;
  for (let i = 0; i < 40; i++) { const ex = r() < .5 ? x + r() * w : (r() < .5 ? x : x + w), ey = r() < .5 ? (r() < .5 ? y : y + h) : y + r() * h; s += `<circle cx="${f(ex)}" cy="${f(ey)}" r="${f(10 + r() * 30)}" fill="#e9e7e1" opacity=".8"/>`; }
  return s + '</g>';
}
function row(t, n, gap, x0, y, h, opts = {}) {
  let s = '';
  for (let i = 0; i < n; i++) {
    if (opts.skip === i) { s += `<ellipse cx="${x0 + i * gap}" cy="${y}" rx="${h * .1}" ry="${h * .018}" fill="#3a3f4b" stroke="${ST}" stroke-width="4"/>`; continue; }
    if (opts.step === i) { s += mannequin(x0 + i * gap, y + h * .12, h * 1.14, { dim: opts.dim }); continue; }
    s += mannequin(x0 + i * gap, y, h, { dim: opts.dim, mask: opts.mask === i, bag: opts.mask === i });
  }
  return s;
}
const HUDOFF = []; // интервалы, где HUD скрыт
const DRONE = [];  // ключевые точки громкости дрона
const SC = {};     // точки сцен

// 0. Хук: присыпка, цепочка босых следов уходит в темноту
add(0, S(1) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0d13');
  s += powderField(60, 300, 960, 1500, 3, .72);
  // база манекенов вверху
  for (let i = 0; i < 6; i++) s += `<ellipse cx="${110 + i * 170}" cy="330" rx="70" ry="14" fill="#3a3f4b" stroke="${ST}" stroke-width="4"/><rect x="${106 + i * 170}" y="200" width="8" height="130" fill="#8b909c"/>`;
  const tb = Wt(0, 'СЛЕДЫ');
  for (let i = 0; i < 9; i++) {
    const k = seg(t, .1 + i * .12, .4 + i * .12); if (k <= 0) continue;
    const y = 1680 - i * 150, x = 540 + (i % 2 ? 60 : -60) + Math.sin(i * .7) * 40;
    const hot = seg(t, tb + .9, tb + 1.2);
    s += bareFoot(x, y, 1.35, (i % 2 ? 8 : -8), i % 2 === 0, hot > 0 ? '#5a2a22' : '#4a3a2c', .85 * k);
  }
  s += `<rect x="-400" y="-400" width="1880" height="900" fill="url(#wallG)" opacity=".0"/>`;
  s += dust(t, 20, 31, 0, 200, 1080, 1600, '#fff', .25, 2.5);
  const k = eio(seg(t, 0, S(1)));
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="url(#vig)" opacity=".9"/>`;
  return cam(s, lerp(1.15, 1.0, k), 540, lerp(1250, 860, k));
}, .25);
DRONE.push([0, .2], [1.2, .7], [S(1) - .1, .8], [S(1), .45]);

// 1. Название
add(S(1) - .25, P(2, 0) - .05, t => {
  const T = t - S(1);
  let s = mallFloors(.8) + exitSign(860, 640, .8) + dust(t, 60, 9, 0, 0, 1080, 1920, '#cfe0ff', .45, 2.6);
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#000" opacity=".45"/>`;
  return cam(s, lerp(1.12, 1.04, eout(seg(T, 0, 5))), 540, 960);
}, .4);

// 2. День 6: ряд из 13, лупа по ногам, «прятаться лучше меня»
add(P(2, 0) - .05, S(5) - .1, t => {
  let s = room(1300) + rackRail(560, -400, 2400);
  const gap = 150, x0 = 140, N = 13;
  s += row(t, N, gap, x0, 1290, 600);
  const t0 = S(2), t3 = S(3), t4 = S(4), t5 = S(5);
  // камера: вдоль ряда (l02-l03), затем наезд на головы (l04)
  let cx, cy = 980, sc = 1;
  const kPan = eio(seg(t, t0, E(3)));
  cx = lerp(x0 + 200, x0 + (N - 1) * gap - 200, kPan);
  const kPush = eio(seg(t, t4 - .2, t5));
  sc = lerp(1, 1.55, kPush); cy = lerp(980, 760, kPush);
  // лупа: по ногам во время l03
  const lk = seg(t, t3, E(3));
  if (lk > 0 && lk < 1) {
    const lx = cx + Math.sin(t * 2.3) * 60, ly = 1180;
    const id = 'lens' + gid++;
    const zoomed = `<g transform="translate(${f(lx)} ${f(ly)}) scale(2.2) translate(${f(-lx)} ${f(-ly)})">${room(1300)}${row(t, N, gap, x0, 1290, 600)}</g>`;
    s += `<clipPath id="${id}"><circle cx="${f(lx)}" cy="${f(ly)}" r="150"/></clipPath><g clip-path="url(#${id})">${zoomed}</g>`;
    s += `<circle cx="${f(lx)}" cy="${f(ly)}" r="150" fill="none" stroke="#e9edf5" stroke-width="12"/><path d="M${f(lx + 106)} ${f(ly + 106)} l90 90" stroke="#e9edf5" stroke-width="26" stroke-linecap="round"/>`;
    // галочки «чисто»
    s += txt(lx, ly - 175, '✓ ЧИСТО', 40, '#3ddc84', `stroke="${ST}" stroke-width="8" paint-order="stroke"`);
  }
  if (kPush > 0) s += `<rect x="-400" y="-400" width="2800" height="2800" fill="#000" opacity="${f(.35 * kPush)}"/>`;
  return cam(s, sc, cx, cy);
});

// 3. Аптека: банка присыпки
add(S(5) - .1, P(5, 1) - .05, t => {
  const T = t - S(5);
  let s = room(1320);
  for (let j = 0; j < 4; j++) {
    const y = 700 + j * 170; s += rect(60, y + 120, 960, 16, '#3a4560');
    for (let i = 0; i < 8; i++) { if (j === 2 && (i === 3 || i === 4)) continue; s += rect(80 + i * 118, y + 40 + (i % 3) * 8, 96, 80 - (i % 3) * 8, ['#d8dde6', '#a9c7e8', '#e8c3c3', '#cfe8cf'][(i + j) % 4], `rx="8" stroke="${ST}" stroke-width="3"`); }
  }
  // банка
  const g = .6 + .4 * Math.sin(t * 3);
  s += `<ellipse cx="540" cy="1000" rx="230" ry="200" fill="url(#warmBlob)" opacity="${f(.5 * g)}"/>`;
  s += rect(455, 930, 170, 160, '#f4f2ec', `rx="20" stroke="${ST}" stroke-width="5"`) + rect(470, 900, 140, 40, '#6fa8dc', `rx="10" stroke="${ST}" stroke-width="5"`);
  s += rect(468, 975, 144, 70, '#ffd6e0', `stroke="${ST}" stroke-width="3"`) + txt(540, 1004, 'ДЕТСКАЯ', 22, '#0d1018') + txt(540, 1032, 'ПРИСЫПКА', 22, '#0d1018');
  const k = eout(seg(T, 0, 2.5));
  return cam(s, lerp(1.0, 1.4, k), 540, lerp(900, 1000, k));
});

// 4. Схема: ловушка из присыпки (вид сверху)
add(P(5, 1) - .05, S(7) - .25, t => {
  let s = blueprint(t, 'СХЕМА №4 · ЛОВУШКА (ВИД СВЕРХУ)');
  const t0 = P(5, 1), t6 = S(6);
  const fk = seg(t, t0 + .1, E(5));
  const bx = 120, by = 820, bw = 840, bh = 300;
  // присыпка заливается слева направо
  if (fk > 0) s += `<rect x="${bx}" y="${by}" width="${f(bw * fk)}" height="${bh}" fill="#e9e7e1" opacity=".28"/>`;
  s += `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" fill="none" stroke="#fff" stroke-width="4" stroke-dasharray="18 12" opacity="${f(seg(t, t0, t0 + .4))}"/>`;
  s += mono(bx, by - 20, typeText('СЛОЙ ПРИСЫПКИ', seg(t, t0 + .3, t0 + 1.1)), 28, '#ffd23f');
  // 13 манекенов сверху: плечи + голова
  for (let i = 0; i < 13; i++) {
    const x = bx + 40 + i * 63, y = by + bh / 2;
    s += `<ellipse cx="${x}" cy="${y}" rx="26" ry="14" fill="none" stroke="#fff" stroke-width="3"/><circle cx="${x}" cy="${y}" r="10" fill="#fff"/>`;
  }
  // «если сдвинется — увижу»
  const mk = seg(t, t6, t6 + .8);
  if (mk > 0) {
    const x = bx + 40 + 6 * 63;
    s += parrow(x, by + bh / 2 + 20, x + 40, by + bh + 120, mk, '#ff9a4a');
    for (let j = 0; j < 3; j++) { const kk = seg(t, t6 + .5 + j * .25, t6 + .7 + j * .25); if (kk > 0) s += bareFoot(x + 60 + j * 34, by + bh + 150 + j * 60, .55, 165, j % 2 === 0, '#ff9a4a', kk); }
    s += mono(540, by + bh + 380, typeText('СДВИНЕТСЯ = СЛЕД', seg(t, Wt(6, 'УВИЖУ') - .3, Wt(6, 'УВИЖУ') + .4)), 34, '#3ddc84', 'middle');
  }
  return cam(s, lerp(1.0, 1.04, seg(t, t0, S(7))), 540, 1000);
}, .3);

// 5. День 7: автомат гаснет, вода на неделю
add(S(7) - .25, S(8) - .1, t => {
  const toff = Wt(7, 'ПОГАСЛИ');
  const on = t < toff ? 1 : (t < toff + .25 ? (Math.sin((t - toff) * 60) > 0 ? .6 : 0) : 0);
  let s = room(1320);
  s += `<ellipse cx="540" cy="900" rx="520" ry="420" fill="url(#warmBlob)" opacity="${f(.7 * on)}"/>`;
  s += rect(330, 560, 420, 760, '#2a3142', `rx="16" stroke="${ST}" stroke-width="6"`);
  s += rect(360, 600, 270, 520, on > .3 ? '#ffcf8a' : '#141925', `stroke="${ST}" stroke-width="5"`);
  for (let j = 0; j < 5; j++) for (let i = 0; i < 4; i++) s += rect(375 + i * 64, 615 + j * 100, 46, 70, ['#e0322f', '#3d7be0', '#3ddc84', '#ffd23f'][(i + j) % 4], `rx="8" stroke="${ST}" stroke-width="3" opacity="${f(on > .3 ? 1 : .35)}"`);
  s += rect(650, 640, 70, 120, '#141925', `stroke="${ST}" stroke-width="4"`) + rect(390, 1160, 220, 80, '#07090d', `stroke="${ST}" stroke-width="4"`);
  s += txt(540, 540, 'ФУДКОРТ', 36, '#7e889c', 'letter-spacing="6"');
  // холоднее после
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#0a1a33" opacity="${f(.35 * (1 - on) * seg(t, toff, toff + .8))}"/>`;
  // бутылки «на неделю»
  const tw = Wt(7, 'НЕДЕЛЮ') - .3;
  for (let i = 0; i < 7; i++) {
    const k = popScale(t, tw + i * .08); if (k <= 0) continue;
    s += `<g transform="translate(${170 + i * 124} 1180) scale(${k.toFixed(3)})">${rect(-28, -60, 56, 110, 'rgba(160,210,255,.55)', `rx="14" stroke="${ST}" stroke-width="4"`)}${rect(-12, -82, 24, 24, '#3d7be0', `rx="4" stroke="${ST}" stroke-width="3"`)}${txt(0, 28, ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС'][i], 20, '#0d1018')}</g>`;
  }
  return cam(s, lerp(1.0, 1.07, seg(t, S(7), S(8))), 540, 960);
});

// 6. Мутная вода в раковине
add(S(8) - .1, S(9) - .1, t => {
  let s = room(1250) + rect(-400, 500, 1880, 760, '#1d2a36');
  for (let i = 0; i < 12; i++) for (let j = 0; j < 6; j++) s += rect(-60 + i * 110, 520 + j * 110, 106, 106, 'none', 'stroke="#2c3a4a" stroke-width="3"');
  s += `<path d="M220 1000 L860 1000 Q860 1240 540 1250 Q220 1240 220 1000Z" fill="#dfe6ee" stroke="${ST}" stroke-width="6"/>`;
  s += `<ellipse cx="540" cy="1040" rx="270" ry="50" fill="#6b5a3a"/><ellipse cx="540" cy="1040" rx="270" ry="50" fill="none" stroke="${ST}" stroke-width="4"/>`;
  for (let i = 0; i < 5; i++) s += `<circle cx="${f(430 + i * 50 + Math.sin(t * 2 + i) * 10)}" cy="${f(1035 + Math.cos(t * 3 + i) * 10)}" r="${6 + i % 3 * 3}" fill="#4d3f27" opacity=".7"/>`;
  s += `<path d="M640 1000 L640 860 Q640 820 600 820 L520 820" fill="none" stroke="#b8c0cc" stroke-width="34" stroke-linecap="round"/><path d="M640 1000 L640 860 Q640 820 600 820 L520 820" fill="none" stroke="${ST}" stroke-width="4"/>`;
  const dk = (t * 1.4) % 1; s += `<ellipse cx="520" cy="${f(850 + dk * 180)}" rx="9" ry="13" fill="#7a6640" opacity="${f(1 - dk * .5)}"/>`;
  return cam(s, lerp(1.0, 1.12, seg(t, S(8), S(9))), 540, 980);
});

// 7. Схема фильтра в бутылке
add(S(9) - .1, P(10, 1) - .05, t => {
  let s = blueprint(t, 'СХЕМА №5 · ФИЛЬТР ДЛЯ ВОДЫ');
  const cx = 420;
  // бутылка горлышком вниз, без дна (верх открыт)
  const bk = seg(t, Wt(9, 'БУТЫЛКА') - .1, Wt(9, 'БУТЫЛКА') + .7);
  const bottle = `M${cx - 150} 720 L${cx - 150} 1060 Q${cx - 150} 1130 ${cx - 50} 1170 L${cx - 30} 1230 L${cx + 30} 1230 L${cx + 50} 1170 Q${cx + 150} 1130 ${cx + 150} 1060 L${cx + 150} 720`;
  const layers = [['МАРЛЯ', '#f4f2ec', 1110, 1170, 'МАРЛЯ'], ['УГОЛЬ', '#1b1d22', 960, 1110, 'УГОЛЬ'], ['ПЕСОК', '#e2c27a', 830, 960, 'ПЕСОК']];
  layers.forEach(([nm, col, y1, y2, w]) => {
    const tw = Wt(9, w); const k = seg(t, tw - .1, tw + .4); if (k <= 0) return;
    const yy1 = lerp(y2, y1, eout(k));
    const id = 'bcl' + gid++;
    s += `<clipPath id="${id}"><path d="${bottle} Z"/></clipPath><rect x="${cx - 160}" y="${f(yy1)}" width="320" height="${f(y2 - yy1)}" fill="${col}" clip-path="url(#${id})" opacity=".92"/>`;
    s += pline(cx + 160, (y1 + y2) / 2, cx + 260, (y1 + y2) / 2, k, '#fff', 3) + mono(cx + 275, (y1 + y2) / 2 + 10, typeText(nm, k), 32, col === '#1b1d22' ? '#fff' : col);
  });
  s += `<path d="${bottle}" fill="none" stroke="#fff" stroke-width="6" stroke-dasharray="${f(2000 * bk)} 3000"/>`;
  s += mono(cx, 690, typeText('БЕЗ ДНА ↓ ЛЬЁМ СЮДА', seg(t, Wt(9, 'БУТЫЛКА') + .3, Wt(9, 'БУТЫЛКА') + 1)), 26, '#a9cbf5', 'middle');
  // мутная вода сверху и чистые капли снизу
  const pk = seg(t, P(10, 0), P(10, 0) + .3);
  if (pk > 0) {
    s += `<rect x="${cx - 146}" y="770" width="292" height="60" fill="#7a6640" opacity="${f(.8 * pk)}"/>`;
    for (let i = 0; i < 3; i++) { const d = ((t * 1.2 + i / 3) % 1); s += `<ellipse cx="${cx}" cy="${f(1240 + d * 120)}" rx="9" ry="13" fill="#9fd4ff" opacity="${f(1 - d)}"/>`; }
    s += `<path d="M${cx - 70} 1370 L${cx - 60} 1460 L${cx + 60} 1460 L${cx + 70} 1370" fill="rgba(159,212,255,.35)" stroke="#fff" stroke-width="5"/>`;
    s += mono(cx + 120, 1430, typeText('СЛОЙ ЗА СЛОЕМ', seg(t, P(10, 0), P(10, 0) + .8)), 28, '#3ddc84');
  }
  return cam(s, lerp(1.0, 1.04, seg(t, S(9), S(10))), 540, 1000);
}, .3);

// 8. Кипячу на горелке
add(P(10, 1) - .05, S(11) - .3, t => {
  let s = room(1300);
  s += `<ellipse cx="540" cy="1160" rx="300" ry="160" fill="url(#warmBlob)" opacity=".35"/>`;
  s += rect(430, 1150, 220, 150, '#5a6273', `rx="16" stroke="${ST}" stroke-width="5"`) + rect(460, 1180, 160, 36, '#2a3142', 'rx="6"');
  for (let i = 0; i < 9; i++) { const h = 40 + Math.sin(t * 20 + i * 1.7) * 12; s += `<path d="M${470 + i * 18} 1150 q9 ${-h} 18 0Z" fill="#4da3ff" opacity=".9"/>`; }
  s += `<path d="M380 1060 L700 1060 L680 1140 L400 1140Z" fill="#8b909c" stroke="${ST}" stroke-width="5"/>` + rect(360, 1040, 360, 30, '#a6acb8', `rx="8" stroke="${ST}" stroke-width="5"`);
  s += `<path d="M720 1055 L800 1040" stroke="${ST}" stroke-width="14" stroke-linecap="round"/>`;
  for (let i = 0; i < 4; i++) { const d = ((t * .5 + i / 4) % 1); s += `<path d="M${f(450 + i * 60)} ${f(1030 - d * 300)} q30 -40 0 -80 q-30 -40 0 -80" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity="${f(.4 * (1 - d))}"/>`; }
  return cam(s, lerp(1.08, 1.0, eout(seg(t, P(10, 1), S(11)))), 540, 1000);
}, .3);

// 9. Утро: следы от ряда до спальника и обратно (вид сверху)
const SLP = { x: 830, y: 1150 };
add(S(11) - .3, S(13) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0e15');
  s += rect(80, 540, 920, 780, '#141926', `stroke="#3a4560" stroke-width="6"`);
  s += rect(100, 560, 380, 300, '#121722', `stroke="#3a4560" stroke-width="5"`) + txt(290, 600, 'ОДЕЖДА', 28, '#ffd23f');
  s += rect(560, 980, 420, 320, '#121722', `stroke="#3a4560" stroke-width="5"`) + txt(770, 1020, 'ФУДКОРТ', 28, '#7e889c');
  s += rect(130, 690, 320, 70, 'rgba(233,231,225,.35)', 'rx="12"');
  for (let i = 0; i < 13; i++) s += `<circle cx="${150 + i * 23.5}" cy="725" r="9" fill="#ecebe7" stroke="${ST}" stroke-width="2"/>`;
  // спальник + рюкзак
  s += rect(SLP.x - 110, SLP.y - 40, 220, 90, '#3d5a3a', `rx="40" stroke="${ST}" stroke-width="5"`) + rect(SLP.x - 100, SLP.y - 32, 60, 74, '#566f52', 'rx="26"');
  s += `<g transform="translate(${SLP.x + 150} ${SLP.y + 40})">${backpack(0, 0, 90)}</g>`;
  // путь
  const pts = [[300, 770], [330, 900], [480, 940], [620, 960], [720, 1060], [SLP.x + 120, SLP.y - 20]];
  const back = pts.slice().reverse().map(([x, y]) => [x - 26, y + 18]);
  const walk = (P0, k, col) => {
    let tot = 0; const L2 = []; for (let i = 1; i < P0.length; i++) { const d = Math.hypot(P0[i][0] - P0[i - 1][0], P0[i][1] - P0[i - 1][1]); L2.push(d); tot += d; }
    let r = '', acc = 0, step = 34, n = Math.floor(tot / step), cnt = Math.floor(n * k);
    for (let j = 0; j < cnt; j++) {
      let dd = j * step, i = 0; while (i < L2.length - 1 && dd > L2[i]) { dd -= L2[i]; i++; }
      const a = P0[i], b = P0[i + 1], q = clamp(dd / L2[i]); const x = lerp(a[0], b[0], q), y = lerp(a[1], b[1], q);
      const ang = Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI + 90; const off = (j % 2 ? 7 : -7);
      r += bareFoot(x + off * Math.cos(ang * Math.PI / 180), y + off * Math.sin(ang * Math.PI / 180), .2, ang, j % 2 === 0, col, .95);
    }
    return r;
  };
  s += walk(pts, seg(t, P(11, 1), E(11) + .3), '#e9e7e1');
  s += walk(back, seg(t, P(12, 2), E(12)), '#ff9a4a');
  // камера: общий план → наезд к спальнику на «где сплю я»
  const zk = eio(seg(t, P(12, 1) - .2, P(12, 1) + .5)) * (1 - eio(seg(t, P(12, 2), P(12, 2) + .6)));
  // крупный след у рюкзака
  if (zk > 0.05) s += bareFoot(SLP.x + 108, SLP.y + 16, .5, -20, false, '#e9e7e1', zk);
  return cam(s, lerp(1.0, 3.0, zk), lerp(540, SLP.x + 110, zk), lerp(930, SLP.y + 10, zk));
}, .3);
DRONE.push([P(12, 1) - .5, .9], [P(12, 1) - .1, 0], [P(12, 2) + .8, 0], [S(13), .8]);

// 10. День 9: тащу манекена на склад
add(S(13) - .25, S(14) - .25, t => {
  let s = room(1300);
  s += rect(780, 560, 260, 740, '#141925', `stroke="#3a4560" stroke-width="6"`) + rect(800, 590, 220, 70, '#1b2131') + txt(910, 640, 'СКЛАД', 38, '#ffd23f', 'letter-spacing="4"');
  const tg = P(13, 2);
  const k = eio(seg(t, tg, E(13) + .1));
  const hx = lerp(260, 760, k);
  // ряд вдали
  for (let i = 0; i < 5; i++) s += mannequin(-60 + i * 110, 1000, 260, { dim: .35, sw: 3 });
  // манекен, который тащат (наклонён)
  const tilt = lerp(0, -58, seg(t, tg - .2, tg + .4));
  const mx = hx + lerp(-120, 110, seg(t, tg - .2, tg + .4));
  s += `<g transform="rotate(${f(tilt)} ${f(mx)} 1290)">${mannequin(mx, 1290, 520, {})}</g>`;
  s += hero(hx, 1300, 520, 'front', k > 0 && k < 1 ? 'read' : 'stand');
  return cam(s, 1.02, 540, 980);
});

// 11. Ночь: луч по ряду с пустым местом, останавливается
const GAPI = 3;
add(S(14) - .25, S(15) - .1, t => {
  let s = room(1340) + rackRail(500, -200, 1280);
  s += row(t, 7, 160, 60, 1330, 700, { skip: GAPI });
  const tS = Wt(14, 'ОСТАНОВИЛСЯ') - .3;
  let bx;
  if (t < P(14, 2)) bx = -300;
  else if (t < tS) bx = lerp(-200, 60 + GAPI * 160, eio(seg(t, P(14, 2), tS)));
  else bx = 60 + GAPI * 160 + Math.sin(t * 1.5) * 3;
  s += beam(1300, -300, bx, 1300 - .6 * 700, 110, t < P(14, 2) ? 0 : 1);
  const kz = eio(seg(t, tS, E(14)));
  return cam(s, lerp(1.0, 1.25, kz), lerp(540, 60 + GAPI * 160, kz), 960);
});

// 12. Шаги пошли ко мне: свет поворачивается на камеру
add(S(15) - .1, S(16) - .1, t => {
  let s = room(1340) + rackRail(500, -200, 1280);
  s += row(t, 7, 160, 60, 1330, 700, { skip: GAPI });
  const k = seg(t, S(15), E(15));
  const id = 'glow' + gid++;
  s += `<radialGradient id="${id}"><stop offset="0" stop-color="#fffbe6" stop-opacity="1"/><stop offset=".4" stop-color="#fffbe6" stop-opacity=".5"/><stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient>`;
  const gx = lerp(1200, 600, eio(k)), r = lerp(80, 900, Math.pow(k, 1.6));
  s += `<circle cx="${f(gx)}" cy="1100" r="${f(r)}" fill="url(#${id})" style="mix-blend-mode:screen"/>`;
  return cam(s, lerp(1.0, 1.12, k), 540, 980, Math.sin(t * 30) * k * .6);
});
DRONE.push([S(14) + 1.5, .9], [Wt(14, 'СТИХЛИ'), 0], [S(16) + 1, 0], [S(17), .6]);

// 13. Бегом вернул манекена
add(S(16) - .1, S(17) - .25, t => {
  let s = room(1340) + rackRail(500, -200, 1280);
  const tp = Wt(16, 'МЕСТО');
  const k = eout(seg(t, S(16), tp));
  const placed = k >= 1;
  s += row(t, 7, 160, 60, 1330, 700, placed ? {} : { skip: GAPI });
  if (!placed) {
    const mx = lerp(1250, 60 + GAPI * 160, k);
    s += `<g transform="rotate(${f(lerp(-50, 0, k))} ${f(mx)} 1330)">${mannequin(mx, 1330, 700, {})}</g>`;
    s += hero(mx + 230, 1340, 640, 'front', 'read');
  } else {
    const hx = lerp(60 + GAPI * 160 + 230, 1350, eio(seg(t, tp, tp + .8)));
    s += hero(hx, 1340, 640, 'front');
  }
  const fade = 1 - seg(t, Wt(16, 'ЗАТИХЛИ') - .2, Wt(16, 'ЗАТИХЛИ') + .4);
  const id = 'glow' + gid++;
  s += `<radialGradient id="${id}"><stop offset="0" stop-color="#fffbe6" stop-opacity=".8"/><stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient><circle cx="700" cy="1100" r="700" fill="url(#${id})" opacity="${f(.55 * fade)}" style="mix-blend-mode:screen"/>`;
  return cam(s, 1.08, 540, 980);
}, .2);

// 14. Правило №1 на листке блокнота
add(S(17) - .25, S(18) - .3, t => {
  let s = rect(-400, -400, 1880, 2800, '#0d1018');
  s += `<g transform="rotate(-3 540 1000)">`;
  s += rect(150, 640, 780, 700, '#f3efe3', `rx="10" stroke="${ST}" stroke-width="6"`);
  for (let i = 0; i < 12; i++) s += `<line x1="170" y1="${720 + i * 52}" x2="910" y2="${720 + i * 52}" stroke="#9fb8d8" stroke-width="2"/>`;
  s += `<line x1="240" y1="640" x2="240" y2="1340" stroke="#e08a8a" stroke-width="3"/>`;
  for (let i = 0; i < 7; i++) s += `<circle cx="${210 + i * 110}" cy="640" r="14" fill="#0d1018"/>`;
  const ink = '#1d2f6b';
  const t1 = P(17, 1);
  const w1 = typeText('СЧЁТ ДОЛЖЕН', seg(t, t1, t1 + .6)), w2 = typeText('СХОДИТЬСЯ', seg(t, t1 + .5, t1 + 1.0));
  s += `<text x="270" y="830" font-family="Inter" font-style="italic" font-weight="900" font-size="70" fill="${ink}">${w1}</text>`;
  s += `<text x="270" y="920" font-family="Inter" font-style="italic" font-weight="900" font-size="78" fill="${ink}">${w2}</text>`;
  s += pline(270, 945, 760, 940, seg(t, t1 + 1.0, t1 + 1.4), '#c0392b', 7);
  const t2 = P(17, 2);
  s += `<text x="270" y="1060" font-family="Inter" font-style="italic" font-weight="800" font-size="44" fill="${ink}">${typeText('НЕ ХВАТАЕТ ОДНОГО —', seg(t, t2, t2 + .8))}</text>`;
  s += `<text x="270" y="1120" font-family="Inter" font-style="italic" font-weight="800" font-size="44" fill="#c0392b">${typeText('ОН БЕРЁТ ЗАМЕНУ', seg(t, Wt(17, 'БЕРЁТ') - .2, Wt(17, 'ЗАМЕНУ') + .3))}</text>`;
  s += '</g>';
  const ts = t1 + 1.3; const k = seg(t, ts, ts + .12);
  if (k > 0) s += `<g transform="translate(720 1230) rotate(-12) scale(${f(lerp(1.5, 1, k))})" opacity="${f(k * .9)}"><rect x="-190" y="-60" width="380" height="120" rx="14" fill="none" stroke="#e0322f" stroke-width="10"/>${txt(0, 18, 'ПРАВИЛО № 1', 54, '#e0322f')}</g>`;
  return cam(s, lerp(1.0, 1.05, seg(t, S(17), S(18))), 540, 990, Math.sin(t * 40) * 1.5 * seg(t, ts, ts + .05) * (1 - seg(t, ts + .05, ts + .25)));
}, .3);

// 15. День 12: схема-счёт, лишний — я
add(S(18) - .3, S(20) - .25, t => {
  let s = blueprint(t, 'СХЕМА №6 · ПЕРЕСЧЁТ');
  const fig = (x, y, sc, col, fill = 'none') => `<g transform="translate(${f(x)} ${f(y)}) scale(${sc})" stroke="${col}" stroke-width="${(4 / sc).toFixed(3)}" fill="${fill}">
     <ellipse cx="0" cy="-.915" rx=".052" ry=".066"/><path d="M-.112 -.825 Q0 -.85 .112 -.825 L.12 -.56 L.1 -.33 L-.1 -.33 L-.12 -.56Z"/><path d="M-.07 -.33 L-.06 -.05 M.07 -.33 L.06 -.05"/></g>`;
  const t12 = Wt(18, 'ДВЕНАДЦАТЬ');
  for (let i = 0; i < 12; i++) {
    const k = popScale(t, t12 - .2 + i * .09); if (k <= 0) continue;
    const x = 140 + (i % 6) * 100, y = i < 6 ? 960 : 1240;
    s += `<g transform="translate(${x} ${y}) scale(${k.toFixed(3)}) translate(${-x} ${-y})">${fig(x, y, 240, '#a9cbf5', 'rgba(169,203,245,.15)')}</g>`;
  }
  s += mono(390, 1300, typeText('БЫЛИ ВСЕГДА: 12', seg(t, Wt(18, 'ВСЕГДА') - .3, Wt(18, 'ВСЕГДА') + .5)), 30, '#a9cbf5', 'middle');
  // я и 13-й
  const tA = S(19), tB = P(19, 1), tC = P(19, 2);
  const kA = popScale(t, Wt(19, 'ТРИНАДЦАТЫЙ'));
  const kH = popScale(t, Wt(19, 'ВСТАЛ') - .1);
  const X13 = 830, XH = 830, Y13 = 960, YH = 1240;
  if (kA > 0) s += `<g transform="translate(${X13} ${Y13}) scale(${kA.toFixed(3)}) translate(${-X13} ${-Y13})">${fig(X13, Y13, 240, '#fff', 'rgba(255,255,255,.2)')}</g>` + mono(X13, Y13 + 40, '13-Й', 30, '#fff', 'middle');
  if (kH > 0) s += `<g transform="translate(${XH} ${YH}) scale(${kH.toFixed(3)}) translate(${-XH} ${-YH})">${fig(XH, YH, 240, '#ff9a4a', 'rgba(255,122,26,.25)')}<g transform="translate(${XH + 24} ${YH - 170})">${backpack(0, 0, 60)}</g></g>` + mono(XH, YH + 40, 'Я', 30, '#ff9a4a', 'middle');
  s += parrow(XH - 60, YH - 160, X13 - 60, Y13 - 40, seg(t, Wt(19, 'ВСТАЛ') + .2, Wt(19, 'ВСТАЛ') + .7), '#fff', 4);
  // красная рамка: 13-й → я
  if (t > tB - .1) {
    const k = eio(seg(t, tC - .1, tC + .35));
    const fy = lerp(Y13, YH, k);
    const pulse = 1 + .03 * Math.sin(t * 10);
    s += `<rect x="${f(X13 - 95 * pulse)}" y="${f(fy - 260 * pulse)}" width="${f(190 * pulse)}" height="${f(300 * pulse)}" rx="14" fill="none" stroke="#ff4040" stroke-width="8"/>`;
    const lk = popScale(t, Wt(19, 'ЛИШНИЙ') > tC ? Wt(19, 'ЛИШНИЙ') : tC + .25);
    if (k >= 1 && lk > 0) s += `<g transform="translate(${XH} ${YH - 300}) scale(${lk.toFixed(3)})">${rect(-140, -40, 280, 80, '#e0322f', `rx="12" stroke="${ST}" stroke-width="5"`)}${txt(0, 18, 'ЛИШНИЙ', 48, '#fff')}</g>`;
  }
  return cam(s, lerp(1.0, 1.05, seg(t, S(18), S(20))), 540, 1040);
}, .3);

// 16. Ночь: тринадцатый шагнул из ряда. Ко мне.
const tStep = () => Wt(21, 'ШАГНУЛ');
function finalRow(t) {
  let s = room(1340) + rackRail(500, -200, 1280);
  s += row(t, 7, 160, 60, 1330, 700, t >= tStep() ? { step: 3 } : {});
  s += beam(-260, -260, 540, 520, 200, .75);
  return s;
}
add(S(20) - .25, S(22) - .15, t => {
  let s = finalRow(t);
  const tk = P(21, 1);
  const zk = eout(seg(t, tk - .05, tk + .35));
  const T = t - S(20);
  if (t >= tStep() && t < tStep() + .06) s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#fff" opacity=".25"/>`;
  return cam(s, lerp(1.0, 1.05, seg(T, 0, 8)) + zk * 1.4, 540, lerp(960, 600, zk));
}, .35);
HUDOFF.push([S(20) - .2, S(22) - .1]);
DRONE.push([S(20), .8], [P(21, 1) - .05, .9], [P(21, 1) + .02, 0], [S(22) + .3, 0], [S(22) + 1.2, .5]);

// 17. Экран выбора
add(S(22) - .15, DUR + 1, t => {
  let s = `<g opacity=".28">${cam(finalRow(t), 1.05, 540, 960)}</g>`;
  s += rect(-10, -10, 1100, 1940, '#000', 'opacity=".35"');
  const card = (cx, n, label, icon, tt, col) => {
    const k = popScale(t, tt, .3); if (k <= 0) return '';
    const glow = .5 + .5 * Math.sin(t * 5 + n);
    return `<g transform="translate(${cx} 900) scale(${k.toFixed(3)})">
      <rect x="-200" y="-260" width="400" height="520" rx="34" fill="#141925" stroke="${col}" stroke-width="${f(8 + 4 * glow)}"/>
      <circle cx="0" cy="-160" r="62" fill="${col}"/>${txt(0, -136, n, 76, '#0d1018')}
      ${icon}
      ${txt(0, 215, label, 58, '#fff')}</g>`;
  };
  const esc = `<g transform="translate(0 20)" stroke="#e9edf5" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M-120 90 L-60 90 L60 -30 L120 -30"/><path d="M-120 40 L-80 40 L40 -80 L120 -80"/><path d="M-60 90 L-60 40 M-20 50 L-20 0 M20 10 L20 -40 M60 -30 L60 -80"/></g>`;
  const msk = `<g transform="translate(0 20)"><ellipse cx="0" cy="0" rx="78" ry="98" fill="#f7f6f2" stroke="${ST}" stroke-width="6"/><ellipse cx="-28" cy="-12" rx="16" ry="9" fill="#1a1d24"/><ellipse cx="28" cy="-12" rx="16" ry="9" fill="#1a1d24"/></g>`;
  s += card(285, '1', 'БЕЖАТЬ', esc, Wt(22, 'БЕЖАТЬ'), '#ffd23f');
  s += card(795, '2', 'ЗАМЕРЕТЬ', msk, Wt(22, 'ЗАМЕРЕТЬ'), '#ffd23f');
  const ok = seg(t, Wt(22, 'ЗАМЕРЕТЬ'), Wt(22, 'ЗАМЕРЕТЬ') + .3);
  if (ok > 0) s += `<g opacity="${f(ok)}"><circle cx="540" cy="900" r="52" fill="#0d1018" stroke="#9aa6bd" stroke-width="5"/>${txt(540, 914, 'ИЛИ', 34, '#e9edf5')}</g>`;
  const pk = popScale(t, P(22, 2));
  const pul = 1 + .03 * Math.sin(t * 6);
  if (pk > 0) s += `<g transform="translate(540 1250) scale(${(pk * pul).toFixed(3)})">${rect(-440, -48, 880, 96, '#e0322f', `rx="16" stroke="${ST}" stroke-width="5"`)}${txt(0, 16, 'ПИШИ 1 ИЛИ 2 — РЕШАЕТ БОЛЬШИНСТВО', 40, '#fff')}</g>`;
  if (pk > 0) s += mono(540, 1660, 'ЧАСТЬ 3 — ДЕНЬ 13', 34, '#9aa6bd', 'middle', `opacity="${f(seg(t, P(22, 2) + .4, P(22, 2) + .9))}"`);
  return s;
}, .3);

// ---------- HUD ----------
const DAYS = [[S(2), 6], [S(7), 7], [S(13), 9], [S(18), 12]];
DAYS.forEach(([t]) => sfx(t, 'page', .9));
function dayAt(t) { let d = null, t0 = 0; for (const [tt, n] of DAYS) if (t >= tt) { d = n; t0 = tt; } return [d, t0]; }
function keyf(t, kf) {
  if (t <= kf[0][0]) return kf[0][1];
  for (let i = 1; i < kf.length; i++) if (t < kf[i][0]) return lerp(kf[i - 1][1], kf[i][1], eio(seg(t, kf[i - 1][0], kf[i][0])));
  return kf[kf.length - 1][1];
}
const tSleep = Wt(12, 'СПЛЮ');
const FOOD = [[0, 62], [S(7), 58], [S(13), 50], [S(18), 44]];
const CHARGE = [[0, 95], [S(7), 92], [S(13), 88], [S(18), 84]];
const SLEEP = [[0, 30], [tSleep - .1, 30], [tSleep + .5, 8], [S(13), 22], [S(18), 14]];
const WATER = [[S(7), 60], [Wt(7, 'ПОГАСЛИ'), 60], [Wt(7, 'ПОГАСЛИ') + .6, 30], [S(8), 30], [Wt(8, 'МУТНАЯ'), 15], [P(10, 1), 15], [P(10, 1) + 1.5, 90], [S(18), 80]];
const DROPS = [Wt(7, 'ПОГАСЛИ'), Wt(8, 'МУТНАЯ'), tSleep];
const PLATES = [
  [P(2, 1), 'p', 'КТО НОВЫЙ?', S(7) - .3],
  [P(5, 1) + .2, 's', 'ЛОВУШКА ИЗ ПРИСЫПКИ', S(7) - .3],
  [Wt(7, 'ПОГАСЛИ'), 'p', 'ВОДА', S(11) - .3],
  [Wt(9, 'ФИЛЬТР'), 's', 'ФИЛЬТР', S(11) - .3],
  [P(13, 1), 'p', 'ЗАЧЕМ ОН СЧИТАЕТ?', S(14) - .3],
];
PLATES.forEach(([t]) => sfx(t, 'stamp', .8));
DROPS.forEach(t => sfx(t, 'alarm', .5));
const tTake = Wt(13, 'УНЁС'), tBack = Wt(16, 'ВЕРНУЛ');

const elDay = document.getElementById('day'), elHud = document.getElementById('hud'), elPl = document.getElementById('plates');
const elB = [0, 1, 2, 3].map(i => document.getElementById('b' + i)), elV = [0, 1, 2, 3].map(i => document.getElementById('v' + i));
const elW = document.getElementById('wbar'), elMC = document.getElementById('mcount');
function renderHUD(t) {
  const [d, t0] = dayAt(t);
  let on = d !== null ? clamp((t - S(2)) / .3) : 0;
  HUDOFF.forEach(([a, b]) => { if (t > a && t < b) on *= clamp(Math.abs(t - a) / .2) * 0; });
  elHud.style.opacity = on;
  if (d !== null) {
    const fk = seg(t, t0, t0 + .35); const sy = fk < .5 ? 1 - fk * 2 : (fk - .5) * 2;
    const idx = DAYS.findIndex(x => x[1] === d); const shown = fk < .5 && idx > 0 ? DAYS[idx - 1][1] : d;
    elDay.innerHTML = `ДЕНЬ ${shown} <small>/ 365</small>`;
    elDay.style.transform = `scaleY(${Math.max(.02, sy).toFixed(3)})`;
  }
  // шкала воды появляется на 7-й день
  const wk = seg(t, S(7), S(7) + .4);
  elW.style.display = wk > 0 ? 'flex' : 'none';
  elW.style.transform = `scale(${(wk > 0 ? lerp(.3, 1, back(wk)) : 0).toFixed(3)})`;
  const vals = [keyf(t, FOOD), keyf(t, CHARGE), keyf(t, SLEEP), keyf(t, WATER)];
  vals.forEach((v, i) => {
    elB[i].style.width = v.toFixed(1) + '%';
    elB[i].style.background = v < 20 ? '#ff4040' : v < 45 ? '#ffd23f' : (i === 3 ? '#6cc0ff' : '#e9edf5');
    elV[i].textContent = Math.round(v) + '%';
  });
  // счётчик манекенов
  const n = t >= tTake && t < tBack ? 12 : 13;
  const blink = n === 12 ? (Math.sin(t * 12) > 0 ? 1 : .35) : 1;
  const back13 = t >= tBack && t < tBack + 1 ? 1 : 0;
  elMC.innerHTML = `МАНЕКЕНЫ: <b style="color:${n === 12 ? '#ff4040' : back13 ? '#3ddc84' : '#fff'}">${n}</b>`;
  elMC.style.opacity = blink;
  let h = '';
  PLATES.forEach(([tp, ty, tx, tEnd]) => {
    if (t < tp || t > tEnd) return;
    const k = seg(t, tp, tp + .14); const sc = lerp(1.6, 1, eout(k)); const o = k * (1 - seg(t, tEnd - .25, tEnd));
    const sh = t - tp < .25 ? Math.sin((t - tp) * 80) * 4 * (1 - (t - tp) / .25) : 0;
    h += `<div class="plate ${ty}" style="transform:translateX(${sh.toFixed(1)}px) scale(${sc.toFixed(3)}) rotate(${ty === 'p' ? -2 : 2}deg);opacity:${o.toFixed(2)}"><span>${ty === 'p' ? 'ПРОБЛЕМА:' : 'РЕШЕНИЕ:'}</span>${tx}</div>`;
  });
  elPl.innerHTML = h;
  let rf = 0; DROPS.concat([tTake]).forEach(td => { const q = t - td; if (q > 0 && q < .7) rf = Math.max(rf, (1 - q / .7) * (Math.sin(q * 30) * .3 + .7)); });
  document.getElementById('redflash').style.opacity = rf.toFixed(2);
}

const elTitle = document.getElementById('title');
function renderOverlays(t) {
  const a = S(1) - .1, b = P(2, 0) - .15;
  elTitle.style.opacity = (seg(t, a, a + .5) * (1 - seg(t, b - .4, b))).toFixed(2);
  elTitle.style.transform = `scale(${lerp(1.08, 1, eout(seg(t, a, a + 1.5))).toFixed(3)})`;
  let black = 0;
  if (t < .35) black = 1 - t / .35;
  // затемнение после «Ко мне»
  const tk = P(21, 1);
  black = Math.max(black, seg(t, tk + .35, tk + .6) * (1 - seg(t, S(22) - .25, S(22) + .1)));
  if (t > DUR - .6) black = Math.max(black, seg(t, DUR - .6, DUR));
  document.getElementById('flash').style.opacity = black.toFixed(2);
}

// ---------- звуки ----------
(function () {
  sfx(.2, 'sand', .6, { d: 4 });
  sfx(Wt(0, 'БОСЫЕ'), 'heart', .7);
  sfx(S(1) - .1, 'boom', 1);
  sfx(P(2, 1), 'tick', .6);
  sfx(S(3) + .2, 'whoosh', .5);
  sfx(P(5, 1), 'pencil', .6, { d: 2.0 }); sfx(P(5, 1) + .2, 'sand', .7, { d: 2.4 });
  for (let j = 0; j < 3; j++) sfx(S(6) + .6 + j * .25, 'step', .35);
  sfx(Wt(7, 'ПОГАСЛИ') - .05, 'click', .9); sfx(Wt(7, 'ПОГАСЛИ'), 'powerdown', .8);
  for (let i = 0; i < 7; i++) sfx(Wt(7, 'НЕДЕЛЮ') - .3 + i * .08, 'pop', .4);
  for (let i = 0; i < 4; i++) sfx(S(8) + .3 + i * .72, 'drip', .6);
  sfx(S(9) + .1, 'pencil', .6, { d: 3.5 });
  ['МАРЛЯ', 'УГОЛЬ', 'ПЕСОК'].forEach(w => sfx(Wt(9, w), 'pop', .5));
  for (let i = 0; i < 5; i++) sfx(P(10, 0) + .2 + i * .55, 'drip', .5);
  sfx(P(10, 1), 'hiss', .7, { d: 3.2 });
  sfx(P(11, 1), 'pencil', .45, { d: 2.4 });
  for (let i = 0; i < 6; i++) sfx(P(12, 1) + i * .62, 'heart', .8);
  for (let i = 0; i < 5; i++) sfx(P(13, 2) + i * .35, 'scrape', .5);
  sfx(Wt(13, 'УНЁС'), 'alarm', .4);
  sfx(Wt(14, 'КЛЮЧИ'), 'keys', .9); sfx(P(14, 2) + .2, 'keys', .6);
  for (let i = 0; i < 9; i++) sfx(S(15) + i * .42, 'step', .45 + i * .06, { pan: 1 - i / 8 * 2 });
  for (let i = 0; i < 6; i++) sfx(S(16) + i * .18, 'step', .55);
  sfx(Wt(16, 'МЕСТО'), 'clack', .8);
  sfx(P(17, 1) + 1.3, 'stamp', 1.1);
  sfx(P(17, 1), 'pencil', .5, { d: 1.5 });
  const t12 = Wt(18, 'ДВЕНАДЦАТЬ');
  for (let i = 0; i < 12; i++) sfx(t12 - .2 + i * .09, 'tick', .5);
  sfx(Wt(19, 'ТРИНАДЦАТЫЙ'), 'tick', .7); sfx(Wt(19, 'ВСТАЛ') - .1, 'tick', .7);
  sfx(P(19, 2), 'boom', 1.0);
  sfx(S(20) + .2, 'keys', .8); sfx(S(20) + 1.8, 'keys', .5);
  sfx(Wt(21, 'ШАГНУЛ'), 'clack', 1.1); sfx(Wt(21, 'ШАГНУЛ') + .02, 'boom', .7);
  for (let i = 0; i < 14; i++) sfx(S(22) + .4 + i * .5, 'tick', .45);
  sfx(Wt(22, 'БЕЖАТЬ'), 'pop', .6); sfx(Wt(22, 'ЗАМЕРЕТЬ'), 'pop', .6); sfx(P(22, 2), 'stamp', .9);
  DRONE.sort((a, b) => a[0] - b[0]).forEach(([t, v]) => sfx(t, 'drone_kf', v));
  sfx(DUR, 'drone_kf', 0); sfx(DUR - 2.5, 'drone_kf', .4);
})();

// обложка
window.COVER = function () {
  let s = rect(-400, -400, 1880, 2800, '#0b0d13') + powderField(60, 200, 960, 1700, 3, .72);
  for (let i = 0; i < 5; i++) { const y = 1840 - i * 140, x = 540 + (i % 2 ? 60 : -60) + Math.sin(i * .7) * 40; s += bareFoot(x, y, 1.35, (i % 2 ? 8 : -8), i % 2 === 0, '#4a3a2c', .85); }
  s += backpack(560, 1200, 240);
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="url(#vig)" opacity=".9"/>`;
  return s;
};
