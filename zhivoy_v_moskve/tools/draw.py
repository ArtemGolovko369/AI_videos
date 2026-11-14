"""Кадры для «Живой в Москве», серия 1. Плоский 2D-вектор, 1080×1920.
Запуск: python3 tools/draw.py  → frames/*.png
"""
import math, random, os, subprocess
W, H = 1080, 1920
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frames")
os.makedirs(OUT, exist_ok=True)

YELLOW = "#f2c230"      # куртка героя — единственный тёплый цвет
ZSKIN = ["#a9b0a4", "#9fa79c", "#b3b6ad", "#a2a89f"]   # кожа зомби
HSKIN = "#b9bab1"       # герой тоже серый (поворот сюжета)
CLOTH = ["#4b5160", "#5c5f66", "#6b6f78", "#3f4652", "#73706a", "#545a52", "#62584f"]

DEFS = '''<defs>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix type="saturate" values="0"/></filter>
<filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="blur30"><feGaussianBlur stdDeviation="30"/></filter>
<filter id="blur60"><feGaussianBlur stdDeviation="60"/></filter>
<filter id="glow"><feGaussianBlur stdDeviation="16" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".5"/></radialGradient>
</defs>'''

def svg(body, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            + DEFS + extra + body +
            f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".08"/>'
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')

def save(name, s):
    """SVG пишется в frames/, растеризуется потом одним проходом Chromium (render.js)."""
    open(f"{OUT}/{name}.svg", "w").write(s)

def grad(id_, top, bot, x2="0", y2="1"):
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>'

# ---------------------------------------------------------------- персонажи
def head(x, y, r, skin, hair="#2e2f33", eyes="empty", mouth="flat", bags=True, look=0, bite=False):
    """Лицо анфас. eyes: empty (белые без зрачков) | hero | hero_tense | closed. look: сдвиг зрачков."""
    s = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{skin}"/>'
    s += f'<path d="M{x-r},{y-r*.15} q{r*.1},{-r*1.05} {r},{-r*.95} q{r*.95},{-.1*r} {r},{r*.95} q{-r*.5},{-r*.45} {-r*1.15},{-r*.4} q{-r*.5},0 {-r*.85},{r*.4}z" fill="{hair}"/>'
    ex, ey, er = r*.36, y + r*.08, r*.17
    for sx in (-1, 1):
        cx = x + sx*ex
        if bags:
            s += f'<path d="M{cx-er*1.3},{ey+er*1.1} q{er*1.3},{er*1.1} {er*2.6},0" stroke="#6e7268" stroke-width="{r*.06:.1f}" fill="none" opacity=".8"/>'
        if eyes == "empty":
            s += f'<ellipse cx="{cx}" cy="{ey}" rx="{er*1.05}" ry="{er*.9}" fill="#e9ece4"/>'
            s += f'<path d="M{cx-er*1.1},{ey-er*.25} h{er*2.2}" stroke="{skin}" stroke-width="{er*.9:.1f}" opacity=".9"/>'  # тяжёлые веки
        elif eyes == "stare":
            s += f'<ellipse cx="{cx}" cy="{ey}" rx="{er*1.1}" ry="{er*1.1}" fill="#eef0e8"/>'
            s += f'<circle cx="{cx}" cy="{ey}" r="{er*.28}" fill="#2a2c2a"/>'
        elif eyes in ("hero", "hero_tense"):
            s += f'<ellipse cx="{cx}" cy="{ey}" rx="{er}" ry="{er*(1.05 if eyes=="hero_tense" else .85)}" fill="#f4f4ee"/>'
            s += f'<circle cx="{cx+look*er*.5}" cy="{ey}" r="{er*.55}" fill="#3b2e26"/><circle cx="{cx+look*er*.5-er*.2}" cy="{ey-er*.25}" r="{er*.18}" fill="#fff"/>'
            if eyes == "hero_tense":
                s += f'<path d="M{cx-er*1.2},{ey-er*1.9+sx*0} l{er*2.4},{er*.5*(-sx)}" stroke="{hair}" stroke-width="{r*.07:.1f}" stroke-linecap="round"/>'
            else:
                s += f'<path d="M{cx-er*1.1},{ey-er*1.7} h{er*2.2}" stroke="{hair}" stroke-width="{r*.06:.1f}" stroke-linecap="round"/>'
        elif eyes == "closed":
            s += f'<path d="M{cx-er},{ey} q{er},{er*.6} {er*2},0" stroke="#3b3d3a" stroke-width="{r*.05:.1f}" fill="none"/>'
    my = y + r*.58
    if mouth == "flat":
        s += f'<path d="M{x-r*.2},{my} h{r*.4}" stroke="#5d625a" stroke-width="{r*.06:.1f}" stroke-linecap="round"/>'
    elif mouth == "open":
        s += f'<ellipse cx="{x}" cy="{my}" rx="{r*.16}" ry="{r*.12}" fill="#3e3a38"/>'
    elif mouth == "smile":
        s += f'<path d="M{x-r*.2},{my} h{r*.28} q{r*.1},0 {r*.16},{-r*.09}" stroke="#5d4a44" stroke-width="{r*.06:.1f}" stroke-linecap="round" fill="none"/>'
    elif mouth == "tense":
        s += f'<path d="M{x-r*.18},{my+r*.03} q{r*.18},{-r*.08} {r*.36},0" stroke="#5d625a" stroke-width="{r*.06:.1f}" stroke-linecap="round" fill="none"/>'
    if bite:
        s += f'<g transform="translate({x+r*.55},{y+r*1.05})"><ellipse rx="{r*.22}" ry="{r*.14}" fill="#7a3b38"/>'
        for i in range(5):
            s += f'<circle cx="{-r*.16+i*r*.08}" cy="{-r*.09 if i%2 else r*.09}" r="{r*.03}" fill="#4a2422"/>'
        s += '</g>'
    return s

def body(x, y, s, col, hood=False):
    """Туловище от плеч (y) вниз, ширина ~ 150*s."""
    b = f'<path d="M{x-95*s},{y+50*s} q0,-50 {50*s},-50 h{90*s} q{50*s},0 {50*s},50 v{360*s} h{-190*s}z" fill="{col}"/>'
    for sx in (-1, 1):
        b += f'<path d="M{x+sx*88*s},{y+60*s} q{sx*14*s},{150*s} {sx*6*s},{300*s}" stroke="{col}" stroke-width="{34*s}" stroke-linecap="round" fill="none"/>'
        b += f'<path d="M{x+sx*88*s},{y+60*s} q{sx*14*s},{150*s} {sx*6*s},{300*s}" stroke="#000" stroke-opacity=".12" stroke-width="{4*s}" fill="none"/>'
    if hood:
        b += f'<path d="M{x-50*s},{y} q{50*s},{50*s} {100*s},0" stroke="#d9a51e" stroke-width="{12*s}" fill="none"/>'
        b += f'<path d="M{x},{y+20*s} v{340*s}" stroke="#c99a1c" stroke-width="{5*s}"/>'
    return b

def figure(x, y, s=1, col=None, skin=None, eyes="empty", mouth="flat", hero=False, look=0, bite=False, tilt=0):
    col = YELLOW if hero else (col or random.choice(CLOTH))
    skin = HSKIN if hero else (skin or random.choice(ZSKIN))
    hair = "#2b2a2d" if hero else random.choice(["#3a3a3c", "#57534d", "#2e2f33", "#77736c"])
    g = f'<g transform="rotate({tilt} {x} {y})">'
    g += body(x, y + 70*s, s, col, hood=hero)
    g += f'<rect x="{x-14*s}" y="{y+40*s}" width="{28*s}" height="{40*s}" fill="{skin}"/>'
    g += head(x, y, 62*s, skin, hair, eyes if not hero else eyes, mouth, look=look, bite=bite)
    return g + '</g>'

def back_figure(x, y, s=1, col=None, slouch=0):
    """Вид со спины (толпа)."""
    col = col or random.choice(CLOTH)
    hair = random.choice(["#3a3a3c", "#57534d", "#2e2f33", "#77736c", "#8a857c"])
    g = f'<g transform="rotate({slouch} {x} {y+300*s})">'
    g += body(x, y + 70*s, s, col)
    g += f'<circle cx="{x}" cy="{y}" r="{60*s}" fill="{random.choice(ZSKIN)}"/>'
    g += f'<path d="M{x-60*s},{y+6*s} a{60*s},{60*s} 0 0 1 {120*s},0 q{-60*s},{-14*s} {-120*s},0z" fill="{hair}"/>'
    g += f'<circle cx="{x}" cy="{y-4*s}" r="{58*s}" fill="{hair}" opacity=".9"/>'
    return g + '</g>'

def walker_side(x, y, s=1, col="#555a62", skin="#a6ab9f", step=0, hero=False):
    """Профиль идущего, согнутая спина."""
    col = YELLOW if hero else col
    g = ''
    # ноги
    g += f'<path d="M{x-10*s},{y-170*s} l{-40*s-step*20*s},{170*s}" stroke="#34373d" stroke-width="{30*s}" stroke-linecap="round"/>'
    g += f'<path d="M{x+10*s},{y-170*s} l{30*s+step*20*s},{170*s}" stroke="#2c2f35" stroke-width="{30*s}" stroke-linecap="round"/>'
    # тело (наклон вперёд)
    g += f'<path d="M{x-40*s},{y-160*s} q{-10*s},{-140*s} {40*s},{-210*s} q{60*s},{-10*s} {70*s},{40*s} l{-10*s},{180*s}z" fill="{col}"/>'
    # рука висит
    g += f'<path d="M{x+30*s},{y-330*s} q{30*s},{90*s} {40*s},{170*s}" stroke="{col}" stroke-width="{26*s}" stroke-linecap="round" fill="none"/>'
    g += f'<circle cx="{x+72*s}" cy="{y-150*s}" r="{14*s}" fill="{skin}"/>'
    # голова опущена
    hx, hy = x + 55*s, y - 395*s
    g += f'<circle cx="{hx}" cy="{hy}" r="{48*s}" fill="{skin}"/>'
    g += f'<path d="M{hx-48*s},{hy} a{48*s},{48*s} 0 0 1 {80*s},{-34*s} q{-30*s},{20*s} {-80*s},{34*s}z" fill="#3a3a3c"/>'
    g += f'<ellipse cx="{hx+28*s}" cy="{hy+4*s}" rx="{10*s}" ry="{7*s}" fill="#e6e9e1"/>'
    g += f'<path d="M{hx+16*s},{hy-2*s} h{24*s}" stroke="{skin}" stroke-width="{6*s}"/>'
    return g

def city_towers(y0, fog=.6, seed=1, light=False):
    """Кластер стеклянных небоскрёбов (обобщённый деловой центр, без копии реальных зданий)."""
    random.seed(seed); s = ''
    specs = [(170, 150, 820, "#7f8b99"), (330, 170, 1080, "#8e9aa8"), (520, 190, 1300, "#6f7c8c"),
             (720, 160, 1010, "#8794a3"), (880, 150, 760, "#9aa5b1"), (60, 130, 560, "#a3adb7"), (1010, 140, 600, "#a8b1ba")]
    for (cx, w, h, c) in specs:
        x = cx - w/2; top = y0 - h
        # срезанная/скрученная вершина
        s += f'<path d="M{x},{y0} V{top+60} L{x+w*.55},{top} L{x+w},{top+40} V{y0}z" fill="{c}"/>'
        s += f'<path d="M{x+w*.55},{top} L{x+w},{top+40} V{y0} H{x+w*.55}z" fill="#000" opacity=".12"/>'
        for yy in range(int(top+80), int(y0), 26):
            s += f'<line x1="{x+6}" y1="{yy}" x2="{x+w-6}" y2="{yy}" stroke="#c9d3dc" stroke-width="2" opacity=".25"/>'
        if light:
            for _ in range(14):
                wx = random.uniform(x+10, x+w-20); wy = random.uniform(top+100, y0-20)
                s += f'<rect x="{wx:.0f}" y="{wy:.0f}" width="14" height="10" fill="#f3dfa0" opacity=".55"/>'
    return s

def panel_houses(y0, seed=2, col="#8d9196", lit=.12, n=6):
    random.seed(seed); s = ''; x = -30
    while x < W + 30:
        w = random.randint(200, 300); h = random.randint(420, 720)
        c = random.choice([col, "#999da1", "#83888e"])
        s += f'<rect x="{x}" y="{y0-h}" width="{w}" height="{h+600}" fill="{c}"/>'
        for wy in range(y0-h+30, y0-30, 58):
            for wx in range(x+18, x+w-30, 44):
                f = "#e8d79a" if random.random() < lit else "#6e7378"
                s += f'<rect x="{wx}" y="{wy}" width="24" height="30" fill="{f}"/>'
        x += w + random.randint(4, 18)
    return s

def fog(seed, n, y0, y1, op=.45, col="#dfe3e6"):
    random.seed(seed); s = ''
    for _ in range(n):
        x = random.randint(-200, W+200); y = random.randint(y0, y1); rx = random.randint(250, 520)
        s += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*.28:.0f}" fill="{col}" opacity="{random.uniform(op*.5, op):.2f}" filter="url(#blur60)"/>'
    return s

# ---------------------------------------------------------------- сцены
def s01():  # Деловой центр в утреннем тумане
    d = grad("sk", "#b9c2c9", "#e3e2dc")
    b = f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b += '<circle cx="760" cy="520" r="110" fill="#f4ecd6" opacity=".6" filter="url(#blur30)"/>'
    b += f'<g opacity=".55">{panel_houses(1500, seed=9, col="#a8adb2", lit=0)}</g>'
    b += city_towers(1500, seed=1)
    b += fog(3, 14, 900, 1600, .6)
    b += '<path d="M0,1500 q540,-30 1080,0 v420 h-1080z" fill="#7b8185"/>'
    b += '<path d="M0,1560 q540,-24 1080,0" stroke="#9aa0a3" stroke-width="10" fill="none"/>'  # набережная
    b += '<rect y="1580" width="1080" height="340" fill="#6c7378"/>'
    for i in range(10):
        b += f'<path d="M{random.randint(0,1000)},{1620+i*28} h{random.randint(60,200)}" stroke="#8d969b" stroke-width="4" opacity=".6"/>'
    b += fog(5, 8, 1500, 1900, .5)
    save("01_siti", svg(b, "<defs>"+d+"</defs>"))

def s02():  # вид сверху, серые точки, одна жёлтая
    b = f'<rect width="{W}" height="{H}" fill="#8b8f92"/>'
    random.seed(4)
    # кварталы
    for gx in range(-40, W, 260):
        for gy in range(-40, H, 300):
            b += f'<rect x="{gx+30}" y="{gy+30}" width="200" height="240" rx="6" fill="{random.choice(["#9a9ea1","#a3a6a8","#939799"])}"/>'
            b += f'<rect x="{gx+50}" y="{gy+50}" width="160" height="200" rx="4" fill="#b0b3b4" opacity=".6"/>'
    # улицы с толпой
    for gx in range(-40, W, 260):
        for _ in range(140):
            x = gx + random.uniform(0, 30); y = random.uniform(0, H)
            b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.uniform(3,5):.1f}" fill="{random.choice(["#5d625f","#6b6f6a","#50544f","#767a74"])}"/>'
    for gy in range(-40, H, 300):
        for _ in range(110):
            x = random.uniform(0, W); y = gy + random.uniform(0, 30)
            b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.uniform(3,5):.1f}" fill="{random.choice(["#5d625f","#6b6f6a","#50544f","#767a74"])}"/>'
    # единственная жёлтая точка (перекрёсток рядом с центром)
    b += '<circle cx="534" cy="1166" r="26" fill="#f2c230" opacity=".35" filter="url(#glow)"/><circle cx="534" cy="1166" r="7" fill="#f2c230"/>'
    save("02_sverhu", svg(b))

def s03():  # выход из подъезда
    b = f'<rect width="{W}" height="{H}" fill="#9a9c9c"/>'
    b += '<rect x="0" y="0" width="1080" height="1500" fill="#8c8f90"/>'
    for y in range(0, 1500, 90):
        b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#7d8081" stroke-width="3"/>'
    # козырёк и дверь
    b += '<rect x="180" y="300" width="720" height="60" fill="#6d7072"/><rect x="200" y="360" width="680" height="16" fill="#585b5d"/>'
    b += '<rect x="290" y="420" width="500" height="1080" fill="#4d5a55"/><rect x="310" y="440" width="460" height="1060" fill="#2a2e2d"/>'
    b += '<rect x="660" y="900" width="60" height="110" rx="10" fill="#6f7774"/>'  # домофон
    b += '<text x="540" y="410" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#c8cbc9">ПОДЪЕЗД 3</text>'
    b += '<rect y="1500" width="1080" height="420" fill="#7f8182"/><rect x="160" y="1500" width="760" height="40" fill="#929495"/>'
    random.seed(2)
    b += figure(540, 900, 1.9, hero=True, eyes="hero_tense", mouth="tense", look=-0.6)
    b += '<path d="M120,600 q-30,30 0,60 M960,600 q30,30 0,60" stroke="#c8cbc9" stroke-width="5" fill="none" opacity=".5"/>'
    save("03_podezd", svg(b))

def s04():  # двор, сосед-зомби бредёт к машине
    d = grad("sk", "#b6bbbf", "#d6d7d4")
    b = f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b += panel_houses(1150, seed=5)
    b += fog(8, 6, 800, 1200, .35)
    b += f'<rect y="1150" width="{W}" height="770" fill="#7c7f80"/>'
    b += '<rect y="1150" width="1080" height="60" fill="#929596"/>'
    # машина
    b += '<path d="M560,1560 v-120 q10,-60 70,-70 l70,-90 h220 q60,0 90,80 l60,20 v180z" fill="#5f6a74"/>'
    b += '<path d="M720,1300 h180 q36,0 54,60 h-286z" fill="#a9b4bb"/>'
    b += '<circle cx="660" cy="1570" r="54" fill="#2a2c2e"/><circle cx="960" cy="1570" r="54" fill="#2a2c2e"/><circle cx="660" cy="1570" r="22" fill="#808487"/><circle cx="960" cy="1570" r="22" fill="#808487"/>'
    # детская площадка
    b += '<path d="M60,1300 v160 M200,1300 v160 M50,1300 h160" stroke="#6a6f75" stroke-width="10" fill="none"/>'
    b += walker_side(330, 1760, 1.35, col="#4f5a66", skin="#a3a99e", step=.4)
    # портфель
    b += '<rect x="400" y="1500" width="70" height="56" rx="6" fill="#3b3631"/>'
    save("04_dvor", svg(b, "<defs>"+d+"</defs>"))

def s04b():  # крупно лицо соседа
    b = f'<rect width="{W}" height="{H}" fill="#a3a7a8"/>'
    b += f'<g opacity=".5" filter="url(#blur6)">{panel_houses(1400, seed=5)}</g>'
    random.seed(11)
    b += figure(540, 820, 4.2, col="#4f5a66", skin="#a3a99e", eyes="empty", mouth="flat")
    save("04b_sosed", svg(b))

def s05():  # эскалатор, толпа со спины
    d = grad("tn", "#6a6e70", "#3c3f41")
    b = f'<rect width="{W}" height="{H}" fill="url(#tn)"/>'
    # арка метро
    b += '<path d="M0,0 h1080 v500 q-540,-260 -1080,0z" fill="#585b5d"/>'
    for x in range(80, 1080, 160):
        b += f'<rect x="{x}" y="120" width="70" height="20" rx="10" fill="#efe9d2" opacity=".85"/>'
    # эскалатор уходит вниз-вдаль
    b += '<polygon points="300,1920 780,1920 640,700 440,700" fill="#4a4d50"/>'
    for i in range(30):
        t = i/30; y = 700 + (1920-700)*t**1.3
        xl = 440 - 140*t**1.3; xr = 640 + 140*t**1.3
        b += f'<line x1="{xl:.0f}" y1="{y:.0f}" x2="{xr:.0f}" y2="{y:.0f}" stroke="#2f3133" stroke-width="3"/>'
    b += '<polygon points="250,1920 300,1920 440,700 420,700" fill="#2a2c2e"/><polygon points="780,1920 830,1920 660,700 640,700" fill="#2a2c2e"/>'
    # лампы-«факелы»
    for i in range(5):
        t = i/5; y = 760 + 1000*t; x = 400 - 160*t
        b += f'<rect x="{x-20*(1+t)}" y="{y}" width="{12*(1+t)}" height="{60*(1+t)}" fill="#efe1b0" opacity=".7"/>'
        b += f'<rect x="{1080-x+8}" y="{y}" width="{12*(1+t)}" height="{60*(1+t)}" fill="#efe1b0" opacity=".7"/>'
    random.seed(7)
    rows = [(760, .35, 4), (900, .5, 4), (1080, .7, 4), (1320, .95, 4), (1640, 1.3, 3)]
    for (y, s, n) in rows:
        span = 260 + 420*s
        for k in range(n):
            x = 540 - span/2 + span*(k+.5)/n + random.uniform(-20, 20)
            b += back_figure(x, y, s, slouch=random.uniform(-6, 6))
    b += fog(12, 4, 300, 800, .25, "#cfd2d0")
    save("05_metro", svg(b, "<defs>"+d+"</defs>"))

def s06():  # герой зажат между зомби
    b = f'<rect width="{W}" height="{H}" fill="#5e6163"/>'
    b += '<rect y="0" width="1080" height="260" fill="#4c4f51"/>'
    for x in range(60, 1080, 220): b += f'<rect x="{x}" y="80" width="120" height="16" rx="8" fill="#efe9d2"/>'
    random.seed(21)
    # задний ряд
    for x in (90, 330, 750, 990):
        b += figure(x, 560, 1.5, eyes="empty", tilt=random.uniform(-6, 6))
    # герой в центре
    b += figure(540, 760, 2.2, hero=True, eyes="hero_tense", mouth="tense", look=-0.8)
    # передние плечи зомби
    b += figure(110, 900, 2.6, eyes="empty", tilt=8)
    b += figure(980, 920, 2.6, eyes="empty", tilt=-7)
    # капля пота
    b += '<path d="M676,700 q14,24 0,36 q-14,-12 0,-36z" fill="#d7ecf2" opacity=".9"/>'
    save("06_zazhat", svg(b))

def office(boss_front):
    b = f'<rect width="{W}" height="{H}" fill="#a9aca8"/>'
    b += '<rect y="0" width="1080" height="160" fill="#c6c8c3"/>'
    for x in range(60, 1080, 250): b += f'<rect x="{x}" y="60" width="180" height="24" fill="#f2f4ee"/>'
    b += '<rect x="0" y="160" width="1080" height="700" fill="#b6b8b3"/>'
    b += '<rect x="80" y="260" width="380" height="420" fill="#c9d0d4" stroke="#8d9192" stroke-width="10"/>'  # окно
    b += '<path d="M80,680 V520 h60 V420 h50 V560 h70 V380 h60 V600 h80 V500 h60 V680z" fill="#9aa4ab" opacity=".6"/>'
    b += '<rect x="600" y="300" width="360" height="240" fill="#e9ebe6" stroke="#8d9192" stroke-width="6"/>'  # доска с графиком
    b += '<path d="M630,500 l60,-40 l60,20 l60,-70 l60,90 l60,-30" stroke="#8a8e8f" stroke-width="8" fill="none"/>'
    b += '<rect y="1240" width="1080" height="680" fill="#8e918d"/>'
    random.seed(31)
    # ряд коллег за мониторами (со спины/сбоку)
    for i, x in enumerate((150, 410, 670, 930)):
        b += f'<rect x="{x-80}" y="930" width="160" height="110" rx="6" fill="#2e3236"/><rect x="{x-70}" y="940" width="140" height="90" fill="#9fb3bd" opacity=".85"/><rect x="{x-8}" y="1040" width="16" height="40" fill="#2e3236"/>'
        b += f'<rect x="{x-120}" y="1075" width="240" height="26" fill="#6e6a62"/>'
        b += back_figure(x, 1080, .8, slouch=random.uniform(-10, 10))
    # начальник ближе к камере
    if boss_front:
        b += figure(540, 1380, 2.6, col="#30343c", eyes="empty", mouth="open")
        b += '<path d="M500,1690 l40,40 l40,-40 l-20,200 h-40z" fill="#7a2f2f"/>'  # галстук
    else:
        b += back_figure(540, 1380, 2.6, col="#30343c")
    return b

def s07(): save("07_ofis", svg(office(False)))
def s07b(): save("07b_nachalnik", svg(office(True)))

def s08():  # курьер с укусом
    b = f'<rect width="{W}" height="{H}" fill="#8c8e8b"/>'
    b += '<rect x="0" y="0" width="300" height="1920" fill="#6f716e"/><rect x="40" y="200" width="220" height="1500" fill="#4a4c49"/>'  # дверь
    b += '<rect y="1600" width="1080" height="320" fill="#6d6f6c"/>'
    random.seed(41)
    b += figure(600, 760, 3.0, col="#3d6a5a", skin="#a2a99c", eyes="empty", mouth="flat", bite=True)
    # кепка
    b += '<path d="M420,620 q180,-150 360,0 z" fill="#3d6a5a"/><rect x="560" y="610" width="260" height="26" rx="13" fill="#2f5446"/>'
    # протянутый пакет
    b += '<path d="M320,1250 h300 l-30,330 h-240z" fill="#d7c9a6"/><path d="M400,1250 q70,-110 140,0" stroke="#bfae86" stroke-width="16" fill="none"/>'
    b += '<rect x="360" y="1360" width="220" height="70" fill="#c4b38c"/>'
    b += '<path d="M640,1180 q-60,60 -80,120" stroke="#3d6a5a" stroke-width="80" stroke-linecap="round" fill="none"/><circle cx="560" cy="1300" r="40" fill="#a2a99c"/>'
    # бейдж «ВОВРЕМЯ»
    b += '<g transform="rotate(-6 780 1480)"><rect x="660" y="1440" width="260" height="80" rx="40" fill="#e6e8e2"/><text x="790" y="1494" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#4b6b4f">✓ 12:00</text></g>'
    save("08_kuryer", svg(b))

def s08b():  # пробка
    d = grad("sk", "#a7adb1", "#cfd0cc")
    b = f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b += panel_houses(900, seed=14, lit=0)
    b += fog(2, 6, 600, 950, .4)
    b += '<polygon points="0,900 1080,900 1080,1920 0,1920" fill="#6b6e70"/>'
    random.seed(51)
    for row, (y, s) in enumerate([(980, .45), (1120, .65), (1330, .95), (1640, 1.4)]):
        n = 4 if s < .8 else 3
        for k in range(n):
            x = (k+.5)*W/n + random.uniform(-30, 30)
            w, h = 280*s, 160*s
            c = random.choice(["#5f6a74", "#7a7468", "#5a5f58", "#83878b", "#4e5257"])
            b += f'<path d="M{x-w/2},{y} v{-h*.5} q0,{-h*.2} {w*.1},{-h*.25} l{w*.12},{-h*.35} h{w*.56} l{w*.12},{h*.35} q{w*.1},{h*.05} {w*.1},{h*.25} v{h*.5}z" fill="{c}"/>'
            b += f'<path d="M{x-w*.28},{y-h*.78} h{w*.56} l{w*.08},{h*.22} h{-w*.72}z" fill="#a9b4bb"/>'
            # водитель-зомби в стекле
            b += f'<circle cx="{x-w*.12}" cy="{y-h*.68}" r="{h*.13}" fill="#9ea59a"/>'
            b += f'<ellipse cx="{x-w*.16}" cy="{y-h*.68}" rx="{h*.03}" ry="{h*.025}" fill="#eef0e8"/><ellipse cx="{x-w*.08}" cy="{y-h*.68}" rx="{h*.03}" ry="{h*.025}" fill="#eef0e8"/>'
            b += f'<rect x="{x-w*.45}" y="{y-h*.42}" width="{w*.12}" height="{h*.1}" fill="#c9504a"/><rect x="{x+w*.33}" y="{y-h*.42}" width="{w*.12}" height="{h*.1}" fill="#c9504a"/>'
    save("08b_probka", svg(b, "<defs>"+d+"</defs>"))

def s09():  # отражение в витрине
    b = f'<rect width="{W}" height="{H}" fill="#7b7e7f"/>'
    b += '<rect x="60" y="180" width="960" height="1440" fill="#5f6a70"/>'
    b += '<rect x="60" y="180" width="960" height="1440" fill="none" stroke="#3e4245" stroke-width="30"/>'
    # манекены в витрине
    for x in (230, 850):
        b += f'<circle cx="{x}" cy="540" r="54" fill="#8d979c"/><path d="M{x-80},{620} h160 l20,500 h-200z" fill="#7f898e"/>'
    # отражение героя: полупрозрачное
    random.seed(61)
    b += f'<g opacity=".8">{figure(540, 760, 3.0, hero=True, eyes="hero", mouth="flat", look=0)}</g>'
    # блики стекла
    b += '<polygon points="120,180 300,180 60,700 60,420" fill="#fff" opacity=".12"/><polygon points="700,180 760,180 300,1620 240,1620" fill="#fff" opacity=".07"/>'
    b += '<rect x="60" y="1620" width="960" height="300" fill="#5c5f60"/>'
    b += '<text x="540" y="140" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="56" fill="#c8cbc9" letter-spacing="8">ОДЕЖДА</text>'
    save("09_vitrina", svg(b))

def wagon(heads_turned=False, hero=False):
    d = grad("wg", "#565b5c", "#3a3d3f")
    b = f'<rect width="{W}" height="{H}" fill="url(#wg)"/>'
    # окна-полосы, тёмный тоннель
    b += '<rect x="0" y="420" width="1080" height="360" fill="#1d2022"/>'
    for x in range(0, 1080, 270): b += f'<rect x="{x}" y="420" width="16" height="360" fill="#6c7173"/>'
    b += '<rect x="0" y="120" width="1080" height="40" fill="#e9e3c8" opacity=".85"/>'  # лампы
    b += '<path d="M0,200 h1080" stroke="#8d9294" stroke-width="10"/>'  # поручень
    for x in (180, 540, 900): b += f'<line x1="{x}" y1="200" x2="{x}" y2="1920" stroke="#9aa0a2" stroke-width="12"/>'
    # сиденья
    b += '<rect x="0" y="1300" width="1080" height="160" fill="#4d5a6b"/><rect y="1460" width="1080" height="460" fill="#2f3234"/>'
    random.seed(71)
    xs = [120, 300, 470, 640, 810, 980]
    for i, x in enumerate(xs):
        if heads_turned:
            b += figure(x, 1000, 1.25, eyes="stare", mouth="flat")
        else:
            b += figure(x, 1010, 1.25, eyes="closed", mouth="flat", tilt=random.choice([-14, -8, 8, 14]))
    # стоящие спереди
    random.seed(72)
    for x in (60, 1020):
        if heads_turned:
            b += figure(x, 1250, 2.4, eyes="stare")
        else:
            b += back_figure(x, 1250, 2.4)
    return b, d

def s10():
    b, d = wagon(False)
    save("10_vagon", svg(b, "<defs>"+d+"</defs>"))

def s10c():  # все повернулись
    b, d = wagon(True)
    b += '<rect width="1080" height="1920" fill="#000" opacity=".18"/>'
    save("10c_golovy", svg(b, "<defs>"+d+"</defs>"))

def phone_scene():
    b = f'<rect width="{W}" height="{H}" fill="#34383a"/>'
    b += '<rect x="0" y="0" width="1080" height="1920" fill="#2a2d2f"/>'
    b += '<circle cx="540" cy="900" r="520" fill="#f2c230" opacity=".06" filter="url(#blur60)"/>'
    b += '<path d="M220,1920 q-40,-400 80,-560 l140,-40 q60,10 40,80 l-40,140 q120,-30 180,20 l40,360z" fill="#b9bab1"/>'
    b += f'<path d="M180,1920 q-20,-300 60,-420 l90,40 q-40,140 -20,380z" fill="{YELLOW}"/>'
    b += '<rect x="270" y="420" width="540" height="1060" rx="64" fill="#15171a"/><rect x="294" y="450" width="492" height="1000" rx="46" fill="#232a33"/>'
    b += '<text x="540" y="640" text-anchor="middle" font-family="DejaVu Sans" font-size="120" fill="#e9edf2">21:47</text>'
    b += '<text x="540" y="700" text-anchor="middle" font-family="DejaVu Sans" font-size="30" fill="#aab3bd">пятница, 14 ноября</text>'
    # уведомление
    b += '<rect x="318" y="800" width="444" height="170" rx="30" fill="#e9ecef" opacity=".96"/>'
    b += '<circle cx="380" cy="860" r="34" fill="#e78b8b"/><text x="380" y="874" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#fff">М</text>'
    b += '<text x="432" y="852" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#1c1f26">Мама</text>'
    b += '<text x="700" y="852" text-anchor="end" font-family="DejaVu Sans" font-size="22" fill="#7a818a">сейчас</text>'
    b += '<text x="432" y="900" font-family="DejaVu Sans" font-size="30" fill="#1c1f26">Я тебя люблю</text>'
    b += '<path d="M720,890 c-12,-22 -42,-14 -36,8 c4,14 24,26 36,36 c12,-10 32,-22 36,-36 c6,-22 -24,-30 -36,-8z" fill="#e0443e"/>'
    return b

def s10a(): save("10a_telefon", svg(phone_scene()))

def s10b(smile):
    b = f'<rect width="{W}" height="{H}" fill="#3a3d3f"/>'
    b += '<rect x="0" y="300" width="1080" height="500" fill="#1d2022"/>'
    b += '<circle cx="540" cy="1300" r="460" fill="#f2c230" opacity=".05" filter="url(#blur60)"/>'
    random.seed(81)
    b += figure(540, 980, 5.0, hero=True, eyes="hero", mouth="smile" if smile else "flat", look=.2)
    # подсветка экрана снизу
    b += '<ellipse cx="540" cy="1500" rx="400" ry="200" fill="#cfe0ef" opacity=".08" filter="url(#blur30)"/>'
    return b

def s10b_flat(): save("10b_lico", svg(s10b(False)))
def s10b_smile(): save("10b_ulybka", svg(s10b(True)))

def s11():
    b = f'<rect width="{W}" height="{H}" fill="#121416"/>'
    b += fog(91, 8, 600, 1400, .12, "#6c7378")
    b += f'<g opacity=".18">{city_towers(1300, seed=1)}</g>'
    b += '<text x="540" y="880" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="150" fill="#e8e4d8" letter-spacing="6">ЖИВОЙ</text>'
    b += '<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="110" fill="#f2c230" letter-spacing="6">В МОСКВЕ</text>'
    b += '<rect x="390" y="1110" width="300" height="4" fill="#8a8f92"/>'
    b += '<text x="540" y="1200" text-anchor="middle" font-family="DejaVu Sans" font-size="48" fill="#a9aeb1" letter-spacing="14">СЕРИЯ 1</text>'
    save("11_zastavka", svg(b))

if __name__ == "__main__":
    for f in [s01, s02, s03, s04, s04b, s05, s06, s07, s07b, s08, s08b, s09, s10, s10a, s10b_flat, s10b_smile, s10c, s11]:
        f(); print("ok", f.__name__)
    subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "render.js"), OUT], check=True)
