"""Кадры серии 6 «Стук». Использует помощники серий 1–5.
Запуск: python3 s06/tools/draw.py → s06/frames/*.png
"""
import importlib.util, os, random, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
spec = importlib.util.spec_from_file_location("s4draw", os.path.join(ROOT, "s04", "tools", "draw.py"))
S4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(S4)
S3, S2, D = S4.S3, S4.S2, S4.D
D.OUT = os.path.join(HERE, "..", "frames"); os.makedirs(D.OUT, exist_ok=True)
W, H = D.W, D.H
svg, save, grad, head, body, figure, back_figure, fog = D.svg, D.save, D.grad, D.head, D.body, D.figure, D.back_figure, D.fog
her, mama = S2.her, S4.mama
YELLOW, SCARF, COAT, HER_SKIN, GREEN, HSKIN = D.YELLOW, S2.SCARF, S2.COAT, S2.HER_SKIN, S4.GREEN, D.HSKIN
RED_MARK = "#c8463c"

def fisheye(inner, extra=""):
    """Вид в дверной глазок: круг, всё вокруг чёрное."""
    d = '<clipPath id="eye"><circle cx="540" cy="900" r="430"/></clipPath>'
    b = f'<rect width="{W}" height="{H}" fill="#050608"/>'
    b += f'<g clip-path="url(#eye)"><g transform="translate(540 900) scale(1.15) translate(-540 -900)">{inner}</g>'
    b += '<circle cx="540" cy="900" r="430" fill="url(#lens)"/></g>'
    b += '<circle cx="540" cy="900" r="430" fill="none" stroke="#1a1c20" stroke-width="22"/>'
    lens = '<radialGradient id="lens" cx="50%" cy="50%" r="50%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".85"/></radialGradient>'
    return b, "<defs>" + d + lens + extra + "</defs>"

def landing(floor):
    b = f'<rect width="{W}" height="{H}" fill="#4a5a52"/><rect y="0" width="1080" height="700" fill="#5d6a64"/>'
    b += '<rect x="330" y="740" width="420" height="900" fill="#8a8f92"/><rect x="345" y="755" width="190" height="885" fill="#9ea3a6"/><rect x="545" y="755" width="190" height="885" fill="#9ea3a6"/>'
    b += '<rect x="460" y="580" width="160" height="110" rx="12" fill="#141618"/>'
    b += f'<text x="540" y="665" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="92" fill="#e8453c">{floor}</text>'
    b += '<rect y="1380" width="1080" height="540" fill="#3c3d3e"/>'
    b += '<rect x="80" y="240" width="60" height="60" rx="30" fill="#e9e2c4" opacity=".7"/><circle cx="110" cy="270" r="200" fill="#e9e2c4" opacity=".12" filter="url(#blur30)"/>'
    return b

def s01():
    for fl in (5, 6, 7, 8, 9):
        b, d = fisheye(landing(fl)); save(f"01_lift{fl}", svg(b, d))

def s02_dver():
    b = f'<rect width="{W}" height="{H}" fill="#14161a"/>'
    b += '<rect x="250" y="260" width="580" height="1400" fill="#2a2522"/><rect x="250" y="260" width="580" height="1400" fill="none" stroke="#3a3430" stroke-width="20"/>'
    b += '<rect x="250" y="1650" width="580" height="14" fill="#f3d27a"/><polygon points="250,1664 830,1664 1000,1920 80,1920" fill="#f3d27a" opacity=".12"/>'
    b += '<circle cx="540" cy="760" r="14" fill="#8a8170"/><circle cx="540" cy="760" r="6" fill="#f3d27a" opacity=".8"/>'  # глазок светится
    b += '<rect x="720" y="980" width="60" height="26" rx="8" fill="#8a8170"/><rect x="740" y="1040" width="20" height="40" fill="#5a5248"/>'
    b += '<rect x="230" y="900" width="40" height="300" fill="#3a3430"/>'  # цепочка
    save("02_dver", svg(b))

def s03_ruka():
    b = f'<rect width="{W}" height="{H}" fill="#14161a"/>'
    b += '<circle cx="540" cy="1000" r="500" fill="#3a4a6a" opacity=".15" filter="url(#blur60)"/>'
    b += f'<path d="M1080,760 L380,1000 q-60,40 -20,120 l60,90 L1080,1120z" fill="#8a7420"/>'  # жёлтый рукав в темноте
    b += f'<path d="M0,1500 q240,-120 420,-330 l90,70 q-130,250 -330,420 h-180z" fill="#3c5236"/>'  # мамин зелёный рукав
    b += f'<path d="M420,1170 q40,-70 120,-80 q60,0 70,50 q-20,30 -60,30 q30,40 0,70 q-40,30 -90,10z" fill="#7d7f78"/>'
    save("03_ruka", svg(b))

def s03_uho():
    b = f'<rect width="{W}" height="{H}" fill="#14161a"/>'
    b += '<rect x="0" y="0" width="420" height="1920" fill="#2a2522"/>'  # дверь слева
    b += '<rect x="0" y="1650" width="420" height="14" fill="#f3d27a" opacity=".6"/>'
    # голова героя в профиль, ухо к двери
    b += f'<path d="M420,1500 v-260 q160,-60 300,0 v260z" fill="#8a7420"/>'
    b += f'<ellipse cx="560" cy="980" rx="190" ry="220" fill="#7f8079"/>'
    b += '<path d="M380,940 a190,220 0 0 1 340,-120 q-60,-80 -170,-60 q-140,30 -170,180z" fill="#1c1b1d"/>'
    b += '<ellipse cx="455" cy="1000" rx="46" ry="70" fill="#8d8e86"/><path d="M445,965 q-20,35 0,70" stroke="#5f605a" stroke-width="8" fill="none"/>'
    b += '<ellipse cx="690" cy="980" rx="16" ry="12" fill="#e8e8e0"/><circle cx="694" cy="980" r="7" fill="#2a2420"/>'  # глаз
    b += '<rect width="1080" height="1920" fill="#000" opacity=".2"/>'
    save("03_uho", svg(b))

def s04_vera_glazok():
    inner = landing(9) + '<rect width="1080" height="1920" fill="#000" opacity=".15"/>'
    inner += her(540, 860, 5.6, eyes="hero", mouth="flat", look=0, scarf=True)
    b, d = fisheye(inner)
    save("04_vera_glazok", svg(b, d))

def s05_mama_temno():
    b = S4.kitchen_bg(table=False)
    b += mama(540, 860, 3.0, eyes="hero", mouth="flat", look=.6)
    # блокнот в её руках и жест к балкону
    b += f'<path d="M300,1500 q60,-180 220,-220 l20,70 q-120,40 -170,190z" fill="{GREEN}"/>'
    b += '<rect x="420" y="1240" width="240" height="170" rx="8" fill="#6b7d6a" transform="rotate(-8 540 1320)"/>'
    b += '<text x="540" y="1340" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#efe9d6" transform="rotate(-8 540 1320)">ПРАВИЛА</text>'
    b += '<rect width="1080" height="1920" fill="#050812" opacity=".72"/>'
    b += '<rect x="40" y="420" width="300" height="300" fill="#3c4c70" opacity=".5"/>'
    b += '<circle cx="190" cy="570" r="260" fill="#5a6c96" opacity=".12" filter="url(#blur60)"/>'
    save("05_mama_temno", svg(b))

def s06_luk():
    b = f'<rect width="{W}" height="{H}" fill="#1c2028"/>'
    b += '<rect x="80" y="200" width="920" height="1520" fill="#4a4d52"/>'  # пол балкона сверху
    for x in range(80, 1000, 115): b += f'<line x1="{x}" y1="200" x2="{x}" y2="1720" stroke="#3f4247" stroke-width="4"/>'
    b += '<rect x="80" y="200" width="920" height="1520" fill="none" stroke="#2a2d33" stroke-width="40"/>'
    # открытый люк, лестница вниз
    b += '<rect x="330" y="760" width="420" height="420" fill="#0d0f13"/>'
    for y in range(800, 1180, 70): b += f'<rect x="400" y="{y}" width="280" height="14" fill="#6a6e74"/>'
    b += '<rect x="390" y="770" width="14" height="410" fill="#6a6e74"/><rect x="676" y="770" width="14" height="410" fill="#6a6e74"/>'
    b += '<polygon points="330,760 750,760 820,520 400,520" fill="#5c6066"/><polygon points="330,760 400,520 410,520 345,760" fill="#2a2d33"/>'  # откинутая крышка
    b += '<text x="575" y="660" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="40" fill="#c8463c" transform="skewX(-12)">ЛЮК</text>'
    # рука в жёлтом рукаве держит край
    b += f'<path d="M1080,1500 q-200,-60 -300,-280 l50,-30 q110,190 250,240z" fill="{YELLOW}"/>'
    b += f'<circle cx="760" cy="1200" r="44" fill="{HSKIN}"/>'
    b += '<rect width="1080" height="1920" fill="#0a0d16" opacity=".35"/>'
    save("06_luk", svg(b))

def s06_spusk():
    """Фасад: три балкона друг над другом (8, 7, 6), герой на лестнице."""
    b = f'<rect width="{W}" height="{H}" fill="#2f3542"/>'
    for y in range(0, H, 60): b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#2a303c" stroke-width="3"/>'
    for k, (fl, y) in enumerate([(8, 160), (7, 800), (6, 1440)]):
        b += f'<rect x="200" y="{y}" width="680" height="420" fill="#1b1f27"/>'  # проём
        b += f'<rect x="160" y="{y+420}" width="760" height="40" fill="#5a5f68"/>'  # плита балкона
        b += f'<rect x="160" y="{y+260}" width="760" height="160" fill="#4a4f58"/>'  # ограждение
        b += f'<rect x="420" y="{y+420}" width="200" height="40" fill="#0d0f13"/>'  # люк в плите
        b += f'<text x="980" y="{y+300}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="90" fill="#c8463c" opacity=".85">{fl}</text>'
        for yy in range(y+460, y+800, 60): b += f'<rect x="450" y="{yy}" width="140" height="10" fill="#6a6e74"/>'
        b += f'<rect x="440" y="{y+460}" width="10" height="340" fill="#6a6e74"/><rect x="590" y="{y+460}" width="10" height="340" fill="#6a6e74"/>'
    # герой на лестнице между 7 и 6
    x, y = 520, 1300
    b += body(x, y + 70*1.1, 1.1, YELLOW) + f'<circle cx="{x}" cy="{y}" r="{62*1.1}" fill="#2b2a2d"/>'
    b += '<rect width="1080" height="1920" fill="#0a0d16" opacity=".25"/>'
    save("06_spusk", svg(b))

def s07_pyatyy():
    b = f'<rect width="{W}" height="{H}" fill="#14171e"/>'
    b += '<rect x="120" y="240" width="840" height="1200" fill="#0c0e12"/>'  # тёмная комната за дверью
    b += '<rect x="120" y="240" width="840" height="1200" fill="none" stroke="#4a4f58" stroke-width="24"/>'
    # телевизор с отражениями
    b += '<rect x="330" y="420" width="420" height="260" rx="10" fill="#050608" stroke="#2a2d33" stroke-width="12"/>'
    for x in (430, 540, 650):
        b += f'<circle cx="{x}" cy="560" r="34" fill="#1d2129"/><ellipse cx="{x-10}" cy="555" rx="7" ry="5" fill="#5a5f66"/><ellipse cx="{x+10}" cy="555" rx="7" ry="5" fill="#5a5f66"/>'
    # семья на диване спиной
    random.seed(181)
    b += '<rect x="230" y="1020" width="620" height="200" rx="30" fill="#2a2d33"/>'
    for x in (340, 540, 740):
        b += back_figure(x, 940, 1.05, col=random.choice(["#2f343d", "#383c44", "#33302e"]))
    b += '<rect x="120" y="240" width="840" height="1200" fill="#05070c" opacity=".45"/>'
    b += '<rect y="1440" width="1080" height="480" fill="#3a3e46"/><rect y="1440" width="1080" height="160" fill="#4a4f58"/>'  # ограждение балкона
    b += '<circle cx="540" cy="550" r="300" fill="#3a4a6a" opacity=".08" filter="url(#blur60)"/>'
    save("07_pyatyy", svg(b))

def capture(fn):
    out = {}
    def cap(name, s): out["s"] = s
    old = S4.save; S4.save = cap
    try: fn()
    finally: S4.save = old
    return out["s"]

def s08_zemlya():
    s = capture(S4.s06_ulica)
    hero = body(540, 1420 + 70*1.5, 1.5, YELLOW) + f'<circle cx="540" cy="1420" r="{62*1.5}" fill="#2b2a2d"/>'
    s = s.replace('<rect width="1080" height="1920" fill="#0b0d14" opacity=".2"/>', hero + '<rect width="1080" height="1920" fill="#0b0d14" opacity=".2"/>', 1)
    save("08_zemlya", s)

def s09_dom():
    b, (x, y) = S4.mamin_dom()
    defs = "<defs>" + S4.night_sky() + "</defs>"
    fh = (1450 - 260 - 40)/12
    save("09a_dom_temno", svg(b.replace('fill="#f3d27a" opacity=".2"', 'fill="#f3d27a" opacity="0"').replace('#f3d27a', '#20242d'), defs))
    save("09b_dom_svet", svg(b, defs))

def okno_dvoe(pose):
    """Светлое окно, мама и Вера рядом; pose: 0 — руки внизу, 1/2 — взмах влево/вправо."""
    b = f'<rect width="{W}" height="{H}" fill="#2a2f3b"/>'
    for y in range(0, H, 220): b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#232733" stroke-width="6"/>'
    b += '<rect x="140" y="420" width="800" height="1000" fill="#f0cf7a"/>'
    def sil_mama(x):
        s = f'<path d="M{x-110},1420 v-230 q0,-90 110,-100 q110,10 110,100 v230z" fill="#2b2a2c"/>'
        s += f'<circle cx="{x}" cy="1010" r="78" fill="#2b2a2c"/><path d="M{x-84},1000 q0,-100 84,-100 q84,0 84,100 q-40,-40 -84,-40 q-44,0 -84,40z" fill="#2b2a2c"/>'
        return s
    def sil_vera(x):
        s = f'<path d="M{x-100},1420 v-240 q0,-90 100,-100 q100,10 100,100 v240z" fill="#2b2a2c"/>'
        s += f'<circle cx="{x}" cy="1000" r="74" fill="#2b2a2c"/><path d="M{x-86},990 v90 h40 v-60z M{x+86},990 v90 h-40 v-60z" fill="#2b2a2c"/>'
        s += f'<path d="M{x-80},1080 q80,40 160,0 v30 q-80,40 -160,0z" fill="{SCARF}"/>'
        return s
    def arm(x, side):
        if pose == 0: return ''
        ang = 12 if pose == 1 else 38
        return (f'<g transform="rotate({ang} {x+side*90} 1120)"><path d="M{x+side*90},1120 v-200" stroke="#2b2a2c" stroke-width="44" stroke-linecap="round"/>'
                f'<circle cx="{x+side*90}" cy="905" r="30" fill="#2b2a2c"/></g>')
    b += sil_mama(380) + arm(380, 1) + sil_vera(700) + arm(700, 1)
    b += '<rect x="140" y="420" width="800" height="1000" fill="none" stroke="#e8e4da" stroke-width="28"/><rect x="526" y="420" width="28" height="1000" fill="#e8e4da" opacity=".95"/>'
    b += '<rect x="140" y="1420" width="800" height="40" fill="#c9a35a"/>'
    b += '<rect y="1500" width="1080" height="420" fill="#20242d"/>'
    return b

def s10():
    for p in (0, 1, 2): save(f"10_okno{p}", svg(okno_dvoe(p)))

def s11():
    b = f'<rect width="{W}" height="{H}" fill="#121416"/>'
    b += fog(91, 8, 600, 1400, .12, "#6c7378")
    b += f'<g opacity=".18">{D.city_towers(1300, seed=1)}</g>'
    b += '<text x="540" y="880" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="150" fill="#e8e4d8" letter-spacing="6">ЖИВОЙ</text>'
    b += '<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="110" fill="#f2c230" letter-spacing="6">В МОСКВЕ</text>'
    b += '<rect x="390" y="1110" width="300" height="4" fill="#8a8f92"/>'
    b += '<text x="540" y="1200" text-anchor="middle" font-family="DejaVu Sans" font-size="48" fill="#a9aeb1" letter-spacing="14">СЕРИЯ 6</text>'
    b += f'<rect x="420" y="1250" width="110" height="8" fill="{GREEN}"/><rect x="550" y="1250" width="110" height="8" fill="{SCARF}"/>'
    save("11_zastavka", svg(b))

if __name__ == "__main__":
    for f in [s01, s02_dver, s03_ruka, s03_uho, s04_vera_glazok, s05_mama_temno, s06_luk, s06_spusk, s07_pyatyy,
              s08_zemlya, s09_dom, s10, s11]:
        f(); print("ok", f.__name__)
    subprocess.run(["node", os.path.join(ROOT, "tools", "render.js"), D.OUT], check=True)
    shutil.copy(os.path.join(ROOT, "s02", "frames", "08_chek.png"), os.path.join(D.OUT, "04b_chek.png"))
