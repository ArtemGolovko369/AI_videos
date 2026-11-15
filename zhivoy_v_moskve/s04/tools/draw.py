"""Кадры серии 4 «Мама». Использует помощники серий 1–3.
Запуск: python3 s04/tools/draw.py → s04/frames/*.png
"""
import importlib.util, os, random, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
spec = importlib.util.spec_from_file_location("s3draw", os.path.join(ROOT, "s03", "tools", "draw.py"))
S3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(S3)
S2, D = S3.S2, S3.D
D.OUT = os.path.join(HERE, "..", "frames"); os.makedirs(D.OUT, exist_ok=True)
W, H = D.W, D.H
svg, save, grad, head, body, figure, back_figure, fog = D.svg, D.save, D.grad, D.head, D.body, D.figure, D.back_figure, D.fog
her = S2.her
YELLOW, HSKIN, SCARF, COAT, HER_SKIN = D.YELLOW, D.HSKIN, S2.SCARF, S2.COAT, S2.HER_SKIN
RED_MARK = "#c8463c"
GREEN = "#6f9a5e"           # мамина кофта — её цветовой маркер
MSKIN = "#b6b8af"
MHAIR = "#8e8a84"

# ---------------------------------------------------------------- мама
def mama(x, y, s=1, eyes="hero", mouth="flat", back=False, tears=False, look=0):
    g = body(x, y + 70*s, s, GREEN)
    if not back:
        g += f'<path d="M{x-40*s},{y+80*s} l{40*s},{120*s} l{40*s},{-120*s}" stroke="#5c8150" stroke-width="{8*s}" fill="none"/>'  # вырез кофты
        for k in range(4): g += f'<circle cx="{x}" cy="{y+230*s + k*60*s}" r="{8*s}" fill="#e6e2d4"/>'
    g += f'<rect x="{x-14*s}" y="{y+40*s}" width="{28*s}" height="{40*s}" fill="{MSKIN}"/>'
    if back:
        g += f'<circle cx="{x}" cy="{y}" r="{64*s}" fill="{MHAIR}"/>'
        g += f'<path d="M{x-40*s},{y-30*s} q{40*s},{-20*s} {80*s},0" stroke="#b3afa8" stroke-width="{6*s}" fill="none"/>'
        return g
    g += head(x, y, 62*s, MSKIN, MHAIR, eyes, mouth, look=look)
    # пышная короткая стрижка с проседью
    g += f'<path d="M{x-70*s},{y+5*s} q{-6*s},{-80*s} {70*s},{-80*s} q{76*s},0 {70*s},{80*s} q{-20*s},{-50*s} {-70*s},{-46*s} q{-50*s},{-4*s} {-70*s},{46*s}z" fill="{MHAIR}"/>'
    g += f'<path d="M{x-30*s},{y-62*s} q{30*s},{-12*s} {60*s},{4*s}" stroke="#bdb9b2" stroke-width="{5*s}" fill="none"/>'
    if tears:
        for sx in (-1, 1):
            cx = x + sx*22*s; cy = y + 22*s
            g += f'<path d="M{cx},{cy} q{3*s},{14*s} 0,{20*s} q{-3*s},{-6*s} 0,{-20*s}z" fill="#bfe0ee" opacity=".9"/>'
            g += f'<path d="M{cx-1*s},{cy+20*s} q{2*s},{14*s} {-1*s},{30*s}" stroke="#bfe0ee" stroke-width="{3*s}" fill="none" opacity=".7"/>'
    return g

# ---------------------------------------------------------------- телефон
def phone_call(state):
    b = f'<rect width="{W}" height="{H}" fill="#2a2d2f"/>'
    b += '<circle cx="540" cy="900" r="520" fill="#f2c230" opacity=".05" filter="url(#blur60)"/>'
    b += '<path d="M220,1920 q-40,-400 80,-560 l140,-40 q60,10 40,80 l-40,140 q120,-30 180,20 l40,360z" fill="#b9bab1"/>'
    b += f'<path d="M180,1920 q-20,-300 60,-420 l90,40 q-40,140 -20,380z" fill="{YELLOW}"/>'
    b += '<rect x="270" y="380" width="540" height="1100" rx="64" fill="#15171a"/><rect x="294" y="410" width="492" height="1040" rx="46" fill="#1f2a24"/>'
    b += '<circle cx="540" cy="640" r="110" fill="#e78b8b"/><text x="540" y="682" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="110" fill="#fff">М</text>'
    b += '<text x="540" y="830" text-anchor="middle" font-family="DejaVu Sans" font-size="64" fill="#eef2ee">Мама</text>'
    sub = {"out": "вызов…", "talk": "00:03", "end": "вызов завершён"}[state]
    b += f'<text x="540" y="890" text-anchor="middle" font-family="DejaVu Sans" font-size="34" fill="#a9b6ad">{sub}</text>'
    if state == "talk":  # волна дыхания
        b += '<path d="M330,1010 q30,-10 60,0 t60,0 q30,-40 60,0 t60,0 q30,-60 60,0 t60,0 t60,0" stroke="#7fbf8a" stroke-width="6" fill="none"/>'
    btn = "#8c8f8d" if state == "end" else "#e0443e"
    b += f'<circle cx="540" cy="1280" r="80" fill="{btn}"/><path d="M490,1290 q50,-40 100,0" stroke="#fff" stroke-width="18" stroke-linecap="round" fill="none"/>'
    if state == "end":  # палец Веры, рукав с красным шарфом
        b += f'<path d="M1080,1700 q-300,-120 -460,-360 l40,-40 q200,180 420,240z" fill="{COAT}"/>'
        b += f'<path d="M640,1330 q-60,-30 -60,-80 q20,-20 50,0 l60,50z" fill="{HER_SKIN}"/>'
        b += f'<path d="M1080,1640 q-140,-30 -230,-120 l30,-30 q100,80 200,100z" fill="{SCARF}"/>'
    return b

def s01(): save("01_zvonok", svg(phone_call("out")))
def s02(): save("02_razgovor", svg(phone_call("talk")))
def s03(): save("03_sbros", svg(phone_call("end")))

def s04_bloknot():
    b = f'<rect width="{W}" height="{H}" fill="#3f3a34"/>'
    b += '<circle cx="540" cy="700" r="600" fill="#f2d78a" opacity=".1" filter="url(#blur60)"/>'
    b += '<g transform="rotate(2 540 920)"><rect x="130" y="300" width="820" height="1240" rx="16" fill="#efe9d6"/>'
    for y in range(470, 1520, 80): b += f'<line x1="150" y1="{y}" x2="930" y2="{y}" stroke="#bcc8d6" stroke-width="3"/>'
    b += '<line x1="240" y1="300" x2="240" y2="1540" stroke="#e0a3a0" stroke-width="4"/>'
    old = ["1. НЕ УЛЫБАЙСЯ", "2. НЕ ТОРОПИСЬ", "3. НЕ СМОТРИ В ГЛАЗА…", "4. НЕ УСТУПАЙ МЕСТО"]
    for k, t in enumerate(old):
        b += f'<text x="260" y="{450 + k*80}" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="38" fill="#2b2f6a" opacity=".55">{t}</text>'
    new = ["5. НЕ ХОДИ К ТЕМ,", "КОГО ЛЮБИШЬ.", "ИХ ВЫУЧИВАЮТ", "ПЕРВЫМИ."]
    for k, t in enumerate(new):
        b += f'<text x="{260 if k == 0 else 310}" y="{860 + k*130}" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="58" fill="{RED_MARK}">{t}</text>'
    b += '<path d="M300,1400 q240,30 520,-10" stroke="#c8463c" stroke-width="7" fill="none"/></g>'
    b += f'<path d="M1080,1500 q-200,-60 -300,-200 l40,-30 q120,120 260,150z" fill="{COAT}"/>'  # рука Веры у края
    b += f'<path d="M780,1300 q-50,-20 -40,-60 q30,-10 60,20z" fill="{HER_SKIN}"/>'
    save("04_bloknot5", svg(b))

def night_sky():
    return grad("ns", "#1b2030", "#3a3f52")

def s05_vyhod():
    b = f'<rect width="{W}" height="{H}" fill="url(#ns)"/>'
    b += f'<g opacity=".9">{D.panel_houses(1150, seed=31, col="#3b4150", lit=.18)}</g>'.replace('#e8d79a', '#e9c977').replace('#6e7378', '#2a2f3b')
    b += f'<rect y="1150" width="{W}" height="770" fill="#2c3038"/>'
    # павильон метро
    b += '<rect x="160" y="760" width="760" height="460" fill="#4a505c"/><rect x="200" y="880" width="680" height="340" fill="#e8dcae" opacity=".85"/>'
    b += '<rect x="160" y="730" width="760" height="70" fill="#2f343d"/>'
    b += '<text x="540" y="782" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="48" fill="#d9dde3" letter-spacing="10">МЕТРО</text>'
    # фонарь
    b += '<rect x="960" y="700" width="14" height="560" fill="#1f232a"/><circle cx="967" cy="700" r="24" fill="#f2d78a"/><circle cx="967" cy="700" r="140" fill="#f2d78a" opacity=".15" filter="url(#blur30)"/>'
    # герой со спины выходит
    b += body(540, 1290 + 70*2.0, 2.0, YELLOW) + f'<circle cx="540" cy="1290" r="{62*2.0}" fill="#2b2a2d"/>'
    b += '<ellipse cx="540" cy="1250" rx="360" ry="200" fill="#f2c230" opacity=".05" filter="url(#blur60)"/>'
    save("05_vyhod", svg(b, "<defs>" + night_sky() + "</defs>"))

def s06_ulica():
    b = f'<rect width="{W}" height="{H}" fill="url(#ns)"/>'
    random.seed(41)
    hs = D.panel_houses(1250, seed=42, col="#3b4150", lit=.35).replace('#e8d79a', '#efcf7c').replace('#6e7378', '#262b36')
    b += hs
    b += f'<rect y="1250" width="{W}" height="670" fill="#2a2e35"/><rect y="1250" width="{W}" height="40" fill="#3a3f48"/>'
    # отсвет окон на асфальте
    b += '<ellipse cx="540" cy="1300" rx="600" ry="80" fill="#efcf7c" opacity=".08" filter="url(#blur30)"/>'
    # неподвижные зомби лицом к окнам (со спины), ряды
    for (y, s, xs) in [(1060, .55, (90, 230, 380, 700, 860, 1000)), (1180, .8, (150, 420, 640, 930)), (1400, 1.25, (240, 820))]:
        for x in xs:
            b += back_figure(x, y, s, col=random.choice(["#3a3f4a", "#454a55", "#4c4f57", "#3d3b40"]), slouch=0)
    b += '<rect width="1080" height="1920" fill="#0b0d14" opacity=".2"/>'
    save("06_ulica", svg(b, "<defs>" + night_sky() + "</defs>"))

def mamin_dom(lit_only=True):
    b = f'<rect width="{W}" height="{H}" fill="url(#ns)"/>'
    x0, w, top = 140, 800, 260
    b += f'<rect x="{x0}" y="{top}" width="{w}" height="{1500-top}" fill="#353b48"/>'
    floors = 12; fh = (1450 - top - 40)/floors
    for f in range(floors):
        y = top + 40 + f*fh
        for c in range(6):
            x = x0 + 40 + c*125
            on = (f == floors - 9 and c == 2)   # 9-й этаж снизу
            col = "#f3d27a" if on else "#20242d"
            b += f'<rect x="{x}" y="{y:.0f}" width="80" height="{fh*.55:.0f}" fill="{col}"/>'
            if on:
                b += f'<rect x="{x-60}" y="{y-60:.0f}" width="200" height="{fh*.55+120:.0f}" fill="#f3d27a" opacity=".2" filter="url(#blur30)"/>'
                OKNO = (x, y)
    b += f'<rect y="1500" width="{W}" height="420" fill="#23272e"/>'
    b += '<rect x="440" y="1360" width="200" height="140" fill="#2a2f37"/><rect x="420" y="1340" width="240" height="24" fill="#4a505c"/>'  # подъезд
    return b, OKNO

def s07_dom():
    b, _ = mamin_dom()
    save("07_dom", svg(b, "<defs>" + night_sky() + "</defs>"))

def s08_okno():
    b = f'<rect width="{W}" height="{H}" fill="#2a2f3b"/>'
    for y in range(0, H, 220): b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#232733" stroke-width="6"/>'
    b += '<rect x="190" y="500" width="700" height="860" fill="#f0cf7a"/>'
    b += '<rect x="190" y="500" width="700" height="860" fill="none" stroke="#e8e4da" stroke-width="26"/><rect x="527" y="500" width="26" height="860" fill="#e8e4da"/>'
    # занавеска и силуэт над телефоном
    b += '<path d="M204,514 q60,300 0,832 h90 q-40,-420 20,-832z" fill="#e2b862" opacity=".8"/>'
    b += '<path d="M560,1350 v-250 q0,-120 120,-140 q40,-80 0,-150 a70,70 0 1 1 90,40 q30,40 20,110 q80,40 80,140 v250z" fill="#2b2a2c"/>'
    b += '<rect x="610" y="1090" width="60" height="90" rx="10" fill="#bfe3f2"/><circle cx="640" cy="1120" r="90" fill="#bfe3f2" opacity=".25" filter="url(#blur30)"/>'
    b += '<rect x="190" y="1180" width="700" height="30" fill="#c9a35a"/>'  # подоконник/стол
    b += '<rect y="1400" width="1080" height="520" fill="#20242d"/>'
    save("08_okno", svg(b))

def s09_dver():
    b = f'<rect width="{W}" height="{H}" fill="#3a3f45"/>'
    b += '<rect x="0" y="0" width="1080" height="1500" fill="#4a5a52"/><rect x="0" y="0" width="1080" height="700" fill="#5d6a64"/>'  # покрашенный подъезд
    b += '<rect x="300" y="380" width="480" height="1120" fill="#5a3f30"/>'
    # приоткрытая дверь: щель света
    b += '<polygon points="780,380 830,400 830,1480 780,1500" fill="#f3d27a"/><polygon points="830,400 1080,250 1080,1700 830,1480" fill="#f3d27a" opacity=".18" filter="url(#blur30)"/>'
    b += '<polygon points="300,380 780,380 780,1500 300,1500" fill="#6b4a36"/>'
    b += '<rect x="700" y="920" width="40" height="80" rx="8" fill="#c9b98a"/>'
    b += '<text x="540" y="560" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="60" fill="#d8c79a">97</text>'
    b += '<rect y="1500" width="1080" height="420" fill="#3c3d3e"/><polygon points="780,1500 830,1480 1080,1920 860,1920" fill="#f3d27a" opacity=".25"/>'
    b += '<rect x="80" y="240" width="60" height="60" rx="30" fill="#e9e2c4" opacity=".6"/>'  # лампочка
    save("09_dver", svg(b))

def kitchen_bg(table=True):
    b = f'<rect width="{W}" height="{H}" fill="#6b6152"/>'
    for y in range(0, 1300, 60):
        for x in range(0, W, 60): b += f'<rect x="{x+2}" y="{y+2}" width="56" height="56" fill="#7a705f"/>'  # кафель
    b += '<rect x="0" y="0" width="1080" height="300" fill="#5b5245"/>'
    b += '<line x1="540" y1="0" x2="540" y2="120" stroke="#2a2826" stroke-width="6"/><path d="M460,120 h160 l-30,-40 h-100z" fill="#c9a35a"/>'
    b += '<circle cx="540" cy="160" r="360" fill="#f3d27a" opacity=".18" filter="url(#blur60)"/>'
    b += '<rect x="820" y="420" width="240" height="900" rx="16" fill="#d9d6cc"/><rect x="820" y="760" width="240" height="8" fill="#a9a59a"/>'  # холодильник
    b += '<rect x="40" y="420" width="300" height="300" fill="#2b3446"/><rect x="40" y="420" width="300" height="300" fill="none" stroke="#e8e4da" stroke-width="16"/>'  # тёмное окно
    b += '<rect y="1300" width="1080" height="620" fill="#4a4136"/>'
    if table:
        b += '<rect x="80" y="1260" width="920" height="50" fill="#c9b48a"/><rect x="80" y="1310" width="920" height="20" fill="#a8946c"/>'  # стол
    return b

def s10_spina():
    b = kitchen_bg()
    b += '<rect x="110" y="1200" width="160" height="60" rx="6" fill="#6b7d6a"/><text x="190" y="1240" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="26" fill="#efe9d6">ПРАВИЛА</text>'
    b += '<rect x="850" y="1200" width="80" height="60" rx="8" fill="#e9e2c4"/><path d="M930,1215 q30,0 25,25 q-5,15 -25,15" stroke="#e9e2c4" stroke-width="8" fill="none"/>'  # чашка
    b += '<circle cx="540" cy="1100" r="200" fill="#bfe3f2" opacity=".22" filter="url(#blur30)"/>'  # свет экрана перед ней
    b += mama(540, 1000, 2.6, back=True)
    b += '<rect x="330" y="1420" width="420" height="40" rx="10" fill="#5a4535"/><rect x="350" y="1460" width="30" height="460" fill="#5a4535"/><rect x="700" y="1460" width="30" height="460" fill="#5a4535"/>'  # спинка стула
    save("10_spina", svg(b))

def mama_close(mouth):
    b = kitchen_bg(table=False)
    b += '<rect width="1080" height="1920" fill="#000" opacity=".18"/>'
    b += mama(540, 960, 4.6, eyes="hero", mouth=mouth, tears=True, look=.1)
    return b

def s11(): save("11_mama", svg(mama_close("flat"))); save("11b_mama_rot", svg(mama_close("open")))

def s12_stranica():
    b = f'<rect width="{W}" height="{H}" fill="#4a4136"/>'
    b += '<circle cx="540" cy="700" r="600" fill="#f3d27a" opacity=".12" filter="url(#blur60)"/>'
    b += '<g transform="rotate(-2 540 960)"><rect x="110" y="280" width="860" height="1300" rx="14" fill="#efe9d6"/>'
    for y in range(440, 1560, 80): b += f'<line x1="130" y1="{y}" x2="950" y2="{y}" stroke="#bcc8d6" stroke-width="3"/>'
    b += '<text x="540" y="400" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="44" fill="#3c5a3a">НЕ ДОВЕРЯТЬ</text>'
    # фото Веры на скотче
    x, y = 540, 860
    b += f'<rect x="{x-200}" y="{y-260}" width="400" height="500" fill="#f8f6f0"/><rect x="{x-170}" y="{y-230}" width="340" height="360" fill="#8c9496"/>'
    b += f'<clipPath id="vp"><rect x="{x-170}" y="{y-230}" width="340" height="360"/></clipPath><g clip-path="url(#vp)">{her(x, y - 70, 1.7, eyes="hero", scarf=True)}</g>'
    b += f'<rect x="{x-90}" y="{y-280}" width="180" height="50" fill="#e6dfc0" opacity=".8" transform="rotate(-4 {x} {y-255})"/>'
    b += f'<path d="M{x-190},{y-250} L{x+190},{y+230} M{x+190},{y-250} L{x-190},{y+230}" stroke="{RED_MARK}" stroke-width="18" stroke-linecap="round" opacity=".9"/>'
    b += f'<text x="{x}" y="{y+200}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="46" fill="#2b2f6a">Вера</text>'
    b += f'<text x="540" y="1300" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="64" fill="{RED_MARK}">14.11.2023</text>'
    b += '</g>'
    save("12_stranica", svg(b))

def s13():
    b = f'<rect width="{W}" height="{H}" fill="#121416"/>'
    b += fog(91, 8, 600, 1400, .12, "#6c7378")
    b += f'<g opacity=".18">{D.city_towers(1300, seed=1)}</g>'
    b += '<text x="540" y="880" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="150" fill="#e8e4d8" letter-spacing="6">ЖИВОЙ</text>'
    b += '<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="110" fill="#f2c230" letter-spacing="6">В МОСКВЕ</text>'
    b += '<rect x="390" y="1110" width="300" height="4" fill="#8a8f92"/>'
    b += '<text x="540" y="1200" text-anchor="middle" font-family="DejaVu Sans" font-size="48" fill="#a9aeb1" letter-spacing="14">СЕРИЯ 4</text>'
    b += f'<rect x="420" y="1250" width="240" height="8" fill="{GREEN}"/>'
    save("13_zastavka", svg(b))

if __name__ == "__main__":
    for f in [s01, s02, s03, s04_bloknot, s05_vyhod, s06_ulica, s07_dom, s08_okno, s09_dver, s10_spina, s11, s12_stranica, s13]:
        f(); print("ok", f.__name__)
    subprocess.run(["node", os.path.join(ROOT, "tools", "render.js"), D.OUT], check=True)
    shutil.copy(os.path.join(ROOT, "s03", "frames", "09_tel1.png"), os.path.join(D.OUT, "08b_vibro.png"))
