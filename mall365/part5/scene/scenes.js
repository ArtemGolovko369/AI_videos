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
  if (!c || (t > S(3) - .2 && t < P(4, 0) - .1)) { elSub.innerHTML = ''; return; } // на названии субтитров нет
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
