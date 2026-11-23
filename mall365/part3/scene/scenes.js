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

const scenes = [];
const add = (t0, t1, draw, fade = .35) => scenes.push({ t0, t1, draw, fade });
function blueprint(t, title) {
  let s = rect(-400, -400, 1880, 2800, '#123a6b') + rect(-400, -400, 1880, 2800, 'url(#bpgrid)') + rect(-400, -400, 1880, 2800, 'url(#bpgrid2)');
  s += rect(60, 1150, 960, 4, '#5b92d6', 'opacity=".0"');
  if (title) s += mono(80, 740, title, 30, '#a9cbf5') + `<line x1="80" y1="755" x2="1000" y2="755" stroke="#a9cbf5" stroke-width="2"/>`;
  return s;
}

// ================= ЧАСТЬ 3 · «Шестнадцатая камера» =================
function row(t, n, gap, x0, y, h, opts = {}) {
  let s = '';
  for (let i = 0; i < n; i++) {
    if (opts.skip === i) { s += `<ellipse cx="${x0 + i * gap}" cy="${y}" rx="${h * .1}" ry="${h * .018}" fill="#3a3f4b" stroke="${ST}" stroke-width="3"/>`; continue; }
    s += mannequin(x0 + i * gap, y, h, { dim: opts.dim, sw: opts.sw });
  }
  return s;
}
const HUDOFF = [];
const DRONE = [];
const INITIALS = 'М.Р.'; // инициалы на рюкзаке и в подписи дежурного (подсказка на часть 4)
function choiceCard(t, cx, cy, n, label, icon, tt, col, dimK = 0, big = 1) {
  const k = popScale(t, tt, .3); if (k <= 0) return '';
  const glow = .5 + .5 * Math.sin(t * 5 + (+n));
  const lines = label.split('|');
  let lab = lines.length === 1 ? txt(0, 215, lines[0], 56, '#fff') : txt(0, 190, lines[0], 44, '#fff') + txt(0, 238, lines[1], 44, '#fff');
  return `<g transform="translate(${cx} ${cy}) scale(${(k * big).toFixed(3)})" opacity="${f(1 - .75 * dimK)}">
    <rect x="-200" y="-260" width="400" height="520" rx="34" fill="#141925" stroke="${col}" stroke-width="${f(8 + 4 * glow)}"/>
    <circle cx="0" cy="-160" r="62" fill="${col}"/>${txt(0, -136, n, 76, '#0d1018')}${icon}${lab}</g>`;
}
const ICON_ESC = `<g transform="translate(0 20)" stroke="#e9edf5" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M-120 90 L-60 90 L60 -30 L120 -30"/><path d="M-120 40 L-80 40 L40 -80 L120 -80"/><path d="M-60 90 L-60 40 M-20 50 L-20 0 M20 10 L20 -40 M60 -30 L60 -80"/></g>`;
const ICON_MASK = `<g transform="translate(0 20)"><ellipse cx="0" cy="0" rx="78" ry="98" fill="#f7f6f2" stroke="${ST}" stroke-width="6"/><ellipse cx="-28" cy="-12" rx="16" ry="9" fill="#1a1d24"/><ellipse cx="28" cy="-12" rx="16" ry="9" fill="#1a1d24"/></g>`;
const ICON_SWITCH = `<g transform="translate(0 10)"><rect x="-70" y="-90" width="140" height="180" rx="16" fill="#2a3142" stroke="#e9edf5" stroke-width="7"/><rect x="-22" y="-60" width="44" height="120" rx="10" fill="#0d1018" stroke="#e9edf5" stroke-width="5"/><rect x="-34" y="10" width="68" height="40" rx="8" fill="#e0322f" stroke="#e9edf5" stroke-width="5"/>${'<text x="0" y="-100" text-anchor="middle" font-family="Inter" font-weight="900" font-size="28" fill="#e9edf5">OFF</text>'}</g>`;
const ICON_EYE = `<g transform="translate(0 20)"><path d="M-120 0 Q0 -110 120 0 Q0 110 -120 0Z" fill="#f7f6f2" stroke="${ST}" stroke-width="6"/><circle cx="0" cy="0" r="44" fill="#3d7be0" stroke="${ST}" stroke-width="5"/><circle cx="0" cy="0" r="20" fill="#0d1018"/><circle cx="12" cy="-12" r="8" fill="#fff"/></g>`;
function heroPack(x, y, h, view, pose, k) { // герой + инициалы на кармане рюкзака
  let s = hero(x, y, h, view, pose, k);
  if (view === 'back') s += `<text x="${f(x)}" y="${f(y - h * .5)}" text-anchor="middle" font-family="Inter" font-weight="900" font-size="${f(h * .04)}" fill="#3a1a05">${INITIALS}</text>`;
  return s;
}

// ---------- мини-сцены для мониторов ----------
function miniScene(i, x, y, w, h, t, o = {}) {
  const cx = x + w / 2, cy = y + h / 2;
  let s = rect(x, y, w, h, '#0c1622');
  const L = '#7fa3c7';
  switch (i) {
    case 0: for (let k = 0; k < 9; k++) s += rect(x + 12 + k * 21, y + 30, 16, h - 50, ['#3c5a7a', '#5a4a3a', '#4a5a4a'][k % 3]); break; // книжный
    case 1: s += rect(x + 30, y + 15, w - 60, h - 25, '#9aa6b4') + `<line x1="${cx}" y1="${y + 15}" x2="${cx}" y2="${y + h - 10}" stroke="#c7cfdb" stroke-width="4"/>`; break; // двери
    case 2: s += `<path d="M${x + 20} ${y + h - 15} L${x + w - 30} ${y + 20}" stroke="${L}" stroke-width="16"/>`; break; // эскалатор
    case 3: { const n = o.n13 ?? 13; for (let k = 0; k < 13; k++) { if (k === (o.gap ?? -1)) continue; s += `<circle cx="${x + 14 + k * 14.5}" cy="${y + h - 60}" r="5" fill="#ecebe7"/><rect x="${x + 10 + k * 14.5}" y="${y + h - 54}" width="8" height="34" fill="#9aa3b6"/>`; } break; }
    case 4: s += rect(x + 20, y + 20, 50, 100, '#ffcf8a') + rect(x + 100, y + 90, 80, 8, '#5a6273'); if (o.hero) s += `<circle cx="${f(x + 90 + Math.sin(t * 2) * 50)}" cy="${y + 80}" r="7" fill="#ff7a1a"/><rect x="${f(x + 85 + Math.sin(t * 2) * 50)}" y="${y + 88}" width="10" height="22" fill="#2c3e63"/>`; break; // фудкорт
    case 5: for (let k = 0; k < 9; k++) s += `<line x1="${x + 10}" y1="${y + 15 + k * 15}" x2="${x + w - 10}" y2="${y + 15 + k * 15}" stroke="${L}" stroke-width="4"/>`; break; // электроника
    case 6: s += `<path d="M${cx - 12} ${cy - 36}h24v24h24v24h-24v24h-24v-24h-24v-24h24z" fill="#3ddc84" opacity=".8"/>`; break; // аптека
    case 7: for (let k = 0; k < 3; k++) s += `<line x1="${x}" y1="${y + 40 + k * 40}" x2="${x + w}" y2="${y + 40 + k * 40}" stroke="${L}" stroke-width="5"/>`; break; // атриум
    case 8: s += rect(x, y + h * .55, w, h * .45, '#56606d') + `<ellipse cx="${cx}" cy="${cy}" rx="${w * .5}" ry="${h * .35}" fill="#dfe6ee" opacity=".45"/>`; break; // парковка
    case 9: for (let k = 0; k < 4; k++) s += rect(x + 20 + k * 45, y + h - 60 - (k % 2) * 30, 38, 40, '#6b5a3a', `stroke="${ST}" stroke-width="2"`); break; // склад
    case 10: s += `<circle cx="${cx}" cy="${cy}" r="30" fill="#e8742a"/>`; break; // спорт
    case 11: s += `<circle cx="${cx}" cy="${y + 26}" r="12" fill="#ffd23f"/><path d="M${x + 30} ${y + h} L${cx - 20} ${y + 40} L${cx + 20} ${y + 40} L${x + w - 30} ${y + h}" fill="none" stroke="${L}" stroke-width="4"/>`; break; // коридор
    case 12: for (let k = 0; k < 2; k++) s += `<circle cx="${cx - 30 + k * 60}" cy="${y + 40}" r="10" fill="#ecebe7"/><rect x="${cx - 44 + k * 60}" y="${y + 52}" width="28" height="70" fill="#59627a"/>`; break; // одежда
    case 13: s += rect(x + 20, y + 20, w - 40, 60, '#1b2131') + `<line x1="${x + 20}" y1="${y + 110}" x2="${x + w - 20}" y2="${y + 110}" stroke="${L}" stroke-width="10" stroke-dasharray="14 8"/>`; break; // кино
    case 14: s += `<rect x="${cx - 30}" y="${cy - 10}" width="60" height="40" fill="#e0322f"/><circle cx="${cx - 18}" cy="${cy + 36}" r="10" fill="#222"/><circle cx="${cx + 18}" cy="${cy + 36}" r="10" fill="#222"/>`; break; // игрушки
    case 15: s += rect(x + 30, y + 20, w - 60, 40, '#2a5a8a') + `<circle cx="${cx}" cy="${y + 100}" r="12" fill="#2a1d14"/><rect x="${cx - 14}" y="${y + 110}" width="28" height="30" fill="#ff7a1a"/>`; break; // охрана
  }
  // скан-линии и подпись
  for (let k = 0; k < h; k += 6) s += `<line x1="${x}" y1="${y + k}" x2="${x + w}" y2="${y + k}" stroke="#000" stroke-width="2" opacity=".18"/>`;
  s += `<text x="${x + 8}" y="${y + 18}" font-family="JetBrains Mono" font-weight="700" font-size="13" fill="#cfe0ff" opacity=".8">CAM ${String(i + 1).padStart(2, '0')}</text>`;
  return s;
}
const MG = { x: 90, y: 560, w: 210, h: 150, g: 20 };
function monPos(i) { return [MG.x + (i % 4) * (MG.w + MG.g), MG.y + Math.floor(i / 4) * (MG.h + MG.g)]; }
function monitors(t, o = {}) {
  let s = rect(-400, -400, 1880, 2800, '#080b12');
  s += rect(60, 530, 960, 750, '#151a24', `rx="16" stroke="#2a3142" stroke-width="6"`);
  for (let i = 0; i < 16; i++) {
    const [x, y] = monPos(i);
    const on = o.on ? o.on(i) : 1;
    s += rect(x - 6, y - 6, MG.w + 12, MG.h + 12, '#0b0d12', 'rx="8"');
    if (on > 0) s += `<g opacity="${f(on)}">${miniScene(i, x, y, MG.w, MG.h, t, o)}</g>`;
    if (o.hi === i) s += rect(x - 8, y - 8, MG.w + 16, MG.h + 16, 'none', `rx="10" stroke="${o.hiCol || '#ffd23f'}" stroke-width="7"`);
  }
  // синий свет экранов
  s += `<ellipse cx="540" cy="1350" rx="600" ry="200" fill="#3d7be0" opacity=".12"/>`;
  s += rect(40, 1290, 1000, 40, '#2a3142', `stroke="${ST}" stroke-width="5"`);
  return s;
}

// 0. Итог голосования
add(0, S(1) - .15, t => {
  let s = rect(-400, -400, 1880, 2800, '#0b0d12');
  const tb = Wt(0, 'БЕЖАТЬ');
  const dk = seg(t, .3, tb - .1), win = eout(seg(t, tb - .2, tb + .3));
  s += choiceCard(t, lerp(795, 900, win), 900, '2', 'ЗАМЕРЕТЬ', ICON_MASK, -1, '#56627c', dk, 1 - .25 * win);
  s += choiceCard(t, lerp(285, 470, win), lerp(900, 860, win), '1', 'БЕЖАТЬ', ICON_ESC, -1, '#ffd23f', 0, 1 + .25 * win);
  const sk = seg(t, tb, tb + .14);
  if (sk > 0) s += `<g transform="translate(540 1290) rotate(-4) scale(${f(lerp(1.6, 1, eout(sk)))})" opacity="${f(sk)}">${rect(-360, -56, 720, 112, '#e0322f', `rx="14" stroke="${ST}" stroke-width="6"`)}${txt(0, 18, 'ВЫ ВЫБРАЛИ: БЕЖАТЬ', 54, '#fff')}</g>`;
  return cam(s, 1, 540, 960, sk > 0 && sk < 1 ? Math.sin(t * 60) * .8 : 0);
}, .2);
HUDOFF.push([0, S(1) - .2]);

// 1. Бег вверх по эскалатору (вид от первого лица) + кадр назад
add(S(1) - .15, S(2) - .2, t => {
  const back = P(1, 2) - .05, backEnd = PE(1, 2) + .55;
  if (t >= back && t < backEnd) {
    // взгляд назад: внизу белая фигура на первой ступени
    let s = rect(-400, -400, 1880, 2800, '#07090d');
    for (let i = 0; i < 14; i++) {
      const q = i / 13, y = lerp(300, 1500, Math.pow(q, 1.2)), w = lerp(560, 180, q);
      s += `<line x1="${540 - w}" y1="${f(y)}" x2="${540 + w}" y2="${f(y)}" stroke="#3a4560" stroke-width="${f(lerp(10, 3, q))}"/>`;
    }
    s += `<path d="M-20 300 L360 1500 M1100 300 L720 1500" stroke="#56627c" stroke-width="22"/>`;
    s += mannequin(540, 1560, 260, { dim: .95 });
    s += `<ellipse cx="540" cy="1400" rx="260" ry="200" fill="#fff" opacity=".06"/>`;
    return cam(s, 1.05 + .1 * seg(t, back, backEnd), 540, 1000, Math.sin(t * 50) * 1.2);
  }
  let s = rect(-400, -400, 1880, 2800, '#07090d');
  const sp = 2.2, ph = (t * sp) % 1;
  for (let i = 0; i < 12; i++) {
    const q = Math.pow((i + ph) / 12, 2.2), y = lerp(380, 2300, q), w = lerp(150, 1200, q);
    s += `<path d="M${f(540 - w)} ${f(y)} L${f(540 + w)} ${f(y)}" stroke="#56627c" stroke-width="${f(lerp(3, 26, q))}"/>`;
    for (let k = -6; k <= 6; k++) s += `<line x1="${f(540 + k * w / 7)}" y1="${f(y)}" x2="${f(540 + k * w / 7 * 1.12)}" y2="${f(y + lerp(10, 140, q))}" stroke="#2a3142" stroke-width="${f(lerp(1, 5, q))}"/>`;
  }
  s += `<path d="M380 380 L-500 2300 M700 380 L1580 2300" stroke="#3a4560" stroke-width="60"/>`;
  s += rect(380, 200, 320, 180, '#0d1018', `stroke="#3a4560" stroke-width="4"`) + exitSign(540, 250, .6, .8);
  const bob = Math.sin(t * 14) * 18;
  return cam(s, 1.05, 540 + Math.sin(t * 7) * 14, 960 + bob, Math.sin(t * 9) * 1.5);
}, .2);

// 2. Заставка
add(S(2) - .2, P(3, 0) - .05, t => {
  let s = mallFloors(.8) + exitSign(860, 640, .8) + dust(t, 60, 9, 0, 0, 1080, 1920, '#cfe0ff', .45, 2.6);
  s += `<rect x="-400" y="-400" width="1880" height="2800" fill="#000" opacity=".45"/>`;
  return cam(s, lerp(1.12, 1.04, eout(seg(t, S(2), S(2) + 5))), 540, 960);
}, .4);
HUDOFF.push([S(2) - .3, P(3, 0) - .1]);

// 3. Металлическая дверь «Только для персонала»
add(P(3, 0) - .05, S(4) - .1, t => {
  let s = room(1340);
  s += rect(330, 560, 420, 780, '#5d6677', `stroke="${ST}" stroke-width="7"`) + rect(350, 580, 380, 740, '#6c7586');
  for (let i = 0; i < 4; i++) s += rect(380, 620 + i * 170, 320, 130, 'none', 'stroke="#56607a" stroke-width="4"');
  s += rect(380, 700, 320, 110, '#e9edf5', `rx="8" stroke="${ST}" stroke-width="4"`) + txt(540, 745, 'ТОЛЬКО ДЛЯ', 34, '#0d1018') + txt(540, 788, 'ПЕРСОНАЛА', 34, '#e0322f');
  s += rect(660, 960, 50, 80, '#2a3142', `rx="6" stroke="${ST}" stroke-width="4"`);
  const lk = seg(t, Wt(3, 'ЗАПЕРТА'), Wt(3, 'ЗАПЕРТА') + .2);
  s += `<circle cx="685" cy="940" r="10" fill="${lk > 0 && Math.sin(t * 12) > 0 ? '#ff4040' : '#5a1a1a'}"/>`;
  s += rect(330, 1330, 420, 10, '#000') + `<path d="M330 1336 h420" stroke="#ffd23f" stroke-width="2" opacity=".35"/>`;
  s += heroPack(200, 1345, 520, 'back');
  // стук сзади: белая фигура далеко на эскалаторе слева
  s += `<ellipse cx="540" cy="520" rx="300" ry="120" fill="url(#warmBlob)" opacity=".18"/>`;
  return cam(s, lerp(1.0, 1.1, seg(t, S(3), S(4))), 500, 980, lk > 0 ? Math.sin(t * 40) * .4 * (1 - seg(t, Wt(3, 'ЗАПЕРТА'), Wt(3, 'ЗАПЕРТА') + .4)) : 0);
});

// 4. Схема-разрез: обмануть датчик движения
add(S(4) - .1, P(6, 1) - .05, t => {
  let s = blueprint(t, 'СХЕМА №7 · ДВЕРЬ С ДАТЧИКОМ (РАЗРЕЗ)');
  const a = seg(t, S(4), S(4) + .7);
  const fy = 1300, dx = 560;
  const open = seg(t, Wt(6, 'ЩЕЛЧОК'), Wt(6, 'ЩЕЛЧОК') + .5);
  s += `<g opacity="${f(a)}"><line x1="80" y1="${fy}" x2="1000" y2="${fy}" stroke="#fff" stroke-width="5"/>
    <line x1="${dx}" y1="760" x2="${dx}" y2="790" stroke="#fff" stroke-width="5"/>
    ${rect(dx - 30, 760, 60, 30, 'none', 'stroke="#fff" stroke-width="4"')}
    <g transform="rotate(${f(-70 * eout(open))} ${dx} 800)"><rect x="${dx - 14}" y="800" width="28" height="${fy - 800 - 26}" fill="rgba(255,255,255,.12)" stroke="#fff" stroke-width="5"/></g></g>`;
  s += mono(250, 740, 'СНАРУЖИ', 26, '#a9cbf5', 'middle') + mono(820, 740, 'ВНУТРИ', 26, '#a9cbf5', 'middle');
  s += mono(dx, fy + 50, typeText('ЩЕЛЬ 2 СМ', seg(t, S(4) + .5, S(4) + 1)), 24, '#a9cbf5', 'middle');
  // датчик и конус
  const td = Wt(4, 'ДАТЧИК');
  const sk = seg(t, td - .1, td + .5);
  if (sk > 0) {
    s += rect(dx + 40, 820, 70, 40, '#ffd23f', `rx="8" opacity="${f(sk)}"`);
    s += `<path d="M${dx + 75} 860 L${dx + 30} ${fy - 10} L${dx + 330} ${fy - 10}Z" fill="rgba(255,210,63,.18)" stroke="#ffd23f" stroke-width="4" stroke-dasharray="14 10" opacity="${f(sk)}"/>`;
    s += mono(dx + 130, 848, typeText('ДАТЧИК ДВИЖЕНИЯ', seg(t, td, td + .7)), 26, '#ffd23f');
    s += mono(dx + 200, fy - 40, typeText('ЗОНА ДАТЧИКА', seg(t, td + .4, td + 1)), 24, '#ffd23f', 'middle');
  }
  // вешалка + пакет: просунуть под дверь и помахать
  const t1 = Wt(5, 'РАЗОГНУЛ'), t2 = Wt(5, 'ПРИВЯЗАЛ'), t3 = Wt(5, 'ПРОСУНУЛ'), t4 = Wt(5, 'ПОМАХАЛ');
  const pk = eio(seg(t, t3, t4));
  const wave = t > t4 ? Math.sin((t - t4) * 14) * 28 * (1 - seg(t, Wt(6, 'ЩЕЛЧОК'), Wt(6, 'ЩЕЛЧОК') + .4)) : 0;
  if (t > t1 - .1) {
    const ex = lerp(330, dx + 200, pk), ey = lerp(fy - 6, fy - 6, pk);
    const tipX = ex + (pk > .9 ? 40 : 0), tipY = ey - (pk > .5 ? lerp(0, 180, seg(pk, .5, 1)) : 0) + wave;
    s += `<path d="M120 ${fy - 6} L${f(ex)} ${f(ey)} L${f(tipX)} ${f(tipY)}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>`;
    if (t > t2 - .1) {
      const bk = popScale(t, t2 - .1);
      s += `<g transform="translate(${f(tipX)} ${f(tipY - 40)}) rotate(${f(wave * .6)}) scale(${f(bk)})"><path d="M-36 -40 L36 -40 L44 46 L-44 46Z" fill="rgba(255,255,255,.25)" stroke="#fff" stroke-width="5"/><path d="M-20 -40 q20 -26 40 0" fill="none" stroke="#fff" stroke-width="4"/></g>`;
    }
  }
  const steps = ['1. РАЗОГНУТЬ ВЕШАЛКУ', '2. ПРИВЯЗАТЬ ПАКЕТ', '3. ПОМАХАТЬ В ЗОНЕ'];
  [t1, t2, t3].forEach((tt, i) => s += mono(110, 1420 + i * 0, '', 1));
  steps.forEach((st, i) => { const a2 = [t1, t2, t4][i]; s += mono(110, 860 + i * 52, typeText(st, seg(t, a2 - .1, a2 + .5)), 30, i === 2 ? '#ffd23f' : '#fff'); });
  if (open > 0) s += mono(dx - 60, 1000, 'ОТКРЫТО', 40, '#3ddc84', 'end', `opacity="${f(open)}"`);
  return cam(s, lerp(1.0, 1.04, seg(t, S(4), S(6))), 540, 1060);
}, .3);

// 5. Внутри: спиной к двери, стук обрывается
add(P(6, 1) - .05, S(7) - .25, t => {
  let s = rect(-400, -400, 1880, 2800, '#2b2a27');
  for (let i = 0; i < 9; i++) s += `<line x1="-400" y1="${500 + i * 110}" x2="1480" y2="${500 + i * 110}" stroke="#24231f" stroke-width="4"/>`;
  s += rect(-400, 1330, 1880, 800, '#1d1c1a');
  s += `<ellipse cx="540" cy="520" rx="420" ry="260" fill="url(#warmBlob)" opacity=".55"/><circle cx="540" cy="470" r="26" fill="#ffd23f" stroke="${ST}" stroke-width="5"/>`;
  s += rect(320, 560, 440, 780, '#5d6677', `stroke="${ST}" stroke-width="7"`) + rect(330, 1330, 420, 10, '#000');
  s += hero(540, 1360, 620, 'front');
  const kn = t < Wt(6, 'ОСТАНОВИЛСЯ') + .3;
  if (kn) { const wk = (t * 2.2) % 1; s += `<circle cx="540" cy="900" r="${f(60 + wk * 220)}" fill="none" stroke="#ff4040" stroke-width="5" opacity="${f(.6 * (1 - wk))}"/>`; }
  return cam(s, lerp(1.0, 1.08, seg(t, P(6, 1), S(7))), 540, 1000);
}, .25);
DRONE.push([0, .3], [S(1), .9], [S(2), .5], [P(3, 0), .8], [Wt(6, 'ОСТАНОВИЛСЯ') + .2, .9], [Wt(6, 'ОСТАНОВИЛСЯ') + .5, .2], [S(7), .55]);

// 6. День 13: служебный коридор (панорама)
add(S(7) - .25, S(8) - .1, t => {
  let s = rect(-400, -400, 3200, 2800, '#2b2a27');
  for (let i = 0; i < 9; i++) s += `<line x1="-400" y1="${500 + i * 110}" x2="2800" y2="${500 + i * 110}" stroke="#24231f" stroke-width="4"/>`;
  s += rect(-400, 1330, 3200, 900, '#1d1c1a');
  const doors = [[300, 'ЩИТОК', 'ЩИТОК'], [900, 'СКЛАД', 'СКЛАД'], [1500, 'ОХРАНА', 'КОМНАТА']];
  doors.forEach(([x, lb, w]) => {
    const tw = Wt(7, w); const k = seg(t, tw - .1, tw + .3);
    s += rect(x - 160, 620, 320, 710, '#4a5262', `stroke="${ST}" stroke-width="6"`) + rect(x - 120, 660, 240, 70, k > 0 ? '#ffd23f' : '#e9edf5', `rx="6" stroke="${ST}" stroke-width="4"`) + txt(x, 708, lb, 36, '#0d1018');
    if (lb === 'ОХРАНА') s += rect(x - 100, 780, 200, 120, '#3d7be0', `opacity="${f(.35 + .1 * Math.sin(t * 9))}"`);
    if (lb === 'ЩИТОК') s += rect(x + 180, 760, 120, 170, '#6c7586', `stroke="${ST}" stroke-width="5"`) + `<path d="M${x + 230} 790 l20 40 h-16 l12 40" fill="none" stroke="#ffd23f" stroke-width="6"/>`;
  });
  for (let i = 0; i < 4; i++) { const lx = 0 + i * 600; s += `<ellipse cx="${lx}" cy="520" rx="260" ry="160" fill="url(#warmBlob)" opacity="${f(.45 + .05 * Math.sin(t * 20 + i))}"/><circle cx="${lx}" cy="470" r="18" fill="#ffd23f"/>`; }
  const k = eio(seg(t, S(7), E(7)));
  return cam(s, 1.0, lerp(300, 1500, k), 980);
}, .3);

// 7. Журнал обхода
add(S(8) - .1, S(10) - .2, t => {
  let s = rect(-400, -400, 1880, 2800, '#1a1712');
  s += `<ellipse cx="540" cy="1000" rx="620" ry="460" fill="url(#warmBlob)" opacity=".35"/>`;
  s += rect(110, 620, 860, 720, '#4a3a28', `rx="14" stroke="${ST}" stroke-width="6"`);
  s += rect(140, 640, 400, 680, '#efe8d6', `stroke="${ST}" stroke-width="4"`) + rect(540, 640, 400, 680, '#f3eddc', `stroke="${ST}" stroke-width="4"`);
  // перелистывание: страницы листаются сами на «Восемь лет подряд»
  const tf = S(9), te = E(9);
  const flips = Math.floor(clamp((t - tf) / (te - tf)) * 16);
  const year = 2018 + Math.min(8, Math.floor(clamp((t - tf) / (te - tf)) * 9));
  const ink = '#1d2f6b';
  const page = (x, off) => {
    let r = '';
    for (let i = 0; i < 9; i++) {
      const y = 700 + i * 66; const day = ((i + off * 9) % 28) + 1;
      r += `<line x1="${x + 20}" y1="${y + 14}" x2="${x + 380}" y2="${y + 14}" stroke="#c9bfa5" stroke-width="2"/>`;
      r += `<text x="${x + 24}" y="${y}" font-family="JetBrains Mono" font-weight="700" font-size="22" fill="${ink}">${String(day).padStart(2, '0')}.11</text>`;
      r += `<text x="${x + 120}" y="${y}" font-family="Inter" font-style="italic" font-weight="800" font-size="26" fill="${ink}">манекенов — 12</text>`;
    }
    return r;
  };
  const showLines = seg(t, P(8, 1), P(8, 1) + 1);
  s += `<g opacity="${f(showLines)}">${page(140, flips) + page(540, flips + 1)}</g>`;
  s += mono(540, 610, String(year), 44, '#ffd23f', 'middle', `opacity="${f(seg(t, tf - .2, tf + .2))}"`);
  // переворачивающаяся страница
  if (t > tf && t < te) {
    const q = (clamp((t - tf) / (te - tf)) * 16) % 1;
    const w = 400 * Math.cos(q * Math.PI);
    s += `<path d="M540 640 L${f(540 + w)} ${f(640 - 30 * Math.sin(q * Math.PI))} L${f(540 + w)} ${f(1320 - 30 * Math.sin(q * Math.PI))} L540 1320Z" fill="#e6dfca" stroke="${ST}" stroke-width="3"/>`;
  }
  // подпись дежурного: мелькает 2 кадра
  const tsig = Wt(9, 'ПОЧЕРК') - .1;
  if (t >= tsig && t < tsig + 2 / 30) s += `<text x="900" y="1300" text-anchor="end" font-family="Inter" font-style="italic" font-weight="900" font-size="40" fill="#c0392b">подп. ${INITIALS}</text>`;
  // крупно «12» на «двенадцать»
  const t12 = Wt(8, 'ДВЕНАДЦАТЬ');
  const hk = seg(t, t12, t12 + .2) * (1 - seg(t, tf - .2, tf));
  if (hk > 0) s += pcircle(735, 700, 46, hk, '#ffd23f', 6);
  const k = eio(seg(t, S(8), P(8, 2)));
  return cam(s, lerp(1.0, 1.22, k) - .12 * seg(t, tf, tf + .6), lerp(540, 640, k), lerp(980, 820, k));
}, .3);

// 8. Схема-план: маршрут обхода, служебный коридор вне маршрута
add(S(10) - .2, S(12) - .25, t => {
  let s = blueprint(t, 'СХЕМА №8 · МАРШРУТ ОБХОДА');
  const fl = [[120, 1000, 'ЭТАЖ 3'], [120, 1170, 'ЭТАЖ 2'], [120, 1340, 'ЭТАЖ 1']];
  // этажи и магазины
  fl.forEach(([x, y, nm], k) => {
    s += rect(x, y - 140, 640, 140, 'none', 'stroke="#fff" stroke-width="4"');
    for (let i = 1; i < 5; i++) s += `<line x1="${x + i * 128}" y1="${y - 140}" x2="${x + i * 128}" y2="${y - 50}" stroke="#fff" stroke-width="3"/>`;
    s += mono(x + 8, y - 12, nm, 22, '#a9cbf5');
  });
  // маршрут красным пунктиром: «змейка» по этажам
  const tr = P(10, 0);
  const pts = [[150, 1300], [730, 1300], [730, 1130], [150, 1130], [150, 960], [730, 960]];
  let tot = 0; const segL = []; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); segL.push(d); tot += d; }
  const rk = seg(t, tr, E(10)) * tot;
  let acc = 0;
  for (let i = 1; i < pts.length; i++) {
    const kk = clamp((rk - acc) / segL[i - 1]); acc += segL[i - 1];
    s += pline(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], kk, '#ff4040', 7, '18 12');
  }
  s += mono(440, 790, typeText('ВСЕ ЭТАЖИ · ВСЕ МАГАЗИНЫ', seg(t, P(10, 1), PE(10, 2))), 26, '#ff8080', 'middle');
  // служебный коридор
  const ck = seg(t, S(11), S(11) + .6);
  s += rect(800, 860, 190, 480, ck > 0 ? 'rgba(61,220,132,.15)' : 'none', `stroke="${ck > 0 ? '#3ddc84' : '#fff'}" stroke-width="${ck > 0 ? 8 : 4}"`);
  s += mono(895, 1100, 'СЛУЖ.', 24, ck > 0 ? '#3ddc84' : '#a9cbf5', 'middle') + mono(895, 1130, 'КОРИДОР', 24, ck > 0 ? '#3ddc84' : '#a9cbf5', 'middle');
  const nz = seg(t, Wt(11, 'НЕ'), Wt(11, 'ЗАХОДИТ') + .3);
  if (nz > 0) s += `<g opacity="${f(nz)}">${rect(780, 1380, 230, 60, '#22b45e', `rx="10" stroke="${ST}" stroke-width="4"`)}${txt(895, 1421, 'НЕ ЗАХОДИТ', 28, '#fff')}</g>`;
  return cam(s, lerp(1.0, 1.04, seg(t, S(10), S(12))), 540, 1080);
}, .3);

// 9. День 15: сетка мониторов
add(S(12) - .25, S(16) - .25, t => {
  const t13 = S(13), tPow = Wt(13, 'АВАРИЙНОГО'), t14 = S(14), t15 = S(15);
  const onF = i => {
    if (t < t13) return i === 4 ? 1 : .25;            // фудкорт подсвечен
    if (t < tPow) return Math.sin(t * 40 + i) > .3 ? .6 : .15; // мерцание
    if (t < t14) return 1;
    return seg(t, t14 + i * .07, t14 + i * .07 + .1);  // загораются 1..16
  };
  const o = { on: onF, hi: t < t13 ? 4 : (t > t15 + .2 ? 3 : -1), hero: t > PE(15, 0) };
  let s = monitors(t, o);
  if (t < t13) s += txt(monPos(4)[0] + MG.w / 2, monPos(4)[1] - 20, 'ЕДА ТУТ', 26, '#ffd23f');
  // счёт на экране с манекенами
  if (t > t15) {
    const [mx, my] = monPos(3);
    for (let k = 0; k < 13; k++) {
      const tk = lerp(t15 + .3, Wt(15, 'ТРИНАДЦАТЬ'), k / 12); const pk = popScale(t, tk, .15); if (pk <= 0) continue;
      s += `<g transform="translate(${mx + 14 + k * 14.5} ${my + 60}) scale(${f(pk)})"><circle r="7" fill="#e9edf5"/><text y="4" text-anchor="middle" font-family="Inter" font-weight="900" font-size="9" fill="#0d1018">${k + 1}</text></g>`;
    }
    // крошечный герой на экране фудкорта
    if (t > PE(15, 0)) s += rect(monPos(4)[0] - 8, monPos(4)[1] - 8, MG.w + 16, MG.h + 16, 'none', 'rx="10" stroke="#ff7a1a" stroke-width="5"');
  }
  // камера: общий → наезд на экран манекенов
  const zk = eio(seg(t, t15, t15 + 1.2));
  const [mx, my] = monPos(3);
  const zk2 = eio(seg(t, PE(15, 0) + .1, PE(15, 0) + .8));
  const cx = lerp(lerp(540, mx + MG.w / 2, zk), 540, zk2), cy = lerp(lerp(900, my + MG.h / 2, zk), 900, zk2);
  return cam(s, lerp(1, 2.6, zk) * (1 - zk2) + zk2 * 1.15, cx, cy);
}, .3);

// 10. День 18: на экране 12, пустое место; быстрые склейки
add(S(16) - .25, S(17) - .2, t => {
  const t12 = Wt(16, 'ДВЕНАДЦАТЬ'), tNo = P(16, 3);
  if (t > tNo + .2) {
    // быстрые склейки по другим экранам
    const order = [7, 2, 12, 8, 13, 9, 1, 5];
    const idx = Math.min(order.length - 1, Math.floor((t - tNo - .2) / .32));
    let s = rect(-400, -400, 1880, 2800, '#080b12');
    s += `<g transform="translate(90 600) scale(4.3)">${miniScene(order[idx], 0, 0, MG.w, MG.h, t)}</g>`;
    s += rect(90, 600, 903, 645, 'none', 'stroke="#2a3142" stroke-width="14"');
    s += mono(130, 1300, 'НЕТ', 40, '#ff4040');
    return s;
  }
  let s = rect(-400, -400, 1880, 2800, '#080b12');
  s += rect(60, 600, 960, 680, '#0c1622', `stroke="#2a3142" stroke-width="16"`);
  const N = 13, gap = 70, x0 = 120;
  for (let i = 0; i < N; i++) {
    if (i === 8) { s += `<ellipse cx="${x0 + i * gap}" cy="1160" rx="24" ry="5" fill="#3a3f4b"/>`; continue; }
    s += mannequin(x0 + i * gap, 1160, 300, { sw: 2.5 });
  }
  for (let k = 0; k < 6 * 680 / 6; k += 6) s += `<line x1="60" y1="${600 + k}" x2="1020" y2="${600 + k}" stroke="#000" stroke-width="2" opacity=".18"/>`;
  s += mono(80, 640, 'CAM 04 · ОДЕЖДА', 26, '#cfe0ff');
  let num = 0;
  for (let i = 0, c = 0; i < N; i++) {
    if (i === 8) continue;
    const tk = lerp(P(16, 1) + .2, t12, c / 11); c++;
    const pk = popScale(t, tk, .15); if (pk <= 0) continue; num = c;
    s += `<g transform="translate(${x0 + i * gap} 820) scale(${f(pk)})"><circle r="22" fill="#e9edf5" stroke="${ST}" stroke-width="3"/>${txt(0, 9, c, 24, '#0d1018')}</g>`;
  }
  if (t > t12) s += `<rect x="${x0 + 8 * gap - 40}" y="820" width="80" height="360" rx="10" fill="none" stroke="#ff4040" stroke-width="6" stroke-dasharray="14 10" opacity="${f(.5 + .5 * Math.sin(t * 10))}"/>` + txt(x0 + 8 * gap, 800, '?', 48, '#ff4040');
  return cam(s, lerp(1.0, 1.08, seg(t, S(16), tNo)), 540, 960);
}, .25);

// 11–14. Камера №16: запись, оборот, «стала ближе»
function cctv(t, figK, figX, figS) {
  // вид сверху-сзади: герой у мониторов, ч/б
  let s = rect(60, 520, 960, 760, '#2a2a2a');
  s += rect(60, 520, 960, 240, '#1a1a1a');
  for (let i = 0; i < 8; i++) s += rect(110 + i * 110, 560, 96, 70, '#5a5a5a', `stroke="#111" stroke-width="3"`) + rect(110 + i * 110, 650, 96, 70, '#4e4e4e', `stroke="#111" stroke-width="3"`);
  s += rect(80, 760, 920, 50, '#3a3a3a');
  s += `<path d="M60 1280 L60 810 L1020 810 L1020 1280" fill="none" stroke="#111" stroke-width="4"/>`;
  s += hero(540, 1100, 360, 'back');
  if (figK > 0) s += `<g opacity="${f(figK)}">${mannequin(figX, 1240, figS, { coat: false })}</g>`;
  return s;
}
function cctvFrame(t, inner, glitch = 0) {
  const id = 'gs' + gid++;
  let s = `<filter id="${id}"><feColorMatrix type="saturate" values="0"/></filter><g filter="url(#${id})">${inner}</g>`;
  for (let k = 0; k < 760; k += 5) s += `<line x1="60" y1="${520 + k}" x2="1020" y2="${520 + k}" stroke="#000" stroke-width="2" opacity=".22"/>`;
  if (glitch > 0) { const r = rng(Math.floor(t * 30)); for (let i = 0; i < 8; i++) { const y = 520 + r() * 760; s += rect(60 + (r() - .5) * 80, y, 960, 6 + r() * 30, '#fff', `opacity="${f(.25 * glitch)}"`); } }
  const sec = Math.floor(t) % 60;
  s += mono(90, 570, 'CAM 16 · ОХРАНА', 28, '#fff') + mono(990, 1250, `02:13:${String(sec).padStart(2, '0')}`, 30, '#fff', 'end');
  s += `<circle cx="960" cy="560" r="10" fill="#ff4040" opacity="${Math.sin(t * 6) > 0 ? 1 : .2}"/>`;
  s += rect(40, 500, 1000, 800, 'none', `rx="14" stroke="#2a3142" stroke-width="22"`);
  return s;
}
add(S(17) - .2, S(19) - .1, t => {
  const t16 = Wt(17, 'ШЕСТНАДЦАТЫЙ');
  if (t < t16) {
    // проверяет все экраны: подсветка бежит по сетке
    const i = Math.min(15, Math.floor(seg(t, S(17), t16) * 16));
    return monitors(t, { hi: i, hiCol: '#ffd23f', n13: 12, gap: 8 });
  }
  let s = rect(-400, -400, 1880, 2800, '#05070b');
  const fig = seg(t, Wt(18, 'СПИНОЙ'), Wt(18, 'СПИНОЙ') + .8);
  const tSp = P(18, 0);
  s += cctvFrame(t, cctv(t, fig, 820, 300), t > tSp - .1 && t < tSp + .1 ? 1 : 0);
  const zk = eio(seg(t, t16, t16 + .6));
  const fz = eio(seg(t, tSp, PE(18, 0)));
  return cam(s, lerp(1.0, 1.0, zk) + .15 * fz, lerp(540, 600, fz), 900);
}, .2);
HUDOFF.push([S(17) + .3, S(21) - .2]);

add(S(19) - .1, S(20) - .15, t => {
  // обернулся: комната в цвете, никого
  const tN = Wt(19, 'НИКОГО');
  let s = rect(-400, -400, 1880, 2800, '#11151d');
  s += rect(-400, 1350, 1880, 900, '#0d1016');
  s += rect(380, 560, 320, 790, '#05070b', `stroke="#2a3142" stroke-width="8"`);
  s += `<ellipse cx="540" cy="1250" rx="700" ry="500" fill="#3d7be0" opacity=".16"/>`;
  s += hero(540, 1500, 900, 'front');
  const k = seg(t, tN - .1, tN + .3);
  s += `<g opacity="${f(1 - k)}">${rect(-400, -400, 1880, 2800, '#05070b')}${hero(540, 1500, 900, 'back')}</g>`;
  return cam(s, lerp(1.25, 1.1, eout(seg(t, S(19), tN))), 540, lerp(1150, 1050, k));
}, .08);

add(S(20) - .15, S(21) - .15, t => {
  const tB = Wt(20, 'БЛИЖЕ');
  let s = rect(-400, -400, 1880, 2800, '#05070b');
  const near = t >= tB - .25;
  const g = (t > S(20) - .15 && t < S(20) + .05) || (t > tB - .27 && t < tB - .17) ? 1 : 0;
  s += cctvFrame(t, cctv(t, 1, near ? 640 : 820, near ? 470 : 300), g);
  const zk = eout(seg(t, tB - .25, tB + .4));
  return cam(s, 1 + zk * .45, lerp(540, 640, zk), lerp(900, 850, zk), g ? 1.5 : 0);
}, .08);
DRONE.push([S(16), .7], [S(17), .8], [Wt(18, 'ФИГУРА'), .2], [S(19), .0], [S(20), .0], [Wt(20, 'БЛИЖЕ') + .5, .0], [S(21) + .5, .45]);

// 15. Экран выбора
add(S(21) - .15, DUR + 1, t => {
  let s = `<g opacity=".25">${monitors(t, { n13: 12, gap: 8 })}</g>` + rect(-10, -10, 1100, 1940, '#000', 'opacity=".35"');
  s += choiceCard(t, 285, 900, '1', 'ВЫКЛЮЧИТЬ|КАМЕРЫ', ICON_SWITCH, Wt(21, 'ВЫКЛЮЧИТЬ'), '#ffd23f');
  s += choiceCard(t, 795, 900, '2', 'СМОТРЕТЬ|ДАЛЬШЕ', ICON_EYE, Wt(21, 'СМОТРЕТЬ'), '#ffd23f');
  const ok = seg(t, Wt(21, 'СМОТРЕТЬ'), Wt(21, 'СМОТРЕТЬ') + .3);
  if (ok > 0) s += `<g opacity="${f(ok)}"><circle cx="540" cy="900" r="52" fill="#0d1018" stroke="#9aa6bd" stroke-width="5"/>${txt(540, 914, 'ИЛИ', 34, '#e9edf5')}</g>`;
  const pk = popScale(t, P(21, 2));
  const pul = 1 + .03 * Math.sin(t * 6);
  if (pk > 0) s += `<g transform="translate(540 1250) scale(${(pk * pul).toFixed(3)})">${rect(-440, -48, 880, 96, '#e0322f', `rx="16" stroke="${ST}" stroke-width="5"`)}${txt(0, 16, 'ПИШИ 1 ИЛИ 2 — РЕШАЕТ БОЛЬШИНСТВО', 40, '#fff')}</g>`;
  if (pk > 0) s += mono(540, 1660, 'ЧАСТЬ 4 — ДЕНЬ 19', 34, '#9aa6bd', 'middle', `opacity="${f(seg(t, P(21, 2) + .4, P(21, 2) + .9))}"`);
  return s;
}, .3);

// ---------- HUD ----------
const DAYS = [[S(1), 12], [S(7), 13], [S(12), 15], [S(16), 18]];
DAYS.slice(1).forEach(([t]) => sfx(t, 'page', .9));
function dayAt(t) { let d = null, t0 = 0; for (const [tt, n] of DAYS) if (t >= tt) { d = n; t0 = tt; } return [d, t0]; }
function keyf(t, kf) {
  if (t <= kf[0][0]) return kf[0][1];
  for (let i = 1; i < kf.length; i++) if (t < kf[i][0]) return lerp(kf[i - 1][1], kf[i][1], eio(seg(t, kf[i - 1][0], kf[i][0])));
  return kf[kf.length - 1][1];
}
const tSafe = Wt(6, 'ЩЕЛЧОК');
const FOOD = [[0, 44], [S(12), 30], [P(12, 1), 30], [P(12, 1) + .6, 18], [S(15), 18], [PE(15, 0) + .5, 18], [E(15), 65], [S(16), 62]];
const CHARGE = [[0, 84], [S(7), 80], [S(12), 76], [S(16), 72]];
const SLEEP = [[0, 14], [S(11), 14], [S(11) + 1.5, 70], [S(12), 75], [S(16), 68]];
const WATER = [[0, 80], [S(7), 74], [S(12), 66], [S(16), 58]];
const DROPS = [P(12, 1) + .1, Wt(16, 'ДВЕНАДЦАТЬ')];
const PLATES = [
  [Wt(3, 'ЗАПЕРТА'), 'p', 'ДВЕРЬ ЗАПЕРТА', S(7) - .3],
  [S(5), 's', 'ОБМАНУТЬ ДАТЧИК', S(7) - .3],
  [P(7, 1), 'p', 'ГДЕ СПАТЬ?', S(12) - .3],
  [P(11, 1), 's', 'ВНЕ МАРШРУТА', S(12) - .3],
  [P(12, 1), 'p', 'ЕДА НА МАРШРУТЕ', S(16) - .3],
  [S(14), 's', '16 КАМЕР', S(16) - .3],
];
PLATES.forEach(([t]) => sfx(t, 'stamp', .8));
DROPS.forEach(t => sfx(t, 'alarm', .5));
const t12gone = Wt(16, 'ДВЕНАДЦАТЬ');

const elDay = document.getElementById('day'), elHud = document.getElementById('hud'), elPl = document.getElementById('plates');
const elB = [0, 1, 2, 3].map(i => document.getElementById('b' + i)), elV = [0, 1, 2, 3].map(i => document.getElementById('v' + i));
const elMC = document.getElementById('mcount'), elZ = document.getElementById('zone');
function renderHUD(t) {
  const [d, t0] = dayAt(t);
  let on = d !== null ? clamp((t - S(1)) / .3) : 0;
  HUDOFF.forEach(([a, b]) => { if (t > a && t < b) on = 0; });
  elHud.style.opacity = on;
  if (d !== null) {
    const fk = seg(t, t0, t0 + .35); const sy = fk < .5 ? 1 - fk * 2 : (fk - .5) * 2;
    const idx = DAYS.findIndex(x => x[1] === d); const shown = fk < .5 && idx > 0 ? DAYS[idx - 1][1] : d;
    elDay.innerHTML = `ДЕНЬ ${shown} <small>/ 365</small>`;
    elDay.style.transform = `scaleY(${Math.max(.02, sy).toFixed(3)})`;
  }
  const safe = t >= tSafe;
  const zk = seg(t, tSafe, tSafe + .2);
  elZ.textContent = safe ? 'ЗОНА: ВНЕ МАРШРУТА' : 'ЗОНА: НА МАРШРУТЕ';
  elZ.style.background = safe ? '#22b45e' : '#e0322f';
  elZ.style.transform = `scale(${f(safe && zk < 1 ? lerp(1.5, 1, eout(zk)) : 1)})`;
  const vals = [keyf(t, FOOD), keyf(t, CHARGE), keyf(t, SLEEP), keyf(t, WATER)];
  vals.forEach((v, i) => {
    elB[i].style.width = v.toFixed(1) + '%';
    elB[i].style.background = v < 20 ? '#ff4040' : v < 45 ? '#ffd23f' : (i === 3 ? '#6cc0ff' : '#e9edf5');
    elV[i].textContent = Math.round(v) + '%';
  });
  const n = t >= t12gone ? 12 : 13;
  elMC.innerHTML = `МАНЕКЕНЫ: <b style="color:${n === 12 ? '#ff4040' : '#fff'}">${n}</b>`;
  elMC.style.opacity = n === 12 ? (Math.sin(t * 12) > 0 ? 1 : .35) : 1;
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
  const a = S(2) - .1, b = P(3, 0) - .15;
  elTitle.style.opacity = (seg(t, a, a + .5) * (1 - seg(t, b - .4, b))).toFixed(2);
  elTitle.style.transform = `scale(${lerp(1.08, 1, eout(seg(t, a, a + 1.5))).toFixed(3)})`;
  let black = 0;
  if (t < .35) black = 1 - t / .35;
  black = Math.max(black, seg(t, S(2) - .45, S(2) - .2) * (1 - seg(t, S(2) - .2, S(2) + .2))); // затемнение перед заставкой
  if (t > DUR - .6) black = Math.max(black, seg(t, DUR - .6, DUR));
  document.getElementById('flash').style.opacity = black.toFixed(2);
}

// ---------- звуки ----------
(function () {
  sfx(Wt(0, 'БЕЖАТЬ'), 'stamp', 1.1);
  sfx(S(1), 'breath', .7, { d: P(1, 2) - S(1) });
  for (let i = 0; i < 16; i++) sfx(S(1) + .1 + i * .3, 'step', .55);
  for (let i = 0; i < 6; i++) sfx(P(1, 2) + .1 + i * .42, 'clack', .75, { pan: -.4 });
  sfx(S(2) - .1, 'boom', 1);
  sfx(Wt(3, 'ЗАПЕРТА'), 'knock', .7);
  for (let i = 0; i < 6; i++) sfx(S(3) + .3 + i * .7, 'clack', .4, { pan: -.6 });
  sfx(S(4) + .05, 'pencil', .6, { d: 3 });
  sfx(Wt(5, 'РАЗОГНУЛ'), 'scrape', .6); sfx(Wt(5, 'ПРИВЯЗАЛ'), 'sand', .6, { d: .8 });
  sfx(Wt(5, 'ПОМАХАЛ'), 'sand', .7, { d: 1.2 });
  sfx(Wt(6, 'ЩЕЛЧОК'), 'click', 1); sfx(Wt(6, 'ЩЕЛЧОК') + .05, 'clack', .8);
  for (let i = 0; i < 5; i++) sfx(P(6, 1) + .2 + i * .45, 'knock', .55 - i * .07);
  sfx(S(7), 'buzz', .4);
  sfx(P(8, 1), 'page', .5);
  for (let i = 0; i < 16; i++) sfx(S(9) + i * (E(9) - S(9)) / 16, 'page', .35);
  sfx(S(10), 'pencil', .6, { d: 4 });
  sfx(S(11) + .2, 'chime', .5);
  sfx(S(13), 'buzz', .5); sfx(Wt(13, 'АВАРИЙНОГО'), 'static', .5, { d: .8 });
  for (let i = 0; i < 16; i++) sfx(S(14) + i * .07, 'click', .35);
  for (let i = 0; i < 13; i++) sfx(lerp(S(15) + .3, Wt(15, 'ТРИНАДЦАТЬ'), i / 12), 'tick', .45);
  for (let i = 0; i < 12; i++) sfx(lerp(P(16, 1) + .2, Wt(16, 'ДВЕНАДЦАТЬ'), i / 11), 'tick', .5);
  for (let i = 0; i < 8; i++) sfx(P(16, 3) + .2 + i * .32, 'click', .5);
  for (let i = 0; i < 6; i++) sfx(S(17) + i * .3, 'click', .35);
  sfx(Wt(17, 'ШЕСТНАДЦАТЫЙ'), 'static', .5, { d: .6 });
  sfx(Wt(18, 'ФИГУРА'), 'static', .35, { d: 1.5 });
  sfx(S(19) + .05, 'whoosh', .7);
  sfx(S(20) - .15, 'static', .6, { d: .4 });
  sfx(Wt(20, 'БЛИЖЕ') - .25, 'boom', 1.1); sfx(Wt(20, 'БЛИЖЕ') - .25, 'static', .7, { d: .5 });
  for (let i = 0; i < 14; i++) sfx(S(21) + .4 + i * .5, 'tick', .45);
  sfx(Wt(21, 'ВЫКЛЮЧИТЬ'), 'pop', .6); sfx(Wt(21, 'СМОТРЕТЬ'), 'pop', .6); sfx(P(21, 2), 'stamp', .9);
  DRONE.sort((a, b) => a[0] - b[0]).forEach(([t, v]) => sfx(t, 'drone_kf', v));
  sfx(DUR - 2.5, 'drone_kf', .4); sfx(DUR, 'drone_kf', 0);
})();

// обложка
window.COVER = function () {
  let s = monitors(3, { hi: 15, hiCol: '#ff4040' });
  const [x, y] = monPos(15);
  s += `<g transform="translate(${x} ${y}) scale(${(MG.w / 960).toFixed(4)}) translate(-60 -520)">${cctvFrame(3, cctv(3, 1, 680, 430), 0)}</g>`;
  s += rect(x - 10, y - 10, MG.w + 20, MG.h + 20, 'none', 'rx="10" stroke="#ff4040" stroke-width="10"');
  return cam(s, 2.1, x + MG.w / 2 - 60, y + MG.h / 2 - 120);
};
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
  if (!c || (t > S(2) - .2 && t < P(3, 0) - .1)) { elSub.innerHTML = ''; return; } // на названии субтитров нет
  let h = '<div class="ln">';
  c.forEach(w => {
    const k = seg(t, w.t0 - .03, w.t0 + .09);
    const sc = k <= 0 ? .8 : lerp(.8, 1, eout(k));
    h += `<span class="w ${w.c || ''}" style="opacity:${k.toFixed(2)};transform:scale(${sc.toFixed(3)})">${w.w}</span> `;
  });
  elSub.innerHTML = h + '</div>';
}

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
