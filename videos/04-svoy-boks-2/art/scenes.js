// Сцены «Свой бокс. Часть 2 — Шесть боксов»: одна сцена на фразу, SVG 1080×1920.
const L = require("./lib.js");
const { P, INK } = L;
const TM = require("../timing.json");

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const eback = t => { t = clamp(t) - 1; return t * t * (2.7 * t + 1.7) + 1; };
const pstart = i => TM[i].start;
function wt(i, stem) { for (const [w, t] of TM[i].words) if (w.toLowerCase().includes(stem)) return t; return TM[i].start; }
function rnd(seed) { let s = seed * 9301 + 49297; return () => ((s = (s * 9301 + 49297) % 233280) / 233280); }
function blink(t, seed) { const r = rnd(seed); let tt = 0; while (tt < 90) { tt += 2 + r() * 2.5; if (t >= tt && t < tt + 0.11) return true; } return false; }
const ch = (svg, x, y, s = 1, flip = false) => `<g transform="translate(${x},${y}) scale(${flip ? -s : s},${s}) translate(-200,-900)">${svg}</g>`;
const at = (svg, x, y, s = 1, r = 0) => `<g transform="translate(${x},${y}) rotate(${r}) scale(${s})">${svg}</g>`;
const cam = (svg, z = 1, cx = 540, cy = 960) => {
  z = Math.max(1, z);
  cx = Math.min(Math.max(cx, 540 / z), 1080 - 540 / z);
  cy = Math.min(Math.max(cy, 960 / z), 1920 - 960 / z);
  return `<g transform="translate(540,960) scale(${z}) translate(${-cx},${-cy})">${svg}</g>`;
};
const txt = (x, y, s, size, fill = INK, o = {}) =>
  `<text x="${x}" y="${y}" font-family="DejaVu Sans" font-weight="bold" font-size="${size}" fill="${fill}" text-anchor="${o.anchor || "middle"}" ${o.stroke ? `stroke="${o.stroke}" stroke-width="${o.sw || 10}" paint-order="stroke" stroke-linejoin="round"` : ""} opacity="${o.op ?? 1}">${s}</text>`;
const popS = (t, t0, d = 0.3) => (t < t0 ? 0 : eback((t - t0) / d));
const steam = (x, y, t) => [0, 1, 2].map(i => { const p = (t * 0.6 + i / 3) % 1;
  return `<path d="M${x + i * 24 - 24},${y - p * 120} q-14,-30 4,-60" stroke="#fff" stroke-width="9" stroke-linecap="round" fill="none" opacity="${(1 - p) * 0.9}"/>`; }).join("");
const bubble = (x, y, text, k, col = "#fff", size = 42) => {
  if (k <= 0) return ""; const ww = 60 + text.length * size * 0.62;
  return `<g transform="translate(${x},${y}) scale(${k})"><path d="M-30,46 L-6,90 L18,46 Z" fill="${col}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/>
  <rect x="${-ww / 2}" y="-50" width="${ww}" height="100" rx="44" fill="${col}" stroke="${INK}" stroke-width="6"/><path d="M-34,44 L18,44" stroke="${col}" stroke-width="10"/>${txt(0, 16, text, size)}</g>`;
};
const sign = (text, w, col = P.mustard, fg = INK, size = 44) =>
  `<rect x="${-w / 2}" y="-50" width="${w}" height="100" rx="14" fill="${col}" stroke="${INK}" stroke-width="7"/>${txt(0, 16, text, size, fg)}`;
const insideLift = (o = {}) => at(L.lift(o), 320, 640, 1.0);   // подъёмник внутри (низ на y=1200)

const SC = [];
const def = (phrase, fn) => SC.push({ phrase, fn });

// 0. Крючок: 62 000 на счету и 86 000 в месяц
def(0, (t, lt) => {
  const t86 = wt(0, "восемьдесят");
  let s = L.bgOwn() + ch(L.anton({ expr: t > t86 ? "worried" : "neutral", blink: blink(t, 1) }), 540, 1720, 1.05);
  const k = popS(t, t86);
  if (k > 0) {
    s += at(`<rect x="-260" y="-150" width="520" height="300" rx="16" fill="#fffdf6" stroke="${INK}" stroke-width="7"/>
      ${txt(0, -80, "ПЛАТЁЖ ЗА ВЫКУП", 34, P.greyD)}${txt(0, 10, "86 000 ₽", 84, P.red)}${txt(0, 90, "КАЖДЫЙ МЕСЯЦ · 36 РАЗ", 30, INK)}`, 540, 700, k * 0.85, -3);
  }
  return cam(s, lerp(1.0, 1.08, lt / 4.8), 540, 1100);
});

// 1. Шесть пустых боксов
def(1, (t, lt) => {
  let s = L.bgOwn();
  for (let i = 0; i < 6; i++) { const k = popS(t, pstart(1) + 0.3 + i * 0.22);
    if (k > 0) s += at(`<circle r="40" fill="#fff" stroke="${INK}" stroke-width="5"/>${txt(0, 14, "0", 40, P.red)}`, 138 + i * 162, 1000, k * 0.9); }
  s += ch(L.anton({ back: true }), lerp(200, 520, eio(lt / 2.4)), 1800, 0.8);
  return cam(s, lerp(1.06, 1.0, lt / 2.4), 540, 1000);
});

// 2. Он и старый подъёмник
def(2, (t, lt) => {
  const wob = Math.sin(t * 9) * 2;
  let s = L.bgInside() + insideLift({ old: true, h: 280, tilt: wob }) + ch(L.anton({ expr: "tired", ra: "up", blink: blink(t, 2) }), 290, 1780, 1.0);
  const k = popS(t, wt(2, "двое"));
  s += at(sign("ДВОЕ: ОН И ПОДЪЁМНИК", 640, P.mustard, INK, 38), 600, 520, k * 0.9, -4);
  if (Math.sin(t * 9) > 0.8) s += txt(800, 900, "СКРИП", 44, P.red, { stroke: "#fff", sw: 8 });
  return cam(s, lerp(1.0, 1.05, lt / 2.7));
});

// 3. Лена зовёт ребят из «Авто-Профи»
def(3, (t, lt) => {
  let s = L.bgInside() + ch(L.lena({ expr: "smile", la: "phone", blink: blink(t, 3) }), 300, 1780, 1.05);
  const names = [["СЕРЁГА", "serega"], ["ВИТЯ", "vitya"], ["КОЛЯ", "kolya"]];
  names.forEach(([n, w], i) => {
    const k = popS(t, pstart(3) + 0.6 + i * 0.4);
    if (k <= 0) return;
    s += at(`<circle r="110" fill="#fffaf0" stroke="${INK}" stroke-width="6"/><clipPath id="cl${i}"><circle r="104"/></clipPath>
      <g clip-path="url(#cl${i})">${at(L.mech({ who: w, expr: "neutral" }), -110, -60, 0.55)}</g>${txt(0, 150, n, 34, INK, { stroke: "#fff", sw: 8 })}`,
      620 + (i % 2) * 230 - (i === 2 ? 115 : 0), 640 + Math.floor(i / 2) * 330, k * 0.9);
  });
  return cam(s, 1.02);
});

// 4. Пришли трое; половина выручки — ваша
def(4, (t, lt) => {
  const ts = wt(4, "половина");
  let s = L.bgInside();
  ["serega", "vitya", "kolya"].forEach((w, i) => {
    const k = eout((t - pstart(4) - i * 0.25) / 0.8);
    s += ch(L.mech({ who: w, expr: t > ts ? "smile" : "neutral", blink: blink(t, 10 + i) }), lerp(1300, 520 + i * 190, k), 1780, 0.82);
  });
  s += ch(L.anton({ expr: "neutral", ra: t > ts ? "out" : "down", blink: blink(t, 4) }), 230, 1780, 0.9);
  const k = popS(t, ts);
  if (k > 0) s += at(`<circle r="130" fill="#fffaf0" stroke="${INK}" stroke-width="7"/><path d="M0,0 L0,-130 A130,130 0 0,1 0,130 Z" fill="${P.money}" stroke="${INK}" stroke-width="6"/>
    ${txt(-60, 14, "50", 52, INK)}${txt(60, 14, "50", 52, INK)}${txt(0, 190, "ВЫРУЧКА БОКСА", 34, INK, { stroke: "#fff", sw: 8 })}`, 680, 620, k * 0.9);
  return cam(s, 1.02);
});

// 5. Апрель: +70 000
def(5, (t, lt) => {
  let s = L.bgOwn();
  for (let i = 0; i < 6; i++) { const on = i < 4 && lt > 0.2 + i * 0.25;
    s += `<rect x="${70 + i * 162}" y="760" width="136" height="420" fill="${on ? "#ffe7a3" : "#58656b"}" stroke="${INK}" stroke-width="6"/>`;
    if (on) s += at(L.car(["#6d9bd1", P.coral, P.green, "#c68fd1"][i]), 72 + i * 162, 1060, 0.26); }
  s += `<g transform="translate(860,330)"><rect x="-130" y="-60" width="260" height="120" rx="14" fill="#fffdf6" stroke="${INK}" stroke-width="6"/>${txt(0, 18, "АПРЕЛЬ", 48)}</g>`;
  s += at(L.plaque("+70 000", true, -4), 540, 1350, popS(t, wt(5, "семьдесят")));
  s += ch(L.anton({ expr: "smile", blink: blink(t, 5) }), 300, 1880, 0.75) + ch(L.mech({ who: "serega", expr: "smile", ra: "up" }), 780, 1880, 0.72);
  return cam(s, lerp(1.0, 1.04, lt / 2.4), 540, 1000);
});

// 6. Май: первый платёж −86
def(6, (t, lt) => {
  let s = L.bgKitchen() + ch(L.anton({ expr: t > wt(6, "минус") ? "worried" : "neutral", la: "hold", blink: blink(t, 6) }), 280, 1760, 1.0);
  s += at(L.contract().replace("ВЫКУП СЕРВИСА", "ПЛАТЁЖ 1 ИЗ 36"), 640, 860, 0.95, 4);
  if (t > wt(6, "платёж")) s += at(`<rect x="-200" y="-60" width="400" height="120" rx="14" fill="none" stroke="${P.red}" stroke-width="10"/>${txt(0, 22, "ОПЛАЧЕНО", 60, P.red)}`, 790, 1180, 1 + 0.4 * (1 - eout((t - wt(6, "платёж")) / 0.25)), -10);
  return cam(s, lerp(1.0, 1.06, lt / 2.8));
});

// 7. Сломался старый подъёмник
def(7, (t, lt) => {
  const tb = wt(7, "сломался");
  const k = eout((t - tb) / 0.35);
  const sh = t > tb && t < tb + 0.6 ? 14 * Math.sin(t * 70) * (1 - (t - tb) / 0.6) : 0;
  let s = L.bgInside() + insideLift({ old: true, h: lerp(380, 40, k), tilt: lerp(0, 9, k) });
  s += at(L.car(P.coral), 330, lerp(1200 - 380 - 200, 1200 - 40 - 200, k), 0.82, lerp(0, 8, k));
  if (t > tb) s += txt(540, 640, "КРАК!", 110, P.red, { stroke: "#fff", sw: 14, op: clamp(1.5 - (t - tb)) });
  s += ch(L.anton({ expr: t > tb ? "shock" : "tired", blink: false }), 860, 1800, 0.9, true);
  return `<g transform="translate(${sh},${sh * 0.6})">${cam(s, 1.02)}</g>`;
});

// 8. Новый стоит 240 000
def(8, (t, lt) => {
  let s = L.bgInside() + insideLift({ h: 420, newTag: true });
  const k = popS(t, wt(8, "двести"));
  s += at(`<rect x="-250" y="-120" width="500" height="240" rx="20" fill="#ffe26a" stroke="${INK}" stroke-width="8"/>${txt(0, -40, "НОВЫЙ ПОДЪЁМНИК", 34)}${txt(0, 60, "240 000 ₽", 90)}`, 540, 1380, k * 0.9, -4);
  s += ch(L.anton({ expr: "worried", blink: blink(t, 8) }), 180, 1880, 0.7);
  return cam(s, lerp(1.0, 1.05, lt / 1.8));
});

// 9. Ночь, таблица
def(9, (t, lt) => {
  let s = L.bgKitchen();
  const n = Math.floor(clamp((lt - 0.1) / 2.2) * 12);
  for (let i = 0; i < n; i++) s += `<rect x="${340 + (i % 3) * 110}" y="${1000 + Math.floor(i / 3) * 40}" width="96" height="30" fill="${i % 3 === 2 ? "#ffd0c8" : "#ffe9b8"}"/>`;
  s += ch(L.anton({ expr: "tired", la: "hold", blink: blink(t, 9) }), 880, 1760, 0.95) + at(L.thermos(), 160, 960, 0.8) + steam(192, 950, t);
  return cam(s, lerp(1.04, 1.12, lt / 2.8), 560, 1080);
});

// 10. По утрам три бокса пустуют (таблица крупно)
def(10, (t, lt) => {
  const tu = wt(10, "утрам");
  let s = `<rect width="1080" height="1920" fill="#2f3446"/><rect x="80" y="420" width="920" height="900" rx="20" fill="#eef6f2" stroke="${INK}" stroke-width="8"/>`;
  s += txt(540, 490, "ЗАГРУЗКА БОКСОВ", 40);
  ["8:00", "11:00", "14:00", "17:00"].forEach((h, c) => { s += txt(310 + c * 170, 570, h, 30, P.greyD); });
  for (let r = 0; r < 6; r++) {
    s += txt(160, 650 + r * 105, `БОКС ${r + 1}`, 28);
    for (let c = 0; c < 4; c++) {
      const empty = c === 0 && r >= 3;
      const hl = empty && t > tu;
      s += `<rect x="${240 + c * 170}" y="${605 + r * 105}" width="150" height="80" rx="10" fill="${empty ? (hl ? (Math.sin(t * 10) > 0 ? P.red : "#ffb3a8") : "#ffffff") : P.money}" stroke="${INK}" stroke-width="4"/>`;
    }
  }
  if (t > tu) s += at(bubble(0, 0, "3 БОКСА ПУСТЫЕ!", 1, "#fff", 40), 560, 330, popS(t, tu + 0.2));
  return cam(s, lerp(1.0, 1.08, lt / 2.3), 540, 900);
});

// 11. Объявление на воротах
def(11, (t, lt) => {
  const k = eout((t - pstart(11) - 0.3) / 0.6);
  let s = L.bgOwn() + `<g transform="translate(540,${lerp(-300, 980, k)}) rotate(${-3 + 2 * Math.sin(t * 3)})">${sign("УТРОМ — БЕЗ ЗАПИСИ", 620, "#fffdf6", INK, 46)}
    <g transform="translate(0,104)">${sign("ЗА ЧАС", 300, P.mustard, INK, 48)}</g></g>`;
  s += ch(L.lena({ expr: "smile", ra: "up", blink: blink(t, 11) }), 300, 1820, 0.95);
  return cam(s, lerp(1.0, 1.05, lt / 3.3), 540, 1100);
});

// 12. Очередь из таксистов
def(12, (t, lt) => {
  let s = L.bgOwn();
  for (let i = 0; i < 5; i++) {
    const k = eout((t - pstart(12) - 0.2 - i * 0.3) / 0.8);
    s += at(L.taxi(), lerp(1300, -120 + i * 250, k), 1380 + (i % 2) * 160, 0.62);
  }
  s += at(L.plaque("+55 000", true, 4), 760, 640, popS(t, wt(12, "таксистов")));
  return cam(s, lerp(1.05, 1.0, lt / 2.4), 540, 1100);
});

// 13. Подъёмник в рассрочку. Вторую
def(13, (t, lt) => {
  const tr = wt(13, "рассрочку"), tv = wt(13, "вторую");
  let s = L.bgInside() + insideLift({ h: 420, newTag: true }) + ch(L.anton({ expr: "tired", blink: blink(t, 13) }), 200, 1820, 0.9);
  s += at(L.contract().replace("ВЫКУП СЕРВИСА", "ПОДЪЁМНИК").replace("РАССРОЧКА 3 ГОДА", "РАССРОЧКА"), 600, 1160, popS(t, tr) * 0.85, 5);
  if (t > tv) s += at(`<circle r="90" fill="${P.red}" stroke="${INK}" stroke-width="7"/>${txt(0, 30, "№2", 72, "#fff")}`, 900, 1160, popS(t, tv, 0.25), 10);
  return cam(s, 1.02);
});

// 14. Июль: новый сервис через дорогу
def(14, (t, lt) => {
  const td = wt(14, "дорогу");
  let s = L.bgRival() + ch(L.boss({ expr: "grin", ra: "wave", blink: blink(t, 14) }), 760, 1880, 0.85);
  s += `<g transform="translate(220,650)"><rect x="-130" y="-60" width="260" height="120" rx="14" fill="#fffdf6" stroke="${INK}" stroke-width="6"/>${txt(0, 18, "ИЮЛЬ", 52)}</g>`;
  if (t > td) s += at(`<path d="M-160,0 H120 M80,-40 L130,0 L80,40" stroke="${P.red}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round" fill="none"/>${txt(0, -40, "ЧЕРЕЗ ДОРОГУ", 34, P.red, { stroke: "#fff", sw: 8 })}`, 300, 1460, popS(t, td));
  return cam(s, lerp(1.0, 1.05, lt / 3.4), 540, 1000);
});

// 15. Позвал троих: вдвое больше
def(15, (t, lt) => {
  let s = L.bgRival({ banner: true }) + ch(L.boss({ expr: "grin", ra: "point", blink: blink(t, 15) }), 260, 1880, 0.85);
  ["serega", "vitya", "kolya"].forEach((w, i) => { s += ch(L.mech({ who: w, expr: i === 0 ? "worried" : "shock", look: -1, blink: blink(t, 20 + i) }), 600 + i * 170, 1880, 0.72); });
  s += at(L.plaque("×2", true, -6), 760, 1000, popS(t, wt(15, "вдвое")) * 1.3);
  return cam(s, lerp(1.0, 1.05, lt / 2.9), 540, 1100);
});

// 16. Двое ушли, остался Серёга
def(16, (t, lt) => {
  const tl = wt(16, "ушли");
  let s = L.bgInside();
  ["vitya", "kolya"].forEach((w, i) => { const k = eio((t - tl - i * 0.15) / 1.2); s += ch(L.mech({ who: w, expr: "neutral" }), lerp(640 + i * 200, 1350 + i * 200, k), 1800, 0.82, k > 0.05); });
  s += ch(L.mech({ who: "serega", expr: t > wt(16, "серёга") ? "smile" : "neutral", ra: t > wt(16, "серёга") ? "wave" : "down", blink: blink(t, 16) }), 440, 1800, 0.82);
  s += ch(L.anton({ expr: "tired", blink: blink(t, 17) }), 180, 1800, 0.85);
  if (t > wt(16, "серёга")) s += at(bubble(0, 0, "Я ОСТАЮСЬ", 1, "#fff", 40), 470, 760, popS(t, wt(16, "серёга") + 0.1));
  return cam(s, 1.02);
});

// 17. Антон снова сам у подъёмника, 41 000
def(17, (t, lt) => {
  let s = L.bgInside() + insideLift({ h: 420 }) + at(L.car("#6d9bd1"), 330, 600, 0.82);
  s += ch(L.anton({ expr: "tired", ra: "up", blink: blink(t, 18) }), 560, 1800, 1.0);
  return cam(s, lerp(1.0, 1.08, lt / 3.4), 540, 1150);
});

// 18. Но утренняя очередь пока на месте
def(18, (t, lt) => {
  let s = L.bgOwn().replace(`fill="${P.sky}"`, `fill="#ffd8b0"`).replace(`fill="#ffe08a" opacity=".9"`, `fill="#ffb36a" opacity=".9"`);
  for (let i = 0; i < 4; i++) s += at(L.taxi(), -120 + i * 250, 1380 + (i % 2) * 160, 0.62);
  s += at(L.thermos(), 900, 1640, 0.7) + steam(928, 1630, t);
  return cam(s, lerp(1.0, 1.06, lt / 2), 540, 1150);
});

function subscribeBanner(t, lt, part) {
  const k = eback(clamp(lt / 0.35));
  const pulse = 1 + 0.035 * Math.sin(Math.max(0, lt - 0.4) * 6);
  return `<g transform="translate(540,800) scale(${k * pulse})">
    <rect x="-430" y="-95" width="860" height="190" rx="95" fill="${P.red}" stroke="${INK}" stroke-width="8"/>
    ${txt(0, -12, "ПОДПИШИСЬ 🔔", 64, "#fff")}
    ${txt(0, 52, `чтобы не пропустить ${part} часть`, 40, "#fff3e6")}</g>`;
}
function endCard(t, lt) {
  const k = clamp(lt / 0.4);
  return `<rect width="1080" height="1920" fill="${P.cream}"/>${subscribeBanner(t, lt, 3)}${at(L.lift({ h: 420 }), 382, 250, 0.7)}
  ${txt(540, 1060, "ЧТО ДЕЛАТЬ АНТОНУ?", 74, INK, { op: k })}
  ${txt(540, 1160, "ВЕРНУТЬ МАСТЕРОВ", 58, P.red, { op: k })}${txt(540, 1240, "ИЛИ РАСТИТЬ СВОИХ?", 58, P.tealD, { op: k })}
  ${txt(540, 1380, "Пишите в комментариях 👇", 52, P.greyD, { op: clamp((lt - 0.6) / 0.4) })}`;
}

module.exports = { SC, endCard, TM, clamp, lerp, eio, eout, eback, wt, pstart, txt, at, popS };
