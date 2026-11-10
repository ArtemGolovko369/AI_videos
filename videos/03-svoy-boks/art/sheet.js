// Собирает лист персонажей и фонов в sheet.html и рендерит sheet.png через Chromium.
const fs = require("fs");
const path = require("path");
const L = require("./lib.js");
const { chromium } = require("playwright");

const W = 2400, H = 2560;
const label = (x, y, t, s = 34) => `<text x="${x}" y="${y}" font-family="DejaVu Sans" font-weight="bold" font-size="${s}" fill="${L.INK}" text-anchor="middle">${t}</text>`;
const chars = [
  ["Антон · обычный", L.anton({})], ["Антон · улыбка", L.anton({ expr: "smile", ra: "up" })],
  ["Антон · устал", L.anton({ expr: "tired" })], ["Антон · со спины", L.anton({ back: true })],
  ["Лена · улыбка", L.lena({ expr: "smile", ra: "wave" })], ["Лена · тревога", L.lena({ expr: "worried", la: "phone" })],
  ["Хозяин · злой", L.boss({ expr: "angry", red: true, ra: "phone" })], ["Клиент · недоволен", L.client({ expr: "angry", ra: "point" })],
  ["Брат клиента", L.client({ expr: "smile", beard: true })],
];
let body = `<rect width="${W}" height="${H}" fill="${L.P.cream}"/>`;
body += label(W / 2, 80, "«СВОЙ БОКС» — ЛИСТ ПЕРСОНАЖЕЙ И ФОНОВ (история вымышлена)", 46);
chars.forEach(([name, svg], i) => {
  const x = 30 + i * 262, s = 0.62;
  body += `<g transform="translate(${x},${140}) scale(${s})">${svg}</g>` + label(x + 124, 740, name, 24);
});
const bgs = [["Чужой сервис", L.bgForeign()], ["Кухня, вечер", L.bgKitchen()], ["Старая мойка, декабрь", L.bgWash()],
  ["Свой сервис, 6 боксов", L.bgOwn()]];
bgs.forEach(([name, svg], i) => {
  const x = 60 + i * 590, s = 0.5;
  body += `<g transform="translate(${x},800)"><clipPath id="c${i}"><rect width="540" height="960"/></clipPath>
    <g clip-path="url(#c${i})"><g transform="scale(${s})">${svg}</g></g><rect width="540" height="960" fill="none" stroke="${L.INK}" stroke-width="6"/></g>` +
    label(x + 270, 1810, name, 30);
});
const y3 = 1900;
body += `<g transform="translate(60,${y3 + 40}) scale(0.8)">${L.car(L.P.coral)}</g>`;
body += `<g transform="translate(520,${y3 + 40}) scale(0.8)">${L.car("#6d9bd1", { hood: true })}</g>`;
body += `<g transform="translate(980,${y3 + 60})">${L.bill("5000")}</g><g transform="translate(1010,${y3 + 150}) rotate(-8)">${L.bill("1000")}</g>`;
body += `<g transform="translate(1220,${y3 + 80})">${L.thermos()}</g>`;
body += `<g transform="translate(1360,${y3 + 70})">${L.cashbox()}</g>`;
body += `<g transform="translate(1700,${y3}) scale(0.75)">${L.phone("АВТО-ПРОФИ", true)}</g>`;
body += `<g transform="translate(1900,${y3}) scale(0.75)">${L.contract()}</g>`;
body += `<g transform="translate(80,${y3 + 400})">${L.counter("500 000")}</g>`;
body += `<g transform="translate(700,${y3 + 400})">${L.counter("230 500", { neg: true })}</g>`;
body += `<g transform="translate(1520,${y3 + 460})">${L.plaque("−150 000", false)}</g>`;
body += `<g transform="translate(1980,${y3 + 460})">${L.plaque("+12 000", true, 5)}</g>`;
body += label(W / 2, H - 60, "Предметы: машины клиентов, деньги, термос, касса, звонок, договор, счётчик и плашки ±", 30);
const html = `<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${body}</svg></body></html>`;
fs.writeFileSync(path.join(__dirname, "sheet.html"), html);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.goto("file://" + path.join(__dirname, "sheet.html"));
  await p.screenshot({ path: path.join(__dirname, "sheet.png") });
  await b.close();
})();
