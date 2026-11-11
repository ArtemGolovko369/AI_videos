// ВЫЖИВАНИЕ В ЛЕСУ — общий модуль рисовки (SVG-строки).
// Используется и для листа персонажей, и для рендера анимации.

const PAL = {
  night0: '#0a0e1a', night1: '#121829', night2: '#1b2236', night3: '#262c44',
  plum: '#2b2438', plum2: '#372d45',
  wood0: '#1f1822', wood1: '#2a2129', wood2: '#352a31', wood3: '#433439',
  fire0: '#fff1b8', fire1: '#ffc75a', fire2: '#ff8a2a', fire3: '#d9481c',
  glow: '#ffb347',
  skin: '#e6b594', skinSh: '#c08b6c', skinCold: '#b9a4a0',
  snow: '#c9d4e8',
  // Света — тёплая
  sJacket: '#de8a2c', sJacketSh: '#a95f17', sStripe: '#efe3c4', sHair: '#6a3520', sHairSh: '#4a2314', sJeans: '#34435f',
  // Марина — холодная
  mJacket: '#2b3b5c', mJacketSh: '#1c2840', mHair: '#b8a27c', mHairSh: '#8f7a58', mPants: '#1d2333', badge: '#d8b23a',
  // Старый хозяин
  oCoat: '#4a4a3b', oCoatSh: '#33332a', oHat: '#2a241f', oBeard: '#8d877a', oShadow: '#15140f', oEye: '#f0e6c2',
  red: '#e4473b', yellow: '#ffd34d',
};

// детерминированный генератор случайных чисел
function rng(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

// ---------- общие фильтры и эффекты ----------
function defs() {
  return `
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="table" tableValues="0 0.10"/></feComponentTransfer>
    <feComposite in2="SourceGraphic" operator="in"/>
  </filter>
  <filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blur20"><feGaussianBlur stdDeviation="20"/></filter>
  <filter id="blur40"><feGaussianBlur stdDeviation="40"/></filter>
  <radialGradient id="vign" cx="50%" cy="48%" r="70%">
    <stop offset="55%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0.85"/>
  </radialGradient>
  <radialGradient id="fireGlow">
    <stop offset="0%" stop-color="${PAL.fire1}" stop-opacity="0.75"/>
    <stop offset="35%" stop-color="${PAL.fire2}" stop-opacity="0.30"/>
    <stop offset="100%" stop-color="${PAL.fire2}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="coldGlow">
    <stop offset="0%" stop-color="#9fb4d8" stop-opacity="0.45"/>
    <stop offset="100%" stop-color="#9fb4d8" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="skyNight" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#070a14"/><stop offset="100%" stop-color="#1c2338"/>
  </linearGradient>
  <linearGradient id="skyDay" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#9aa3a6"/><stop offset="100%" stop-color="#c9c7bd"/>
  </linearGradient>`;
}

// Затемнение сцены: всё тёмное, кроме пятен света. lights: [{x,y,r,a}]
function darkness(w, h, lights, amount = 0.82, id = 'dk') {
  const holes = lights.map((l, i) => `
    <radialGradient id="${id}g${i}" cx="${l.x}" cy="${l.y}" r="${l.r}" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#000" stop-opacity="${l.a ?? 1}"/>
      <stop offset="60%" stop-color="#000" stop-opacity="${(l.a ?? 1) * 0.45}"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0"/>
    </radialGradient>`).join('');
  const circles = lights.map((l, i) => `<circle cx="${l.x}" cy="${l.y}" r="${l.r}" fill="url(#${id}g${i})"/>`).join('');
  return `<defs>${holes}<mask id="${id}m"><rect width="${w}" height="${h}" fill="#fff"/>${circles}</mask></defs>
  <rect width="${w}" height="${h}" fill="#05060c" opacity="${amount}" mask="url(#${id}m)"/>`;
}

function warmLight(x, y, r, a = 1) {
  return `<circle cx="${x}" cy="${y}" r="${r}" fill="url(#fireGlow)" opacity="${a}" style="mix-blend-mode:screen"/>`;
}

function vignette(w, h, a = 1) { return `<rect width="${w}" height="${h}" fill="url(#vign)" opacity="${a}"/>`; }
function grain(w, h) { return `<rect width="${w}" height="${h}" fill="#888" filter="url(#grain)"/>`; }

// ---------- лица ----------
// opts: blink (0..1), mouth 0/1/2, emo: neutral|scared|smirk|serious|smile
function eyes(cx, cy, gap, o) {
  const emo = o.emo || 'neutral';
  const look = o.look || 0; // -1..1 взгляд по горизонтали
  let out = '';
  for (const side of [-1, 1]) {
    const x = cx + side * gap;
    if (o.blink) {
      out += `<path d="M${x - 13} ${cy + 2} Q${x} ${cy + 9} ${x + 13} ${cy + 2}" stroke="#2a1a14" stroke-width="4" fill="none" stroke-linecap="round"/>`;
    } else {
      const ry = emo === 'scared' ? 19 : emo === 'smirk' && side === 1 ? 12 : 16;
      const pr = emo === 'scared' ? 5.5 : 8;
      out += `<ellipse cx="${x}" cy="${cy}" rx="13" ry="${ry}" fill="#f6f1ea"/>
        <circle cx="${x + look * 4}" cy="${cy + 2}" r="${pr}" fill="#241712"/>
        <circle cx="${x + look * 4 + 2.5}" cy="${cy - 2}" r="2.6" fill="#fff"/>`;
      if (emo === 'smirk' && side === 1) out += `<rect x="${x - 15}" y="${cy - 20}" width="30" height="10" fill="${o.skin || PAL.skin}"/>`;
    }
    // брови
    const by = cy - 27;
    let d;
    if (emo === 'scared') d = side < 0 ? `M${x - 14} ${by + 2} L${x + 12} ${by - 8}` : `M${x - 12} ${by - 8} L${x + 14} ${by + 2}`;
    else if (emo === 'serious') d = side < 0 ? `M${x - 14} ${by - 4} L${x + 12} ${by + 4}` : `M${x - 12} ${by + 4} L${x + 14} ${by - 4}`;
    else if (emo === 'smirk') d = side < 0 ? `M${x - 14} ${by - 2} L${x + 12} ${by - 6}` : `M${x - 12} ${by + 2} L${x + 14} ${by + 2}`;
    else d = `M${x - 13} ${by} Q${x} ${by - 6} ${x + 13} ${by}`;
    out += `<path d="${d}" stroke="${o.brow || '#3a2016'}" stroke-width="5.5" stroke-linecap="round" fill="none"/>`;
  }
  return out;
}

function mouth(cx, cy, o) {
  const m = o.mouth || 0, emo = o.emo || 'neutral';
  if (m === 2) return `<ellipse cx="${cx}" cy="${cy + 4}" rx="11" ry="13" fill="#4a1d1a"/><ellipse cx="${cx}" cy="${cy + 11}" rx="6" ry="4" fill="#c4615a"/>`;
  if (m === 1) return `<ellipse cx="${cx}" cy="${cy + 2}" rx="9" ry="6" fill="#4a1d1a"/>`;
  if (emo === 'smirk') return `<path d="M${cx - 12} ${cy + 2} Q${cx + 2} ${cy + 6} ${cx + 15} ${cy - 5}" stroke="#5a2a22" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  if (emo === 'smile') return `<path d="M${cx - 13} ${cy - 2} Q${cx} ${cy + 10} ${cx + 13} ${cy - 2}" stroke="#5a2a22" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  if (emo === 'scared') return `<path d="M${cx - 10} ${cy + 4} Q${cx} ${cy - 3} ${cx + 10} ${cy + 4}" stroke="#5a2a22" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  return `<path d="M${cx - 10} ${cy} L${cx + 10} ${cy}" stroke="#5a2a22" stroke-width="4" stroke-linecap="round"/>`;
}

// ---------- СВЕТА ----------
// Курьер, 38. Каштановые волосы в хвост, оранжевая курьерская куртка со светоотражающей полосой, короб за спиной.
function sveta(o = {}) {
  const skin = o.cold ? PAL.skinCold : PAL.skin;
  const armL = o.armL ?? 0, armR = o.armR ?? 0; // поворот рук в градусах
  return `<g>
    <!-- короб за спиной -->
    <rect x="124" y="226" width="152" height="190" rx="14" fill="#9c5414"/>
    <rect x="124" y="226" width="152" height="24" rx="10" fill="#b66419"/>
    <!-- ноги -->
    <rect x="152" y="560" width="42" height="190" rx="18" fill="${PAL.sJeans}"/>
    <rect x="206" y="560" width="42" height="190" rx="18" fill="${PAL.sJeans}"/>
    <rect x="204" y="560" width="12" height="190" fill="#2a3650" opacity=".6"/>
    <ellipse cx="170" cy="756" rx="30" ry="16" fill="#241c19"/>
    <ellipse cx="230" cy="756" rx="30" ry="16" fill="#241c19"/>
    <!-- руки -->
    <g transform="rotate(${armL} 138 330)">
      <rect x="104" y="318" width="44" height="210" rx="22" fill="${PAL.sJacketSh}"/>
      <rect x="104" y="440" width="44" height="14" fill="${PAL.sStripe}" opacity=".8"/>
      <circle cx="126" cy="532" r="20" fill="${skin}"/>
    </g>
    <g transform="rotate(${armR} 262 330)">
      <rect x="252" y="318" width="44" height="210" rx="22" fill="${PAL.sJacketSh}"/>
      <rect x="252" y="440" width="44" height="14" fill="${PAL.sStripe}" opacity=".8"/>
      <circle cx="274" cy="532" r="20" fill="${skin}"/>
      ${o.match ? `<rect x="270" y="470" width="6" height="52" rx="2" fill="#d9c08a" transform="rotate(-20 274 520)"/><circle cx="262" cy="468" r="10" fill="${PAL.fire1}"/><circle cx="262" cy="460" r="22" fill="url(#fireGlow)"/>` : ''}
    </g>
    <!-- куртка -->
    <path d="M140 310 Q200 290 260 310 L276 580 Q200 600 124 580 Z" fill="${PAL.sJacket}"/>
    <path d="M200 300 L200 590" stroke="${PAL.sJacketSh}" stroke-width="5"/>
    <rect x="128" y="470" width="144" height="16" fill="${PAL.sStripe}" opacity=".9"/>
    <rect x="216" y="500" width="40" height="32" rx="4" fill="${PAL.sJacketSh}"/>
    <!-- лямки короба -->
    <path d="M150 312 L162 460" stroke="#6b3a10" stroke-width="12" stroke-linecap="round"/>
    <path d="M250 312 L238 460" stroke="#6b3a10" stroke-width="12" stroke-linecap="round"/>
    <!-- воротник -->
    <path d="M160 298 Q200 330 240 298 L232 284 Q200 304 168 284 Z" fill="${PAL.sJacketSh}"/>
    <!-- голова -->
    <rect x="186" y="262" width="28" height="30" fill="${PAL.skinSh}"/>
    <path d="M254 150 Q300 175 286 250 Q282 232 262 214 Z" fill="${PAL.sHairSh}"/>
    <ellipse cx="200" cy="200" rx="66" ry="76" fill="${skin}"/>
    <path d="M132 200 Q128 118 200 116 Q276 116 270 196 Q256 152 214 148 Q190 172 150 170 Q138 186 132 200 Z" fill="${PAL.sHair}"/>
    <circle cx="200" cy="120" r="10" fill="${PAL.sHairSh}"/>
    <ellipse cx="160" cy="228" rx="11" ry="6" fill="#e48a74" opacity=".35"/>
    <ellipse cx="240" cy="228" rx="11" ry="6" fill="#e48a74" opacity=".35"/>
    ${eyes(200, 202, 26, { ...o, skin })}
    ${mouth(200, 245, o)}
  </g>`;
}

// ---------- МАРИНА ----------
// Полицейская, одноклассница. Пепельно-русые волосы в пучок, тёмно-синяя форменная куртка, жетон, фонарик.
function marina(o = {}) {
  const skin = o.cold ? PAL.skinCold : PAL.skin;
  const armR = o.armR ?? 0, armL = o.armL ?? 0;
  return `<g>
    <!-- ноги -->
    <rect x="154" y="580" width="40" height="172" rx="16" fill="${PAL.mPants}"/>
    <rect x="206" y="580" width="40" height="172" rx="16" fill="${PAL.mPants}"/>
    <ellipse cx="172" cy="756" rx="30" ry="15" fill="#0e1018"/>
    <ellipse cx="228" cy="756" rx="30" ry="15" fill="#0e1018"/>
    <!-- руки -->
    <g transform="rotate(${armL} 140 330)">
      <rect x="106" y="318" width="42" height="216" rx="21" fill="${PAL.mJacketSh}"/>
      <circle cx="127" cy="538" r="19" fill="${skin}"/>
    </g>
    <g transform="rotate(${armR} 260 330)">
      <rect x="252" y="318" width="42" height="216" rx="21" fill="${PAL.mJacketSh}"/>
      <circle cx="273" cy="538" r="19" fill="${skin}"/>
      ${o.torch ? `<rect x="262" y="500" width="22" height="70" rx="6" fill="#202020"/><rect x="258" y="566" width="30" height="16" rx="4" fill="#3a3a3a"/>` : ''}
      ${o.stick ? `<rect x="266" y="430" width="12" height="130" rx="5" fill="#4a3020" transform="rotate(8 272 540)"/><ellipse cx="282" cy="420" rx="18" ry="30" fill="${PAL.fire2}"/><ellipse cx="282" cy="428" rx="9" ry="16" fill="${PAL.fire0}"/><circle cx="282" cy="420" r="70" fill="url(#fireGlow)"/>` : ''}
    </g>
    <!-- куртка -->
    <path d="M140 310 Q200 292 260 310 L272 610 Q200 626 128 610 Z" fill="${PAL.mJacket}"/>
    <path d="M200 300 L200 616" stroke="${PAL.mJacketSh}" stroke-width="5"/>
    <rect x="132" y="560" width="136" height="16" fill="#151b2a"/>
    <rect x="190" y="556" width="20" height="24" rx="3" fill="#8c8f99"/>
    <path d="M148 308 L176 314 L172 330 L144 324 Z" fill="#3d5280"/>
    <path d="M252 308 L224 314 L228 330 L256 324 Z" fill="#3d5280"/>
    <path d="M232 380 l12 -8 l12 8 l-2 18 l-10 8 l-10 -8 Z" fill="${PAL.badge}"/>
    <rect x="148" y="390" width="40" height="30" rx="4" fill="${PAL.mJacketSh}"/>
    <path d="M162 296 Q200 330 238 296 L232 282 Q200 304 168 282 Z" fill="${PAL.mJacketSh}"/>
    <!-- голова -->
    <rect x="186" y="262" width="28" height="30" fill="${PAL.skinSh}"/>
    <circle cx="200" cy="112" r="30" fill="${PAL.mHair}"/>
    <ellipse cx="200" cy="200" rx="64" ry="76" fill="${skin}"/>
    <path d="M134 196 Q130 122 200 120 Q272 122 266 196 Q252 158 200 150 Q150 158 134 196 Z" fill="${PAL.mHair}"/>
    <path d="M150 160 Q190 150 222 140" stroke="${PAL.mHairSh}" stroke-width="4" fill="none"/>
    ${eyes(200, 204, 25, { ...o, skin, brow: '#6a5a40' })}
    ${mouth(200, 246, o)}
  </g>`;
}

// ---------- СТАРЫЙ ХОЗЯИН ----------
// Высокий, сутулый, в ватнике и ушанке. Лицо в тени — видны только блики глаз и улыбка.
function owner(o = {}) {
  const smile = o.smile ?? 1; // 0..1 ширина улыбки
  const sil = o.silhouette;
  const coat = sil ? '#07080c' : PAL.oCoat, coatSh = sil ? '#050609' : PAL.oCoatSh;
  const stitches = sil ? '' : [0, 1, 2, 3, 4, 5].map(i => `<path d="M130 ${360 + i * 50} Q205 ${370 + i * 50} 280 ${360 + i * 50}" stroke="${PAL.oCoatSh}" stroke-width="4" fill="none"/>`).join('');
  const sw = 22 + 26 * smile; const face = o.face && !sil;
  return `<g transform="rotate(4 200 760)">
    <rect x="150" y="610" width="44" height="146" rx="12" fill="${sil ? '#06070a' : '#24231d'}"/>
    <rect x="212" y="610" width="44" height="146" rx="12" fill="${sil ? '#06070a' : '#24231d'}"/>
    <ellipse cx="170" cy="758" rx="32" ry="14" fill="#0a0a08"/><ellipse cx="236" cy="758" rx="32" ry="14" fill="#0a0a08"/>
    <!-- длинные руки -->
    <rect x="94" y="320" width="46" height="290" rx="22" fill="${coatSh}" transform="rotate(6 117 330)"/>
    <rect x="268" y="320" width="46" height="290" rx="22" fill="${coatSh}" transform="rotate(-6 291 330)"/>
    <ellipse cx="96" cy="616" rx="20" ry="26" fill="${sil ? '#06070a' : '#8f7a68'}"/>
    <ellipse cx="312" cy="616" rx="20" ry="26" fill="${sil ? '#06070a' : '#8f7a68'}"/>
    <!-- ватник -->
    <path d="M128 316 Q205 280 282 316 L292 630 Q205 650 118 630 Z" fill="${coat}"/>
    ${stitches}
    <path d="M205 300 L205 640" stroke="${coatSh}" stroke-width="6"/>
    <!-- голова наклонена вперёд -->
    <g transform="translate(10 6)">
      <ellipse cx="200" cy="214" rx="62" ry="74" fill="${sil ? '#07080c' : '#5c4d42'}"/>
      ${sil ? '' : `<path d="M142 236 Q200 330 258 236 Q250 300 200 312 Q150 300 142 236 Z" fill="${PAL.oBeard}"/>`}
      ${face ? `<ellipse cx="200" cy="205" rx="56" ry="58" fill="#b88f74"/>` : `<ellipse cx="200" cy="200" rx="58" ry="60" fill="${PAL.oShadow}" opacity="${sil ? 1 : .8}"/>`}
      <!-- ушанка -->
      <path d="M128 196 Q126 118 200 112 Q276 118 272 196 L262 196 Q254 150 200 148 Q146 150 138 196 Z" fill="${PAL.oHat}"/>
      <rect x="126" y="186" width="24" height="70" rx="10" fill="${PAL.oHat}"/>
      <rect x="250" y="186" width="24" height="70" rx="10" fill="${PAL.oHat}"/>
      <path d="M132 150 Q200 128 268 150" stroke="#3a322b" stroke-width="16" fill="none" stroke-linecap="round"/>
      ${face ? `<circle cx="178" cy="204" r="6" fill="#2a1d16"/><circle cx="222" cy="204" r="6" fill="#2a1d16"/>
      <path d="M162 188 L190 182 M210 182 L238 188" stroke="#4a3a30" stroke-width="5" stroke-linecap="round"/>
      <path d="M186 246 Q200 238 214 246" stroke="#4a2a22" stroke-width="4" fill="none"/>` : `
      <!-- глаза-блики -->
      <ellipse cx="176" cy="200" rx="7" ry="${o.blink ? 1 : 5}" fill="${PAL.oEye}"/>
      <ellipse cx="224" cy="200" rx="7" ry="${o.blink ? 1 : 5}" fill="${PAL.oEye}"/>
      ${smile > 0.05 ? `<!-- улыбка -->
      <path d="M${200 - sw} 236 Q200 ${262 + 14 * smile} ${200 + sw} 236 Q200 ${248 + 6 * smile} ${200 - sw} 236 Z" fill="#efe7d0"/>
      <path d="M${200 - sw} 236 Q200 ${262 + 14 * smile} ${200 + sw} 236" stroke="#2a1f18" stroke-width="2.5" fill="none"/>
      ${[...Array(7)].map((_, i) => { const x = 200 - sw + (i + 1) * (2 * sw / 8); return `<path d="M${x} 240 L${x} ${250 + 8 * smile}" stroke="#2a1f18" stroke-width="2"/>`; }).join('')}` : `<path d="M182 242 L218 242" stroke="#efe7d0" stroke-width="3" opacity=".6"/>`}`}
    </g>
  </g>`;
}

// ---------- РЕКВИЗИТ ----------
function fir(x, y, h, color) {
  const w = h * 0.42;
  return `<path d="M${x} ${y - h} L${x + w * 0.55} ${y - h * 0.62} L${x + w * 0.3} ${y - h * 0.62} L${x + w * 0.8} ${y - h * 0.28} L${x + w * 0.45} ${y - h * 0.28} L${x + w} ${y} L${x - w} ${y} L${x - w * 0.45} ${y - h * 0.28} L${x - w * 0.8} ${y - h * 0.28} L${x - w * 0.3} ${y - h * 0.62} L${x - w * 0.55} ${y - h * 0.62} Z" fill="${color}"/>`;
}

function snowStreaks(w, h, n, seed, t = 0, a = 0.5) {
  const r = rng(seed); let s = '';
  for (let i = 0; i < n; i++) {
    const x = ((r() * (w + 400) + t * 260 * (0.7 + r() * 0.6)) % (w + 400)) - 200;
    const y = ((r() * h + t * 900 * (0.6 + r() * 0.8)) % h);
    const len = 18 + r() * 30;
    s += `<line x1="${x}" y1="${y}" x2="${x - len * 0.35}" y2="${y - len}" stroke="${PAL.snow}" stroke-width="${2 + r() * 2.5}" stroke-linecap="round" opacity="${a * (0.4 + r() * 0.6)}"/>`;
  }
  return s;
}

function stars(x0, y0, w, h, n, seed, t = 0) {
  const r = rng(seed); let s = '';
  for (let i = 0; i < n; i++) {
    const tw = 0.5 + 0.5 * Math.sin(t * (1 + r() * 3) + i);
    s += `<circle cx="${x0 + r() * w}" cy="${y0 + r() * h}" r="${1.2 + r() * 2.4}" fill="#e8ecff" opacity="${0.3 + 0.7 * tw}"/>`;
  }
  return s;
}

function flame(x, y, s = 1, t = 0) {
  const f = 1 + 0.08 * Math.sin(t * 17) + 0.05 * Math.sin(t * 29);
  return `<g transform="translate(${x} ${y}) scale(${s} ${s * f})">
    <path d="M0 0 C-60 -10 -50 -90 -10 -150 C-6 -110 20 -100 16 -140 C60 -90 70 -10 0 0 Z" fill="${PAL.fire3}"/>
    <path d="M0 0 C-40 -8 -34 -70 -6 -110 C-2 -80 16 -76 14 -100 C44 -64 46 -8 0 0 Z" fill="${PAL.fire2}"/>
    <path d="M0 0 C-22 -6 -18 -44 0 -66 C18 -44 22 -6 0 0 Z" fill="${PAL.fire1}"/>
    <path d="M0 -4 C-10 -6 -8 -24 0 -34 C8 -24 10 -6 0 -4 Z" fill="${PAL.fire0}"/>
  </g>`;
}

function note(x, y, s = 1, rot = -4, sign = "#2a2420") {
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
    <rect x="-150" y="-100" width="300" height="200" fill="#d8ccae"/>
    <path d="M-150 -100 L150 -100 L150 90 L130 100 L-150 100 Z" fill="#e4d8bb"/>
    <text x="0" y="-38" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-weight="bold" font-size="30" fill="#2a2420">НОЧУЙТЕ.</text>
    <text x="0" y="6" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-weight="bold" font-size="26" fill="#2a2420">ПОДВАЛ</text>
    <text x="0" y="40" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-weight="bold" font-size="26" fill="#2a2420">НЕ ОТКРЫВАТЬ.</text>
    <text x="40" y="82" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-size="22" fill="${sign}">— ХОЗЯИН</text>
  </g>`;
}
var o_noteRed = '#2a2420';

function matchbox(x, y, s = 1, count = 3) {
  let m = '';
  for (let i = 0; i < count; i++) m += `<rect x="${-70 + i * 26}" y="-38" width="12" height="120" rx="3" fill="#e3c98f"/><ellipse cx="${-64 + i * 26}" cy="-40" rx="10" ry="13" fill="#9b2a1c"/>`;
  return `<g transform="translate(${x} ${y}) scale(${s})">
    <rect x="-110" y="-60" width="220" height="160" rx="8" fill="#3a2a1c"/>
    <rect x="-100" y="-50" width="200" height="140" rx="6" fill="#5a4430"/>
    ${m}
    <rect x="-120" y="70" width="240" height="70" rx="6" fill="#b3402a"/>
    <rect x="-120" y="70" width="240" height="16" fill="#6b4a32"/>
    <text x="0" y="122" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-weight="bold" font-size="30" fill="#f1d9a8">СПИЧКИ</text>
  </g>`;
}

function photo(x, y, s = 1, rot = 3) {
  return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">
    <rect x="-150" y="-120" width="300" height="240" fill="#e6dfcf"/>
    <rect x="-134" y="-104" width="268" height="190" fill="#8f8a7c"/>
    <rect x="-134" y="-104" width="268" height="110" fill="#b3ae9f"/>
    <path d="M-90 30 L-90 -30 L0 -80 L90 -30 L90 30 Z" fill="#5d564a"/>
    <path d="M-104 -24 L0 -88 L104 -24" stroke="#3d382f" stroke-width="12" fill="none"/>
    <rect x="-60" y="-18" width="30" height="30" fill="#2e2a24"/><rect x="30" y="-18" width="30" height="30" fill="#2e2a24"/>
    <rect x="-20" y="30" width="80" height="12" fill="#4a443a"/>
    <!-- мужчина на крыльце -->
    <rect x="-8" y="-12" width="24" height="46" rx="8" fill="#3a382f"/>
    <circle cx="4" cy="-22" r="12" fill="#3a382f"/>
    <rect x="-134" y="40" width="268" height="46" fill="#7c776a"/>
  </g>`;
}

function mug(x, y, s = 1, t = 0, steam = true) {
  let st = '';
  if (steam) for (let i = 0; i < 3; i++) {
    const k = ((t * 0.6 + i / 3) % 1);
    st += `<path d="M${-14 + i * 14} ${-60 - k * 90} q12 -20 0 -40 q-12 -20 0 -40" stroke="#d9dde6" stroke-width="5" fill="none" stroke-linecap="round" opacity="${0.5 * (1 - k)}"/>`;
  }
  return `<g transform="translate(${x} ${y}) scale(${s})">
    ${st}
    <rect x="-40" y="-50" width="80" height="90" rx="10" fill="#6a7a8a"/>
    <ellipse cx="0" cy="-50" rx="40" ry="10" fill="#3a2a1e"/>
    <path d="M40 -30 q34 0 34 28 q0 28 -34 28" stroke="#6a7a8a" stroke-width="12" fill="none"/>
    <circle cx="-14" cy="-10" r="6" fill="#d8dfe6" opacity=".6"/>
  </g>`;
}

// ---------- ЛОКАЦИИ (1080×1920) ----------
const W = 1080, H = 1920;

// Изба внутри. opts: fire (0..1), hatch: closed|ajar|open, light: [{x,y,r}], t, holeStars
function bgInterior(o = {}) {
  const r = rng(3); let planks = '';
  for (let i = 0; i < 14; i++) planks += `<rect x="${i * 80}" y="0" width="78" height="1300" fill="${[PAL.wood1, PAL.wood2, PAL.wood1, '#2e242b'][i % 4]}"/><line x1="${i * 80 + 78}" y1="0" x2="${i * 80 + 78}" y2="1300" stroke="#140f15" stroke-width="3"/>`;
  let floor = '';
  for (let i = 0; i < 8; i++) floor += `<rect x="0" y="${1300 + i * 80}" width="${W}" height="78" fill="${i % 2 ? PAL.wood0 : '#241c22'}"/>`;
  const hatch = o.hatch || 'closed';
  const hx = 640, hy = 1560;
  let hatchSvg = '';
  const quad = `M${hx - 170} ${hy - 55} L${hx + 170} ${hy - 55} L${hx + 205} ${hy + 65} L${hx - 205} ${hy + 65} Z`;
  if (hatch === 'closed') hatchSvg = `<path d="${quad}" fill="#2c2228" stroke="#120d12" stroke-width="6"/>
     <path d="M${hx - 185} ${hy - 15} L${hx + 185} ${hy - 15} M${hx - 195} ${hy + 25} L${hx + 195} ${hy + 25}" stroke="#120d12" stroke-width="3"/>
     <ellipse cx="${hx}" cy="${hy + 5}" rx="22" ry="12" fill="none" stroke="#6b6460" stroke-width="6"/>`;
  else {
    const open = hatch === 'open' ? 1 : 0.4;
    hatchSvg = `<path d="${quad}" fill="#020204"/>
     <ellipse cx="${hx}" cy="${hy}" rx="260" ry="110" fill="url(#coldGlow)" opacity="${0.7 * open}"/>
     <path d="M${hx - 170} ${hy - 55} L${hx + 170} ${hy - 55} L${hx + 160} ${hy - 55 - 200 * open} L${hx - 160} ${hy - 55 - 200 * open} Z" fill="#3a2e35" stroke="#120d12" stroke-width="6"/>
     <ellipse cx="${hx}" cy="${hy - 55 - 110 * open}" rx="20" ry="${10 + 6 * open}" fill="none" stroke="#6b6460" stroke-width="6"/>`;
  }
  const fire = o.fire ?? 0, t = o.t || 0;
  return `
  <rect width="${W}" height="${H}" fill="${PAL.wood1}"/>
  ${planks}
  <!-- потолочные балки и дыра в крыше -->
  <rect x="0" y="0" width="${W}" height="190" fill="#1a141a"/>
  <path d="M700 30 Q780 0 860 40 Q900 110 820 150 Q740 160 700 110 Z" fill="#0b1124"/>
  <g clip-path="url(#roofHole)">${stars(690, 0, 220, 160, 14, 5, t)}</g>
  <clipPath id="roofHole"><path d="M700 30 Q780 0 860 40 Q900 110 820 150 Q740 160 700 110 Z"/></clipPath>
  ${[0, 1].map(i => `<rect x="0" y="${150 + i * 0}" width="${W}" height="44" fill="#120e13"/>`).join('')}
  <rect x="300" y="0" width="40" height="194" fill="#120e13"/>
  <!-- окно -->
  <rect x="80" y="420" width="260" height="320" fill="#0c1326" stroke="#140f15" stroke-width="18"/>
  <line x1="210" y1="420" x2="210" y2="740" stroke="#140f15" stroke-width="12"/>
  <line x1="80" y1="580" x2="340" y2="580" stroke="#140f15" stroke-width="12"/>
  ${fir(150, 740, 200, '#060a14')}${fir(290, 740, 260, '#060a14')}
  <!-- печь -->
  <rect x="760" y="620" width="320" height="700" fill="#4a4550"/>
  <rect x="740" y="600" width="360" height="40" fill="#57525e"/>
  <rect x="820" y="300" width="140" height="320" fill="#423d47"/>
  ${[...Array(9)].map((_, i) => `<line x1="760" y1="${680 + i * 70}" x2="1080" y2="${680 + i * 70}" stroke="#3a3540" stroke-width="3"/>`).join('')}
  <rect x="820" y="980" width="200" height="150" rx="70" fill="#0c0808"/>
  ${fire > 0 ? `<g opacity="${fire}">${flame(920, 1130, 0.9, t)}${flame(880, 1130, 0.55, t + 1.3)}${flame(965, 1130, 0.6, t + 2.1)}</g>` : ''}
  <!-- стол с запиской -->
  <rect x="120" y="1080" width="460" height="34" fill="#4a3528"/>
  <rect x="140" y="1110" width="30" height="230" fill="#3a2a20"/><rect x="530" y="1110" width="30" height="230" fill="#3a2a20"/>
  ${o.noteOnTable !== false ? `<g transform="translate(320 1066) scale(0.38 0.16)"><rect x="-150" y="-100" width="300" height="200" fill="#d8ccae"/></g>` : ''}
  <!-- стул отодвинут -->
  <g transform="rotate(-8 640 1320)"><rect x="600" y="1000" width="22" height="320" fill="#3a2a20"/><rect x="600" y="1150" width="160" height="22" fill="#3a2a20"/><rect x="738" y="1150" width="22" height="170" fill="#3a2a20"/></g>
  <!-- пол -->
  ${floor}
  ${hatchSvg}
  ${fire > 0 ? warmLight(920, 1080, 900, fire) : ''}
  `;
}

function bgForest(o = {}) {
  const t = o.t || 0;
  let far = '', mid = '', near = '';
  const r = rng(11);
  for (let i = 0; i < 12; i++) far += fir(i * 100 + r() * 40, 1150, 380 + r() * 200, '#141b2e');
  for (let i = 0; i < 8; i++) mid += fir(i * 150 + r() * 60 - 40, 1300, 560 + r() * 260, '#0d1322');
  near = fir(-40, 1960, 1300, '#05080f') + fir(1130, 1960, 1200, '#05080f');
  return `
  <rect width="${W}" height="${H}" fill="url(#skyNight)"/>
  <circle cx="780" cy="300" r="70" fill="#c9cfe0" opacity=".25"/><circle cx="780" cy="300" r="200" fill="url(#coldGlow)" opacity=".5"/>
  ${far}${mid}
  <rect x="0" y="1260" width="${W}" height="660" fill="#17141a"/>
  <path d="M0 1300 Q300 1260 540 1310 Q800 1360 1080 1290 L1080 1920 L0 1920 Z" fill="#1e1a1f"/>
  <!-- колея и грязь -->
  <path d="M260 1920 Q420 1500 520 1330" stroke="#0f0c0f" stroke-width="60" fill="none"/>
  <path d="M820 1920 Q640 1500 580 1330" stroke="#0f0c0f" stroke-width="60" fill="none"/>
  ${o.van !== false ? van(560, 1640, 1) : ''}
  ${near}
  `;
}

function van(x, y, s = 1) {
  return `<g transform="translate(${x} ${y}) scale(${s}) rotate(-3)">
    <!-- лучи фар -->
    <path d="M-330 40 L-1100 -120 L-1100 260 Z" fill="${PAL.fire1}" opacity=".10"/>
    <rect x="-320" y="-190" width="560" height="250" rx="30" fill="#7c8496"/>
    <path d="M-320 -60 L-320 40 Q-320 60 -300 60 L-180 60 L-180 -190 L-250 -190 Q-300 -180 -320 -60 Z" fill="#8a93a6"/>
    <path d="M-300 -60 L-250 -170 L-200 -170 L-200 -60 Z" fill="#1b2336"/>
    <rect x="-180" y="-60" width="420" height="40" fill="${PAL.sJacket}"/>
    <rect x="-150" y="-170" width="160" height="90" rx="6" fill="#1b2336"/>
    <circle cx="-322" cy="0" r="16" fill="${PAL.fire0}"/>
    <!-- колёса в грязи -->
    <circle cx="-200" cy="64" r="58" fill="#141214"/><circle cx="150" cy="64" r="58" fill="#141214"/>
    <path d="M-340 90 Q-200 50 -60 96 Q60 60 280 96 L300 140 L-360 140 Z" fill="#241d1c"/>
    <!-- коробки внутри -->
    <rect x="-130" y="-150" width="50" height="40" fill="#9c5414"/><rect x="-70" y="-140" width="40" height="30" fill="#b66419"/>
  </g>`;
}

function bgHouseExt(o = {}) {
  const r = rng(21); let trees = '';
  for (let i = 0; i < 10; i++) trees += fir(i * 120 + r() * 50 - 30, 1180, 500 + r() * 300, i % 2 ? '#0e1424' : '#111829');
  return `
  <rect width="${W}" height="${H}" fill="url(#skyNight)"/>
  <circle cx="260" cy="320" r="60" fill="#d5d9e6" opacity=".35"/>
  ${trees}
  <rect y="1150" width="${W}" height="770" fill="#1a1820"/>
  <path d="M0 1160 Q540 1110 1080 1170 L1080 1260 L0 1260 Z" fill="#27242c"/>
  <!-- изба -->
  <g transform="translate(540 1180)">
    <rect x="-300" y="-380" width="600" height="380" fill="#2c2226"/>
    ${[...Array(8)].map((_, i) => `<rect x="-310" y="${-372 + i * 47}" width="620" height="40" rx="20" fill="${i % 2 ? '#33282c' : '#2e2428'}"/>`).join('')}
    <path d="M-360 -370 L0 -640 L360 -370 Z" fill="#1c161c"/>
    <path d="M-380 -360 L0 -650 L380 -360" stroke="#120e13" stroke-width="30" fill="none"/>
    <path d="M110 -560 L170 -590 L200 -520 Z" fill="#0b1124"/>
    <rect x="-90" y="-500" width="60" height="70" fill="#090b12"/>
    <rect x="-230" y="-290" width="120" height="140" fill="#080a12" stroke="#1a141a" stroke-width="14"/>
    <rect x="110" y="-290" width="120" height="140" fill="#080a12" stroke="#1a141a" stroke-width="14"/>
    <rect x="-50" y="-260" width="100" height="260" fill="#1a1216"/>
    <rect x="-130" y="-10" width="260" height="30" fill="#241c20"/>
  </g>
  ${fir(-60, 1980, 1100, '#04060c')}${fir(1150, 1980, 1000, '#04060c')}
  `;
}

function bgCellar(o = {}) {
  const t = o.t || 0; const r = rng(31); let stones = '';
  for (let y = 0; y < 15; y++) for (let x = 0; x < 7; x++) {
    const ox = (y % 2) * 80;
    stones += `<rect x="${x * 170 - ox + r() * 10}" y="${y * 120 + r() * 10}" width="${150 + r() * 20}" height="${100 + r() * 10}" rx="28" fill="${['#2a2d38', '#262833', '#30333f', '#23252e'][Math.floor(r() * 4)]}"/>`;
  }
  return `
  <rect width="${W}" height="${H}" fill="#15161c"/>
  ${stones}
  <rect y="1450" width="${W}" height="470" fill="#1b1a1d"/>
  <!-- лестница из люка -->
  <rect x="440" y="0" width="200" height="40" fill="#5f6a84" opacity=".25"/>
  <rect x="450" y="0" width="22" height="1480" fill="#3a2a20"/><rect x="608" y="0" width="22" height="1480" fill="#3a2a20"/>
  ${[...Array(9)].map((_, i) => `<rect x="450" y="${120 + i * 160}" width="180" height="18" fill="#4a3528"/>`).join('')}
  <!-- матрас и одеяло -->
  <rect x="60" y="1480" width="420" height="110" rx="30" fill="#6b6a5a"/>
  <path d="M120 1470 Q260 1420 400 1480 L420 1580 L110 1590 Z" fill="#5a3a3a"/>
  <path d="M140 1500 L400 1500" stroke="#4a2e2e" stroke-width="6"/>
  <!-- ящик с кружкой -->
  <rect x="720" y="1400" width="220" height="190" fill="#4a3528"/>
  <line x1="720" y1="1495" x2="940" y2="1495" stroke="#2e2018" stroke-width="5"/>
  ${mug(830, 1350, 0.9, t, o.steam !== false)}
  <!-- фото на стене -->
  ${photo(820, 980, 0.8, 4)}
  <circle cx="824" cy="884" r="8" fill="#888"/>
  `;
}

function bgEviction() {
  return `
  <rect width="${W}" height="${H}" fill="url(#skyDay)"/>
  ${[...Array(8)].map((_, i) => fir(i * 150 - 30, 1150, 460 + (i % 3) * 90, '#6e7268')).join('')}
  <rect y="1130" width="${W}" height="790" fill="#9a968a"/>
  <g transform="translate(560 1160)">
    <rect x="-280" y="-360" width="560" height="360" fill="#6f655c"/>
    <path d="M-330 -350 L0 -600 L330 -350 Z" fill="#4e463f"/>
    <rect x="-210" y="-270" width="110" height="120" fill="#3c3631"/><rect x="100" y="-270" width="110" height="120" fill="#3c3631"/>
    <rect x="-45" y="-240" width="90" height="240" fill="#4a423b"/>
  </g>
  <!-- полицейская машина (без бренда) -->
  <g transform="translate(250 1500)">
    <rect x="-200" y="-110" width="400" height="120" rx="30" fill="#e2e4e6"/>
    <path d="M-120 -110 L-80 -190 L100 -190 L140 -110 Z" fill="#cfd3d6"/>
    <rect x="-200" y="-60" width="400" height="30" fill="#3a5a9c"/>
    <text x="0" y="-38" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="26" fill="#fff">ПОЛИЦИЯ</text>
    <rect x="-40" y="-214" width="80" height="24" rx="6" fill="#3a5a9c"/>
    <circle cx="-120" cy="14" r="40" fill="#2e2e2e"/><circle cx="120" cy="14" r="40" fill="#2e2e2e"/>
  </g>
  <!-- хозяин с сумкой оборачивается -->
  <g transform="translate(700 1420) scale(.75)">${owner({ smile: 0, face: true })}<rect x="300" y="520" width="120" height="90" rx="12" fill="#5a4a3a"/></g>
  <rect width="${W}" height="${H}" fill="#b5a68a" opacity=".22" style="mix-blend-mode:multiply"/>
  `;
}

// Финал: вид снизу на открытый люк, в проёме — Старый хозяин, освещённый спичкой снизу
function bgHatchFromBelow(o = {}) {
  const open = o.open ?? 1, smile = o.smile ?? 1, lit = o.lit ?? 1;
  const lift = 260 * open;
  return `
  <rect width="${W}" height="${H}" fill="#050508"/>
  <rect width="${W}" height="1000" fill="#0e0d10"/>
  ${[...Array(7)].map((_, i) => `<rect x="0" y="${i * 150}" width="${W}" height="138" fill="#141216"/>`).join('')}
  <clipPath id="hatchHole"><rect x="300" y="420" width="480" height="${Math.max(1, 360 * open)}"/></clipPath>
  <rect x="300" y="420" width="480" height="${360 * open}" fill="#191a24"/>
  <g clip-path="url(#hatchHole)">
    <rect x="300" y="420" width="480" height="360" fill="#22202a"/>
    <g transform="translate(130 ${190 + (1 - open) * 420}) scale(2.0)">${owner({ smile, blink: o.blink })}</g>
    <rect x="300" y="420" width="480" height="360" fill="${PAL.fire2}" opacity="${0.22 * lit}" style="mix-blend-mode:screen"/><ellipse cx="540" cy="760" rx="300" ry="200" fill="url(#fireGlow)" opacity="${0.8 * lit}"/>
  </g>
  <!-- крышка люка поднята -->
  <path d="M300 ${420} L780 420 L800 ${420 - lift * 0.5} L280 ${420 - lift * 0.5} Z" fill="#2a2026" opacity="${open > 0 ? 1 : 0}"/>
  <rect x="300" y="420" width="480" height="360" fill="none" stroke="#08070a" stroke-width="16"/>
  `;
}

function titleCard(o = {}) {
  const t = o.t || 0; const r = rng(77); let sparks = '';
  for (let i = 0; i < 40; i++) {
    const x = r() * W, sp = 60 + r() * 120; const y = H - ((r() * H + t * sp) % H);
    sparks += `<circle cx="${x + Math.sin(t + i) * 20}" cy="${y}" r="${2 + r() * 4}" fill="${r() > .5 ? PAL.fire1 : PAL.fire2}" opacity="${0.3 + r() * 0.6}"/>`;
  }
  return `
  <rect width="${W}" height="${H}" fill="#060509"/>
  <circle cx="540" cy="1250" r="700" fill="url(#fireGlow)" opacity=".35"/>
  ${sparks}
  ${fir(540, 1700, 520, '#0d0b10')}${fir(300, 1720, 380, '#0d0b10')}${fir(800, 1720, 400, '#0d0b10')}
  <text x="540" y="760" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="120" fill="#efe2c4" letter-spacing="6">ВЫЖИВАНИЕ</text>
  <text x="540" y="890" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="120" fill="#efe2c4" letter-spacing="6">В ЛЕСУ</text>
  <text x="540" y="990" text-anchor="middle" font-family="DejaVu Sans" font-size="44" fill="${PAL.fire1}" letter-spacing="8">СЕРИЯ 1 · ДОМИК В ЛЕСУ</text>
  `;
}

// HUD сериала: время + счётчик спичек
function hud(time, matches, o = {}) {
  const red = matches <= 3;
  return `<g transform="translate(540 150)">
    <rect x="-200" y="-60" width="400" height="104" rx="22" fill="#05070d" opacity=".72"/>
    <text x="-60" y="12" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="56" fill="#e8ecf4">${time}</text>
    <g transform="translate(110 0) scale(${o.pulse || 1})">
      <rect x="-56" y="-38" width="112" height="70" rx="16" fill="${red ? PAL.red : '#3a2a20'}" opacity="${red ? .9 : .8}"/>
      <rect x="-40" y="-20" width="7" height="38" rx="2" fill="#e3c98f"/><ellipse cx="-36.5" cy="-22" rx="7" ry="8" fill="#9b2a1c"/>
      <text x="14" y="16" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="46" fill="#fff">${matches}</text>
    </g>
    <text x="0" y="86" text-anchor="middle" font-family="DejaVu Sans" font-size="26" fill="#aab3c6" letter-spacing="6">НОЯБРЬ · ЛЕС</text>
  </g>`;
}

if (typeof module !== 'undefined') module.exports = { PAL, rng, defs, darkness, warmLight, vignette, grain, sveta, marina, owner, fir, snowStreaks, stars, flame, note, matchbox, photo, mug, van, bgInterior, bgForest, bgHouseExt, bgCellar, bgEviction, bgHatchFromBelow, titleCard, hud, W, H };
