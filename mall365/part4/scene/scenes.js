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

// ================= ЧАСТЬ 4 · «Мой почерк» =================
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
