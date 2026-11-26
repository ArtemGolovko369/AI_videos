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
