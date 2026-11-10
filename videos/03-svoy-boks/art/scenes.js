// Сцены «Свой бокс»: каждая — функция времени, возвращает SVG 1080×1920.
const L = require("./lib.js");
const { P, INK } = L;
const TM = require("../timing.json");

// ---------------------------------------------------------------- утилиты
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const eback = t => { t = clamp(t) - 1; return t * t * (2.7 * t + 1.7) + 1; };
const pstart = i => TM[i].start;
function wt(i, stem) {
  for (const [w, t] of TM[i].words) if (w.toLowerCase().includes(stem)) return t;
  return TM[i].start;
}
function rnd(seed) { let s = seed * 9301 + 49297; return () => ((s = (s * 9301 + 49297) % 233280) / 233280); }
function blink(t, seed) {
  const r = rnd(seed); let tt = 0;
  while (tt < 90) { tt += 2 + r() * 2.5; if (t >= tt && t < tt + 0.11) return true; }
  return false;
}
const ch = (svg, x, y, s = 1, flip = false) =>
  `<g transform="translate(${x},${y}) scale(${flip ? -s : s},${s}) translate(-200,-900)">${svg}</g>`;
const at = (svg, x, y, s = 1, r = 0) => `<g transform="translate(${x},${y}) rotate(${r}) scale(${s})">${svg}</g>`;
const cam = (svg, z = 1, cx = 540, cy = 960) =>
  `<g transform="translate(540,960) scale(${z}) translate(${-cx},${-cy})">${svg}</g>`;
const txt = (x, y, s, size, fill = INK, o = {}) =>
  `<text x="${x}" y="${y}" font-family="DejaVu Sans" font-weight="bold" font-size="${size}" fill="${fill}" text-anchor="${o.anchor || "middle"}" ${o.stroke ? `stroke="${o.stroke}" stroke-width="${o.sw || 10}" paint-order="stroke" stroke-linejoin="round"` : ""} opacity="${o.op ?? 1}">${s}</text>`;
const popS = (t, t0, d = 0.3) => (t < t0 ? 0 : eback((t - t0) / d));
const bubble = (x, y, text, k, w = null, col = "#fff") => {
  if (k <= 0) return "";
  const ww = w || 60 + text.length * 26;
  return `<g transform="translate(${x},${y}) scale(${k})"><path d="M-30,46 L-6,90 L18,46 Z" fill="${col}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/>
  <rect x="${-ww / 2}" y="-50" width="${ww}" height="100" rx="44" fill="${col}" stroke="${INK}" stroke-width="6"/>
  <path d="M-34,44 L18,44" stroke="${col}" stroke-width="10"/>${txt(0, 16, text, 42)}</g>`;
};
function snow(t, n = 60, seed = 3, region = [0, 0, 1080, 1920], speed = 90) {
  const r = rnd(seed); let s = "";
  for (let i = 0; i < n; i++) {
    const x0 = region[0] + r() * (region[2] - region[0]), ph = r(), sz = 4 + r() * 7, sp = speed * (0.6 + r() * 0.8);
    const h = region[3] - region[1];
    const y = region[1] + ((ph * h + sp * t) % h);
    const x = x0 + 18 * Math.sin(t * 1.4 + i);
    s += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${sz.toFixed(1)}" fill="#fff" opacity=".9"/>`;
  }
  return s;
}
const steam = (x, y, t) => [0, 1, 2].map(i => {
  const p = ((t * 0.6 + i / 3) % 1);
  return `<path d="M${x + i * 24 - 24},${y - p * 120} q-14,-30 4,-60" stroke="#fff" stroke-width="9" stroke-linecap="round" fill="none" opacity="${(1 - p) * 0.9}"/>`;
}).join("");

// ---------------------------------------------------------------- окружения
function office(snowT = null) {
  return `<rect width="1080" height="1920" fill="#f0dcc0"/>
  <rect x="620" y="260" width="360" height="520" rx="10" fill="#cfe1ea" stroke="${INK}" stroke-width="8"/>
  <path d="M800,260 V780 M620,520 H980" stroke="${INK}" stroke-width="8"/>
  ${snowT !== null ? `<g clip-path="url(#win)">${snow(snowT, 40, 5, [620, 260, 980, 780], 70)}</g>` : ""}
  <rect x="90" y="300" width="300" height="200" rx="8" fill="#fbf2e2" stroke="${INK}" stroke-width="6"/>
  ${txt(240, 390, "ЛУЧШИЙ", 30)}${txt(240, 430, "МЕНЕДЖЕР", 30)}
  <rect x="0" y="1300" width="1080" height="620" fill="#d8bf9c"/>`;
}
function desk(y = 1220) {
  return `<rect x="80" y="${y}" width="920" height="70" rx="8" fill="${P.wood}" stroke="${INK}" stroke-width="8"/>
  <rect x="120" y="${y + 70}" width="840" height="420" fill="${P.woodD}" stroke="${INK}" stroke-width="8"/>`;
}
function boxInside(night = false) {
  return `<rect width="1080" height="1920" fill="${night ? "#2f3a52" : "#d9d4cc"}"/>
  ${[0, 1, 2, 3, 4, 5, 6].map(i => `<path d="M0,${200 + i * 160} H1080" stroke="${night ? "#2a3349" : "#cbc5bc"}" stroke-width="8"/>`).join("")}
  <rect x="0" y="1320" width="1080" height="600" fill="${night ? "#252d40" : "#bdb5aa"}"/>
  <path d="M0,1320 H1080" stroke="${INK}" stroke-width="8"/>`;
}

// ---------------------------------------------------------------- сцены
const SC = [];
const def = (phrase, fn) => SC.push({ phrase, fn });

// 1. Руки и чужой сервис
def(0, (t, lt) => {
  const z = lerp(2.6, 1.0, eio((lt - 0.6) / 2.2));
  const lift = `<rect x="560" y="820" width="30" height="500" fill="${P.steel}" stroke="${INK}" stroke-width="6"/>
    <rect x="960" y="820" width="30" height="500" fill="${P.steel}" stroke="${INK}" stroke-width="6"/>
    <rect x="520" y="800" width="510" height="26" fill="${P.mustard}" stroke="${INK}" stroke-width="6"/>${at(L.car("#6d9bd1"), 520, 560, 1.0)}`;
  const wrench = `<g transform="translate(430,690) rotate(${-30 + 12 * Math.sin(t * 8)})"><rect x="-10" y="-90" width="20" height="120" rx="8" fill="${P.steel}" stroke="${INK}" stroke-width="5"/><circle cx="0" cy="-96" r="22" fill="${P.steel}" stroke="${INK}" stroke-width="5"/><circle cx="0" cy="-104" r="10" fill="#efd9bb"/></g>`;
  const scene = L.bgForeign() + lift +
    `<g transform="translate(380,520) rotate(-6)"><rect x="-150" y="-44" width="300" height="88" rx="14" fill="${P.red}" stroke="${INK}" stroke-width="6"/>${txt(0, 16, "МАСТЕРУ — 30%", 36, "#fff")}</g>` +
    ch(L.anton({ ra: "up", expr: "neutral", blink: blink(t, 1) }), 330, 1560, 1.05) + wrench +
    `<circle cx="300" cy="1200" r="18" fill="#4a3a30" opacity=".5"/><circle cx="420" cy="1160" r="10" fill="#4a3a30" opacity=".5"/>`;
  return cam(scene, z, lerp(430, 540, eio((lt - 0.6) / 2.2)), lerp(700, 960, eio((lt - 0.6) / 2.2)));
});

// 2. Накопления за четыре года
def(1, (t, lt) => {
  const t0 = wt(1, "пятьсот");
  let s = L.bgKitchen() + ch(L.anton({ expr: "smile", la: "hold", blink: blink(t, 2) }), 250, 1720, 1.0);
  ["2021", "2022", "2023", "2024"].forEach((y, i) => {
    const k = popS(t, t0 + 0.2 + i * 0.45);
    const fly = eio((t - (wt(1, "года") - 0.2)) / 0.6);
    const x = lerp(520 + (i % 2) * 260, 760, fly), yy = lerp(1300 + Math.floor(i / 2) * 230, 1520 - i * 30, fly);
    if (k > 0) s += at(`<rect x="-110" y="-70" width="220" height="140" rx="10" fill="#fff6e3" stroke="${INK}" stroke-width="6"/>
      <path d="M-110,-70 L0,10 L110,-70" fill="none" stroke="${INK}" stroke-width="6"/>${txt(0, 52, y, 34, P.tealD)}`, x, yy, k * 0.9, (i - 1.5) * 4);
  });
  return cam(s, lerp(1.0, 1.06, lt / 4));
});

// 3. Днём — чужие машины за 30%
def(2, (t, lt) => {
  const tp = wt(2, "тридцать");
  const split = eio((t - tp - 0.2) / 0.6);
  let s = L.bgForeign() + `<rect x="560" y="820" width="30" height="500" fill="${P.steel}" stroke="${INK}" stroke-width="6"/>
    <rect x="960" y="820" width="30" height="500" fill="${P.steel}" stroke="${INK}" stroke-width="6"/>
    <rect x="520" y="800" width="510" height="26" fill="${P.mustard}" stroke="${INK}" stroke-width="6"/>${at(L.car(P.coral), 520, 560, 1.0)}` +
    ch(L.anton({ ra: "up", expr: "tired", blink: blink(t, 3) }), 330, 1560, 1.05);
  const k = popS(t, pstart(2) + 0.3);
  if (split <= 0.01) s += at(`<rect x="-170" y="-110" width="340" height="220" rx="12" fill="#fffdf6" stroke="${INK}" stroke-width="7"/>${txt(0, -40, "ЧЕК", 34, P.greyD)}${txt(0, 40, "10 000 ₽", 64)}`, 760, 1050, k);
  else {
    s += at(L.plaque("7 000 → ХОЗЯИНУ", false, -4), lerp(760, 720, split), lerp(1050, 520, split), 0.8);
    s += at(L.plaque("3 000 → АНТОНУ", true, 4), lerp(760, 420, split), lerp(1050, 820, split), 0.8);
  }
  return cam(s, lerp(1.0, 1.05, lt / 3));
});

// 4. Вечером — таблица, он бухгалтер
def(3, (t, lt) => {
  let s = L.bgKitchen();
  const n = Math.floor(clamp((lt - 0.2) / 2.4) * 12);
  for (let i = 0; i < n; i++) {
    const cx = 340 + (i % 3) * 110, cy = 1000 + Math.floor(i / 3) * 40;
    s += `<rect x="${cx}" y="${cy}" width="96" height="30" fill="${i % 3 === 2 ? P.money : "#ffe9b8"}"/>`;
  }
  s += ch(L.anton({ expr: "tired", la: "hold", blink: blink(t, 4) }), 880, 1760, 0.95);
  const k = popS(t, wt(3, "бухгалтер"));
  s += at(`<rect x="-80" y="-110" width="160" height="220" rx="16" fill="#e9e3d8" stroke="${INK}" stroke-width="6"/><rect x="-60" y="-90" width="120" height="50" fill="#cfe7d2" stroke="${INK}" stroke-width="4"/>
    ${[0, 1, 2].map(r => [0, 1, 2].map(c => `<rect x="${-58 + c * 42}" y="${-26 + r * 42}" width="32" height="32" rx="6" fill="#fff" stroke="${INK}" stroke-width="3"/>`).join("")).join("")}`, 190, 1060, k, -8);
  return cam(s, lerp(1.04, 1.12, lt / 3), 560, 1080);
});

// 5. Декабрь: премия и заявление
def(4, (t, lt) => {
  const tz = wt(4, "заявление");
  const angry = t > tz + 0.2;
  let s = office(t) + ch(L.boss({ expr: angry ? "angry" : "neutral", red: angry, blink: blink(t, 5) }), 560, 1500, 0.95) + desk(1220);
  const kp = popS(t, wt(4, "премия"));
  s += at(`<rect x="-120" y="-70" width="240" height="140" rx="10" fill="${P.money}" stroke="${INK}" stroke-width="6"/>${txt(0, 14, "ПРЕМИЯ", 40)}`, 250, 900, kp * (t < tz ? 1 : 0.8), -6);
  const k = eout((t - tz + 0.2) / 0.5);
  if (k > 0) s += at(`<rect x="-130" y="-170" width="260" height="340" rx="8" fill="#fffdf6" stroke="${INK}" stroke-width="6"/>${txt(0, -110, "ЗАЯВЛЕНИЕ", 30)}
    ${[-50, -10, 30, 70].map(y => `<path d="M-90,${y} h180" stroke="${P.greyL}" stroke-width="8" stroke-linecap="round"/>`).join("")}<path d="M10,130 q30,-26 50,0 t50,-6" stroke="${INK}" stroke-width="5" fill="none"/>`,
    lerp(1250, 620, k), 1230, 0.9, -8);
  return `<defs><clipPath id="win"><rect x="620" y="260" width="360" height="520"/></clipPath></defs>` + cam(s, lerp(1.0, 1.06, lt / 4.4));
});

// 6. Лена уходит вместе с ним
def(5, (t, lt) => {
  const tb = wt(5, "лена");
  const walk = eio((t - wt(5, "начальник")) / 1.2);
  let s = L.bgForeign() + `<rect x="80" y="1100" width="920" height="200" fill="#d0b28a" stroke="${INK}" stroke-width="8"/>
    <rect x="300" y="1020" width="480" height="80" rx="10" fill="${P.navy}" stroke="${INK}" stroke-width="6"/>${txt(540, 1075, "ПРИЁМКА", 44, "#fff")}`;
  const bk = eio((t - tb - 0.3) / 0.6);
  s += ch(L.lena({ expr: "smile", ra: bk < 1 ? "hold" : "down", blink: blink(t, 6) }), lerp(560, 1300, walk), 1650, 1.0);
  s += `<rect x="${lerp(lerp(560, 1300, walk) + 30, 760, bk)}" y="${lerp(1250, 1110, bk)}" width="60" height="40" rx="6" fill="#fff" stroke="${INK}" stroke-width="5"/>`;
  s += ch(L.anton({ back: true }), lerp(980, 1500, walk), 1700, 0.9);
  return cam(s, 1.02);
});

// 7. Старая мойка за городом
def(6, (t, lt) => {
  const gate = Math.sin(t * 5) * 0.25 + 0.7;
  let s = L.bgWash();
  const hb = wt(6, "бокса"), hk = wt(6, "крыша"), hv = wt(6, "ворота");
  if (t > hb && t < hb + 1.0) s += `<rect x="200" y="830" width="680" height="430" fill="${P.mustard}" opacity="${0.35 * Math.sin((t - hb) * Math.PI)}"/>`;
  if (t > hk) s += snow(t, 30, 9, [360, 620, 720, 1260], 160);
  s += `<g transform="translate(580,830) scale(${t > hv ? gate : 1},1)"><rect x="0" y="0" width="300" height="430" fill="#8f9ba0" stroke="${INK}" stroke-width="7"/></g>`;
  s += snow(t, 70, 4);
  s += ch(L.anton({ back: true }), 380, 1800, 0.95) + ch(L.lena({ expr: "worried", blink: blink(t, 7) }), 700, 1800, 0.95);
  return cam(s, lerp(1.0, 1.08, lt / 4.4), 540, 1000);
});

// 8. Половина денег ушла сразу
def(7, (t, lt) => {
  const t1 = wt(7, "платёж"), t2 = wt(7, "ремонт");
  let s = boxInside() + ch(L.anton({ expr: "worried", blink: blink(t, 8) }), 260, 1760, 1.0);
  for (let i = 0; i < 10; i++) {
    const leave = i >= 4 ? (i >= 7 ? eio((t - t2) / 0.7) : eio((t - t1) / 0.7)) : 0;
    const y = 1300 - i * 40 - leave * 600, x = 720 + leave * (500 + i * 30);
    s += at(L.bill("5000"), x - 75, y, 1.1, (i % 3 - 1) * 3 + leave * 40);
  }
  return cam(s, lerp(1.0, 1.05, lt / 4));
});

// 9. Бывший хозяин распускает слухи
def(8, (t, lt) => {
  const t0 = wt(8, "рассказывал");
  let s = L.bgForeign() + ch(L.boss({ expr: "angry", red: true, la: "phone", blink: blink(t, 9) }), 540, 1700, 1.15);
  const words = [["СО СКАНДАЛОМ!", 250, 700], ["НЕНАДЁЖНЫЙ!", 820, 600], ["НЕ ЕЗДИТЕ К НЕМУ", 540, 470]];
  words.forEach(([w, x, y], i) => { s += bubble(x, y, w, popS(t, t0 + i * 0.7), null, i === 0 ? "#ffe0d8" : "#fff"); });
  return cam(s, lerp(1.0, 1.06, lt / 4.6));
});

// 10. Телефон молчал
def(9, (t, lt) => {
  let s = boxInside() + ch(L.lena({ expr: "worried", blink: blink(t, 10) }), 300, 1760, 1.0);
  s += `<rect x="560" y="1180" width="420" height="40" fill="${P.wood}" stroke="${INK}" stroke-width="6"/>` + at(L.phone("0 звонков"), 600, 960, 0.55);
  s += `<rect x="640" y="380" width="340" height="300" rx="10" fill="#fffdf6" stroke="${INK}" stroke-width="6"/>${txt(810, 430, "ЯНВАРЬ", 32)}`;
  for (let d = 0; d < 7; d++) {
    const x = 670 + (d % 4) * 76, y = 480 + Math.floor(d / 4) * 90;
    s += `<rect x="${x}" y="${y}" width="60" height="60" rx="6" fill="#fff" stroke="${INK}" stroke-width="4"/>${txt(x + 30, y + 42, d + 1, 26)}`;
    if (lt > 0.2 + d * 0.25) s += `<path d="M${x + 6},${y + 6} l48,48 M${x + 54},${y + 6} l-48,48" stroke="${P.red}" stroke-width="7"/>`;
  }
  return cam(s, lerp(1.0, 1.06, lt / 2.4));
});

// 11. Первый клиент, второй
def(10, (t, lt) => {
  const c1 = wt(10, "клиент"), c2 = wt(10, "второй");
  let s = L.bgWash({ holes: false });
  s += at(L.car(P.green), lerp(-600, 160, eout((t - c1 + 0.8) / 1.0)), 1240, 0.9);
  s += at(L.car("#6d9bd1"), lerp(-600, 520, eout((t - c2 + 0.8) / 1.0)), 1380, 0.95);
  s += ch(L.lena({ expr: "smile", ra: "wave", blink: blink(t, 11) }), 900, 1820, 0.85);
  s += at(L.plaque("+8 500", true, -5), 330, 1080, popS(t, c1));
  s += at(L.plaque("+12 000", true, 5), 700, 1190, popS(t, c2));
  return cam(s, 1.02, 540, 1000);
});

// 12. Первая выручка: тосол и кофе
def(11, (t, lt) => {
  let s = boxInside() + `<ellipse cx="540" cy="700" rx="420" ry="300" fill="#ffe7a8" opacity=".18"/>`;
  s += ch(L.anton({ expr: "tired", blink: blink(t, 12) }), 270, 1760, 0.95) + ch(L.lena({ expr: "smile", blink: blink(t, 13) }), 820, 1760, 0.95);
  s += `<rect x="300" y="1240" width="480" height="40" fill="${P.wood}" stroke="${INK}" stroke-width="6"/>`;
  s += at(L.cashbox(), 330, 1060, 1.0) + at(L.thermos(), 640, 1030, 1.0) + steam(680, 1020, t);
  const kt = popS(t, wt(11, "тосол"));
  s += at(`<rect x="-80" y="-110" width="160" height="200" rx="14" fill="${P.green}" stroke="${INK}" stroke-width="6"/>${txt(0, 0, "ТОСОЛ", 28, "#fff")}`, 860, 1150, kt * 0.7);
  return cam(s, lerp(1.0, 1.08, lt / 3.7), 540, 1100);
});

// 13. Клиент вернулся
def(12, (t, lt) => {
  const ts = wt(12, "стук"), tf = wt(12, "сорок");
  let s = L.bgWash({ holes: false }) + at(L.car(P.green, { hood: true }), 470, 1280, 1.0);
  s += ch(L.client({ expr: "angry", ra: "point", blink: blink(t, 14) }), 300, 1820, 1.0);
  s += ch(L.anton({ expr: "worried", blink: blink(t, 15) }), 880, 1820, 0.95, true);
  if (t > ts && t < ts + 1.6) [0, 1].forEach(i => { s += txt(650 + i * 150, 1180 - i * 40 + 10 * Math.sin(t * 30), "ТУК!", 52, P.red, { stroke: "#fff", sw: 10, op: clamp((t - ts - i * 0.3) * 4) }); });
  s += snow(t, 30, 21);
  return cam(s, lerp(1.0, 1.06, lt / 5), 540, 1100);
});

// 14. Ночью переделал бесплатно
def(13, (t, lt) => {
  let s = boxInside(true) + at(L.car(P.green, { hood: true }), 280, 1080, 1.05);
  s += `<polygon points="860,1200 560,1130 560,1280" fill="#fff4b0" opacity=".45"/>`;
  s += ch(L.anton({ back: true, ra: "up" }), 560, 1820, 0.95) + ch(L.lena({ expr: "tired", la: "point", blink: blink(t, 16) }), 900, 1820, 0.9, true);
  s += `<rect x="380" y="380" width="320" height="120" rx="18" fill="#1d2433" stroke="${INK}" stroke-width="6"/>${txt(540, 466, lt < 1.7 ? "03:40" : "03:41", 70, "#ff8a6a", { anchor: "middle" })}`;
  return cam(s, lerp(1.0, 1.07, lt / 4));
});

// 15. Через месяц привёз брата
def(14, (t, lt) => {
  const tb = wt(14, "брата");
  let s = L.bgWash({ snow: false, holes: false }) + at(L.car(P.green), 30, 1260, 0.85) + at(L.car("#c68fd1"), 560, 1260, 0.85);
  s += ch(L.client({ expr: "smile", ra: "out", blink: blink(t, 17) }), 330, 1820, 0.95) + ch(L.client({ expr: "smile", beard: true }), 560, 1830, 0.9);
  s += ch(L.anton({ expr: "smile", ra: "out", blink: blink(t, 18) }), 850, 1820, 0.95, true);
  s += at(L.plaque("+31 500", true, 4), 540, 1030, popS(t, tb));
  return cam(s, 1.03, 540, 1050);
});

// 16. Весной позвонил старый хозяин
def(15, (t, lt) => {
  const vib = Math.sin(t * 60) * 6 * (lt > 0.3 ? 1 : 0);
  let s = `<rect width="1080" height="1920" fill="#e8f2df"/>` + boxInside().replace(`fill="#d9d4cc"`, `fill="#e3dccf"`);
  s += `<rect x="640" y="300" width="340" height="300" rx="10" fill="${P.sky}" stroke="${INK}" stroke-width="8"/><circle cx="740" cy="520" r="40" fill="${P.green}"/><circle cx="860" cy="540" r="50" fill="${P.greenD}"/>`;
  s += ch(L.anton({ expr: "shock", la: "hold", blink: false }), 280, 1780, 1.0);
  s += at(L.phone("АВТО-ПРОФИ", true), 620 + vib, 960, 1.15, vib * 0.5);
  return cam(s, lerp(1.0, 1.1, lt / 2.3), 600, 1100);
});

// 17. Закрывается, предлагает выкупить
def(16, (t, lt) => {
  const tz = wt(16, "закрывался"), tv = wt(16, "выкупить"), tr = wt(16, "рассрочку");
  let s = L.bgForeign() + ch(L.boss({ expr: "sad", blink: blink(t, 19) }), 760, 1700, 1.0);
  const kz = eout((t - tz) / 0.5);
  if (kz > 0) s += `<g transform="translate(540,${lerp(-200, 480, kz)}) rotate(${4 * Math.sin(t * 3)})"><path d="M-60,-80 L0,-130 L60,-80" stroke="${INK}" stroke-width="5" fill="none"/>
    <rect x="-200" y="-80" width="400" height="120" rx="12" fill="${P.red}" stroke="${INK}" stroke-width="7"/>${txt(0, 0, "ЗАКРЫТО", 60, "#fff")}</g>`;
  const kc = eout((t - tv) / 0.6);
  if (kc > 0) s += at(L.contract(), lerp(-400, 140, kc), 900, 1.0, -4);
  if (t > tr) s += at(`<rect x="-230" y="-60" width="460" height="120" rx="14" fill="none" stroke="${P.red}" stroke-width="10"/>${txt(0, 20, "ПОДПИСАНО", 60, P.red)}`, 300, 1330, 1 + 0.4 * (1 - eout((t - tr) / 0.25)), -12);
  return cam(s, lerp(1.0, 1.05, lt / 5));
});

// 18. Вывеска с фамилией, шесть боксов
def(17, (t, lt) => {
  const tf = wt(17, "фамилия"), t6 = wt(17, "шесть");
  const z = lerp(1.25, 1.0, eio((t - t6 + 0.2) / 1.0));
  let s = L.bgOwn().replace(/<rect x="130" y="440"[\s\S]*?СЕРВИС КРАВЦОВА<\/text>/, "");
  const ks = eout((t - tf + 0.3) / 0.5);
  s += `<g transform="translate(0,${lerp(-500, 0, ks)})"><rect x="130" y="440" width="820" height="140" rx="20" fill="#fffaf0" stroke="${INK}" stroke-width="7"/>${txt(540, 535, "СЕРВИС КРАВЦОВА", 66, P.tealD)}</g>`;
  s += ch(L.anton({ expr: "smile", blink: blink(t, 20) }), 420, 1640, 0.9) + ch(L.lena({ expr: "smile", ra: "wave", blink: blink(t, 21) }), 680, 1640, 0.9);
  return cam(s, z, 540, lerp(780, 960, eio((t - t6 + 0.2) / 1.0)));
});

// 19. Вечер: выручка и усталость
def(18, (t, lt) => {
  let s = L.bgOwn().replace(`fill="${P.sky}"`, `fill="#f2b88a"`).replace(`fill="#ffe08a" opacity=".9"`, `fill="#ff9d6a" opacity=".9"`);
  for (let i = 0; i < 6; i++) {
    const off = lt > 1.2 + i * 0.45;
    s += `<rect x="${70 + i * 162}" y="760" width="136" height="420" fill="${off ? "#4a5358" : "#ffe7a3"}" stroke="${INK}" stroke-width="6"/>`;
  }
  s += `<rect width="1080" height="1920" fill="#3a2a40" opacity="${0.15 + 0.25 * clamp(lt / 4)}"/>`;
  s += `<rect x="260" y="1560" width="560" height="110" rx="8" fill="${P.wood}" stroke="${INK}" stroke-width="7"/>`;
  s += ch(L.anton({ expr: "tired", blink: blink(t, 22) }), 400, 1720, 0.85) + ch(L.lena({ expr: "smile", blink: blink(t, 23) }), 690, 1720, 0.85);
  s += at(L.thermos(), 500, 1420, 0.7) + steam(528, 1410, t);
  return cam(s, lerp(1.0, 1.08, lt / 4.5), 540, 1150);
});

// Финальная карточка
function endCard(t, lt) {
  const k = clamp(lt / 0.4);
  return `<rect width="1080" height="1920" fill="${P.cream}"/>
  ${at(L.thermos(), 500, 560, 1.4)}${steam(556, 540, t)}
  ${txt(540, 1040, "А ВЫ БЫ УШЛИ", 82, INK, { op: k })}${txt(540, 1140, "НА СВОЁ В 45?", 82, P.tealD, { op: k })}
  ${txt(540, 1300, "Пишите в комментариях 👇", 52, P.greyD, { op: clamp((lt - 0.8) / 0.4) })}
  ${txt(540, 1420, "История и герои вымышлены", 32, P.grey, { op: clamp((lt - 1.2) / 0.4) })}`;
}

module.exports = { SC, endCard, TM, clamp, lerp, eio, eout, eback, wt, pstart, txt, at, popS };
