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

function journalSpread(t, left, right, o = {}) {
  let s = rect(-400, -400, 1880, 2800, '#1a1712') + `<ellipse cx="540" cy="1000" rx="620" ry="460" fill="url(#warmBlob)" opacity=".3"/>`;
  s += rect(80, 600, 920, 760, '#4a3a28', `rx="14" stroke="${ST}" stroke-width="6"`) + rect(110, 620, 430, 720, '#efe8d6', `stroke="${ST}" stroke-width="4"`) + rect(540, 620, 430, 720, '#f3eddc', `stroke="${ST}" stroke-width="4"`);
  return s + left + right;
}
function inkLine(x, y, s, size = 34, col = '#1d2f6b', k = 1) {
  return `<text x="${x}" y="${y}" font-family="Inter" font-style="italic" font-weight="900" font-size="${size}" fill="${col}">${typeText(s, k)}</text>`;
}

