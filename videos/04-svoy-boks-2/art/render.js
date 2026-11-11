// Рендер «Свой бокс»: SVG-кадры → Chromium → ffmpeg.
// node render.js --stills          контрольные кадры в ../out/stills
// node render.js                   видео без звука в ../out/video.mp4
const fs = require("fs");
const path = require("path");
const { spawn, execFileSync } = require("child_process");
const { chromium } = require("playwright");
const L = require("./lib.js");
const S = require("./scenes.js");
const { SC, endCard, TM, clamp, eio, eout, eback, wt, pstart, txt, at } = S;
const { P, INK } = L;

const FPS = 30;
const VOICE_END = TM[TM.length - 1].end;
const END_T = VOICE_END + 0.45;
const TOTAL = END_T + 4.4;
const XF = 0.25;
const OUT = path.join(__dirname, "..", "out");

const starts = SC.map((s, i) => (i === 0 ? 0 : TM[s.phrase].start - 0.3));
function sceneAt(t) { let k = 0; starts.forEach((s, i) => { if (t >= s) k = i; }); return k; }
const sceneEnd = i => (i + 1 < SC.length ? starts[i + 1] : END_T);

// ---------------------------------------------------------------- счётчик денег
const EV = [
  { t: wt(5, "семьдесят"), d: 70000 },
  { t: wt(6, "минус"), d: -86000, label: "−86 000 · платёж 1 из 36" },
  { t: wt(12, "таксистов"), d: 55000 },
  { t: wt(13, "рассрочку"), d: -60000, label: "−60 000 · взнос за подъёмник" },
];
const T_SAVE = -1;
function money(t) {
  let v = 62000;
  for (const e of EV) if (t > e.t) v += e.d * eout((t - e.t) / 0.7);
  return Math.round(v / 100) * 100;
}
const fmt = v => Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
function hud(t) {
  if (t >= END_T) return "";
  const k = clamp(t / 0.4);
  let neg = false, pos = false, shake = 0;
  for (const e of EV) if (t > e.t && t < e.t + 1.2) { neg = e.d < 0; pos = e.d > 0; if (neg) shake = 8 * (1 - (t - e.t) / 1.2) * Math.sin(t * 60); }
    let s = `<g transform="translate(${260 + shake},${64 - (1 - k) * 200})">${L.counter(fmt(money(t)), { neg, pos })}</g>`;
  for (const e of EV) if (e.label && t > e.t && t < e.t + 1.6) {
    const kk = eback((t - e.t) / 0.3), a = clamp((e.t + 1.6 - t) / 0.3);
    s += `<g opacity="${a}">${at(L.plaque(e.label, false, -3), 540, 270, kk * 0.75)}</g>`;
  }
  return s;
}

// ---------------------------------------------------------------- субтитры
const Y = "#ffd447", G = "#9be38a", R = "#ff6b5a";
const HL = {
  0: { шестьдесят: Y, две: Y, восемьдесят: R, шесть: R, месяц: R }, 1: { шестью: Y, боксами: Y }, 2: { двое: Y, старый: R },
  3: { лена: Y, "авто-профи": Y }, 4: { трое: Y, честно: Y, половина: G, ваша: G }, 5: { апрель: G, семьдесят: G, тысяч: G },
  6: { платёж: R, минус: R, восемьдесят: R, шесть: R }, 7: { сломался: R, подъёмник: R }, 8: { двести: R, сорок: R, тысяч: R },
  9: { бухгалтер: Y }, 10: { утрам: Y, три: Y, пустуют: R }, 11: { утром: G, записи: G, час: G }, 12: { очередь: G, таксистов: G },
  13: { рассрочку: Y, вторую: R }, 14: { июле: Y, новый: R, дорогу: R }, 15: { троих: Y, вдвое: R }, 16: { двое: R, ушли: R, серёга: G },
  17: { сам: Y, сорок: Y, одна: Y, тысяча: Y }, 18: { очередь: G, пока: Y },
};
const CHUNKS = [];
TM.forEach((p, i) => {
  const n = p.words.length, k = Math.max(1, Math.ceil(n / 5)), size = Math.ceil(n / k);
  for (let j = 0; j < n; j += size) CHUNKS.push({ i, words: p.words.slice(j, j + size) });
});
CHUNKS.forEach((c, k) => {
  c.s = c.words[0][1] - 0.05;
  const nx = k + 1 < CHUNKS.length ? CHUNKS[k + 1].words[0][1] - 0.05 : END_T;
  c.e = Math.min(nx, TM[c.i].end + 0.6);
});
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
function subs(t) {
  const c = CHUNKS.find(c => t >= c.s && t < c.e);
  if (!c) return "";
  const size = 72, maxc = 19;
  const lines = [[]]; let len = 0;
  for (const w of c.words) {
    if (len && len + w[0].length + 1 > maxc) { lines.push([]); len = 0; }
    lines[lines.length - 1].push(w); len += w[0].length + 1;
  }
  const fade = clamp((c.e - t) / 0.12);
  const y0 = 1480 - (lines.length - 1) * size * 0.6;
  return lines.map((ln, li) => {
    const spans = ln.map(([w, wt_]) => {
      const a = clamp((t - wt_ + 0.05) / 0.12) * fade;
      const key = w.toLowerCase().replace(/[.,:!?…«»—]/g, "");
      const col = (HL[c.i] || {})[key] || "#ffffff";
      return `<tspan fill="${col}" fill-opacity="${a}" stroke-opacity="${a}">${esc(w.toUpperCase())} </tspan>`;
    }).join("");
    return `<text x="540" y="${y0 + li * size * 1.2}" font-family="DejaVu Sans" font-weight="bold" font-size="${size}" text-anchor="middle"
      stroke="${INK}" stroke-width="14" stroke-linejoin="round" paint-order="stroke">${spans}</text>`;
  }).join("");
}

// ---------------------------------------------------------------- кадр
function frame(t) {
  let body;
  if (t >= END_T) {
    const a = clamp((t - END_T) / 0.4);
    const last = SC.length - 1;
    body = (a < 1 ? SC[last].fn(t, t - starts[last]) : "") + `<g opacity="${a}">${endCard(t, t - END_T)}</g>`;
  } else {
    const i = sceneAt(t);
    body = SC[i].fn(t, t - starts[i]);
    const e = sceneEnd(i);
    if (i + 1 < SC.length && e - t < XF) {
      const a = eio(1 - (e - t) / XF);
      body += `<g opacity="${a}">${SC[i + 1].fn(t, t - starts[i + 1])}</g>`;
    }
  }
  let chip = "";
  if (t < 3.0) chip = `<g opacity="${clamp((3.0 - t) / 0.3)}"><rect x="300" y="210" width="480" height="64" rx="32" fill="#fffaf0" stroke="${INK}" stroke-width="5"/>${txt(540, 253, "ЧАСТЬ 2 · СВОЙ БОКС", 28)}</g>`;
  const fadeOut = t > TOTAL - 0.4 ? `<rect width="1080" height="1920" fill="#000" opacity="${clamp((t - (TOTAL - 0.4)) / 0.4)}"/>` : "";
  return body + hud(t) + chip + subs(t) + fadeOut;
}

// ---------------------------------------------------------------- Chromium
const PAGE = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff4e4}</style></head>
<body><svg id="s" xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920"></svg></body></html>`;
async function openPage(b) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent(PAGE);
  return p;
}
async function shot(p, t, type = "jpeg") {
  await p.evaluate(h => { document.getElementById("s").innerHTML = h; }, frame(t));
  return p.screenshot(type === "png" ? { type: "png" } : { type: "jpeg", quality: 93 });
}

async function worker(a, b, out) {
  const br = await chromium.launch();
  const p = await openPage(br);
  const ff = spawn("ffmpeg", ["-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], { stdio: ["pipe", "inherit", "inherit"] });
  for (let n = a; n < b; n++) {
    const buf = await shot(p, n / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await br.close();
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  if (process.argv[2] === "--worker") return worker(+process.argv[3], +process.argv[4], process.argv[5]);
  if (process.argv[2] === "--stills") {
    fs.mkdirSync(path.join(OUT, "stills"), { recursive: true });
    const br = await chromium.launch(); const p = await openPage(br);
    const ts = SC.map((s, i) => starts[i] + (sceneEnd(i) - starts[i]) * 0.7).concat([END_T + 2.5]);
    for (let i = 0; i < ts.length; i++) fs.writeFileSync(path.join(OUT, "stills", `${String(i).padStart(2, "0")}.jpg`), await shot(p, ts[i]));
    await br.close(); return;
  }
  const nfr = Math.round(TOTAL * FPS), parts = 4, step = Math.ceil(nfr / parts);
  const files = [];
  await Promise.all([...Array(parts).keys()].map(k => new Promise((res, rej) => {
    const f = path.join(OUT, `part${k}.mp4`); files.push(f);
    const c = spawn(process.execPath, [__filename, "--worker", k * step, Math.min(nfr, (k + 1) * step), f], { stdio: "inherit" });
    c.on("close", code => (code ? rej(new Error("worker " + k)) : res()));
  })));
  files.sort();
  fs.writeFileSync(path.join(OUT, "parts.txt"), files.map(f => `file '${f}'`).join("\n"));
  execFileSync("ffmpeg", ["-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", path.join(OUT, "parts.txt"), "-c", "copy", path.join(OUT, "video.mp4")]);
  files.forEach(f => fs.unlinkSync(f));
  fs.writeFileSync(path.join(OUT, "meta.json"), JSON.stringify({ TOTAL, END_T, starts, EV, T_SAVE }, null, 1));
  console.log("video", TOTAL.toFixed(2));
}
main();
