/* «365 дней в торговом центре — Часть 1». Детерминированный рендер кадра: window.renderAt(t). */
(function () {
const TL = window.TL;
const L = TL.lines;
const DUR = TL.duration;

// ---------- утилиты ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = k => k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
const eout = k => 1 - Math.pow(1 - k, 3);
const back = k => { const c = 1.70158, c3 = c + 1; return 1 + c3 * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const f = n => (+n).toFixed(1);
const S = (i) => L[i].t0;
const E = (i) => L[i].t1;
const P = (i, p) => L[i].phrases[p].t0;
const PE = (i, p) => L[i].phrases[p].t1;
function Wt(i, word) { // время слова по тексту (первое вхождение)
  for (const ph of L[i].phrases) for (const w of ph.words) if (w.w.replace(/[^А-ЯЁA-Z0-9-]/g, '') === word) return w.t0;
  throw new Error('no word ' + word + ' in ' + i);
}
const ST = '#0b0d12';     // контур
const SW = 5;             // базовая толщина контура

// ---------- звуковые события (для sfx.py) ----------
const SFX = [];
const sfx = (t, type, g = 1, extra = {}) => SFX.push(Object.assign({ t: +t.toFixed(3), type, g }, extra));

// ---------- примитивы ----------
function cam(inner, s, cx, cy, rot = 0) {
  return `<g transform="translate(540 960) rotate(${f(rot)}) scale(${s.toFixed(4)}) translate(${f(-cx)} ${f(-cy)})">${inner}</g>`;
}
function rect(x, y, w, h, fill, extra = '') { return `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" fill="${fill}" ${extra}/>`; }
function txt(x, y, s, size, fill, extra = '') {
  return `<text x="${f(x)}" y="${f(y)}" font-family="Inter" font-weight="900" font-size="${size}" fill="${fill}" text-anchor="middle" ${extra}>${s}</text>`;
}
function mono(x, y, s, size, fill = '#fff', anchor = 'start', extra = '') {
  return `<text x="${f(x)}" y="${f(y)}" font-family="JetBrains Mono" font-weight="700" font-size="${size}" fill="${fill}" text-anchor="${anchor}" ${extra}>${s}</text>`;
}
// частичная линия (дорисовка)
function pline(x1, y1, x2, y2, k, stroke = '#fff', w = 4, dash = '') {
  if (k <= 0) return '';
  const x = lerp(x1, x2, k), y = lerp(y1, y2, k);
  return `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x)}" y2="${f(y)}" stroke="${stroke}" stroke-width="${w}" stroke-linecap="round" ${dash ? `stroke-dasharray="${dash}"` : ''}/>`;
}
function parrow(x1, y1, x2, y2, k, stroke = '#fff', w = 5) {
  if (k <= 0) return '';
  const x = lerp(x1, x2, k), y = lerp(y1, y2, k);
  let s = pline(x1, y1, x2, y2, k, stroke, w, '14 12');
  if (k > .97) {
    const a = Math.atan2(y2 - y1, x2 - x1), l = 28;
    s += `<path d="M${f(x)} ${f(y)} L${f(x - l * Math.cos(a - .45))} ${f(y - l * Math.sin(a - .45))} M${f(x)} ${f(y)} L${f(x - l * Math.cos(a + .45))} ${f(y - l * Math.sin(a + .45))}" stroke="${stroke}" stroke-width="${w}" stroke-linecap="round" fill="none"/>`;
  }
  return s;
}
// дорисовка окружности пунктиром
function pcircle(cx, cy, r, k, stroke = '#ffd23f', w = 5) {
  if (k <= 0) return '';
  const C = 2 * Math.PI * r;
  return `<circle cx="${f(cx)}" cy="${f(cy)}" r="${r}" fill="none" stroke="${stroke}" stroke-width="${w}" stroke-dasharray="${f(C * k)} ${f(C)}" transform="rotate(-90 ${f(cx)} ${f(cy)})"/>`;
}
function typeText(s, k) { const n = Math.round(s.length * clamp(k)); return s.slice(0, n); }
function popScale(t, t0, d = .28) { const k = seg(t, t0, t0 + d); return k <= 0 ? 0 : back(k); }

// пыль/частицы
function dust(t, n, seed, x0, y0, w, h, col = '#fff', op = .5, size = 3) {
  const r = rng(seed); let s = '';
  for (let i = 0; i < n; i++) {
    const bx = r() * w, by = r() * h, sp = 6 + r() * 14, ph = r() * 6.28, sz = size * (.5 + r());
    const x = x0 + (bx + Math.sin(t * .3 + ph) * 30 + t * sp * .4) % w;
    const y = y0 + ((by - t * sp) % h + h) % h;
    const o = op * (.4 + .6 * Math.abs(Math.sin(t * .7 + ph)));
    s += `<circle cx="${f(x)}" cy="${f(y)}" r="${f(sz)}" fill="${col}" opacity="${o.toFixed(2)}"/>`;
  }
  return s;
}
// туман
function fog(t, x, y, w, h, seed = 3, n = 9, op = .55) {
  const r = rng(seed); let s = `<g opacity="${op}">`;
  for (let i = 0; i < n; i++) {
    const cx = x + r() * w, cy = y + r() * h, rx = 160 + r() * 260, ry = 90 + r() * 140, sp = 8 + r() * 14;
    const xx = x + ((cx - x + t * sp) % (w + 400)) - 200;
    s += `<ellipse cx="${f(xx)}" cy="${f(cy + Math.sin(t * .4 + i) * 12)}" rx="${f(rx)}" ry="${f(ry)}" fill="url(#fogBlob)"/>`;
  }
  return s + '</g>';
}
let gid = 0;
// луч фонаря: из (sx,sy) в (tx,ty), полуширина w у цели
function beam(sx, sy, tx, ty, w, op = 1) {
  const id = 'bm' + (gid++);
  const a = Math.atan2(ty - sy, tx - sx), nx = -Math.sin(a), ny = Math.cos(a);
  const len = Math.hypot(tx - sx, ty - sy) * 1.15;
  const ex = sx + (tx - sx) * 1.15, ey = sy + (ty - sy) * 1.15;
  return `<radialGradient id="${id}" gradientUnits="userSpaceOnUse" cx="${f(sx)}" cy="${f(sy)}" r="${f(len)}">
     <stop offset="0" stop-color="#fffbe6" stop-opacity="${(.55 * op).toFixed(2)}"/><stop offset=".8" stop-color="#fffbe6" stop-opacity="${(.22 * op).toFixed(2)}"/><stop offset="1" stop-color="#fffbe6" stop-opacity="0"/></radialGradient>
   <path d="M${f(sx + nx * 8)} ${f(sy + ny * 8)} L${f(ex + nx * w * 1.15)} ${f(ey + ny * w * 1.15)} L${f(ex - nx * w * 1.15)} ${f(ey - ny * w * 1.15)} L${f(sx - nx * 8)} ${f(sy - ny * 8)}Z" fill="url(#${id})" style="mix-blend-mode:screen"/>
   <ellipse cx="${f(tx)}" cy="${f(ty)}" rx="${f(w * 1.1)}" ry="${f(w * .55)}" fill="url(#spot)" opacity="${(.9 * op).toFixed(2)}" style="mix-blend-mode:screen"/>`;
}

// ---------- персонажи ----------
// манекен анфас. x,y = центр основания, h = рост в px. opts: coat, mask(герой), bag, mud, dim
function mannequin(x, y, h, o = {}) {
  const sw = (o.sw || SW) / h;
  const skin = o.skin || '#ecebe7', shade = '#c9c6c0';
  const coat = o.coat === false ? null : (o.coatCol || '#59627a');
  let s = `<g transform="translate(${f(x)} ${f(y)}) scale(${h.toFixed(2)})" stroke="${ST}" stroke-width="${sw.toFixed(4)}" stroke-linejoin="round">`;
  // подставка
  s += `<ellipse cx="0" cy="0" rx=".1" ry=".018" fill="#3a3f4b"/><rect x="-.008" y="-.09" width=".016" height=".09" fill="#8b909c"/>`;
  // ноги
  s += `<path d="M-.088 -.5 L-.072 -.09 L-.028 -.09 L-.004 -.43 L.004 -.43 L.028 -.09 L.072 -.09 L.088 -.5Z" fill="${skin}"/>`;
  if (o.mud) s += `<path d="M-.074 -.13 L-.028 -.13 L-.028 -.09 L-.072 -.09Z M.028 -.13 L.074 -.13 L.072 -.09 L.028 -.09Z" fill="#6b4a2b" stroke="none"/>`;
  // руки
  s += `<path d="M-.1 -.81 Q-.145 -.7 -.14 -.55 L-.115 -.55 Q-.118 -.68 -.085 -.76Z" fill="${skin}"/>`;
  s += `<path d="M.1 -.81 Q.145 -.7 .14 -.55 L.115 -.55 Q.118 -.68 .085 -.76Z" fill="${skin}"/>`;
  // торс
  s += `<path d="M-.105 -.82 Q0 -.845 .105 -.82 L.086 -.62 Q.07 -.56 .09 -.5 L-.09 -.5 Q-.07 -.56 -.086 -.62Z" fill="${skin}"/>`;
  s += `<path d="M.03 -.82 Q.08 -.83 .105 -.82 L.086 -.62 Q.07 -.56 .09 -.5 L.05 -.5Z" fill="${shade}" stroke="none" opacity=".6"/>`;
  if (coat) { // пальто-худи
    s += `<path d="M-.112 -.825 Q0 -.85 .112 -.825 L.12 -.56 L.1 -.33 L-.1 -.33 L-.12 -.56Z" fill="${coat}"/>`;
    s += `<path d="M-.108 -.82 Q-.15 -.7 -.148 -.57 L-.112 -.57 Q-.112 -.68 -.09 -.74Z" fill="${coat}"/>`;
    s += `<path d="M.108 -.82 Q.15 -.7 .148 -.57 L.112 -.57 Q.112 -.68 .09 -.74Z" fill="${coat}"/>`;
    s += `<path d="M0 -.83 L0 -.34" stroke-width="${(sw * .6).toFixed(4)}" fill="none" opacity=".6"/>`;
  }
  // шея и голова
  s += `<rect x="-.017" y="-.86" width=".034" height=".045" fill="${skin}"/>`;
  s += `<ellipse cx="0" cy="-.915" rx=".052" ry=".066" fill="${o.mask ? '#f7f6f2' : skin}"/>`;
  if (o.mask) s += `<ellipse cx="-.02" cy="-.92" rx=".011" ry=".006" fill="#1a1d24" stroke="none"/><ellipse cx=".02" cy="-.92" rx=".011" ry=".006" fill="#1a1d24" stroke="none"/>`;
  if (o.headTurn) s += `<ellipse cx="${(o.headTurn * .03).toFixed(3)}" cy="-.915" rx=".012" ry=".05" fill="#000" opacity=".12" stroke="none"/>`;
  s += '</g>';
  if (o.bag) s += backpack(x + h * .14, y, h * .2);
  if (o.dim) s = `<g opacity="${o.dim}">${s}</g>`;
  return s;
}
function backpack(x, y, h) { // рюкзак стоит на полу, x,y = низ-центр
  return `<g transform="translate(${f(x)} ${f(y)}) scale(${h.toFixed(2)})" stroke="${ST}" stroke-width="${(4 / h).toFixed(4)}" stroke-linejoin="round">
   <path d="M-.3 -.05 Q-.34 -.9 0 -.95 Q.34 -.9 .3 -.05 Q0 .02 -.3 -.05Z" fill="#ff7a1a"/>
   <path d="M-.2 -.42 L.2 -.42 L.18 -.12 L-.18 -.12Z" fill="#e3600a"/>
   <path d="M-.12 -.95 Q0 -1.12 .12 -.95" fill="none"/></g>`;
}
// герой. view: 'front' | 'back'; pose: 'stand' | 'hands' (ладони на стекле) | 'read'
function hero(x, y, h, view = 'front', pose = 'stand', k = 0) {
  const sw = SW / h;
  const hood = '#2c3e63', jeans = '#1f2a40', skin = '#e3c3a3';
  let s = `<g transform="translate(${f(x)} ${f(y)}) scale(${h.toFixed(2)})" stroke="${ST}" stroke-width="${sw.toFixed(4)}" stroke-linejoin="round" stroke-linecap="round">`;
  s += `<ellipse cx="0" cy="-.005" rx=".14" ry=".02" fill="#000" opacity=".35" stroke="none"/>`;
  s += `<path d="M-.085 -.46 L-.08 -.03 L-.02 -.03 L-.005 -.38 L.005 -.38 L.02 -.03 L.08 -.03 L.085 -.46Z" fill="${jeans}"/>`;
  s += `<path d="M-.095 -.035 L-.012 -.035 L-.012 0 L-.105 0Z M.012 -.035 L.095 -.035 L.105 0 L.012 0Z" fill="#e8e8e8"/>`;
  // руки
  if (pose === 'hands') {
    const kk = Math.sin(k * Math.PI) * .02; // стук
    s += `<path d="M-.11 -.76 L-.19 -.84 L-.2 -1.0" fill="none" stroke="${hood}" stroke-width="${(.05).toFixed(3)}"/>`;
    s += `<path d="M.11 -.76 L.19 -.84 L.2 -1.0" fill="none" stroke="${hood}" stroke-width="${(.05).toFixed(3)}"/>`;
    s += `<path d="M-.11 -.76 L-.19 -.84 L-.2 -1.0" fill="none" stroke="${ST}" stroke-width="${(.05 + sw * 2).toFixed(3)}" opacity="0"/>`;
    s += `<circle cx="-.2" cy="${(-1.03 - kk).toFixed(3)}" r=".034" fill="${skin}"/><circle cx=".2" cy="${(-1.03 + kk).toFixed(3)}" r=".034" fill="${skin}"/>`;
  } else if (pose === 'read') {
    s += `<path d="M-.11 -.78 Q-.16 -.62 -.06 -.58" fill="none" stroke="${hood}" stroke-width=".045"/>`;
    s += `<path d="M.11 -.78 Q.16 -.62 .06 -.58" fill="none" stroke="${hood}" stroke-width=".045"/>`;
  } else {
    s += `<path d="M-.115 -.78 Q-.16 -.62 -.15 -.48 L-.115 -.48 Q-.12 -.62 -.09 -.7Z" fill="${hood}"/>`;
    s += `<path d="M.115 -.78 Q.16 -.62 .15 -.48 L.115 -.48 Q.12 -.62 .09 -.7Z" fill="${hood}"/>`;
    s += `<circle cx="-.133" cy="-.465" r=".025" fill="${skin}"/><circle cx=".133" cy="-.465" r=".025" fill="${skin}"/>`;
  }
  // торс
  s += `<path d="M-.12 -.8 Q0 -.83 .12 -.8 L.11 -.47 Q0 -.45 -.11 -.47Z" fill="${hood}"/>`;
  if (view === 'front') {
    s += `<path d="M-.06 -.6 L.06 -.6 L.07 -.5 L-.07 -.5Z" fill="none" opacity=".5"/>`;
    s += `<path d="M-.08 -.8 L-.07 -.55 M.08 -.8 L.07 -.55" stroke="#ff7a1a" stroke-width=".02"/>`;
  }
  // голова
  s += `<rect x="-.02" y="-.85" width=".04" height=".04" fill="${skin}"/>`;
  s += `<circle cx="0" cy="-.9" r=".07" fill="${view === 'back' ? '#2a1d14' : skin}"/>`;
  if (view === 'front') {
    s += `<path d="M-.07 -.91 Q-.07 -.98 0 -.975 Q.07 -.98 .07 -.91 Q.04 -.94 0 -.935 Q-.04 -.94 -.07 -.91Z" fill="#2a1d14" stroke="none"/>`;
    s += `<circle cx="-.024" cy="-.895" r=".006" fill="#222" stroke="none"/><circle cx=".024" cy="-.895" r=".006" fill="#222" stroke="none"/>`;
  }
  if (pose === 'read') s += `<path d="M-.09 -.62 L0 -.6 L.09 -.62 L.09 -.52 L0 -.5 L-.09 -.52Z" fill="#c94f3c"/><path d="M0 -.6 L0 -.5" fill="none"/>`;
  if (view === 'back') { // рюкзак на спине
    s += `<path d="M-.1 -.78 Q-.11 -.47 -.095 -.44 Q0 -.42 .095 -.44 Q.11 -.47 .1 -.78 Q0 -.81 -.1 -.78Z" fill="#ff7a1a"/>`;
    s += `<path d="M-.065 -.6 L.065 -.6 L.06 -.48 L-.06 -.48Z" fill="#e3600a"/>`;
  }
  return s + '</g>';
}

// ---------- окружение ----------
function exitSign(x, y, sc = 1, on = 1) {
  return `<g transform="translate(${x} ${y}) scale(${sc})">
   <ellipse cx="0" cy="0" rx="150" ry="70" fill="url(#greenBlob)" opacity="${(.8 * on).toFixed(2)}"/>
   <rect x="-78" y="-26" width="156" height="52" rx="6" fill="${on > .5 ? '#2fd27a' : '#14402a'}" stroke="${ST}" stroke-width="4"/>
   <text x="0" y="12" text-anchor="middle" font-family="Inter" font-weight="900" font-size="32" fill="#06180e">ВЫХОД</text></g>`;
}
function room(floorY = 1250) { // стена + пол
  return rect(-400, -400, 1880, floorY + 400, 'url(#wallG)') + rect(-400, floorY, 1880, 1400, 'url(#floorG)') +
    `<line x1="-400" y1="${floorY}" x2="1480" y2="${floorY}" stroke="#2a3142" stroke-width="4"/>`;
}
function rackRail(y, x1, x2) {
  return `<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke="#7b8394" stroke-width="6"/>`;
}
function shelves(x, y, w, h, seed, lit = 1) { // книжные полки
  const r = rng(seed); const cols = ['#7a3b34', '#3c5a7a', '#6b6b3a', '#4d3d66', '#8a6a3a', '#2f5f55', '#9b4d3a', '#56607a'];
  let s = rect(x, y, w, h, '#2b2018', `stroke="${ST}" stroke-width="5"`);
  const rows = 5, rh = h / rows;
  for (let j = 0; j < rows; j++) {
    let bx = x + 10; const by = y + (j + 1) * rh - 8;
    while (bx < x + w - 20) {
      const bw = 14 + r() * 18, bh = rh * (.55 + r() * .35);
      if (bx + bw > x + w - 10) break;
      s += rect(bx, by - bh, bw, bh, cols[(r() * cols.length) | 0], `stroke="${ST}" stroke-width="2" opacity="${lit}"`);
      bx += bw + 2;
    }
    s += rect(x, by, w, 10, '#3a2c20');
  }
  return s;
}
function mallFloors(op = 1) { // атриум: три этажа в разрезе
  let s = rect(-400, -400, 1880, 2800, '#0c0f16');
  s += `<path d="M90 300 Q540 120 990 300" fill="none" stroke="#2b3550" stroke-width="6"/>`;
  for (let i = 0; i < 9; i++) s += `<line x1="${120 + i * 105}" y1="${270 - Math.sin(i / 8 * Math.PI) * 140}" x2="${120 + i * 105}" y2="330" stroke="#1f2840" stroke-width="3"/>`;
  const floors = [560, 930, 1300];
  floors.forEach((fy, k) => {
    // витрины
    for (let i = 0; i < 4; i++) {
      const x = 60 + i * 250;
      s += rect(x, fy - 250, 210, 230, '#121722', `stroke="#2a3348" stroke-width="4"`);
      s += rect(x + 20, fy - 236, 170, 26, k === 2 && i === 1 ? '#2e2a1c' : '#1b2131');
      s += rect(x + 14, fy - 196, 182, 170, '#0e121b');
    }
    s += rect(-400, fy, 1880, 26, '#2a3142', `stroke="${ST}" stroke-width="4"`);
    s += rect(-400, fy - 60, 1880, 60, 'rgba(120,160,210,.07)');
    s += `<line x1="-400" y1="${fy - 60}" x2="1480" y2="${fy - 60}" stroke="#56627c" stroke-width="5"/>`;
    for (let i = -4; i < 16; i++) s += `<line x1="${i * 90}" y1="${fy - 60}" x2="${i * 90}" y2="${fy}" stroke="#3a4560" stroke-width="3"/>`;
  });
  // эскалаторы
  s += `<path d="M300 1300 L640 930" stroke="#3b4660" stroke-width="40"/><path d="M300 1300 L640 930" stroke="#596a8c" stroke-width="6"/>`;
  s += `<path d="M440 930 L780 560" stroke="#3b4660" stroke-width="40"/><path d="M440 930 L780 560" stroke="#596a8c" stroke-width="6"/>`;
  s += rect(-400, 1326, 1880, 1000, '#0a0c12');
  return `<g opacity="${op}">${s}</g>`;
}
function glassDoors(t, closeK, frost = 0) { // фасад со стеклянными дверями, туман и парковка за ними
  let s = rect(-400, -400, 1880, 2800, '#0d1018');
  // за стеклом: туман и парковка
  let out = rect(150, 520, 780, 900, '#9aa6b4');
  out += rect(150, 1080, 780, 340, '#7f8a98');
  for (let i = 0; i < 6; i++) out += `<line x1="${200 + i * 140}" y1="1100" x2="${150 + i * 170}" y2="1420" stroke="#e8edf2" stroke-width="6" opacity=".55"/>`;
  out += `<line x1="760" y1="1080" x2="760" y2="760" stroke="#56606d" stroke-width="10"/><path d="M760 760 L820 760" stroke="#56606d" stroke-width="10"/>`;
  out += fog(t, 150, 520, 780, 900, 7, 12, .95) + fog(t * 1.3, 150, 700, 780, 700, 11, 8, .8);
  s += `<clipPath id="gclip"><rect x="150" y="520" width="780" height="900"/></clipPath><g clip-path="url(#gclip)">${out}</g>`;
  // створки
  const gap = lerp(170, 0, closeK);
  const pane = (x, w) => rect(x, 520, w, 900, 'rgba(180,210,240,.14)', `stroke="#c7cfdb" stroke-width="10"`) +
    `<line x1="${x + 40}" y1="560" x2="${x + w * .55}" y2="900" stroke="#fff" stroke-width="6" opacity=".18"/>` +
    rect(x + w / 2 - 70, 960, 140, 18, '#c7cfdb', 'rx="9"');
  s += pane(150 - gap, 390) + pane(540 + gap, 390);
  s += rect(110, 480, 860, 40, '#2a3142', `stroke="${ST}" stroke-width="5"`) + rect(110, 1420, 860, 40, '#2a3142', `stroke="${ST}" stroke-width="5"`);
  s += rect(80, 480, 40, 980, '#2a3142') + rect(960, 480, 40, 980, '#2a3142');
  s += rect(-400, 1460, 1880, 900, 'url(#floorG)');
  s += exitSign(540, 410, 1.1);
  return s;
}

// ---------- сцены ----------
const scenes = [];
const add = (t0, t1, draw, fade = .35) => scenes.push({ t0, t1, draw, fade });

// 0. Хук: ряд манекенов, луч скользит
add(0, S(1) - .25, t => {
  const T = t;
  let s = room(1260);
  s += rackRail(560, -200, 1280);
  const xs = [80, 230, 385, 540, 700, 855, 1005];
  const bx = lerp(-300, 1350, eio(seg(T, .4, 7.6)));
  let m = '';
  xs.forEach((x, i) => {
    const lit = clamp(1 - Math.abs(bx - x) / 260);
    m += mannequin(x, 1250, 640, { mask: i === 3, bag: i === 3, dim: (.35 + .65 * lit).toFixed(2) });
  });
  s += m;
  s += beam(-260, 220, bx, 1330, 170);
  s += dust(T, 26, 5, -100, 300, 1300, 1100, '#fff', .35, 3);
  const k = eio(seg(T, 0, 8));
  return cam(s, lerp(1.0, 1.1, k), 540, lerp(980, 900, k));
}, .25);

// 1. Название
add(S(1) - .25, P(2, 0) - .05, t => {
  const T = t - S(1);
  let s = mallFloors(.8) + exitSign(860, 640, .8) + dust(t, 60, 9, 0, 0, 1080, 1920, '#cfe0ff', .45, 2.6);
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#000" opacity=".45"/>`;
  return cam(s, lerp(1.12, 1.04, eout(seg(T, 0, 5))), 540, 960);
}, .4);

// 2. Книжный, 22:00, свет мигает
add(P(2, 0) - .05, P(3, 1), t => {
  const T = t - S(2);
  let s = room(1300);
  s += shelves(-60, 560, 420, 700, 21) + shelves(720, 560, 420, 700, 22);
  s += rect(380, 600, 320, 40, '#1b2131', `stroke="#2a3348" stroke-width="4"`) + txt(540, 632, 'КНИГИ', 30, '#cfd6e4', 'letter-spacing="8"');
  // часы 22:00
  s += rect(445, 690, 190, 76, '#07090d', `rx="12" stroke="#3a4560" stroke-width="4"`) + mono(540, 744, '22:00', 52, '#ff5a4a', 'middle');
  s += hero(540, 1290, 560, 'front', 'read');
  s += `<ellipse cx="540" cy="520" rx="420" ry="200" fill="url(#warmBlob)" opacity=".35"/>`;
  return cam(s, lerp(1.0, 1.07, seg(T, 0, 5.5)), 540, 960);
});

// 3. Двери закрываются → стекло → ладони на стекле
add(P(3, 1), S(6) - .1, t => {
  const tc = Wt(3, 'ЗАКРЫЛИСЬ');
  const closeK = eout(seg(t, tc - .35, tc + .05));
  let s = glassDoors(t, closeK);
  const handsOn = t > S(5) - .2;
  if (handsOn) {
    // стук: три удара по «Я стучал до утра»
    const kn = [P(5, 0) + .1, P(5, 0) + .55, P(5, 0) + 1.0];
    let k = 0; kn.forEach(q => { const d = t - q; if (d > 0 && d < .18) k = d / .18; });
    s += hero(540, 1530, 760, 'back', 'hands', k);
  }
  // камера: панорама по дверям, потом к стеклу
  let sc = 1.0, cx = 540, cy = 960;
  if (t < S(4)) { sc = lerp(1.0, 1.04, seg(t, P(3, 1), S(4))); }
  else if (t < S(5)) { const k = eio(seg(t, S(4), E(4))); sc = lerp(1.04, 1.32, k); cx = lerp(560, 600, k); cy = lerp(960, 1030, k); }
  else { const k = eio(seg(t, S(5) - .2, S(6))); sc = lerp(1.1, 1.18, k); cy = lerp(1000, 980, k); }
  return cam(s, sc, cx, cy);
});

// 4. Разрез ТЦ: что у меня есть
const DH = { x: 90, y: 520, w: 900, fh: 195 };
add(S(6) - .1, S(7) - .05, t => {
  const T = t - S(6);
  let s = rect(-400, -400, 1880, 2800, '#0d1018');
  const names = [['ФУДКОРТ', 'КИНО', 'ИГРУШКИ'], ['АПТЕКА', 'ОДЕЖДА', 'ОБУВЬ'], ['КНИЖНЫЙ', 'СПОРТТОВАРЫ', 'ЭЛЕКТРОНИКА']];
  const hi = { 'ФУДКОРТ': Wt(6, 'ФУДКОРТ'), 'АПТЕКА': Wt(6, 'АПТЕКА'), 'СПОРТТОВАРЫ': Wt(6, 'СПОРТТОВАРЫ') };
  s += `<path d="M${DH.x - 20} ${DH.y} L540 ${DH.y - 130} L${DH.x + DH.w + 20} ${DH.y}Z" fill="#161b26" stroke="#3a4560" stroke-width="5"/>`;
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) {
    const x = DH.x + c * DH.w / 3, y = DH.y + r * DH.fh, w = DH.w / 3, h = DH.fh;
    const n = names[r][c]; const th = hi[n];
    const k = th ? seg(t, th - .05, th + .25) : 0;
    s += rect(x, y, w, h, k > 0 ? `rgba(255,210,63,${(.2 + .35 * k).toFixed(2)})` : '#141925', `stroke="#3a4560" stroke-width="5"`);
    s += txt(x + w / 2, y + h - 26, n, 30, k > 0 ? '#ffd23f' : '#7e889c', 'letter-spacing="1"');
    // мебель-иконки
    if (n === 'ФУДКОРТ') s += rect(x + 30, y + 40, 60, 100, '#ffb347', `rx="8" stroke="${ST}" stroke-width="4"`) + `<ellipse cx="${x + 60}" cy="${y + 90}" rx="90" ry="70" fill="url(#warmBlob)"/>` + rect(x + 130, y + 110, 120, 12, '#5a6273') + rect(x + 150, y + 122, 10, 30, '#5a6273') + rect(x + 220, y + 122, 10, 30, '#5a6273');
    if (n === 'АПТЕКА') s += `<path d="M${x + w / 2 - 14} ${y + 50}h28v28h28v28h-28v28h-28v-28h-28v-28h28z" fill="#3ddc84" stroke="${ST}" stroke-width="4"/>`;
    if (n === 'СПОРТТОВАРЫ') s += `<circle cx="${x + 90}" cy="${y + 100}" r="34" fill="#e8742a" stroke="${ST}" stroke-width="4"/><path d="M${x + 56} ${y + 100}h68M${x + 90} ${y + 66}v68" stroke="${ST}" stroke-width="3"/>` + rect(x + 160, y + 60, 90, 16, '#9aa6bd') + rect(x + 160, y + 90, 90, 16, '#9aa6bd');
    if (n === 'ЭЛЕКТРОНИКА') for (let i = 0; i < 9; i++) s += `<line x1="${x + 10}" y1="${y + 20 + i * 18}" x2="${x + w - 10}" y2="${y + 20 + i * 18}" stroke="#56627c" stroke-width="4"/>`;
    if (n === 'ОДЕЖДА') for (let i = 0; i < 3; i++) s += mannequin(x + 70 + i * 80, y + h - 50, 130, { sw: 2 });
    if (n === 'КНИЖНЫЙ') s += hero(x + w / 2, y + h - 50, 130, 'front');
  }
  // этажи подпись
  ['3', '2', '1'].forEach((n, r) => { s += mono(DH.x - 40, DH.y + r * DH.fh + 120, n, 40, '#56627c', 'middle'); });
  // карточки инвентаря
  const cards = [['🍔', 'ЕДА', Wt(6, 'ФУДКОРТ')], ['💊', 'АПТЕКА', Wt(6, 'АПТЕКА')], ['🏀', 'СПОРТ', Wt(6, 'СПОРТТОВАРЫ')]];
  cards.forEach(([ic, lb, tt], i) => {
    const k = popScale(t, tt + .1); if (k <= 0) return;
    const cx = 250 + i * 290, cy = 1210;
    s += `<g transform="translate(${cx} ${cy}) scale(${(k * .82).toFixed(3)})">${rect(-120, -80, 240, 160, '#e9edf5', `rx="20" stroke="${ST}" stroke-width="5"`)}
      <text x="0" y="8" text-anchor="middle" font-family="Noto Color Emoji" font-size="70">${ic}</text>${txt(0, 62, lb, 30, '#0d1018')}</g>`;
  });
  return cam(s, lerp(1.0, 1.04, seg(T, 0, 6)), 540, 880);
});

// 5. Телефон: 40 %, нет связи
add(S(7) - .05, S(8) - .3, t => {
  const T = t - S(7);
  let s = rect(-400, -400, 1880, 2800, '#0d1018') + dust(t, 20, 4, 0, 0, 1080, 1920, '#fff', .2, 3);
  const y0 = lerp(1500, 0, eout(seg(T, 0, .5)));
  let p = '';
  p += `<path d="M330 1500 Q300 1200 380 1080 L700 1080 Q780 1200 750 1500Z" fill="#e3c3a3" stroke="${ST}" stroke-width="5"/>`;
  p += rect(370, 520, 340, 680, '#0b0d12', `rx="44" stroke="#3a4560" stroke-width="6"`);
  p += rect(392, 560, 296, 600, '#121a2a', 'rx="26"');
  p += mono(420, 610, '02:14', 26, '#9aa6bd') ;
  // батарея
  const bk = 1 - .6 * seg(t, Wt(7, 'СОРОК') - .2, Wt(7, 'СОРОК') + .6);
  p += rect(440, 700, 200, 96, 'none', `rx="12" stroke="#fff" stroke-width="7"`) + rect(640, 728, 14, 40, '#fff', 'rx="4"');
  p += rect(452, 712, 176 * bk, 72, bk < .5 ? '#ffd23f' : '#3ddc84', 'rx="6"');
  p += txt(540, 880, Math.round(bk * 100) + '%', 74, '#fff');
  // сеть
  const nk = seg(t, Wt(7, 'СВЯЗИ') - .1, Wt(7, 'СВЯЗИ') + .3);
  for (let i = 0; i < 4; i++) p += rect(470 + i * 36, 1030 - i * 26, 24, 30 + i * 26, '#56627c', 'rx="4"');
  if (nk > 0) p += `<path d="M450 940 L640 1070 M640 940 L450 1070" stroke="#ff4040" stroke-width="12" stroke-linecap="round" opacity="${nk.toFixed(2)}"/>`;
  p += txt(540, 1120, nk > 0 ? 'НЕТ СЕТИ' : 'ПОИСК…', 34, nk > 0 ? '#ff4040' : '#9aa6bd');
  s += `<g transform="translate(0 ${f(y0)}) rotate(${f(Math.sin(t * 1.3) * 1.2)} 540 900)">${p}</g>`;
  return cam(s, lerp(1.0, 1.06, seg(T, 0, 4)), 540, 900);
});

// 6. День 2: решётка электроники
add(S(8) - .3, S(9) - .05, t => {
  const T = t - S(8);
  let s = room(1340);
  s += rect(90, 520, 900, 70, '#1b2131', `stroke="#3a4560" stroke-width="5"`) + txt(540, 572, 'ЭЛЕКТРОНИКА', 44, '#7fb0ff', 'letter-spacing="6"');
  s += rect(120, 590, 840, 750, '#0a0d14');
  for (let i = 0; i < 5; i++) s += rect(170 + i * 160, 1000, 120, 160, '#1d2433', `stroke="#2a3348" stroke-width="4"`) + rect(185 + i * 160, 1020, 90, 60, '#25324a');
  for (let i = 0; i < 32; i++) s += `<line x1="120" y1="${600 + i * 23}" x2="960" y2="${600 + i * 23}" stroke="#7b8394" stroke-width="7"/>`;
  for (let i = 0; i < 8; i++) s += `<line x1="${150 + i * 112}" y1="590" x2="${150 + i * 112}" y2="1340" stroke="#5c6474" stroke-width="5"/>`;
  [[150, 1320], [930, 1320], [150, 610], [930, 610]].forEach(([x, y]) => s += `<circle cx="${x}" cy="${y}" r="16" fill="#c0c6d2" stroke="${ST}" stroke-width="4"/>`);
  s += hero(420, 1340, 300, 'back') ;
  return cam(s, lerp(1.0, 1.08, seg(T, 0, 5.5)), 540, 980);
});

// схема (общий фон)
function blueprint(t, title) {
  let s = rect(-400, -400, 1880, 2800, '#123a6b') + rect(-400, -400, 1880, 2800, 'url(#bpgrid)') + rect(-400, -400, 1880, 2800, 'url(#bpgrid2)');
  s += rect(60, 1150, 960, 4, '#5b92d6', 'opacity=".0"');
  if (title) s += mono(80, 640, title, 30, '#a9cbf5') + `<line x1="80" y1="655" x2="1000" y2="655" stroke="#a9cbf5" stroke-width="2"/>`;
  return s;
}
// 7. Схема: четыре болта
add(S(9) - .05, P(10, 1) - .1, t => {
  let s = blueprint(t, 'СХЕМА №1 · РЕШЁТКА ЭЛЕКТРОНИКИ');
  const k0 = seg(t, S(9), S(9) + .8);
  // решётка контурами
  const gx = 160, gy = 700, gw = 600, gh = 420;
  s += `<rect x="${gx}" y="${gy}" width="${gw}" height="${gh}" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="${f((gw + gh) * 2 * k0)} 4000"/>`;
  for (let i = 1; i < 10; i++) s += pline(gx, gy + i * gh / 10, gx + gw, gy + i * gh / 10, seg(t, S(9) + .2 + i * .04, S(9) + .9 + i * .04), '#fff', 2.5);
  const tb = Wt(9, 'ЧЕТЫРЕ');
  [[gx, gy], [gx + gw, gy], [gx, gy + gh], [gx + gw, gy + gh]].forEach(([x, y], i) => {
    s += `<circle cx="${x}" cy="${y}" r="12" fill="#fff"/>`;
    s += pcircle(x, y, 46, seg(t, tb + i * .18, tb + i * .18 + .35));
  });
  s += mono(gx + gw / 2, gy - 30, typeText('4 × БОЛТ M10', seg(t, tb, tb + .6)), 30, '#ffd23f', 'middle');
  // набор ключей
  const tk = Wt(9, 'НАБОР');
  const kk = seg(t, tk - .2, tk + .4);
  if (kk > 0) {
    let w = `<g opacity="${kk.toFixed(2)}" transform="translate(800 1270)">`;
    w += rect(-110, -60, 220, 120, 'none', `rx="14" stroke="#fff" stroke-width="5"`);
    for (let i = 0; i < 5; i++) w += `<path d="M${-80 + i * 40} -40 v70" stroke="#fff" stroke-width="${6 + i * 2}" stroke-linecap="round"/><circle cx="${-80 + i * 40}" cy="-42" r="${8 + i * 1.5}" fill="none" stroke="#fff" stroke-width="4"/>`;
    w += '</g>' + mono(800, 1370, 'НАБОР КЛЮЧЕЙ', 28, '#fff', 'middle');
    s += w + parrow(700, 1240, gx + gw - 10, gy + gh + 40, seg(t, tk + .3, tk + .9));
  }
  // шаги
  const steps = ['1. ОТКРУТИТЬ БОЛТЫ', '2. ПОДНЯТЬ РЕШЁТКУ', '3. ВНУТРИ'];
  const t10 = S(10);
  steps.forEach((st, i) => { const a = t10 - .6 + i * .5; s += mono(120, 1250 + i * 52, typeText(st, seg(t, a, a + .5)), 32, i === 2 ? '#3ddc84' : '#fff'); });
  // решётка уезжает вверх на «и я внутри»
  return cam(s, lerp(1.0, 1.04, seg(t, S(9), S(10) + 1.5)), 540, 960);
}, .3);

// 8. Пауэрбанки
add(P(10, 1) - .1, S(11) - .3, t => {
  const t0 = P(10, 1);
  let s = room(1330);
  s += rect(-400, 520, 1880, 30, '#1b2131');
  const r = rng(77); let items = [];
  for (let i = 0; i < 30; i++) {
    const row = Math.floor(i / 6), col = i % 6;
    items.push([150 + col * 150 + (row % 2) * 70 + (r() - .5) * 30, 1310 - row * 62 - (r() * 10), (r() - .5) * 14, i]);
  }
  items.forEach(([x, y, rot, i]) => {
    const ti = t0 + .05 + i * .045; const d = t - ti; if (d < 0) return;
    const yy = y - Math.max(0, 500 * (1 - eout(clamp(d / .35))));
    s += `<g transform="translate(${f(x)} ${f(yy)}) rotate(${f(rot)})">${rect(-62, -28, 124, 56, '#2b3242', `rx="12" stroke="${ST}" stroke-width="4"`)}
      ${rect(-48, -8, 60, 14, '#3ddc84', 'rx="4"')}<circle cx="34" cy="0" r="6" fill="#3ddc84"/></g>`;
  });
  const n = Math.min(30, Math.max(0, Math.floor((t - t0) / .045)));
  if (n > 0) s += txt(540, 820, '×' + n, 150, '#3ddc84', `stroke="${ST}" stroke-width="10" paint-order="stroke"`);
  s += hero(940, 1330, 360, 'front');
  return cam(s, lerp(1.06, 1.0, eout(seg(t, t0, t0 + 3))), 540, 980);
});

// 9. День 3: вид сверху, обход
const SHOPS = [ // x,y,w,h,name
  [100, 560, 210, 220, 'КНИЖНЫЙ'], [330, 560, 200, 220, 'АПТЕКА'], [550, 560, 200, 220, 'ОБУВЬ'], [770, 560, 210, 220, 'КИНО'],
  [100, 1080, 210, 220, 'СПОРТ'], [330, 1080, 200, 220, 'ЭЛЕКТРОНИКА'], [550, 1080, 200, 220, 'ИГРУШКИ'], [770, 1080, 210, 220, 'ОДЕЖДА'],
];
const ROUTE = [0, 1, 2, 3, 4, 5, 6]; // ОДЕЖДА(7) — следующий
add(S(11) - .3, S(13) - .05, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0e15');
  s += rect(80, 540, 920, 780, '#141926', `stroke="#3a4560" stroke-width="6"`);
  s += rect(330, 830, 420, 200, '#07090d', `stroke="#56627c" stroke-width="5"`);
  for (let i = 0; i < 12; i++) s += `<line x1="${400 + i * 24}" y1="850" x2="${400 + i * 24}" y2="1010" stroke="#2a3348" stroke-width="5"/>`;
  // обход: начинается на «Кто-то шёл»
  const ta = P(12, 0), tb = S(13) - .2;
  const k = seg(t, ta, tb) * ROUTE.length;
  const cur = Math.min(ROUTE.length - 1, Math.floor(k));
  SHOPS.forEach(([x, y, w, h, n], i) => {
    const vi = ROUTE.indexOf(i);
    let fill = '#121722';
    if (vi >= 0 && vi < cur) fill = '#1a2030';
    s += rect(x, y, w, h, fill, `stroke="#3a4560" stroke-width="5"`);
    s += txt(x + w / 2, y + (y < 900 ? 40 : h - 18), n, n.length > 9 ? 22 : 28, i === 7 ? '#ffd23f' : '#7e889c');
  });
  // «Я» в одежде
  const hx = 875, hy = 1190;
  s += `<circle cx="${hx}" cy="${hy}" r="${f(22 + Math.sin(t * 6) * 3)}" fill="#ff7a1a" stroke="${ST}" stroke-width="5"/>` + txt(hx, hy - 40, 'Я', 34, '#ff7a1a');
  for (let i = 0; i < 4; i++) s += `<circle cx="${800 + i * 46}" cy="1250" r="13" fill="#ecebe7" stroke="${ST}" stroke-width="3"/>`;
  // часы
  s += rect(410, 885, 260, 90, '#07090d', `rx="14" stroke="#3a4560" stroke-width="4"`) + mono(540, 950, '02:00', 60, '#ff5a4a', 'middle');
  if (t > ta - .2) {
    // позиция обходчика: коридор между рядами y≈930 (верх 800, низ 1060)
    const kk = clamp(k, 0, ROUTE.length - .001), si = ROUTE[Math.floor(kk)], fr = kk - Math.floor(kk);
    const [x, y, w, h] = SHOPS[si];
    const gx = x + w / 2 + lerp(-40, 40, fr), gy = y < 900 ? 815 : 1050;
    const tx = x + w / 2, ty = y + h / 2;
    const pulse = Math.sin(fr * Math.PI);
    s += beam(gx, gy, tx + Math.sin(fr * 6) * 30, ty, 80, .4 + .6 * pulse);
    s += `<circle cx="${f(gx)}" cy="${f(gy)}" r="9" fill="#fffbe6" opacity=".7"/>`;
    // шаги
    for (let j = 0; j < 8; j++) { const fx = gx - 30 - j * 26, fy = gy + (j % 2 ? 6 : -6); if (fx > 90) s += `<ellipse cx="${f(fx)}" cy="${f(fy)}" rx="7" ry="4" fill="#fff" opacity="${(.3 - j * .035).toFixed(2)}"/>`; }
  } else {
    // ключи звенят где-то внизу: волны
    const wk = (t * 1.6) % 1;
    s += `<circle cx="200" cy="930" r="${f(20 + wk * 120)}" fill="none" stroke="#ffd23f" stroke-width="4" opacity="${(1 - wk).toFixed(2)}"/>`;
    s += txt(200, 945, '🔑', 40, '#fff', 'font-family="Noto Color Emoji"');
  }
  const T = t - S(11);
  return cam(s, lerp(1.0, 1.03, seg(T, 0, 11)), 540, 950);
}, .3);

// 10. Герой в магазине одежды, свет подбирается
add(S(13) - .05, S(14) - .1, t => {
  const T = t - S(13);
  let s = room(1300);
  s += rackRail(560, -200, 1280);
  [130, 300, 780, 950].forEach(x => s += mannequin(x, 1290, 600, {}));
  s += hero(540, 1300, 560, 'front');
  const k = seg(T, 0, E(13) - S(13));
  s += beam(-320, 1100, lerp(-100, 120, k), 1360, lerp(120, 200, k), .9);
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#000" opacity="${f(.15 + .15 * Math.sin(T * 9) ** 2)}"/>`;
  return cam(s, lerp(1.0, 1.14, eio(k)), 540, 1000);
});

// 11. Схема: стать манекеном
add(S(14) - .1, S(15) - .15, t => {
  let s = blueprint(t, 'СХЕМА №2 · МАСКИРОВКА');
  const a = seg(t, S(14), S(14) + .9);
  const ln = (svg) => `<g opacity="${a.toFixed(2)}" fill="none">${svg}</g>`;
  // два контура: манекен и я
  const fig = (x, mask) => `<g transform="translate(${x} 1210) scale(520)" stroke="#fff" stroke-width="${(5 / 520).toFixed(4)}" fill="none">
     <ellipse cx="0" cy="-.915" rx=".052" ry=".066"/><path d="M-.112 -.825 Q0 -.85 .112 -.825 L.12 -.56 L.1 -.33 L-.1 -.33 L-.12 -.56Z"/>
     <path d="M-.108 -.82 Q-.15 -.7 -.148 -.57 M.108 -.82 Q.15 -.7 .148 -.57"/><path d="M-.088 -.33 L-.072 -.09 M.088 -.33 L.072 -.09 M-.01 -.33 L-.02 -.09 M.01 -.33 L.02 -.09"/>
     ${mask ? '' : '<line x1="0" y1="-.09" x2="0" y2="0"/><ellipse cx="0" cy="0" rx=".1" ry=".018"/>'}</g>`;
  s += ln(fig(300, false) + fig(760, true));
  s += mono(300, 1290, 'МАНЕКЕН', 30, '#a9cbf5', 'middle') + mono(760, 1290, 'Я', 30, '#ff9a4a', 'middle');
  s += backpack(860, 1210, 90);
  const t1 = Wt(14, 'НАДЕЛ'), t2 = Wt(14, 'МАСКУ'), t3 = Wt(14, 'ВСТАЛ');
  s += parrow(400, 940, 680, 940, seg(t, t1, t1 + .6)) + mono(540, 910, typeText('ТА ЖЕ ОДЕЖДА', seg(t, t1 + .2, t1 + .8)), 30, '#fff', 'middle');
  const mk = popScale(t, t2);
  if (mk > 0) s += `<g transform="translate(760 734) scale(${mk.toFixed(3)})"><ellipse cx="0" cy="0" rx="30" ry="38" fill="#f7f6f2" stroke="${ST}" stroke-width="4"/><ellipse cx="-11" cy="-4" rx="6" ry="3.5" fill="#1a1d24"/><ellipse cx="11" cy="-4" rx="6" ry="3.5" fill="#1a1d24"/></g>`;
  s += parrow(900, 680, 800, 725, seg(t, t2 + .1, t2 + .5)) + mono(905, 660, typeText('МАСКА', seg(t, t2 + .2, t2 + .6)), 30, '#ffd23f', 'middle');
  const k3 = seg(t, t3, t3 + .4);
  if (k3 > 0) {
    s += `<g opacity="${k3.toFixed(2)}"><rect x="610" y="1320" width="300" height="70" rx="10" fill="none" stroke="#ff4040" stroke-width="5"/>` + mono(760, 1368, 'НЕ ДВИГАТЬСЯ', 32, '#ff4040', 'middle') + '</g>';
  }
  return cam(s, lerp(1.0, 1.04, seg(t, S(14), S(15))), 540, 980);
}, .3);

// 12. Луч на маске. Секунда. Две. Считает. Уходит.
add(S(15) - .15, S(16) - .3, t => {
  const T = t - S(15);
  let s = room(1340);
  s += rackRail(500, -200, 1280);
  const xs = [140, 340, 540, 740, 940];
  xs.forEach((x, i) => s += mannequin(x, 1330, 780, { mask: i === 2, bag: i === 2 }));
  // луч: на маску → держится → «считал» (прыгает по головам) → уходит
  const tOn = P(15, 0), tCount = P(15, 3), tGo = P(15, 4);
  const headY = 1330 - .915 * 780;
  let bx, by = headY + 10, op = 1, w = 120;
  if (t < tOn) { bx = lerp(-200, 540, eout(seg(t, S(15) - .15, tOn + .2))); }
  else if (t < tCount) { bx = 540 + Math.sin(t * 2) * 4; }
  else if (t < tGo) { const k = seg(t, tCount, tGo); const idx = Math.min(4, Math.floor(k * 5)); bx = lerp(xs[Math.max(0, idx - 1)], xs[idx], eout(clamp(k * 5 - idx))); }
  else { bx = lerp(940, 1500, eio(seg(t, tGo, tGo + 1.2))); op = 1 - seg(t, tGo + .6, tGo + 1.4); }
  s += beam(lerp(-200, 1300, .5), -300, bx, by, w, op);
  const k = eio(seg(t, tOn, tCount));
  const k2 = eio(seg(t, tCount, tGo));
  return cam(s, lerp(1.0, 1.7, k) - .5 * k2, 540, lerp(960, headY + 80, k) + (1 - k) * 0 + k2 * 120);
});

// 13. День 5: схема сигнализации на эскалаторе
function escalatorSide(stroke = '#fff', fillSteps = false) {
  let s = '';
  s += `<line x1="40" y1="1180" x2="300" y2="1180" stroke="${stroke}" stroke-width="5"/><line x1="800" y1="700" x2="1040" y2="700" stroke="${stroke}" stroke-width="5"/>`;
  s += `<path d="M300 1180 L800 700" stroke="${stroke}" stroke-width="5"/>`;
  // ступени
  let d = 'M300 1180'; for (let i = 0; i < 12; i++) { const x = 300 + i * 41.7, y = 1180 - i * 40; d += ` L${f(x)} ${f(y - 40)} L${f(x + 41.7)} ${f(y - 40)}`; }
  s += `<path d="${d}" fill="none" stroke="${stroke}" stroke-width="3" opacity=".8"/>`;
  // поручень
  s += `<path d="M250 1060 L300 1060 L800 580 L850 580" fill="none" stroke="${stroke}" stroke-width="6"/>`;
  s += `<path d="M300 1060 L300 1180 M800 580 L800 700" stroke="${stroke}" stroke-width="3" stroke-dasharray="8 8"/>`;
  return s;
}
function bells(t, k, swing = 0, col = '#fff') { // леска + вешалки + колокольчики поперёк эскалатора
  let s = '';
  const x1 = 470, y1 = 880, x2 = 640, y2 = 880;
  s += pline(x1 - 120, y1, x2 + 120, y2, k, col, 3);
  s += `<circle cx="${x1 - 120}" cy="${y1}" r="7" fill="${col}"/>`;
  if (k > .98) s += `<circle cx="${x2 + 120}" cy="${y2}" r="7" fill="${col}"/>`;
  const items = [[390, 'h'], [440, 'b'], [490, 'h'], [540, 'b'], [590, 'h'], [640, 'b'], [690, 'h']];
  items.forEach(([x, ty], i) => {
    const vis = seg(k, (x - 350) / 460 - .05, (x - 350) / 460 + .1); if (vis <= 0) return;
    const ang = Math.sin(t * 11 + i * 1.7) * swing * 22;
    if (ty === 'h') s += `<g transform="rotate(${f(ang)} ${x} ${y1})" opacity="${vis.toFixed(2)}"><path d="M${x} ${y1} q8 -10 0 -16 M${x} ${y1} L${x - 34} ${y1 + 34} L${x + 34} ${y1 + 34}Z" fill="none" stroke="${col}" stroke-width="4"/></g>`;
    else s += `<g transform="rotate(${f(ang)} ${x} ${y1})" opacity="${vis.toFixed(2)}"><line x1="${x}" y1="${y1}" x2="${x}" y2="${y1 + 24}" stroke="${col}" stroke-width="3"/><path d="M${x - 20} ${y1 + 64} Q${x - 18} ${y1 + 24} ${x} ${y1 + 24} Q${x + 18} ${y1 + 24} ${x + 20} ${y1 + 64}Z" fill="#ffd23f" stroke="${ST}" stroke-width="3"/><circle cx="${x}" cy="${y1 + 68}" r="6" fill="#ffd23f" stroke="${ST}" stroke-width="2"/></g>`;
  });
  return s;
}
add(S(16) - .3, S(19) - .3, t => {
  let s = blueprint(t, 'СХЕМА №3 · СИГНАЛИЗАЦИЯ');
  const a = seg(t, S(16), S(16) + 1);
  s += `<g opacity="${a.toFixed(2)}">${escalatorSide()}</g>`;
  s += mono(130, 1225, '1 ЭТАЖ', 26, '#a9cbf5') + mono(860, 745, '2 ЭТАЖ', 26, '#a9cbf5');
  const tl = Wt(17, 'НАТЯНУЛ');
  const lk = seg(t, tl, tl + 1.2);
  s += bells(t, lk, 0);
  s += mono(350, 840, typeText('ЛЕСКА', seg(t, tl + .4, tl + .9)), 28, '#fff');
  const tv = Wt(17, 'ВЕШАЛКИ');
  s += mono(540, 1030, typeText('ВЕШАЛКИ + КОЛОКОЛЬЧИКИ', seg(t, tv, tv + 1)), 28, '#ffd23f', 'middle');
  // «если кто-то поднимется — услышу»
  const te = S(18);
  const pk = seg(t, te, te + 1.4);
  if (pk > 0) {
    // фигура снизу
    s += `<g opacity="${clamp(pk * 3).toFixed(2)}" transform="translate(250 1180) scale(200)" fill="none" stroke="#ff9a4a" stroke-width="${(5 / 200).toFixed(4)}"><circle cx="0" cy="-.9" r=".07"/><path d="M0 -.83 L0 -.45 M0 -.45 L-.08 0 M0 -.45 L.08 0 M0 -.75 L-.12 -.55 M0 -.75 L.12 -.55"/></g>`;
    s += parrow(300, 1060, 520, 860, pk, '#ff9a4a');
  }
  const tz = Wt(18, 'УСЛЫШУ');
  const zk = seg(t, tz - .1, tz + .5);
  if (zk > 0) {
    s += bells(t, 1, zk * (1 - seg(t, tz + 1.2, tz + 2)), '#fff');
    for (let i = 0; i < 3; i++) s += `<path d="M${700 + i * 28} ${830 - i * 10} q30 50 0 100" fill="none" stroke="#3ddc84" stroke-width="5" opacity="${zk.toFixed(2)}"/>`;
    s += mono(860, 960, 'ЗВОН!', 40, '#3ddc84', 'middle', `opacity="${zk.toFixed(2)}"`);
  }
  return cam(s, lerp(1.0, 1.06, seg(t, S(16), S(19))), 540, 940);
}, .3);

// 14a. Ночь: колокольчики звенят
add(S(19) - .3, PE(19, 0) + .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#06080d');
  s += `<g opacity=".55">${escalatorSide('#56627c')}</g>`;
  const k = seg(t, S(19), S(19) + .2);
  s += bells(t, 1, .9 + .3 * Math.sin(t * 3), '#9aa6bd');
  s += `<ellipse cx="540" cy="960" rx="300" ry="160" fill="url(#warmBlob)" opacity="${f(.25 + .15 * Math.sin(t * 13))}"/>`;
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#000" opacity="${f(.25 * (1 - k))}"/>`;
  return cam(s, 1.35 + .05 * seg(t, S(19), PE(19, 0)), 540, 900);
}, .2);

// 14b. Утро: следы на ступенях
add(PE(19, 0) + .25, S(20) + .1, t => {
  const t0 = PE(19, 0) + .25;
  let s = rect(-400, -400, 1880, 2800, '#2a3140');
  // ступени в перспективе (вид сверху вниз)
  for (let i = 0; i < 9; i++) {
    const y = 360 + i * 150, w1 = 380 + i * 40, w2 = 380 + (i + 1) * 40;
    s += `<path d="M${540 - w1} ${y} L${540 + w1} ${y} L${540 + w2} ${y + 150} L${540 - w2} ${y + 150}Z" fill="${i % 2 ? '#3a4356' : '#343c4e'}" stroke="${ST}" stroke-width="4"/>`;
    for (let j = -8; j <= 8; j++) s += `<line x1="${540 + j * w1 / 9}" y1="${y + 6}" x2="${540 + j * w2 / 9}" y2="${y + 144}" stroke="#2a3140" stroke-width="3"/>`;
  }
  s += `<path d="M120 300 L60 1720 M960 300 L1020 1720" stroke="#1b2131" stroke-width="60"/>`;
  // следы снизу вверх
  const tg = Wt(19, 'СЛЕДЫ');
  for (let i = 0; i < 8; i++) {
    const ti = tg - .6 + i * .22; const kk = seg(t, ti, ti + .15); if (kk <= 0) continue;
    const y = 1560 - i * 150, x = 540 + (i % 2 ? 70 : -70), sc = .55 + (y - 360) / 1400 * .6;
    s += `<g transform="translate(${x} ${y}) scale(${sc.toFixed(3)})" opacity="${(kk * .95).toFixed(2)}"><ellipse cx="0" cy="0" rx="34" ry="62" fill="#5b3b20"/><ellipse cx="0" cy="66" rx="26" ry="30" fill="#5b3b20"/>
      <circle cx="-30" cy="-50" r="6" fill="#5b3b20"/><circle cx="34" cy="20" r="5" fill="#5b3b20"/></g>`;
  }
  return cam(s, lerp(1.08, 1.0, eout(seg(t, t0, t0 + 4))), 540, lerp(1100, 900, eio(seg(t, t0, S(20)))));
}, .4);

// 14c. Следы ведут в магазин одежды
add(S(20) + .1, S(21) - .2, t => {
  const t0 = S(20) + .1;
  let s = rect(-400, -400, 1880, 2800, '#1e2430');
  // окно с туманом слева
  s += rect(60, 380, 260, 520, '#9aa6b4', `stroke="#c7cfdb" stroke-width="10"`) + `<clipPath id="wclip"><rect x="60" y="380" width="260" height="520"/></clipPath><g clip-path="url(#wclip)">${fog(t, 60, 380, 260, 520, 5, 6, .95)}</g>`;
  // проход в магазин
  s += rect(560, 420, 400, 70, '#1b2131', `stroke="#3a4560" stroke-width="5"`) + txt(760, 470, 'ОДЕЖДА', 40, '#ffd23f', 'letter-spacing="6"');
  s += rect(600, 490, 320, 520, '#07090d', `stroke="#3a4560" stroke-width="6"`);
  for (let i = 0; i < 3; i++) s += mannequin(680 + i * 80, 990, 300, { dim: .45, sw: 3 });
  // пол в перспективе
  s += `<path d="M-400 1010 L1480 1010 L1480 2400 L-400 2400Z" fill="#2a3140"/>`;
  for (let i = 0; i < 10; i++) s += `<line x1="${760 + (i - 5) * 60}" y1="1010" x2="${760 + (i - 5) * 380}" y2="1920" stroke="#1e2430" stroke-width="4"/>`;
  // следы от зрителя к двери
  const tv = Wt(20, 'ВЕЛИ');
  for (let i = 0; i < 9; i++) {
    const ti = tv - .5 + i * .14; const kk = seg(t, ti, ti + .12); if (kk <= 0) continue;
    const q = i / 8, y = lerp(1820, 1040, Math.pow(q, .8)), x = lerp(360, 760, q) + (i % 2 ? 30 : -30) * (1 - q * .6), sc = lerp(1.2, .3, q);
    s += `<g transform="translate(${f(x)} ${f(y)}) scale(${sc.toFixed(3)} ${(sc * .5).toFixed(3)})" opacity="${(kk * .95).toFixed(2)}"><ellipse cx="0" cy="0" rx="34" ry="62" fill="#5b3b20"/><ellipse cx="0" cy="-70" rx="26" ry="30" fill="#5b3b20"/></g>`;
  }
  return cam(s, lerp(1.0, 1.12, eio(seg(t, t0, S(21)))), lerp(540, 680, eio(seg(t, t0, S(21)))), 960);
}, .35);

// 15. Пересчёт: 12 → 13
add(S(21) - .2, S(22) - .4, t => {
  let s = room(1310);
  s += rackRail(560, -400, 2400);
  const n = 13, gap = 150, x0 = 140;
  const t13 = Wt(21, 'ТРИНАДЦАТЬ');
  const tA = P(21, 0) + .3, tB = PE(21, 1);
  for (let i = 0; i < n; i++) {
    const x = x0 + i * gap;
    s += mannequin(x, 1300, 600, { mud: i === 9 });
    const ti = i < 12 ? lerp(tA, tB, i / 11) : t13;
    const k = popScale(t, ti, .22);
    if (k > 0) {
      const red = i === 12;
      s += `<g transform="translate(${x} 662) scale(${(k * (red ? 1.25 : 1)).toFixed(3)})"><circle r="40" fill="${red ? '#e0322f' : '#e9edf5'}" stroke="${ST}" stroke-width="5"/>${txt(0, 15, i + 1, 40, red ? '#fff' : '#0d1018')}</g>`;
    }
  }
  // камера едет вдоль ряда
  const ct = (() => { if (t < tA) return 0; if (t < tB) return seg(t, tA, tB) * 11 / 12; if (t < t13 - .3) return 11 / 12; return lerp(11 / 12, 1, eout(seg(t, t13 - .3, t13 + .1))); })();
  const cx = lerp(x0 + 150, x0 + 12 * gap - 120, ct);
  const zoom = 1 + .25 * eout(seg(t, t13, t13 + .6));
  // счётчик
  const cnt = t >= t13 ? 13 : Math.max(0, Math.min(12, Math.floor((t - tA) / ((tB - tA) / 11)) + 1));
  let hudc = `<g transform="translate(${f(cx)} 565)">${rect(-190, -70, 380, 120, '#07090d', `rx="16" stroke="${t >= t13 ? '#ff4040' : '#3a4560'}" stroke-width="6"`)}${mono(-150, 12, 'ПЕРЕСЧЁТ:', 32, '#9aa6bd')}${mono(150, 22, String(cnt), 66, t >= t13 ? '#ff4040' : '#fff', 'end')}</g>`;
  s += hudc;
  if (t >= t13) s += `<rect x="-400" y="-400" width="2800" height="2800" fill="#300" opacity="${f(.35 * (1 - seg(t, t13, t13 + 1.2)))}"/>`;
  return cam(s, zoom, cx + (zoom - 1) * 200, 980);
});

// 16. Финал: герой со спины на эскалаторе, манекены вдали
add(S(22) - .4, DUR + 1, t => {
  const T = t - S(22);
  let s = rect(-400, -400, 1880, 2800, '#080a10');
  s += rect(-400, 560, 1880, 30, '#2a3142') + `<line x1="-400" y1="500" x2="1480" y2="500" stroke="#56627c" stroke-width="5"/>`;
  for (let i = -4; i < 16; i++) s += `<line x1="${i * 90}" y1="500" x2="${i * 90}" y2="560" stroke="#3a4560" stroke-width="3"/>`;
  // манекены на втором этаже за перилами
  [620, 700, 780, 860, 940].forEach((x, i) => {
    const turn = i === 2 ? seg(t, E(22) + .8, E(22) + 1.3) : 0;
    s += mannequin(x, 560, 230, { dim: .55, sw: 2.5, headTurn: turn });
  });
  s += `<path d="M120 1500 L900 560" stroke="#2a3348" stroke-width="120"/><path d="M60 1430 L840 490" stroke="#56627c" stroke-width="10"/><path d="M180 1570 L960 630" stroke="#3a4560" stroke-width="10"/>`;
  let d = ''; for (let i = 0; i < 18; i++) { const x = 120 + i * 43.3, y = 1500 - i * 52.2; d += `M${f(x - 40)} ${f(y + 30)} L${f(x + 40)} ${f(y - 30)} `; }
  s += `<path d="${d}" stroke="#1b2131" stroke-width="4"/>`;
  s += hero(430, 1200, 420, 'back');
  s += exitSign(150, 360, .7, .5 + .5 * (Math.sin(t * 7) > -.6 ? 1 : 0));
  s += dust(t, 30, 13, 0, 200, 1080, 1500, '#cfe0ff', .3, 2.5);
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#000" opacity="${f(.55 * seg(t, E(22) + .1, E(22) + .6))}"/>`;
  return cam(s, lerp(1.15, 1.0, eout(seg(T, 0, 6))), lerp(500, 540, seg(T, 0, 6)), lerp(1000, 960, seg(T, 0, 6)));
}, .45);

// ---------- HUD: дни, ресурсы, плашки ----------
const DAYS = [[S(2), 1], [S(8), 2], [S(11), 3], [S(16), 5], [S(22), 6]];
DAYS.forEach(([t]) => sfx(t, 'page', .9));
function dayAt(t) { let d = null, t0 = 0; for (const [tt, n] of DAYS) if (t >= tt) { d = n; t0 = tt; } return [d, t0]; }
function keyf(t, kf) { // [[t,v],...] линейно
  if (t <= kf[0][0]) return kf[0][1];
  for (let i = 1; i < kf.length; i++) if (t < kf[i][0]) return lerp(kf[i - 1][1], kf[i][1], eio(seg(t, kf[i - 1][0], kf[i][0])));
  return kf[kf.length - 1][1];
}
const FOOD = [[0, 100], [S(8), 92], [S(11), 85], [S(16), 72], [S(22), 64]];
const CHARGE = [[0, 100], [Wt(7, 'СОРОК') - .1, 100], [Wt(7, 'СОРОК') + .5, 40], [Wt(8, 'САДИТСЯ'), 40], [Wt(8, 'САДИТСЯ') + .8, 12], [P(10, 2), 12], [P(10, 2) + 1.4, 100], [S(22), 96]];
const SLEEP = [[0, 90], [Wt(11, 'КЛЮЧИ'), 90], [Wt(11, 'КЛЮЧИ') + .6, 35], [S(16), 50], [Wt(21, 'ТРИНАДЦАТЬ'), 50], [Wt(21, 'ТРИНАДЦАТЬ') + .6, 12]];
const DROPS = [Wt(7, 'СОРОК'), Wt(8, 'САДИТСЯ'), Wt(11, 'КЛЮЧИ'), Wt(21, 'ТРИНАДЦАТЬ')];
const PLATES = [ // [t, тип, текст, до какого времени]
  [Wt(3, 'ЗАКРЫЛИСЬ'), 'p', 'ДВЕРИ ЗАКРЫТЫ', S(8) - .3],
  [Wt(8, 'САДИТСЯ'), 'p', 'ТЕЛЕФОН САДИТСЯ', S(11) - .3],
  [S(10), 's', '4 БОЛТА', S(11) - .3],
  [P(11, 1), 'p', 'ОБХОД В 02:00', S(16) - .3],
  [S(14) + .2, 's', 'СТАТЬ МАНЕКЕНОМ', S(16) - .3],
  [P(16, 1), 'p', 'НЕ ЗНАЮ, ГДЕ ОН', S(19) - .3],
  [S(17) + .3, 's', 'СИГНАЛИЗАЦИЯ', S(19) - .3],
];
PLATES.forEach(([t]) => sfx(t, 'stamp', .8));
DROPS.forEach(t => sfx(t, 'alarm', .5));

const elDay = document.getElementById('day'), elHud = document.getElementById('hud'), elPl = document.getElementById('plates');
const elB = [0, 1, 2].map(i => document.getElementById('b' + i)), elV = [0, 1, 2].map(i => document.getElementById('v' + i));
function renderHUD(t) {
  const [d, t0] = dayAt(t);
  const hudOn = d !== null && t < DUR;
  elHud.style.opacity = hudOn ? clamp((t - S(2)) / .3) * (1 - seg(t, E(22) + .3, E(22) + .8) * .0) : 0;
  if (d !== null) {
    const fk = seg(t, t0, t0 + .35); // переворот
    const sy = fk < .5 ? 1 - fk * 2 : (fk - .5) * 2;
    const shown = fk < .5 ? (DAYS.find(x => x[1] === d) === DAYS[0] ? d : DAYS[DAYS.findIndex(x => x[1] === d) - 1][1]) : d;
    elDay.innerHTML = `ДЕНЬ ${shown} <small>/ 365</small>`;
    elDay.style.transform = `scaleY(${Math.max(.02, sy).toFixed(3)})`;
  }
  const vals = [keyf(t, FOOD), keyf(t, CHARGE), keyf(t, SLEEP)];
  vals.forEach((v, i) => {
    elB[i].style.width = v.toFixed(1) + '%';
    elB[i].style.background = v < 20 ? '#ff4040' : v < 45 ? '#ffd23f' : '#e9edf5';
    elV[i].textContent = Math.round(v) + '%';
  });
  // плашки
  let h = '';
  const [dn] = dayAt(t);
  PLATES.forEach(([tp, ty, tx, tEnd]) => {
    if (t < tp || t > tEnd) return;
    const k = seg(t, tp, tp + .14); const sc = lerp(1.6, 1, eout(k)); const o = k * (1 - seg(t, tEnd - .25, tEnd));
    const sh = t - tp < .25 ? Math.sin((t - tp) * 80) * 4 * (1 - (t - tp) / .25) : 0;
    h += `<div class="plate ${ty}" style="transform:translateX(${sh.toFixed(1)}px) scale(${sc.toFixed(3)}) rotate(${ty === 'p' ? -2 : 2}deg);opacity:${o.toFixed(2)}"><span>${ty === 'p' ? 'ПРОБЛЕМА:' : 'РЕШЕНИЕ:'}</span>${tx}</div>`;
  });
  elPl.innerHTML = h;
  // красная вспышка
  let rf = 0; DROPS.forEach(td => { const q = t - td; if (q > 0 && q < .7) rf = Math.max(rf, (1 - q / .7) * (Math.sin(q * 30) * .3 + .7)); });
  document.getElementById('redflash').style.opacity = rf.toFixed(2);
}

// ---------- субтитры ----------
const CHUNKS = [];
L.forEach(l => l.phrases.forEach(ph => {
  let cur = [];
  const flush = () => { if (cur.length) { CHUNKS.push(cur); cur = []; } };
  ph.words.forEach(w => {
    const len = cur.reduce((a, x) => a + x.w.length + 1, 0);
    if (cur.length >= 4 || (cur.length >= 2 && len + w.w.length > 20)) flush();
    cur.push(w);
  });
  flush();
}));
// не оставлять «висячее» короткое слово отдельным блоком
for (let i = 0; i < CHUNKS.length; i++) CHUNKS[i].t0 = CHUNKS[i][0].t0, CHUNKS[i].t1 = CHUNKS[i][CHUNKS[i].length - 1].t1;
const elSub = document.getElementById('subs');
function renderSubs(t) {
  let c = null;
  for (let i = 0; i < CHUNKS.length; i++) {
    const ch = CHUNKS[i], next = CHUNKS[i + 1];
    const end = Math.min(ch.t1 + .45, next ? next.t0 - .02 : 1e9);
    if (t >= ch.t0 - .03 && t < end) { c = ch; break; }
  }
  if (!c || (t > S(1) - .2 && t < P(2, 0) - .1)) { elSub.innerHTML = ''; return; } // на названии субтитров нет
  let h = '<div class="ln">';
  c.forEach(w => {
    const k = seg(t, w.t0 - .03, w.t0 + .09);
    const sc = k <= 0 ? .8 : lerp(.8, 1, eout(k));
    h += `<span class="w ${w.c || ''}" style="opacity:${k.toFixed(2)};transform:scale(${sc.toFixed(3)})">${w.w}</span> `;
  });
  elSub.innerHTML = h + '</div>';
}

// ---------- название и финал ----------
const elTitle = document.getElementById('title'), elFinal = document.getElementById('final');
function renderOverlays(t) {
  const a = S(1) - .1, b = P(2, 0) - .15;
  const o = seg(t, a, a + .5) * (1 - seg(t, b - .4, b));
  elTitle.style.opacity = o.toFixed(2);
  elTitle.style.transform = `scale(${lerp(1.08, 1, eout(seg(t, a, a + 1.5))).toFixed(3)})`;
  const tf = E(22) + .2;
  const k = seg(t, tf, tf + .3);
  elFinal.style.opacity = k.toFixed(2);
  elFinal.style.transform = `scale(${(k > 0 ? lerp(1.4, 1, eout(k)) : 1).toFixed(3)})`;
  // мигание света (книжный) + чёрные кадры
  let black = 0;
  const tf1 = P(3, 0) + .05;
  [[0, .1], [.17, .27], [.38, .43]].forEach(([q0, q1]) => { if (t >= tf1 + q0 && t < tf1 + q1) black = .92; });
  if (t < .35) black = Math.max(black, 1 - t / .35);
  if (t > DUR - .6) black = Math.max(black, seg(t, DUR - .6, DUR));
  document.getElementById('flash').style.opacity = black.toFixed(2);
}

// ---------- звуки сцен ----------
(function () {
  // хук: шаги + ключи
  for (let i = 0; i < 10; i++) sfx(.6 + i * .72, 'step', .55);
  sfx(.3, 'keys', .6); sfx(3.6, 'keys', .5);
  sfx(S(1) - .1, 'boom', 1);
  const tf1 = P(3, 0) + .05; sfx(tf1, 'click', .8); sfx(tf1 + .38, 'buzz', .5);
  sfx(Wt(3, 'ЗАКРЫЛИСЬ'), 'slam', 1);
  [0, .45, .9].forEach(q => sfx(P(5, 0) + .1 + q, 'knock', .9));
  [Wt(6, 'ФУДКОРТ'), Wt(6, 'АПТЕКА'), Wt(6, 'СПОРТТОВАРЫ')].forEach(t => sfx(t + .1, 'pop', .6));
  sfx(Wt(7, 'СВЯЗИ'), 'error', .5);
  sfx(S(9) + .05, 'pencil', .7, { d: 2.2 }); sfx(Wt(9, 'ЧЕТЫРЕ'), 'pencil', .6, { d: 1.2 });
  sfx(S(10) - .5, 'ratchet', .7); sfx(S(10) + .6, 'grate', .6);
  for (let i = 0; i < 30; i += 3) sfx(P(10, 1) + .05 + i * .045 + .3, 'clack', .45);
  sfx(P(10, 2) + .3, 'chime', .6);
  sfx(Wt(11, 'КЛЮЧИ') - .1, 'keys', .9); sfx(Wt(11, 'СВЯЗКУ'), 'keys', .7);
  for (let i = 0; i < 16; i++) sfx(P(12, 0) + i * .55, 'step', .5);
  sfx(S(12) + .5, 'keys', .5); sfx(S(12) + 2.6, 'keys', .55);
  for (let i = 0; i < 9; i++) sfx(S(13) + i * .62, 'heart', .7);
  sfx(S(14) + .05, 'pencil', .6, { d: 2.5 });
  sfx(P(15, 0), 'heart', .8); sfx(P(15, 0) + .7, 'heart', .8);
  for (let i = 0; i < 5; i++) sfx(P(15, 3) + i * .3, 'tick', .5);
  sfx(P(15, 4) + .1, 'keys', .45);
  sfx(S(17) - .1, 'pencil', .6, { d: 2.5 });
  sfx(Wt(18, 'УСЛЫШУ'), 'bells', .55);
  sfx(S(19) + .05, 'bells', 1); sfx(S(19) + 1.0, 'bells', .8);
  sfx(Wt(19, 'СЛЕДЫ'), 'drop', .4);
  const tA = P(21, 0) + .3, tB = PE(21, 1);
  for (let i = 0; i < 12; i++) sfx(lerp(tA, tB, i / 11), 'tick', .55);
  sfx(Wt(21, 'ТРИНАДЦАТЬ'), 'boom', 1.1);
  sfx(E(22) + .2, 'stamp', 1);
})();

// ---------- кадр ----------
const scA = document.getElementById('scA'), scB = document.getElementById('scB');
window.renderAt = function (t) {
  gid = 0;
  const act = scenes.filter(s => t >= s.t0 - s.fade && t < s.t1 + .0001);
  // текущая — последняя начавшаяся; предыдущая гаснет
  let html = '';
  act.sort((a, b) => a.t0 - b.t0);
  act.forEach((s, i) => {
    const o = i === 0 ? 1 : clamp((t - (s.t0 - s.fade)) / s.fade);
    html += `<g opacity="${o.toFixed(3)}">${s.draw(t)}</g>`;
  });
  scA.innerHTML = html; scB.innerHTML = '';
  document.getElementById('turb').setAttribute('seed', String(Math.floor(t * 30) % 17 + 1));
  renderHUD(t); renderSubs(t); renderOverlays(t);
};
window.SFX = SFX.sort((a, b) => a.t - b.t);
window.DUR = DUR;
})();
