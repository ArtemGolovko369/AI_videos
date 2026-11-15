"""Кадры серии 2 «Не один». Использует помощники из ../../tools/draw.py (серия 1).
Запуск: python3 s02/tools/draw.py → s02/frames/*.png
"""
import importlib.util, os, random, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
S1 = os.path.join(HERE, "..", "..")
spec = importlib.util.spec_from_file_location("s1draw", os.path.join(S1, "tools", "draw.py"))
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
D.OUT = os.path.join(HERE, "..", "frames"); os.makedirs(D.OUT, exist_ok=True)
W, H = D.W, D.H
svg, save, grad, head, body, figure, back_figure, fog = D.svg, D.save, D.grad, D.head, D.body, D.figure, D.back_figure, D.fog
YELLOW, HSKIN = D.YELLOW, D.HSKIN
SCARF = "#c8463c"          # её цветовой маркер
COAT = "#6b6e72"
HER_SKIN = "#b2b5ad"

# ---------------------------------------------------------------- она
def her(x, y, s=1, eyes="empty", mouth="flat", look=0, back=False):
    hair = "#2a2628"
    g = body(x, y + 70*s, s, COAT)
    g += f'<rect x="{x-14*s}" y="{y+40*s}" width="{28*s}" height="{40*s}" fill="{HER_SKIN}"/>'
    # каре: боковые пряди позади лица
    g += f'<path d="M{x-72*s},{y-20*s} q-4,{60*s} {6*s},{70*s} h{132*s} q{10*s},{-10*s} {6*s},{-70*s}z" fill="{hair}"/>'
    if back:
        g += f'<circle cx="{x}" cy="{y}" r="{64*s}" fill="{hair}"/>'
    else:
        g += head(x, y, 62*s, HER_SKIN, hair, eyes, mouth, look=look)
        g += f'<path d="M{x-66*s},{y-10*s} q{10*s},{-70*s} {66*s},{-68*s} q{56*s},0 {66*s},{68*s} q{-30*s},{-40*s} {-60*s},{-34*s} q{-20*s},{20*s} {-72*s},{34*s}z" fill="{hair}"/>'
    # красный шарф
    g += f'<path d="M{x-70*s},{y+70*s} q{70*s},{40*s} {140*s},0 v{34*s} q{-70*s},{40*s} {-140*s},0z" fill="{SCARF}"/>'
    g += f'<path d="M{x+30*s},{y+100*s} l{14*s},{110*s} h{34*s} l{-10*s},{-112*s}z" fill="#b13c33"/>'
    return g

def crooked_smile(x, y, r):
    """Неправильно скопированная улыбка: слишком широкая и кривая."""
    my = y + r*.55
    s = f'<path d="M{x-r*.62},{my-r*.18} q{r*.5},{r*.42} {r*1.25},{-r*.02} q{-r*.55},{r*.16} {-r*1.25},{r*.02}z" fill="#3e2e2c"/>'
    for i in range(7):
        tx = x - r*.48 + i*r*.15
        s += f'<rect x="{tx:.1f}" y="{my-r*.06 + abs(i-3)*r*-.015:.1f}" width="{r*.11:.1f}" height="{r*.1:.1f}" fill="#d9d8c8"/>'
    s += f'<path d="M{x-r*.62},{my-r*.18} q{r*.5},{r*.42} {r*1.25},{-r*.02}" stroke="#4d4a44" stroke-width="{r*.04:.1f}" fill="none"/>'
    return s

# ---------------------------------------------------------------- вагон (как в серии 1, со смешанными позами)
def wagon(turned=(), lit=True):
    d = grad("wg", "#565b5c", "#3a3d3f")
    b = f'<rect width="{W}" height="{H}" fill="url(#wg)"/>'
    b += '<rect x="0" y="420" width="1080" height="360" fill="#1d2022"/>'
    for x in range(0, 1080, 270): b += f'<rect x="{x}" y="420" width="16" height="360" fill="#6c7173"/>'
    b += '<rect x="0" y="120" width="1080" height="40" fill="#e9e3c8" opacity=".85"/>'
    b += '<path d="M0,200 h1080" stroke="#8d9294" stroke-width="10"/>'
    for x in (180, 540, 900): b += f'<line x1="{x}" y1="200" x2="{x}" y2="1920" stroke="#9aa0a2" stroke-width="12"/>'
    b += '<rect x="0" y="1300" width="1080" height="160" fill="#4d5a6b"/><rect y="1460" width="1080" height="460" fill="#2f3234"/>'
    random.seed(71)
    for i, x in enumerate([120, 300, 470, 640, 810, 980]):
        tilt = random.choice([-14, -8, 8, 14])
        if i in turned: b += figure(x, 1000, 1.25, eyes="stare", mouth="flat")
        else: b += figure(x, 1010, 1.25, eyes="closed", mouth="flat", tilt=tilt)
    random.seed(72)
    for k, x in enumerate((60, 1020)):
        if ("f%d" % k) in turned: b += figure(x, 1250, 2.4, eyes="stare")
        else: b += back_figure(x, 1250, 2.4)
    return b, d

def s04a():
    b, d = wagon(turned=(0, 2, 3, 5, "f1"))
    save("04a_otvorot", svg(b, "<defs>" + d + "</defs>"))

def s04b():
    b, d = wagon(turned=(3,))
    save("04b_otvorot", svg(b, "<defs>" + d + "</defs>"))

def s03_zevok():
    b = f'<rect width="{W}" height="{H}" fill="#3a3d3f"/>'
    b += '<rect x="0" y="300" width="1080" height="500" fill="#1d2022"/>'
    random.seed(81)
    b += figure(540, 980, 5.0, hero=True, eyes="closed", mouth="flat")
    b += '<ellipse cx="540" cy="1150" rx="70" ry="95" fill="#3e3a38"/><ellipse cx="540" cy="1200" rx="44" ry="30" fill="#7a4d4a"/>'
    save("03_zevok", svg(b))

def s03_pustoy():
    b = f'<rect width="{W}" height="{H}" fill="#3a3d3f"/>'
    b += '<rect x="0" y="300" width="1080" height="500" fill="#1d2022"/>'
    random.seed(81)
    b += figure(540, 980, 5.0, hero=True, eyes="hero", mouth="flat", look=-.9)
    save("03_pustoy", svg(b))

def s05_steklo():
    """Тёмное окно вагона с отражением; одна фигура в красном шарфе смотрит."""
    b = f'<rect width="{W}" height="{H}" fill="#3c3f41"/>'
    b += '<rect x="40" y="260" width="1000" height="1200" rx="40" fill="#121517"/>'
    b += '<rect x="40" y="260" width="1000" height="1200" rx="40" fill="none" stroke="#7d8284" stroke-width="22"/>'
    # отражение: полупрозрачные силуэты
    random.seed(91)
    g = ''
    for x in (180, 380, 820):
        g += figure(x, 900, 1.3, eyes="closed", tilt=random.choice([-10, 10]))
    g += her(610, 860, 1.45, eyes="empty", look=0)
    g += figure(330, 1180, 1.9, hero=True, eyes="hero", mouth="flat", look=.8)
    b += f'<g opacity=".42">{g}</g>'
    # бегущие огни тоннеля
    for y in (420, 760, 1120):
        b += f'<rect x="60" y="{y}" width="960" height="6" fill="#d9cf9e" opacity=".18"/>'
    b += '<polygon points="40,260 240,260 40,700" fill="#fff" opacity=".05"/>'
    b += '<rect y="1460" width="1080" height="460" fill="#4d5a6b"/>'
    save("05_steklo", svg(b))

def s06_ona():
    b = f'<rect width="{W}" height="{H}" fill="#3a3d3f"/>'
    b += '<rect x="0" y="300" width="1080" height="500" fill="#1d2022"/>'
    b += '<circle cx="540" cy="1250" r="420" fill="#c8463c" opacity=".05" filter="url(#blur60)"/>'
    b += her(540, 960, 4.6, eyes="empty", mouth="flat")
    save("06_ona", svg(b))

def s07_stanciya():
    b = f'<rect width="{W}" height="{H}" fill="#565b5c"/>'
    # открытые двери, за ними платформа
    b += '<rect x="250" y="220" width="580" height="1300" fill="#c9c3ae"/>'
    b += '<rect x="250" y="220" width="580" height="420" fill="#9a8f78"/>'
    for x in range(280, 830, 110): b += f'<rect x="{x}" y="300" width="60" height="200" rx="30" fill="#e8dfbf" opacity=".7"/>'  # колонны/светильники
    b += '<rect x="250" y="1300" width="580" height="220" fill="#a59d8a"/>'
    b += '<rect x="170" y="220" width="80" height="1300" fill="#7c8183"/><rect x="830" y="220" width="80" height="1300" fill="#7c8183"/>'
    # она уходит (со спины)
    b += f'<g transform="translate(0,0)">{her(560, 840, 1.6, back=True)}</g>'
    b += '<rect y="1520" width="1080" height="400" fill="#2f3234"/>'
    # сиденье и чек
    b += '<rect x="0" y="1520" width="1080" height="150" fill="#4d5a6b"/>'
    b += '<g transform="rotate(-12 780 1585)"><rect x="720" y="1555" width="130" height="62" fill="#f1efe6"/><path d="M730,1575 h100 M730,1590 h80" stroke="#b9b6aa" stroke-width="4"/></g>'
    b += '<circle cx="785" cy="1586" r="110" fill="#fff" opacity=".07" filter="url(#blur30)"/>'
    save("07_stanciya", svg(b))

def s08_chek():
    b = f'<rect width="{W}" height="{H}" fill="#2f3234"/>'
    b += '<circle cx="540" cy="900" r="520" fill="#f2c230" opacity=".05" filter="url(#blur60)"/>'
    # руки в жёлтых рукавах
    b += f'<path d="M0,1500 q160,-80 230,-260 l120,40 q-40,200 -150,360 h-200z" fill="{YELLOW}"/>'
    b += f'<path d="M1080,1500 q-160,-80 -230,-260 l-120,40 q40,200 150,360 h200z" fill="{YELLOW}"/>'
    b += f'<circle cx="300" cy="1250" r="60" fill="{HSKIN}"/><circle cx="780" cy="1250" r="60" fill="{HSKIN}"/>'
    # чек
    b += '<g transform="rotate(-3 540 900)">'
    b += '<path d="M290,420 h500 v980 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 l-25,-18 l-25,18 z" fill="#f3f1e8"/>'
    lines = [("ТЫ СЛИШКОМ", 640), ("ГРОМКО", 740), ("ДЫШИШЬ.", 840), ("ЗАВТРА 7:40", 1020), ("ПЕРВЫЙ ВАГОН", 1120)]
    for t, y in lines:
        b += f'<text x="540" y="{y}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="50" fill="#2b2f6a" transform="rotate({random.uniform(-2,2):.1f} 540 {y})">{t}</text>'
    b += '<path d="M360,1180 q180,30 360,-6" stroke="#2b2f6a" stroke-width="6" fill="none"/>'
    b += '<text x="540" y="520" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="26" fill="#b9b6aa">КАССОВЫЙ ЧЕК · ОБОРОТ</text>'
    b += '</g>'
    save("08_chek", svg(b))

def bathroom(hero_eyes, mouth):
    b = f'<rect width="{W}" height="{H}" fill="#9aa3a4"/>'
    for y in range(0, H, 120):
        for x in range(0, W, 120):
            b += f'<rect x="{x+3}" y="{y+3}" width="114" height="114" fill="#a8b1b2"/>'
    b += '<rect x="170" y="240" width="740" height="1000" rx="30" fill="#5b6668" stroke="#d6dadb" stroke-width="18"/>'
    b += '<rect x="186" y="256" width="708" height="968" rx="22" fill="#6f7c7e"/>'
    random.seed(81)
    b += f'<g>{figure(540, 760, 3.2, hero=True, eyes=hero_eyes, mouth=mouth)}</g>'
    b += '<polygon points="190,260 330,260 190,520" fill="#fff" opacity=".12"/>'
    b += '<rect x="170" y="240" width="740" height="1000" rx="30" fill="none" stroke="#d6dadb" stroke-width="18"/>'
    b += '<rect x="120" y="1380" width="840" height="540" rx="40" fill="#e7eaea"/><ellipse cx="540" cy="1480" rx="260" ry="70" fill="#c9cfd0"/>'
    b += '<rect x="520" y="1300" width="40" height="110" rx="12" fill="#b3b9ba"/>'
    b += '<rect x="0" y="1240" width="1080" height="20" fill="#7d8687"/>'
    return b

def s09_zerkalo(): save("09_zerkalo", svg(bathroom("empty", "open")))

def s09b_stena():
    b = f'<rect width="{W}" height="{H}" fill="#9aa3a4"/>'
    for y in range(0, H, 120):
        for x in range(0, W, 120):
            b += f'<rect x="{x+3}" y="{y+3}" width="114" height="114" fill="#a8b1b2"/>'
    # трещинка и «волны» звука из стены
    b += '<path d="M540,300 l20,120 l-30,90 l40,140 l-20,100" stroke="#6c7576" stroke-width="5" fill="none"/>'
    for k, r in enumerate((180, 300, 420)):
        b += f'<path d="M{540-r},960 a{r},{r} 0 0 1 {2*r},0" stroke="#5f6869" stroke-width="{10-k*2}" fill="none" opacity="{.6-k*.15:.2f}"/>'
    b += '<circle cx="540" cy="960" r="40" fill="#5f6869" opacity=".5"/>'
    save("09b_stena", svg(b))

def s10_utro():
    d = grad("wg", "#7a7f80", "#4c5052")
    b = f'<rect width="{W}" height="{H}" fill="url(#wg)"/>'
    b += '<rect x="0" y="120" width="1080" height="40" fill="#f2ecd2" opacity=".9"/>'
    b += '<rect x="0" y="420" width="1080" height="360" fill="#b7b9b0"/>'  # светлый тоннель-утро
    b += '<path d="M0,200 h1080" stroke="#8d9294" stroke-width="10"/>'
    # двери
    b += '<rect x="700" y="260" width="300" height="1660" fill="#6a6f71"/><rect x="845" y="260" width="10" height="1660" fill="#3a3d3f"/>'
    random.seed(101)
    for x, y, s in [(80, 900, 1.2), (250, 880, 1.15), (420, 910, 1.2), (590, 890, 1.15)]:
        b += figure(x, y, s, eyes="empty", tilt=random.uniform(-6, 6))
    b += her(850, 980, 1.9, eyes="hero", mouth="flat", look=-1)
    random.seed(102)
    for x in (120, 420):
        b += back_figure(x, 1300, 2.3)
    save("10_utro", svg(b, "<defs>" + d + "</defs>"))

def s10b_telefon():
    b = f'<rect width="{W}" height="{H}" fill="#3d4143"/>'
    b += f'<path d="M820,1920 q60,-420 -60,-560 l-150,-30 q-60,10 -30,80 l50,140 q-130,-20 -180,30 l-40,340z" fill="{HER_SKIN}"/>'
    b += f'<path d="M880,1920 q30,-300 -60,-430 l-90,40 q40,140 20,390z" fill="{COAT}"/>'
    b += f'<path d="M780,1500 q60,30 120,-10 v40 q-60,40 -120,10z" fill="{SCARF}"/>'
    b += '<rect x="270" y="420" width="540" height="1060" rx="64" fill="#15171a"/><rect x="294" y="450" width="492" height="1000" rx="46" fill="#f3efe0"/>'
    b += '<rect x="294" y="450" width="492" height="110" rx="46" fill="#e8dfbf"/><rect x="294" y="510" width="492" height="50" fill="#e8dfbf"/>'
    b += '<text x="330" y="530" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#8a7a50">‹ Заметки</text>'
    for t, y, c in [("НЕ", 760, "#1c1f26"), ("УЛЫБАЙСЯ.", 860, "#1c1f26"), ("ОНИ", 1040, "#c8463c"), ("УЧАТСЯ.", 1140, "#c8463c")]:
        b += f'<text x="540" y="{y}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="62" fill="{c}">{t}</text>'
    b += '<rect x="560" y="1180" width="5" height="70" fill="#1c1f26"/>'
    save("10b_telefon", svg(b))

def s10c_ulybka():
    b = f'<rect width="{W}" height="{H}" fill="#5a5f60"/>'
    b += '<rect x="0" y="0" width="1080" height="700" fill="#4b4f51"/><rect x="0" y="120" width="1080" height="40" fill="#f2ecd2" opacity=".6"/>'
    b += '<line x1="180" y1="0" x2="180" y2="1920" stroke="#9aa0a2" stroke-width="16"/>'
    random.seed(111)
    b += figure(560, 900, 4.6, col="#4a4f58", skin="#a2a89e", eyes="stare", mouth="none")
    b += crooked_smile(560, 900, 62*4.6)
    b += '<rect width="1080" height="1920" fill="#000" opacity=".12"/>'
    save("10c_ulybka_zombi", svg(b))

def s11():
    b = f'<rect width="{W}" height="{H}" fill="#121416"/>'
    b += fog(91, 8, 600, 1400, .12, "#6c7378")
    b += f'<g opacity=".18">{D.city_towers(1300, seed=1)}</g>'
    b += '<text x="540" y="880" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="150" fill="#e8e4d8" letter-spacing="6">ЖИВОЙ</text>'
    b += '<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="110" fill="#f2c230" letter-spacing="6">В МОСКВЕ</text>'
    b += '<rect x="390" y="1110" width="300" height="4" fill="#8a8f92"/>'
    b += '<text x="540" y="1200" text-anchor="middle" font-family="DejaVu Sans" font-size="48" fill="#a9aeb1" letter-spacing="14">СЕРИЯ 2</text>'
    b += f'<rect x="420" y="1250" width="240" height="8" fill="{SCARF}"/>'
    save("11_zastavka", svg(b))

if __name__ == "__main__":
    for f in [s03_zevok, s03_pustoy, s04a, s04b, s05_steklo, s06_ona, s07_stanciya, s08_chek,
              s09_zerkalo, s09b_stena, s10_utro, s10b_telefon, s10c_ulybka, s11]:
        f(); print("ok", f.__name__)
    subprocess.run(["node", os.path.join(S1, "tools", "render.js"), D.OUT], check=True)
    # повтор кадров из серии 1
    for name, new in [("10c_golovy", "01_golovy"), ("10b_ulybka", "02_ulybka"), ("10_vagon", "04c_vagon")]:
        shutil.copy(os.path.join(S1, "frames", name + ".png"), os.path.join(D.OUT, new + ".png"))
