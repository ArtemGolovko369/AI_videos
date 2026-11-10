// Библиотека рисовки «Свой бокс»: плоские 2D-человечки и фоны на SVG.
// Все функции возвращают строки SVG. Персонажи: локальная система 400×900, ноги в (200, 900).

const INK = "#3b2b26";
const P = {
  cream: "#fff4e4", paper: "#fbe9d0", peach: "#f6c9a4", sand: "#e9cf9f", mustard: "#f2b33d",
  orange: "#ee8a3c", coral: "#e86a55", red: "#d9493b", teal: "#2f8f8b", tealD: "#246f6c", navy: "#34506e",
  sky: "#bfe0ec", skyW: "#dcecf2", snow: "#fbfbf8", green: "#7bb661", greenD: "#5a9447",
  skin: "#f3c7a2", skinD: "#e2ab86", blush: "#f39a8a", grey: "#9a9490", greyL: "#cfc8c0", greyD: "#6e6862",
  steel: "#b9c3c8", wood: "#c88b54", woodD: "#a56d3f", money: "#8cc97a", moneyD: "#5f9e52",
};
const S = (w = 7) => `stroke="${INK}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;

// ---------------------------------------------------------------- лица
function eyes(x1, x2, y, o = {}) {
  const lx = (o.look || 0) * 6;
  if (o.blink) return `<path d="M${x1 - 11},${y} h22 M${x2 - 11},${y} h22" ${S(6)} fill="none"/>`;
  if (o.tired) return `<path d="M${x1 - 12},${y - 2} q12,8 24,0 M${x2 - 12},${y - 2} q12,8 24,0" ${S(5)} fill="none"/>
     <circle cx="${x1 + lx}" cy="${y + 4}" r="6" fill="${INK}"/><circle cx="${x2 + lx}" cy="${y + 4}" r="6" fill="${INK}"/>`;
  if (o.wide) return `<circle cx="${x1}" cy="${y}" r="15" fill="#fff" ${S(5)}/><circle cx="${x2}" cy="${y}" r="15" fill="#fff" ${S(5)}/>
     <circle cx="${x1 + lx}" cy="${y}" r="6" fill="${INK}"/><circle cx="${x2 + lx}" cy="${y}" r="6" fill="${INK}"/>`;
  return `<circle cx="${x1 + lx}" cy="${y}" r="8" fill="${INK}"/><circle cx="${x2 + lx}" cy="${y}" r="8" fill="${INK}"/>
     <circle cx="${x1 + lx + 3}" cy="${y - 3}" r="2.5" fill="#fff"/><circle cx="${x2 + lx + 3}" cy="${y - 3}" r="2.5" fill="#fff"/>`;
}
function mouth(x, y, kind) {
  switch (kind) {
    case "smile": return `<path d="M${x - 22},${y - 4} q22,20 44,0" ${S(6)} fill="none"/>`;
    case "grin": return `<path d="M${x - 24},${y - 6} q24,30 48,0 z" ${S(5)} fill="#fff"/>`;
    case "sad": return `<path d="M${x - 18},${y + 6} q18,-14 36,0" ${S(6)} fill="none"/>`;
    case "angry": return `<path d="M${x - 22},${y + 8} q22,-18 44,0 z" ${S(5)} fill="#8a3a33"/>`;
    case "open": return `<ellipse cx="${x}" cy="${y + 2}" rx="13" ry="15" fill="#8a3a33" ${S(5)}/>`;
    case "tired": return `<path d="M${x - 16},${y} q16,6 32,0" ${S(5)} fill="none"/>`;
    default: return `<path d="M${x - 16},${y} h32" ${S(6)} fill="none"/>`;
  }
}
function brows(x1, x2, y, kind) {
  if (kind === "angry") return `<path d="M${x1 - 18},${y - 10} l30,10 M${x2 + 18},${y - 10} l-30,10" ${S(7)} fill="none"/>`;
  if (kind === "worried") return `<path d="M${x1 - 16},${y} l28,-8 M${x2 + 16},${y} l-28,-8" ${S(6)} fill="none"/>`;
  if (kind === "up") return `<path d="M${x1 - 14},${y - 8} q14,-10 28,0 M${x2 - 14},${y - 8} q14,-10 28,0" ${S(6)} fill="none"/>`;
  return `<path d="M${x1 - 14},${y} h28 M${x2 - 14},${y} h28" ${S(6)} fill="none"/>`;
}
const EXPR = {
  neutral: { m: "flat", b: "flat" }, smile: { m: "smile", b: "flat" }, grin: { m: "grin", b: "up" },
  tired: { m: "tired", b: "worried", tired: true }, worried: { m: "sad", b: "worried" },
  angry: { m: "angry", b: "angry" }, shock: { m: "open", b: "up", wide: true }, sad: { m: "sad", b: "worried" },
};

// ---------------------------------------------------------------- тело
function legs(c1, shoe) {
  return `<path d="M150,640 L146,872 L192,872 L196,640 Z" fill="${c1}" ${S()}/>
  <path d="M204,640 L208,872 L254,872 L250,640 Z" fill="${c1}" ${S()}/>
  <ellipse cx="164" cy="880" rx="40" ry="18" fill="${shoe}" ${S(6)}/>
  <ellipse cx="236" cy="880" rx="40" ry="18" fill="${shoe}" ${S(6)}/>`;
}
function arm(side, pose, col, skin = P.skin) {
  // side: -1 левая (со стороны зрителя), 1 правая
  const sx = 200 + side * 92, sy = 400;
  const ends = { down: [side * 22, 230], out: [side * 150, 130], up: [side * 60, -150], hip: [side * -10, 190],
    phone: [side * -40, -10], hold: [side * -60, 140], point: [side * 170, 40], wave: [side * 90, -170] };
  const [dx, dy] = ends[pose] || ends.down;
  const ex = sx + dx, ey = sy + dy;
  return `<path d="M${sx},${sy} L${ex},${ey}" stroke="${INK}" stroke-width="58" stroke-linecap="round"/>
  <path d="M${sx},${sy} L${ex},${ey}" stroke="${col}" stroke-width="44" stroke-linecap="round"/>
  <circle cx="${ex}" cy="${ey}" r="24" fill="${skin}" ${S(6)}/>`;
}
function head(cx, cy, hair, o, extra = "") {
  const e = EXPR[o.expr || "neutral"];
  return `<ellipse cx="${cx}" cy="${cy}" rx="96" ry="104" fill="${P.skin}" ${S()}/>
  ${extra}
  ${hair}
  ${brows(cx - 34, cx + 34, cy - 30, e.b)}
  ${eyes(cx - 34, cx + 34, cy, { blink: o.blink, tired: e.tired || o.tired, wide: e.wide, look: o.look })}
  <ellipse cx="${cx - 58}" cy="${cy + 34}" rx="16" ry="10" fill="${P.blush}" opacity=".7"/>
  <ellipse cx="${cx + 58}" cy="${cy + 34}" rx="16" ry="10" fill="${P.blush}" opacity=".7"/>
  ${mouth(cx, cy + 50, e.m)}`;
}

// ---------------------------------------------------------------- персонажи
// Антон, 45: механик, бирюзовый комбинезон, седеющие виски, щетина.
function anton(o = {}) {
  const la = o.la || "down", ra = o.ra || "down";
  const body = `<path d="M110,380 Q110,340 160,336 L240,336 Q290,340 290,380 L300,650 L100,650 Z" fill="${P.teal}" ${S()}/>
  <path d="M150,420 h100 v90 h-100 z" fill="${P.tealD}" ${S(5)}/>
  <path d="M146,336 L170,440 M254,336 L230,440" ${S(6)} fill="none"/>
  <rect x="160" y="380" width="22" height="22" rx="5" fill="${P.mustard}" ${S(4)}/>
  <rect x="218" y="380" width="22" height="22" rx="5" fill="${P.mustard}" ${S(4)}/>
  <text x="200" y="476" font-family="DejaVu Sans" font-weight="bold" font-size="28" fill="#fff" text-anchor="middle">${o.badge || ""}</text>`;
  const bodyBack = `<path d="M110,380 Q110,340 160,336 L240,336 Q290,340 290,380 L300,650 L100,650 Z" fill="${P.teal}" ${S()}/>
  <path d="M146,336 L190,470 L210,470 L254,336" ${S(6)} fill="none"/>`;
  const hair = `<path d="M106,170 Q110,70 200,64 Q290,70 294,170 Q284,128 250,118 Q200,104 150,118 Q116,128 106,170 Z" fill="#5a4a42" ${S(6)}/>
  <path d="M106,168 Q104,140 118,124 L124,176 Z M294,168 Q296,140 282,124 L276,176 Z" fill="${P.greyL}" ${S(4)}/>`;
  const stubble = `<path d="M128,234 Q200,300 272,234 Q262,286 200,296 Q138,286 128,234 Z" fill="#c9a690" opacity=".55"/>`;
  return `<g>${legs(P.tealD, "#4a3a34")}${o.back ? "" : arm(-1, la, P.teal)}${o.back ? bodyBack : body}${o.back ? "" : arm(1, ra, P.teal)}
  <rect x="176" y="300" width="48" height="44" fill="${P.skin}" ${S(6)}/>
  ${o.back ? `<ellipse cx="200" cy="200" rx="96" ry="104" fill="#5a4a42" ${S()}/>${arm(-1, la, P.teal)}${arm(1, ra, P.teal)}`
    : head(200, 200, hair, o, stubble)}</g>`;
}

// Лена: бывшая приёмщица, горчичный кардиган, рыжий хвост.
function lena(o = {}) {
  const la = o.la || "down", ra = o.ra || "down";
  const body = `<path d="M116,380 Q116,342 164,338 L236,338 Q284,342 284,380 L300,640 L100,640 Z" fill="${P.mustard}" ${S()}/>
  <path d="M184,338 L200,640 L216,338 Z" fill="#fff6e8" ${S(5)}/>
  <circle cx="176" cy="470" r="7" fill="${INK}"/><circle cx="176" cy="540" r="7" fill="${INK}"/>`;
  const hair = `<path d="M100,200 Q96,80 200,70 Q304,80 300,200 Q296,140 250,126 Q240,160 180,150 Q130,150 104,206 Z" fill="${P.orange}" ${S(6)}/>`;
  const tail = `<path d="M286,150 Q360,190 330,290 Q318,230 284,206 Z" fill="${P.orange}" ${S(6)}/>`;
  return `<g>${legs("#4b5d7a", "#7a3b30")}${arm(-1, la, P.mustard)}${body}${arm(1, ra, P.mustard)}
  <rect x="178" y="300" width="44" height="44" fill="${P.skin}" ${S(6)}/>
  ${tail}${head(200, 200, hair, o)}
  ${o.badge ? `<rect x="226" y="400" width="54" height="34" rx="6" fill="#fff" ${S(4)}/>` : ""}</g>`;
}

// Старый хозяин: лысина, бордовый жилет, живот, золотая цепь.
function boss(o = {}) {
  const la = o.la || "down", ra = o.ra || "down";
  const face = o.red ? "#f0a088" : P.skin;
  const body = `<path d="M96,384 Q96,340 160,336 L240,336 Q304,340 304,384 Q330,520 296,650 L104,650 Q70,520 96,384 Z" fill="#fff" ${S()}/>
  <path d="M96,384 Q96,340 160,336 L182,336 L182,650 L104,650 Q70,520 96,384 Z M304,384 Q304,340 240,336 L218,336 L218,650 L296,650 Q330,520 304,384 Z" fill="#8e3b46" ${S()}/>
  <path d="M182,430 Q200,470 218,430" stroke="#e8b74a" stroke-width="7" fill="none"/>`;
  const hair = `<path d="M104,200 Q100,150 118,132 L128,200 Z M296,200 Q300,150 282,132 L272,200 Z" fill="${P.greyD}" ${S(5)}/>
  <path d="M150,96 Q170,84 186,92" stroke="#fff" stroke-width="8" stroke-linecap="round" fill="none" opacity=".7"/>`;
  const moust = `<path d="M160,236 Q200,222 240,236 Q220,250 200,242 Q180,250 160,236 Z" fill="${P.greyD}" ${S(4)}/>`;
  return `<g>${legs("#3e3a44", "#2e2a30")}${arm(-1, la, "#fff")}${body}${arm(1, ra, "#fff")}
  <rect x="176" y="300" width="48" height="44" fill="${face}" ${S(6)}/>
  <g>${head(200, 200, hair, o, moust).replace(`fill="${P.skin}"`, `fill="${face}"`)}</g></g>`;
}

// Клиент: зелёная куртка, кепка. o.beard — его брат.
function client(o = {}) {
  const la = o.la || "down", ra = o.ra || "down";
  const jacket = o.beard ? "#6d7fb0" : P.green;
  const body = `<path d="M108,380 Q108,340 160,336 L240,336 Q292,340 292,380 L300,650 L100,650 Z" fill="${jacket}" ${S()}/>
  <path d="M200,340 V640" ${S(5)}/><rect x="120" y="560" width="160" height="34" fill="${o.beard ? "#5b6c9a" : P.greenD}" ${S(5)}/>`;
  const cap = `<path d="M104,170 Q110,74 200,70 Q290,74 296,170 Z" fill="${o.beard ? "#3d4a6c" : P.red}" ${S(6)}/>
  <path d="M104,166 Q60,170 50,186 L200,186" fill="${o.beard ? "#3d4a6c" : P.red}" ${S(6)}/>`;
  const beard = o.beard ? `<path d="M118,230 Q200,330 282,230 Q280,300 200,316 Q120,300 118,230 Z" fill="#7a5a46" ${S(5)}/>` : "";
  return `<g>${legs("#4a4e5a", "#33302e")}${arm(-1, la, jacket)}${body}${arm(1, ra, jacket)}
  <rect x="176" y="300" width="48" height="44" fill="${P.skin}" ${S(6)}/>
  ${head(200, 200, cap, o, beard)}</g>`;
}

// ---------------------------------------------------------------- предметы
function car(color = P.coral, o = {}) {
  // машина боком, локально 0..520 × 0..240, колёса на y=230
  return `<g>
  <path d="M20,190 Q14,130 70,120 L140,118 L190,60 Q204,46 230,46 L360,46 Q384,46 400,62 L452,118 Q510,124 510,176 L510,200 Q510,212 496,212 L34,212 Q20,212 20,190 Z" fill="${color}" ${S()}/>
  <path d="M206,70 L180,118 L290,118 L290,70 Z M310,70 L310,118 L424,118 L386,74 Q380,70 370,70 Z" fill="${P.skyW}" ${S(6)}/>
  <rect x="480" y="140" width="26" height="20" rx="5" fill="#ffe08a" ${S(4)}/>
  <rect x="24" y="140" width="22" height="20" rx="5" fill="#f26a5a" ${S(4)}/>
  ${o.hood ? `<path d="M396,118 L452,72 L470,82 L420,124 Z" fill="${color}" ${S(6)}/>` : ""}
  <circle cx="126" cy="214" r="44" fill="#3b3330" ${S(6)}/><circle cx="126" cy="214" r="18" fill="${P.steel}"/>
  <circle cx="404" cy="214" r="44" fill="#3b3330" ${S(6)}/><circle cx="404" cy="214" r="18" fill="${P.steel}"/>
  </g>`;
}
function bill(v = "5000") {
  return `<g><rect x="0" y="0" width="150" height="76" rx="8" fill="${P.money}" ${S(5)}/>
  <circle cx="75" cy="38" r="22" fill="${P.moneyD}" ${S(4)}/>
  <text x="18" y="26" font-family="DejaVu Sans" font-weight="bold" font-size="18" fill="${INK}">${v}</text></g>`;
}
function thermos() {
  return `<g><rect x="0" y="40" width="80" height="170" rx="20" fill="${P.red}" ${S()}/>
  <rect x="10" y="10" width="60" height="40" rx="8" fill="${P.greyD}" ${S(6)}/>
  <rect x="0" y="110" width="80" height="26" fill="${P.cream}" ${S(5)}/>
  <path d="M30,0 q-12,-30 4,-56 M52,0 q-12,-30 4,-56" stroke="#fff" stroke-width="8" stroke-linecap="round" fill="none" opacity=".9"/></g>`;
}
function cashbox(open = true) {
  return `<g><rect x="0" y="60" width="260" height="120" rx="12" fill="${P.navy}" ${S()}/>
  ${open ? `<path d="M0,60 L30,0 L290,0 L260,60 Z" fill="#4c6d90" ${S()}/>` : ""}
  <rect x="20" y="70" width="70" height="40" rx="5" fill="${P.money}" ${S(4)}/>
  <rect x="100" y="70" width="70" height="40" rx="5" fill="${P.money}" ${S(4)}/>
  <rect x="180" y="70" width="60" height="40" rx="5" fill="#d6c3a0" ${S(4)}/></g>`;
}
function phone(text = "", ring = false) {
  return `<g><rect x="0" y="0" width="200" height="380" rx="30" fill="#2d2a2e" ${S()}/>
  <rect x="14" y="40" width="172" height="300" rx="12" fill="${ring ? "#eaf6ef" : "#fdf8ef"}"/>
  ${ring ? `<circle cx="100" cy="150" r="44" fill="${P.greyL}" ${S(5)}/><text x="100" y="240" font-family="DejaVu Sans" font-weight="bold" font-size="17" fill="${INK}" text-anchor="middle">${text}</text>
  <circle cx="54" cy="300" r="24" fill="${P.red}" ${S(4)}/><circle cx="146" cy="300" r="24" fill="${P.green}" ${S(4)}/>`
    : `<text x="100" y="190" font-family="DejaVu Sans" font-weight="bold" font-size="26" fill="${INK}" text-anchor="middle">${text}</text>`}
  </g>`;
}
function contract() {
  return `<g><rect x="0" y="0" width="300" height="400" rx="10" fill="#fffdf6" ${S()}/>
  <text x="150" y="60" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="${INK}" text-anchor="middle">ДОГОВОР</text>
  <text x="150" y="100" font-family="DejaVu Sans" font-size="20" fill="${INK}" text-anchor="middle">ВЫКУП СЕРВИСА</text>
  ${[150, 185, 220, 255].map(y => `<path d="M40,${y} h220" stroke="${P.greyL}" stroke-width="8" stroke-linecap="round"/>`).join("")}
  <rect x="40" y="290" width="220" height="44" rx="8" fill="${P.mustard}" ${S(4)}/>
  <text x="150" y="320" font-family="DejaVu Sans" font-weight="bold" font-size="20" fill="${INK}" text-anchor="middle">РАССРОЧКА 3 ГОДА</text>
  <path d="M60,370 q30,-30 50,0 t60,-6" ${S(5)} fill="none"/></g>`;
}
// Плашка счётчика денег (HUD)
function counter(value, o = {}) {
  const col = o.neg ? P.red : o.pos ? P.moneyD : INK;
  return `<g><rect x="0" y="0" width="560" height="120" rx="28" fill="#fffaf0" ${S(6)}/>
  <text x="34" y="44" font-family="DejaVu Sans" font-weight="bold" font-size="24" fill="${P.greyD}">ОСТАЛОСЬ У АНТОНА</text>
  <text x="34" y="100" font-family="DejaVu Sans Mono" font-weight="bold" font-size="54" fill="${col}">${value} ₽</text>
  <circle cx="500" cy="60" r="34" fill="${P.mustard}" ${S(5)}/><text x="500" y="74" font-family="DejaVu Sans" font-weight="bold" font-size="38" fill="${INK}" text-anchor="middle">₽</text></g>`;
}
function plaque(text, pos = true, rot = -6) {
  const w = 40 + text.length * 30;
  return `<g transform="rotate(${rot})"><rect x="${-w / 2}" y="-44" width="${w}" height="88" rx="14" fill="${pos ? P.money : P.red}" ${S(6)}/>
  <text x="0" y="18" font-family="DejaVu Sans" font-weight="bold" font-size="48" fill="${pos ? INK : "#fff"}" text-anchor="middle">${text}</text></g>`;
}

// ---------------------------------------------------------------- фоны (1080×1920)
function bgForeign() {
  // чужой сервис «АВТО-ПРОФИ»: бокс с подъёмником
  return `<g><rect width="1080" height="1920" fill="${P.paper}"/>
  <rect x="0" y="0" width="1080" height="1250" fill="#efd9bb"/>
  ${[0, 1, 2, 3, 4, 5].map(i => `<rect x="${i * 180}" y="0" width="12" height="1250" fill="#e3c9a6"/>`).join("")}
  <rect x="190" y="300" width="700" height="130" rx="18" fill="${P.navy}" ${S()}/>
  <text x="540" y="390" font-family="DejaVu Sans" font-weight="bold" font-size="76" fill="#fff" text-anchor="middle">АВТО-ПРОФИ</text>
  <rect x="80" y="520" width="300" height="420" rx="10" fill="#d6bc98" ${S(6)}/>
  ${[600, 700, 800].map(y => `<path d="M100,${y} h260" ${S(6)}/>`).join("")}
  <rect x="120" y="560" width="60" height="40" fill="${P.red}" ${S(4)}/><rect x="200" y="660" width="90" height="40" fill="${P.mustard}" ${S(4)}/>
  <rect x="0" y="1250" width="1080" height="670" fill="#d9c2a0"/>
  <path d="M0,1250 H1080" ${S(8)}/>
  <rect x="470" y="700" width="40" height="560" fill="${P.steel}" ${S(6)}/><rect x="900" y="700" width="40" height="560" fill="${P.steel}" ${S(6)}/>
  <rect x="440" y="1010" width="530" height="30" fill="${P.mustard}" ${S(6)}/>
  <ellipse cx="300" cy="1500" rx="140" ry="26" fill="#bea47f"/></g>`;
}
function bgKitchen() {
  return `<g><rect width="1080" height="1920" fill="#f3dcc0"/>
  <rect x="600" y="260" width="380" height="460" rx="12" fill="#3d4a6c" ${S()}/>
  <path d="M790,260 V720 M600,490 H980" ${S(8)}/>
  <circle cx="900" cy="350" r="36" fill="#fff6c8" opacity=".9"/>
  ${[[660, 600], [720, 420], [860, 560], [930, 640], [690, 330]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="6" fill="#fff"/>`).join("")}
  <path d="M120,200 h300 v220 h-300 z" fill="#f8e7cf" ${S(6)}/><path d="M150,260 h240 M150,320 h180" stroke="${P.greyL}" stroke-width="10" stroke-linecap="round"/>
  <path d="M480,0 V160" ${S(5)}/><path d="M420,160 h120 l-30,60 h-60 z" fill="${P.mustard}" ${S(6)}/>
  <ellipse cx="480" cy="250" rx="160" ry="40" fill="#fff3b0" opacity=".5"/>
  <rect x="0" y="1180" width="1080" height="60" fill="${P.wood}" ${S()}/>
  <rect x="0" y="1240" width="1080" height="680" fill="#e4c39a"/>
  <rect x="300" y="960" width="420" height="230" rx="14" fill="#3a3d48" ${S()}/>
  <rect x="320" y="980" width="380" height="190" fill="#eef6f2"/>
  ${[0, 1, 2, 3].map(i => `<path d="M340,${1010 + i * 40} h340" stroke="${P.greyL}" stroke-width="4"/>`).join("")}
  ${[0, 1, 2].map(i => `<path d="M${450 + i * 110},990 v170" stroke="${P.greyL}" stroke-width="4"/>`).join("")}
  <path d="M250,1190 h520 l-40,20 h-440 z" fill="#55596a" ${S(6)}/>
  <rect x="790" y="1080" width="90" height="110" rx="14" fill="#fff" ${S(6)}/><path d="M880,1110 q40,10 0,50" ${S(7)} fill="none"/>
  <rect x="140" y="1090" width="110" height="100" rx="10" fill="#cfd4d6" ${S(6)}/></g>`;
}
function bgWash(o = {}) {
  // старая мойка за городом, зима: два бокса, дырявая крыша
  const snow = o.snow !== false;
  return `<g><rect width="1080" height="1920" fill="${snow ? "#dbe9ef" : P.sky}"/>
  <path d="M0,900 Q270,840 540,880 T1080,860 V1920 H0 Z" fill="${snow ? P.snow : "#cfe3c0"}"/>
  ${[[60, 820], [960, 800], [1020, 860]].map(([x, y]) => `<path d="M${x},${y} l40,-120 l40,120 z" fill="#6f9a86" ${S(5)}/>`).join("")}
  <rect x="140" y="700" width="800" height="560" fill="${P.greyL}" ${S()}/>
  <path d="M110,710 L540,560 L970,710 Z" fill="#a58f7e" ${S()}/>
  ${o.holes !== false ? `<path d="M380,640 l40,-12 l10,30 l-36,14 z M660,660 l46,8 l-8,30 l-44,-8 z" fill="#5c4f48"/>` : ""}
  ${snow ? `<path d="M110,710 L540,560 L970,710 L960,720 L540,576 L120,720 Z" fill="#fff" ${S(5)}/>` : ""}
  <rect x="200" y="830" width="300" height="430" fill="#7d8a90" ${S()}/>
  <rect x="580" y="830" width="300" height="430" fill="#7d8a90" ${S()}/>
  ${[880, 940, 1000, 1060, 1120, 1180].map(y => `<path d="M200,${y} h300 M580,${y} h300" stroke="#6b777c" stroke-width="6"/>`).join("")}
  <rect x="${o.signX || 360}" y="740" width="360" height="74" rx="10" fill="${o.sign ? P.teal : "#c9b8a8"}" ${S(6)}/>
  <text x="${(o.signX || 360) + 180}" y="792" font-family="DejaVu Sans" font-weight="bold" font-size="${o.sign ? 34 : 44}" fill="${o.sign ? "#fff" : "#7a6a5c"}" text-anchor="middle">${o.sign || "МОЙКА"}</text>
  <path d="M0,1500 Q540,1440 1080,1500 V1920 H0 Z" fill="${snow ? "#eef2f2" : "#cfe3c0"}"/></g>`;
}
function bgOwn() {
  // свой сервис: шесть боксов, вывеска «СЕРВИС КРАВЦОВА»
  return `<g><rect width="1080" height="1920" fill="${P.sky}"/>
  <circle cx="880" cy="300" r="90" fill="#ffe08a" opacity=".9"/>
  <path d="M0,980 Q540,940 1080,980 V1920 H0 Z" fill="#d9c9a8"/>
  <rect x="40" y="620" width="1000" height="560" fill="#f2e3cc" ${S()}/>
  <rect x="20" y="590" width="1040" height="60" fill="${P.teal}" ${S()}/>
  <rect x="130" y="440" width="820" height="140" rx="20" fill="#fffaf0" ${S()}/>
  <text x="540" y="535" font-family="DejaVu Sans" font-weight="bold" font-size="66" fill="${P.tealD}" text-anchor="middle">СЕРВИС КРАВЦОВА</text>
  ${[0, 1, 2, 3, 4, 5].map(i => `<rect x="${70 + i * 162}" y="760" width="136" height="420" fill="#58656b" ${S(6)}/>
     <rect x="${70 + i * 162}" y="690" width="136" height="54" rx="8" fill="${P.mustard}" ${S(5)}/>
     <text x="${138 + i * 162}" y="730" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="${INK}" text-anchor="middle">${i + 1}</text>`).join("")}
  <path d="M0,1180 H1080" ${S(8)}/></g>`;
}

if (typeof module !== "undefined") module.exports = { P, INK, anton, lena, boss, client, car, bill, thermos, cashbox, phone, contract, counter, plaque, bgForeign, bgKitchen, bgWash, bgOwn };
