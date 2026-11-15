"""Кадры серии 3 «Правила». Использует помощники серий 1 и 2.
Запуск: python3 s03/tools/draw.py → s03/frames/*.png
"""
import importlib.util, os, random, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
spec = importlib.util.spec_from_file_location("s2draw", os.path.join(ROOT, "s02", "tools", "draw.py"))
S2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(S2)
D = S2.D
D.OUT = os.path.join(HERE, "..", "frames"); os.makedirs(D.OUT, exist_ok=True)
W, H = D.W, D.H
svg, save, grad, head, body, figure, back_figure, fog = D.svg, D.save, D.grad, D.head, D.body, D.figure, D.back_figure, D.fog
her, crooked_smile = S2.her, S2.crooked_smile
YELLOW, HSKIN, SCARF, COAT, HER_SKIN = D.YELLOW, D.HSKIN, S2.SCARF, S2.COAT, S2.HER_SKIN
RED_MARK = "#c8463c"

def s01_idet():
    """Вагон: зомби с кривой улыбкой встал и идёт по проходу."""
    b, d = S2.wagon(turned=())
    b += '<rect width="1080" height="1920" fill="#000" opacity=".15"/>'
    random.seed(121)
    b += figure(560, 860, 3.0, col="#4a4f58", skin="#a2a89e", eyes="stare", mouth="none")
    b += crooked_smile(560, 860, 62*3.0)
    save("01_idet", svg(b, "<defs>" + d + "</defs>"))

def s02_lokot():
    b = f'<rect width="{W}" height="{H}" fill="#565b5c"/>'
    # двери разъезжаются
    b += '<rect x="0" y="0" width="300" height="1920" fill="#6a6f71"/><rect x="780" y="0" width="300" height="1920" fill="#6a6f71"/>'
    b += '<rect x="300" y="0" width="480" height="1920" fill="#c9c3ae"/><rect x="300" y="0" width="480" height="600" fill="#9a8f78"/>'
    # жёлтый рукав героя
    b += f'<path d="M1080,700 L380,960 q-60,40 -20,120 l60,90 L1080,1060z" fill="{YELLOW}"/>'
    b += '<path d="M560,920 l40,230 M760,860 l40,220" stroke="#d9a51e" stroke-width="10"/>'
    # её серый рукав и рука сжимает локоть
    b += f'<path d="M0,1500 q240,-120 420,-330 l90,70 q-130,250 -330,420 h-180z" fill="{COAT}"/>'
    b += f'<path d="M420,1170 q40,-70 120,-80 q60,0 70,50 q-20,30 -60,30 q30,40 0,70 q-40,30 -90,10z" fill="{HER_SKIN}"/>'
    b += '<path d="M480,1110 q40,-10 80,0 M490,1150 q40,-6 70,4 M500,1185 q30,-4 55,4" stroke="#8f938b" stroke-width="5" fill="none"/>'
    save("02_lokot", svg(b))

def s03_platforma():
    d = grad("pl", "#a39a86", "#6f6a60")
    b = f'<rect width="{W}" height="{H}" fill="url(#pl)"/>'
    for x in range(-40, 1080, 260):
        b += f'<rect x="{x}" y="0" width="120" height="1300" fill="#8c8473"/><rect x="{x+20}" y="80" width="80" height="20" rx="10" fill="#efe1b0" opacity=".8"/>'
    b += '<rect y="1250" width="1080" height="670" fill="#8a8578"/>'
    random.seed(131)
    # дальний ряд и лицо с улыбкой позади
    for x in (90, 260, 820, 990):
        b += back_figure(x, 980, .9, slouch=random.uniform(-8, 8))
    b += figure(560, 940, 1.0, col="#4a4f58", skin="#a2a89e", eyes="stare", mouth="none") + crooked_smile(560, 940, 62)
    for x in (120, 360, 760, 960):
        b += back_figure(x, 1150, 1.4, slouch=random.uniform(-8, 8))
    # вы вдвоём со спины
    b += her(640, 1380, 2.0, back=True)
    b += body(400, 1360 + 70*2.1, 2.1, YELLOW) + f'<circle cx="400" cy="1360" r="{62*2.1}" fill="#2b2a2d"/>'
    save("03_platforma", svg(b, "<defs>" + d + "</defs>"))

def s04_dver():
    b = f'<rect width="{W}" height="{H}" fill="#8f8a7e"/>'
    for y in range(0, 1500, 70): b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#827d72" stroke-width="3"/>'
    b += '<rect x="290" y="420" width="500" height="1080" fill="#5d6366"/><rect x="310" y="440" width="460" height="1040" fill="#6b7174"/>'
    b += '<rect x="690" y="920" width="40" height="90" rx="8" fill="#c9b98a"/><circle cx="710" cy="980" r="10" fill="#3b3631"/>'
    b += '<rect x="360" y="560" width="360" height="160" fill="#f1efe6" stroke="#c8463c" stroke-width="10"/>'
    b += '<text x="540" y="625" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#c8463c">ПОСТОРОННИМ</text>'
    b += '<text x="540" y="680" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#2b2f33">ВХОД ВОСПРЕЩЁН</text>'
    b += '<rect y="1500" width="1080" height="420" fill="#7a766c"/>'
    # рука с ключом
    b += f'<path d="M1080,1150 q-220,-30 -330,-130 l-30,40 q120,140 360,200z" fill="{COAT}"/>'
    b += f'<path d="M730,1010 q-40,-10 -40,30 q10,40 60,30z" fill="{HER_SKIN}"/>'
    b += '<rect x="690" y="1000" width="40" height="10" fill="#d6c27a"/><circle cx="745" cy="1005" r="16" fill="none" stroke="#d6c27a" stroke-width="7"/>'
    save("04_dver", svg(b))

def kamorka_bg():
    b = f'<rect width="{W}" height="{H}" fill="#4f4a43"/>'
    b += '<rect x="0" y="0" width="1080" height="1300" fill="#5c564d"/>'
    # карта метро с красными пометками
    b += '<rect x="80" y="260" width="460" height="560" fill="#e6e0cf"/>'
    random.seed(141)
    for k, c in enumerate(["#b8a988", "#9aa6ad", "#a8b39b", "#b3a3b0"]):
        pts = " ".join(f"{120+random.randint(0,380)},{300+random.randint(0,480)}" for _ in range(5))
        b += f'<polyline points="{pts}" stroke="{c}" stroke-width="10" fill="none"/>'
    b += '<circle cx="310" cy="540" r="140" fill="none" stroke="#b9b6aa" stroke-width="10"/>'
    for _ in range(9):
        x, y = random.randint(130, 500), random.randint(320, 780)
        b += f'<path d="M{x-14},{y-14} l28,28 M{x+14},{y-14} l-28,28" stroke="{RED_MARK}" stroke-width="7"/>'
    # лампа
    b += '<line x1="760" y1="0" x2="760" y2="200" stroke="#2a2826" stroke-width="6"/><path d="M680,200 h160 l-30,-60 h-100z" fill="#3a3632"/>'
    b += '<circle cx="760" cy="230" r="300" fill="#f2d78a" opacity=".16" filter="url(#blur60)"/>'
    b += '<rect y="1300" width="1080" height="620" fill="#3f3a34"/>'
    b += '<rect x="560" y="1280" width="520" height="40" fill="#6b5b48"/>'  # стол
    b += '<path d="M870,1280 v-90 q0,-40 50,-40 h40 q40,0 40,40 v90z" fill="#8a8f92"/><path d="M1000,1190 q50,0 40,50" stroke="#8a8f92" stroke-width="12" fill="none"/>'  # чайник
    return b

def s05_kamorka():
    b = kamorka_bg()
    b += her(380, 1000, 2.4, eyes="hero", mouth="flat", look=.5, scarf=False)
    # шарф в руке
    b += f'<path d="M640,1270 q80,-30 160,0 q30,10 40,40 h-220z" fill="{SCARF}"/><path d="M780,1290 l30,150 h30 l-20,-150z" fill="#b13c33"/>'
    save("05_kamorka", svg(b))

def vera_close(mouth):
    b = kamorka_bg()
    b += '<rect width="1080" height="1920" fill="#000" opacity=".2"/>'
    b += her(540, 960, 4.6, eyes="hero", mouth=mouth, look=.2, scarf=False)
    return b

def s05b(): save("05b_vera", svg(vera_close("flat")))
def s05c(): save("05c_vera_rot", svg(vera_close("open")))

RULES = ["1. НЕ УЛЫБАЙСЯ", "2. НЕ ТОРОПИСЬ", "3. НЕ СМОТРИ В ГЛАЗА", "   ДОЛЬШЕ СЕКУНДЫ", "4. НИКОГДА НЕ", "   УСТУПАЙ МЕСТО"]
def notebook(nlines):
    b = f'<rect width="{W}" height="{H}" fill="#3f3a34"/>'
    b += '<circle cx="540" cy="700" r="600" fill="#f2d78a" opacity=".1" filter="url(#blur60)"/>'
    b += '<rect x="130" y="300" width="820" height="1240" rx="16" fill="#efe9d6" transform="rotate(-3 540 920)"/>'
    b += '<g transform="rotate(-3 540 920)">'
    for y in range(470, 1520, 80): b += f'<line x1="150" y1="{y}" x2="930" y2="{y}" stroke="#bcc8d6" stroke-width="3"/>'
    b += '<line x1="240" y1="300" x2="240" y2="1540" stroke="#e0a3a0" stroke-width="4"/>'
    b += '<text x="560" y="420" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="76" fill="#2b2f6a" text-decoration="underline">ПРАВИЛА</text>'
    for k in range(nlines):
        col = RED_MARK if k >= 4 else "#2b2f6a"
        b += f'<text x="260" y="{600 + k*130}" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="46" fill="{col}" xml:space="preserve">{RULES[k]}</text>'
    b += '</g>'
    b += '<path d="M980,1700 l-260,-420 l40,-20 l260,420z" fill="#2b2f6a"/><path d="M720,1280 l-10,-50 l50,30z" fill="#1a1c3a"/>'  # ручка
    return b

def s06():
    for n, k in [(1, "06a"), (2, "06b"), (4, "06c"), (6, "06d")]:
        save(f"{k}_bloknot", svg(notebook(n)))

def wall(eighth):
    b = f'<rect width="{W}" height="{H}" fill="#5c564d"/>'
    b += '<circle cx="540" cy="600" r="600" fill="#f2d78a" opacity=".1" filter="url(#blur60)"/>'
    random.seed(151)
    pos = [(230, 420), (540, 400), (850, 430), (230, 800), (540, 790), (850, 810), (380, 1190)]
    for k, (x, y) in enumerate(pos):
        rot = random.uniform(-6, 6)
        g = f'<g transform="rotate({rot:.1f} {x} {y})"><rect x="{x-120}" y="{y-150}" width="240" height="300" fill="#f1efe6"/>'
        g += f'<rect x="{x-100}" y="{y-130}" width="200" height="210" fill="#8c9496"/>'
        clip = f'<clipPath id="ph{k}"><rect x="{x-100}" y="{y-130}" width="200" height="210"/></clipPath>'
        g += clip + f'<g clip-path="url(#ph{k})">'
        if k == 6:
            g += her(x, y - 40, .95, eyes="hero", scarf=True)
        else:
            g += figure(x, y - 40, .95, col=random.choice(D.CLOTH), skin="#d3b9a0", eyes="hero", look=random.uniform(-1, 1)).replace('fill="#f2c230"', 'fill="#7a8a9a"')
        g += '</g>'
        g += f'<rect x="{x-100}" y="{y+80}" width="200" height="60" fill="#f1efe6"/>'
        g += f'<circle cx="{x}" cy="{y-150}" r="10" fill="{RED_MARK}"/></g>'
        b += g
        if k < 6:
            b += f'<path d="M{x-110},{y-120} L{x+110},{y+120} M{x+110},{y-120} L{x-110},{y+120}" stroke="{RED_MARK}" stroke-width="14" stroke-linecap="round" opacity=".9"/>'
    if eighth:
        x, y = 700, 1200
        b += f'<g transform="rotate(4 {x} {y})"><rect x="{x-120}" y="{y-150}" width="240" height="300" fill="#f1efe6"/>'
        b += f'<rect x="{x-100}" y="{y-130}" width="200" height="210" fill="#d9d5c8"/>'
        b += f'<text x="{x}" y="{y+30}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="150" fill="{RED_MARK}">8</text>'
        b += f'<circle cx="{x}" cy="{y-150}" r="10" fill="{RED_MARK}"/></g>'
    b += '<rect y="1500" width="1080" height="420" fill="#3f3a34"/>'
    return b

def s08(): save("08a_stena", svg(wall(False))); save("08b_stena8", svg(wall(True)))

def phone(n):
    b = f'<rect width="{W}" height="{H}" fill="#2a2d2f"/>'
    b += '<circle cx="540" cy="900" r="520" fill="#f2c230" opacity=".06" filter="url(#blur60)"/>'
    b += '<path d="M220,1920 q-40,-400 80,-560 l140,-40 q60,10 40,80 l-40,140 q120,-30 180,20 l40,360z" fill="#b9bab1"/>'
    b += f'<path d="M180,1920 q-20,-300 60,-420 l90,40 q-40,140 -20,380z" fill="{YELLOW}"/>'
    b += '<rect x="270" y="380" width="540" height="1100" rx="64" fill="#15171a"/><rect x="294" y="410" width="492" height="1040" rx="46" fill="#232a33"/>'
    b += '<text x="540" y="560" text-anchor="middle" font-family="DejaVu Sans" font-size="110" fill="#e9edf2">21:47</text>'
    for k in range(n):
        y = 640 + k*165
        b += f'<rect x="318" y="{y}" width="444" height="150" rx="28" fill="#e9ecef" opacity=".96"/>'
        b += f'<circle cx="376" cy="{y+56}" r="30" fill="#e78b8b"/><text x="376" y="{y+68}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#fff">М</text>'
        b += f'<text x="422" y="{y+50}" font-family="DejaVu Sans" font-weight="bold" font-size="28" fill="#1c1f26">Мама</text>'
        b += f'<text x="740" y="{y+50}" text-anchor="end" font-family="DejaVu Sans" font-size="22" fill="#7a818a">21:47</text>'
        b += f'<text x="422" y="{y+96}" font-family="DejaVu Sans" font-size="28" fill="#1c1f26">Я тебя люблю</text>'
        b += f'<path d="M{690},{y+86} c-10,-18 -36,-12 -30,7 c3,12 20,22 30,30 c10,-8 27,-18 30,-30 c6,-19 -20,-25 -30,-7z" fill="#e0443e"/>'
    return b

def s09():
    for n in (1, 2, 3, 5):
        save(f"09_tel{n}", svg(phone(n)))

def s11():
    b = f'<rect width="{W}" height="{H}" fill="#121416"/>'
    b += fog(91, 8, 600, 1400, .12, "#6c7378")
    b += f'<g opacity=".18">{D.city_towers(1300, seed=1)}</g>'
    b += '<text x="540" y="880" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="150" fill="#e8e4d8" letter-spacing="6">ЖИВОЙ</text>'
    b += '<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="110" fill="#f2c230" letter-spacing="6">В МОСКВЕ</text>'
    b += '<rect x="390" y="1110" width="300" height="4" fill="#8a8f92"/>'
    b += '<text x="540" y="1200" text-anchor="middle" font-family="DejaVu Sans" font-size="48" fill="#a9aeb1" letter-spacing="14">СЕРИЯ 3</text>'
    b += f'<rect x="420" y="1250" width="240" height="8" fill="{SCARF}"/>'
    save("11_zastavka", svg(b))

if __name__ == "__main__":
    for f in [s01_idet, s02_lokot, s03_platforma, s04_dver, s05_kamorka, s05b, s05c, s06, s08, s09, s11]:
        f(); print("ok", f.__name__)
    subprocess.run(["node", os.path.join(ROOT, "tools", "render.js"), D.OUT], check=True)
    shutil.copy(os.path.join(ROOT, "s02", "frames", "10c_ulybka_zombi.png"), os.path.join(D.OUT, "07_ulybka_zombi.png"))
