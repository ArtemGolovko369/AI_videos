// Серия 1 «Домик в лесу» — покадровая анимация.
// Работает в браузере после art.js. Время:
//   t — время ролика (сек), v — время исходной озвучки (сек).
// Ролик = вступление LEAD + озвучка со вставленными паузами + заставка.

const FPS = 30;
const LEAD = 0.8;                       // тишина до первой фразы (чирк спички)
const INSERTS = [[25.40, 0.6], [79.20, 0.8]]; // [время в озвучке, добавленная пауза]: после «Тишина», перед «И улыбался»
const TITLE_V = 80.6;                    // начало заставки (по времени озвучки)
const TITLE_LEN = 5.6;

function v2t(v) { let t = v + LEAD; for (const [p, d] of INSERTS) if (v > p) t += d; return t; }
function t2v(t) {
  let v = t - LEAD;
  for (const [p, d] of INSERTS) { const tp = v2t(p); if (t > tp + d) v -= 0; }
  // аккуратно: идём по вставкам по порядку
  let acc = LEAD; v = t - LEAD;
  for (const [p, d] of INSERTS) {
    const tp = p + acc;
    if (t <= tp) return t - acc;
    if (t <= tp + d) return p;
    acc += d;
  }
  return t - acc;
}
const TOTAL = v2t(TITLE_V) + TITLE_LEN;

// ---------- утилиты ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const prog = (x, a, b) => clamp((x - a) / (b - a));
const ease = k => k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
const easeOut = k => 1 - Math.pow(1 - k, 3);
const easeBack = k => { const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
function noise(t, seed = 0) { return Math.sin(t * 12.9 + seed * 7.1) * 0.5 + Math.sin(t * 31.7 + seed * 3.3) * 0.3 + Math.sin(t * 57.1 + seed) * 0.2; }

function cam(inner, o = {}) {
  const z = o.z ?? 1, cx = o.cx ?? 540, cy = o.cy ?? 960;
  let dx = o.dx || 0, dy = o.dy || 0;
  if (o.shake) { dx += noise(o.t, 1) * o.shake; dy += noise(o.t, 2) * o.shake; }
  return `<g transform="translate(${540 + dx} ${960 + dy}) scale(${z}) translate(${-cx} ${-cy})">${inner}</g>`;
}
function place(fn, opts, x, y, s) { return `<g transform="translate(${x - 200 * s} ${y - 760 * s}) scale(${s})">${fn(opts)}</g>`; }

// моргание: детерминированно, раз в 2–5 сек
function blinkAt(t, seed) {
  const r = rng(seed); let x = 0.5 + r() * 2;
  while (x < t + 1) { if (t >= x && t < x + 0.11) return true; x += 2 + r() * 3; }
  return false;
}
function mouthAt(v) {
  const a = DATA.amp[Math.max(0, Math.floor(v * 30))] || 0;
  return a > 0.55 ? 2 : a > 0.18 ? 1 : 0;
}
function flick(t, s = 0) { return 1 + 0.06 * noise(t * 0.8, s); }

// ---------- HUD ----------
function hudState(v) {
  let time = '23:58';
  if (v >= 4.6 && v < 18.2) time = v < 13.7 ? '20:40' : '21:15';
  else if (v >= 18.2 && v < 29.2) time = '00:00';
  else if (v >= 29.2 && v < 44) time = '00:04';
  else if (v >= 44 && v < 59.7) time = '00:11';
  else if (v >= 59.7) time = '00:19';
  let m = 10;
  for (const s of STRIKES) if (v >= s) m--;
  if (v >= 73.3) m = 2;
  let pulse = 1;
  for (const p of [37.55, 73.3, 75.0]) { const k = (v - p) / 0.35; if (k >= 0 && k < 1) pulse = 1 + 0.25 * Math.sin(k * Math.PI); }
  return { time, m, pulse };
}
const STRIKES = [32.55, 33.05, 33.55, 34.05, 34.55, 35.0, 35.4]; // седьмая — загорелось

// ---------- СЦЕНЫ ----------
function sceneNoteClose(v, t, signRed = 0, lit = 1) {
  // крупно: записка на столе
  const z = lerp(1.0, 1.1, prog(v, -0.8, 2.7));
  let planks = '';
  for (let i = 0; i < 12; i++) planks += `<rect x="0" y="${i * 170}" width="1080" height="166" fill="${i % 2 ? '#3a2a20' : '#33251c'}"/>`;
  const red = `rgb(${Math.round(lerp(42, 228, signRed))},${Math.round(lerp(36, 71, signRed))},${Math.round(lerp(32, 59, signRed))})`;
  const fx = 800, fy = 1330;
  const inner = planks + note(520, 880, 2.6, -4, red) +
    `<rect x="${fx - 3}" y="${fy}" width="7" height="160" rx="2" fill="#d9c08a" transform="rotate(-25 ${fx} ${fy + 160})"/>` +
    (lit > 0 ? flame(fx, fy + 6, 0.35 * lit, t) : '');
  const L = 650 * flick(t) * lit;
  return cam(inner + darkness(1080, 1920, [{ x: fx - 150, y: fy - 300, r: Math.max(1, L * 1.3) }], 0.93, 'nc') + warmLight(fx, fy - 40, 420 * lit, 0.8 * lit), { z, cx: 540, cy: 960 });
}

function S1(v, t) {
  if (v < 2.62) {
    if (v < -0.55) return `<rect width="1080" height="1920" fill="#000"/>`;
    const strike = prog(v, -0.55, -0.4);
    let s = sceneNoteClose(v, t, 0, strike);
    if (v < -0.3) s += `<circle cx="800" cy="1320" r="${lerp(10, 160, prog(v, -0.55, -0.4))}" fill="#fff6d0" opacity="${1 - prog(v, -0.45, -0.3)}"/>`;
    return s;
  }
  const z = lerp(1.05, 1.12, prog(v, 2.6, 4.8));
  const L = 520 * flick(t);
  const inner = bgInterior({ t }) +
    `<g transform="translate(470 1050)"><rect x="-3" y="-60" width="6" height="60" fill="#d9c08a"/>${flame(0, -58, 0.22, t)}</g>`;
  return cam(inner + darkness(1080, 1920, [{ x: 400, y: 1000, r: L }], 0.93, 's1') + warmLight(470, 990, 380, .8), { z, cx: 480, cy: 1050 });
}

function S2(v, t) {
  const k = prog(v, 4.6, 8.8);
  const inner = bgForest({ t }) + snowStreaks(1080, 1920, 160, 4, t, 0.6);
  return cam(inner, { z: lerp(1.12, 1.02, ease(k)), cx: lerp(470, 560, k), cy: 1560 }) + snowStreaks(1080, 1920, 40, 8, t * 1.4, 0.8);
}

function S3(v, t) {
  const inner = bgForest({ t, van: false }) + `<rect width="1080" height="1920" fill="#000" opacity=".35"/>` + snowStreaks(1080, 1920, 120, 5, t, 0.5) +
    place(marina, { emo: 'serious', torch: true, blink: blinkAt(t, 2), look: v < 10.5 ? 0 : -0.6 }, 560, 1880, 2.1);
  return cam(inner + darkness(1080, 1920, [{ x: 560, y: 760, r: 760 }], 0.6, 's3'), { z: lerp(1.0, 1.07, prog(v, 8.7, 13.8)), cy: 940 }) + snowStreaks(1080, 1920, 50, 9, t * 1.3, 0.7);
}

function S4(v, t) {
  const smirk = v > 13.9;
  const bob = Math.abs(Math.sin(t * 3)) * 6;
  const inner = bgHouseExt({ t }) + snowStreaks(1080, 1920, 120, 9, t, 0.5) +
    place(marina, { emo: 'serious', blink: blinkAt(t, 3), look: -0.5 }, 700, 1790 - bob, 0.95) +
    place(sveta, { emo: smirk ? 'smirk' : 'neutral', blink: blinkAt(t, 4), look: 0.6 }, 390, 1800 - Math.abs(Math.sin(t * 3 + 1)) * 6, 0.95);
  return cam(inner + darkness(1080, 1920, [{ x: 540, y: 1200, r: 900 }], 0.45, 's4'), { z: lerp(1.0, 1.1, prog(v, 13.7, 18.3)), cy: 1150 }) + snowStreaks(1080, 1920, 40, 3, t * 1.3, 0.7);
}

function S5(v, t) {
  const up = easeOut(prog(v, 19.1, 19.5));
  const scared = v > 20.3;
  const inner = bgInterior({ t }) +
    place(sveta, { emo: scared ? 'scared' : 'neutral', blink: blinkAt(t, 5), cold: true }, 330, 1900, 1.7) +
    place(marina, { emo: scared ? 'scared' : 'serious', torch: true, blink: blinkAt(t, 6), armR: -165 * up }, 760, 1900, 1.7);
  return cam(inner + darkness(1080, 1920, [{ x: 560, y: 1000, r: 820 }], 0.8, 's5'), { z: lerp(1.0, 1.06, prog(v, 18.2, 22.2)), cy: 1000 });
}

function S6(v, t) {
  // потолок крупно; шаги
  let s = `<rect width="1080" height="1920" fill="#1a141a"/>`;
  const steps = [22.38, 23.33];
  let dip = 0, shake = 0;
  for (const st of steps) { const k = v - st; if (k >= 0 && k < 0.5) { dip = Math.max(dip, Math.sin(prog(k, 0, 0.5) * Math.PI)); shake = Math.max(shake, 10 * (1 - k / 0.5)); } }
  for (let i = 0; i < 9; i++) {
    const y = 120 + i * 200, mid = i === 4;
    s += `<rect x="-40" y="${y + (mid ? dip * 18 : 0)}" width="1160" height="180" fill="${i % 2 ? '#2a2129' : '#30252d'}"/>`;
    s += `<line x1="0" y1="${y + 182}" x2="1080" y2="${y + 182}" stroke="#0a070a" stroke-width="6"/>`;
  }
  s += `<rect x="0" y="0" width="120" height="1920" fill="#120e13"/><rect x="960" y="0" width="120" height="1920" fill="#120e13"/>`;
  // пыль
  const r = rng(13);
  for (const st of steps) for (let i = 0; i < 26; i++) {
    const k = v - st - r() * 0.2, x = 540 + (r() - 0.5) * 500;
    if (k > 0 && k < 1.8) s += `<circle cx="${x + Math.sin(k * 3 + i) * 10}" cy="${1000 + k * k * 420}" r="${2 + r() * 4}" fill="#b9a99a" opacity="${0.8 * (1 - k / 1.8)}"/>`;
    else r();
  }
  return cam(s + darkness(1080, 1920, [{ x: 540, y: 1000, r: 1000 }], 0.55, 's6') + `<circle cx="540" cy="1000" r="500" fill="url(#coldGlow)" opacity=".5"/>`, { z: lerp(1.0, 1.08, prog(v, 22, 25.5)), shake, t });
}

function S7(v, t) {
  // резкий поворот вниз к люку, холод
  const whip = easeOut(prog(v, 25.5, 25.95));
  let mist = '';
  const r = rng(17);
  for (let i = 0; i < 22; i++) {
    const ph = (t * 0.25 + r()) % 1, x = 640 + (r() - 0.5) * 360;
    mist += `<ellipse cx="${x + Math.sin(t + i) * 30}" cy="${1520 - ph * 520}" rx="${60 + r() * 60}" ry="${26 + r() * 20}" fill="#b8c6de" opacity="${0.22 * Math.sin(ph * Math.PI)}" filter="url(#blur20)"/>`;
  }
  const z = v < 28.4 ? lerp(1.05, 1.25, prog(v, 25.9, 28.4)) : lerp(1.25, 1.45, easeOut(prog(v, 28.4, 28.7)));
  const inner = bgInterior({ t, hatch: 'ajar' }) + mist;
  return cam(inner + darkness(1080, 1920, [{ x: 640, y: 1500, r: 620 }], 0.86, 's7'), { z, cx: 640, cy: lerp(700, 1480, whip) });
}

function S8(v, t) {
  // достаёт спички
  const up = easeOut(prog(v, 30.6, 31.2));
  const y = lerp(2300, 1050, up);
  const s = `<rect width="1080" height="1920" fill="#0b0a0e"/>` + bgInterior({ t, hatch: 'ajar' }).replace('<rect width', '<rect opacity=".0" width') +
    `<g transform="translate(540 ${y}) rotate(${-6 + 3 * Math.sin(t * 1.2)})"><circle cx="-150" cy="70" r="60" fill="${PAL.skinCold}"/><circle cx="150" cy="70" r="60" fill="${PAL.skinCold}"/>${matchbox(0, 0, 2.0, 10)}</g>`;
  return cam(s + darkness(1080, 1920, [{ x: 540, y: 1100, r: 760 }], 0.88, 's8'), { z: lerp(1.15, 1.25, prog(v, 30.5, 32.5)), cy: 1100 });
}

function S9(v, t) {
  // чирк — гаснет ×6, на седьмой разгорается печь
  const fireK = prog(v, 35.4, 36.2);
  let flash = 0, fx = 900, fy = 1150;
  STRIKES.forEach((s, i) => { const k = v - s; if (k >= 0 && k < 0.45 && i < 6) { flash = Math.max(flash, Math.sin(prog(k, 0, 0.45) * Math.PI)); fx = 860 + i * 15; } });
  if (v >= 35.4) flash = Math.max(flash, 1 - fireK);
  const inner = bgInterior({ t, fire: easeOut(fireK) }) +
    (flash > 0 ? `<g transform="translate(${fx} ${fy})"><rect x="-3" y="0" width="7" height="110" fill="#d9c08a"/>${flame(0, 2, 0.28 * flash, t)}</g>` : '');
  const L = 160 + 420 * flash + 900 * easeOut(fireK);
  return cam(inner + darkness(1080, 1920, [{ x: 910, y: 1080, r: L * flick(t, 3) }], 0.94, 's9') + (flash ? warmLight(fx, fy - 40, 300, flash) : ''),
    { z: lerp(2.0, 1.5, ease(fireK)), cx: 900, cy: 1060 });
}

function S10(v, t) {
  const s = `<rect width="1080" height="1920" fill="#20160f"/>` + `<g transform="rotate(${-4 + Math.sin(t) * 1.5} 540 1000)"><circle cx="280" cy="1250" r="80" fill="${PAL.skin}"/>${matchbox(540, 1000, 3.0, 3)}</g>`;
  return cam(s + warmLight(800, 600, 900, .8) + darkness(1080, 1920, [{ x: 540, y: 950, r: 900 }], 0.6, 's10'), { z: lerp(1.0, 1.12, prog(v, 37, 38.6)), cy: 1000 });
}

function S11(v, t) {
  const pan = ease(prog(v, 41.6, 42.6));
  const talking = v > 38.5 && v < 43.5;
  const inner = bgInterior({ t, fire: 1 }) +
    place(sveta, { emo: 'smirk', mouth: talking ? mouthAt(v) : 0, blink: blinkAt(t, 7) }, 320, 1880, 1.6) +
    place(marina, { emo: 'serious', blink: blinkAt(t, 8), look: -0.8 }, 760, 1890, 1.6);
  return cam(inner + darkness(1080, 1920, [{ x: 920, y: 1060, r: 1100 * flick(t, 4) }], 0.7, 's11') + warmLight(900, 1050, 900, 0.7),
    { z: lerp(1.05, 1.1, prog(v, 38.5, 41.6)), cx: lerp(540, 760, pan), cy: lerp(1050, 300, pan) });
}

function S12(v, t) {
  const mk = ease(prog(v, 44.3, 47.2)), sk = ease(prog(v, 47.6, 49.9));
  const my = lerp(760, 1500, mk), sy = lerp(400, 1480, sk);
  const inner = bgCellar({ t }) +
    place(marina, { emo: 'serious', stick: true, blink: blinkAt(t, 9) }, 610 + (mk >= 1 ? 120 * ease(prog(v, 47.2, 48)) : 0), my, 0.9) +
    (v > 47.5 ? place(sveta, { emo: 'scared', blink: blinkAt(t, 10) }, 470, sy, 0.9) : '');
  const lx = 610 + (mk >= 1 ? 120 * ease(prog(v, 47.2, 48)) : 0) + 74, ly = my - 306;
  return cam(inner + darkness(1080, 1920, [{ x: lx, y: ly, r: 640 * flick(t, 5) }], 0.95, 's12') + warmLight(lx, ly, 380, .9), { z: 1.0, cy: 960 });
}

function S13(v, t) {
  // предметы по словам
  const focus = [[50.2, 540, 1300, 1.0], [51.9, 270, 1540, 1.45], [52.75, 300, 1480, 1.45], [53.8, 830, 1350, 1.6], [54.8, 830, 1330, 2.2]];
  let cx = 540, cy = 1300, z = 1, prev = focus[0];
  for (const f of focus) {
    if (v >= f[0]) {
      const k = ease(prog(v, f[0], f[0] + 0.4));
      cx = lerp(prev[1], f[1], k); cy = lerp(prev[2], f[2], k); z = lerp(prev[3], f[3], k);
      prev = [0, cx, cy, z];
    }
  }
  const inner = bgCellar({ t }) + place(marina, { emo: 'serious', stick: true, blink: blinkAt(t, 9) }, 1000, 1640, 0.9);
  return cam(inner + darkness(1080, 1920, [{ x: cx, y: cy - 60, r: 520 * flick(t, 6) }, { x: 1080, y: 1000, r: 500 }], 0.93, 's13') + warmLight(cx + 100, cy - 200, 600, .7), { z, cx, cy });
}

function S14(v, t) {
  const k = prog(v, 56.2, 59.8);
  const s = `<rect width="1080" height="1920" fill="#2a2d38"/>` + photo(540, 960, 3.2, 3);
  return cam(s + darkness(1080, 1920, [{ x: 600, y: 900, r: 820 * flick(t, 7) }], 0.85, 's14') + warmLight(720, 1100, 700, .6),
    { z: lerp(1.0, 1.9, ease(k)), cx: lerp(540, 560, k), cy: lerp(960, 900, k), t });
}

function S15(v, t) {
  const pop = v >= 61.0 ? easeBack(prog(v, 61.0, 61.35)) : 0;
  const inner = bgCellar({ t }) + `<rect width="1080" height="1920" fill="#000" opacity=".3"/>` +
    place(marina, { emo: v > 60.5 ? 'scared' : 'serious', cold: true, blink: blinkAt(t, 11), stick: true }, 560, 2350, 2.3);
  let s = cam(inner + darkness(1080, 1920, [{ x: 600, y: 1200, r: 800 * flick(t, 8) }], 0.85, 's15') + warmLight(800, 1100, 700, .6), { z: lerp(1.0, 1.06, prog(v, 59.7, 65.9)), cy: 960 });
  if (pop > 0) {
    const R = 270 * pop;
    s += `<defs><clipPath id="memc"><circle cx="540" cy="610" r="${R}"/></clipPath></defs>
      <g clip-path="url(#memc)"><g transform="translate(540 610) scale(${0.5 * (1 + 0.04 * prog(v, 61, 65.9))}) translate(-560 -1250)">${bgEviction()}</g></g>
      <circle cx="540" cy="610" r="${R}" fill="none" stroke="#efe2c4" stroke-width="10"/>`;
  }
  return s;
}

function S16(v, t) {
  return sceneNoteClose(v - 66 + 1.5, t, ease(prog(v, 66.4, 68.4)));
}

function S17(v, t) {
  const slam = v - 69.95, out = prog(v, 71.7, 72.4);
  const shake = slam >= 0 && slam < 0.5 ? 26 * (1 - slam / 0.5) : 0;
  const inner = bgCellar({ t }) +
    place(sveta, { emo: 'scared', blink: blinkAt(t, 12) }, 340, 1640, 1.0) +
    place(marina, { emo: 'scared', stick: out < 1, blink: blinkAt(t, 13) }, 700, 1640, 1.0);
  const L = (620 * flick(t, 9)) * (1 - out) + 1;
  let s = cam(inner + darkness(1080, 1920, [{ x: 790, y: 1150, r: L }], 0.97, 's17') + warmLight(790, 1150, 500, 1 - out), { z: 1.15, cy: 1200, shake, t });
  if (slam >= 0 && slam < 0.12) s += `<rect width="1080" height="1920" fill="#fff" opacity=".35"/>`;
  // дымок от погасшей палки
  if (out > 0) for (let i = 0; i < 6; i++) { const k = (v - 71.7 - i * 0.12); if (k > 0) s += `<circle cx="${790 + Math.sin(k * 3 + i) * 20}" cy="${1000 - k * 200}" r="${14 + k * 20}" fill="#888" opacity="${Math.max(0, 0.25 - k * 0.12)}"/>`; }
  return s;
}

function S18(v, t) {
  const sk = v - 73.3;
  if (sk < 0) return `<rect width="1080" height="1920" fill="#000"/>`;
  const lit = easeOut(prog(sk, 0, 0.3));
  const inner = `<rect width="1080" height="1920" fill="#14141a"/>` +
    place(sveta, { emo: 'scared', blink: blinkAt(t, 14), look: 0.5 }, 330, 2250, 2.0) +
    place(marina, { emo: 'scared', blink: blinkAt(t, 15), look: -0.5 }, 760, 2250, 2.0) +
    `<g transform="translate(560 1350)"><rect x="-3" y="0" width="7" height="140" fill="#d9c08a"/>${flame(0, 2, 0.35 * lit, t)}</g>`;
  let s = cam(inner + darkness(1080, 1920, [{ x: 560, y: 1200, r: 640 * lit * flick(t, 10) + 1 }], 0.97, 's18') + warmLight(560, 1300, 500, lit), { z: lerp(1.0, 1.06, prog(v, 73.3, 75.8)), cy: 1100 });
  if (sk < 0.15) s += `<circle cx="560" cy="1340" r="${200 * sk / 0.15}" fill="#fff6d0" opacity="${1 - sk / 0.15}"/>`;
  return s;
}

function S19(v, t) {
  const open = ease(prog(v, 75.95, 76.9));
  const smile = lerp(0.15, 1, ease(prog(v, 77.2, 80.2)));
  const z = lerp(1.0, 1.35, ease(prog(v, 76.2, 80.6)));
  const inner = bgHatchFromBelow({ open, smile, t }) +
    `<g transform="translate(540 1650)"><rect x="-3" y="0" width="7" height="140" fill="#d9c08a"/>${flame(0, 2, 0.35, t)}</g>`;
  return cam(inner + darkness(1080, 1920, [{ x: 540, y: 1250, r: 1000 * flick(t, 11) }, { x: 540, y: 640, r: 700 * open }], 0.8, 's19') + warmLight(540, 1600, 600, .9),
    { z, cx: 540, cy: lerp(1000, 640, ease(prog(v, 76.2, 80.6))) });
}

function STitle(v, t) {
  const k = v - TITLE_V;
  let s = titleCard({ t });
  // прятать надписи заставки и проявлять по очереди
  s = s.replace('font-size="120" fill="#efe2c4" letter-spacing="6">ВЫЖИВАНИЕ', `font-size="120" fill="#efe2c4" opacity="${prog(k, 0.3, 1.0)}" letter-spacing="6">ВЫЖИВАНИЕ`)
       .replace('letter-spacing="6">В ЛЕСУ', `opacity="${prog(k, 0.3, 1.0)}" letter-spacing="6">В ЛЕСУ`)
       .replace('letter-spacing="8">СЕРИЯ', `opacity="${prog(k, 1.1, 1.6)}" letter-spacing="8">СЕРИЯ`);
  s += `<text x="540" y="1180" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="46" fill="#efe2c4" opacity="${prog(k, 2.2, 2.8)}">Сколько спичек оставили бы вы?</text>
        <text x="540" y="1260" text-anchor="middle" font-family="DejaVu Sans" font-size="40" fill="#aab3c6" opacity="${prog(k, 2.6, 3.2)}">Пиши в комментариях ↓</text>`;
  return cam(s, { z: lerp(1.0, 1.05, prog(k, 0, TITLE_LEN)) });
}

// [начало (v), функция, длительность растворения на входе]
const SCENES = [
  [-9, S1, 0], [4.6, S2, 0.3], [8.7, S3, 0.3], [13.7, S4, 0.3], [18.2, S5, 0.3], [22.1, S6, 0.25], [25.5, S7, 0.1],
  [30.5, S8, 0.25], [32.4, S9, 0.25], [37.0, S10, 0.2], [38.5, S11, 0.25], [43.9, S12, 0.3], [50.0, S13, 0.3],
  [56.2, S14, 0.3], [59.7, S15, 0.3], [65.8, S16, 0.3], [69.6, S17, 0.25], [72.7, S18, 0], [75.7, S19, 0.4], [TITLE_V, STitle, 0.6],
];

// ---------- субтитры (караоке) ----------
const KEY = [
  [/^подвал/i, PAL.red], [/^хозя/i, PAL.red], [/^открыт/i, PAL.red], [/^улыбал/i, PAL.red], [/^выгнал/i, PAL.red], [/^три$/i, PAL.red], [/^две$/i, PAL.red], [/^тишина/i, '#9fb4d8'],
  [/^спич/i, PAL.yellow], [/^огонь/i, PAL.fire1], [/^тёпл/i, PAL.yellow], [/^чердак/i, PAL.yellow], [/^выселил/i, PAL.yellow], [/^марин/i, '#8fb0ff'], [/^шаг/i, '#e8ecf4'], [/^седьм/i, PAL.yellow], [/^ноябр/i, '#9fb4d8'],
];
function keyColor(w) { const c = w.replace(/[^\wёЁ-]/g, ''); for (const [re, col] of KEY) if (re.test(c)) return col; return null; }

function buildBlocks() {
  // блок = фраза (до точки), длинные режем по ~3 строки по 17 знаков
  const words = DATA.words.map(w => ({ ...w, t0: v2t(w.start), t1: v2t(w.end) }));
  const blocks = []; let cur = [];
  const flush = () => { if (cur.length) blocks.push(cur); cur = []; };
  words.forEach((w, i) => {
    cur.push(w);
    const len = cur.reduce((a, x) => a + x.w.length + 1, 0);
    const endS = /[.!?»]$/.test(w.w);
    if (endS && (len > 14 || (words[i + 1] && words[i + 1].t0 - w.t1 > 0.4))) flush();
    else if (len > 38) flush();
  });
  flush();
  blocks.forEach(b => {
    // перенос строк
    const lines = [[]]; let l = 0;
    for (const w of b) { if (l + w.w.length > 16 && lines[lines.length - 1].length) { lines.push([]); l = 0; } lines[lines.length - 1].push(w); l += w.w.length + 1; }
    b.lines = lines; b.t0 = b[0].t0 - 0.12; b.t1 = b[b.length - 1].t1;
  });
  blocks.forEach((b, i) => { const nx = blocks[i + 1]; b.hide = nx ? Math.min(nx.t0, b.t1 + 0.9) : b.t1 + 1.0; });
  return blocks;
}
let BLOCKS = null;
function subtitles(t) {
  if (!BLOCKS) BLOCKS = buildBlocks();
  const b = BLOCKS.find(b => t >= b.t0 && t < b.hide);
  if (!b) return '';
  const a = Math.min(prog(t, b.t0, b.t0 + 0.15), 1 - prog(t, b.hide - 0.15, b.hide));
  const FS = 66, LH = 84, y0 = 1330 - (b.lines.length - 1) * LH / 2;
  let s = `<g opacity="${a}" font-family="DejaVu Serif" font-weight="bold" font-size="${FS}" text-anchor="middle">`;
  b.lines.forEach((ln, li) => {
    const parts = ln.map(w => {
      const on = prog(t, w.t0 - 0.03, w.t0 + 0.07);
      const kc = keyColor(w.w);
      const fill = kc && on > 0 ? kc : '#ffffff';
      const sz = kc && on > 0 ? FS * 1.05 : FS;
      return `<tspan fill="${fill}" fill-opacity="${0.45 + 0.55 * on}" font-size="${sz}">${w.w.toUpperCase().replace(/&/g, '&amp;').replace(/</g, '&lt;')}</tspan>`;
    }).join(' ');
    const y = y0 + li * LH;
    s += `<text x="540" y="${y}" stroke="#000" stroke-width="12" stroke-linejoin="round" paint-order="stroke" xml:space="preserve">${parts}</text>`;
  });
  return s + '</g>';
}

// ---------- кадр ----------
function frame(t) {
  const v = t2v(t);
  let idx = 0;
  for (let i = 0; i < SCENES.length; i++) if (v >= SCENES[i][0]) idx = i;
  const [start, fn, fade] = SCENES[idx];
  let body = '';
  const tFade = fade > 0 ? prog(t, v2t(start), v2t(start) + fade) : 1;
  if (tFade < 1 && idx > 0) body += SCENES[idx - 1][1](v, t);
  body += `<g opacity="${tFade}">${fn(v, t)}</g>`;
  let over = vignette(1080, 1920, 0.9);
  if (v < TITLE_V) {
    const h = hudState(v);
    const ha = prog(v, -0.2, 0.4) * (1 - prog(t, v2t(TITLE_V), v2t(TITLE_V) + 0.4));
    over += `<g opacity="${ha}">${hud(h.time, h.m, { pulse: h.pulse })}</g>`;
  }
  over += subtitles(t);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920"><defs>${defs()}</defs><rect width="1080" height="1920" fill="#000"/>${body}${over}</svg>`;
}
