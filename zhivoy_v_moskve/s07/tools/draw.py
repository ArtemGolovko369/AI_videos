"""Кадры серии 7 (финал) «Живые». Использует помощники серий 1–4.
Запуск: python3 s07/tools/draw.py → s07/frames/*.png
"""
import importlib.util, os, random, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
spec = importlib.util.spec_from_file_location("s4draw", os.path.join(ROOT, "s04", "tools", "draw.py"))
S4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(S4)
S3, S2, D = S4.S3, S4.S2, S4.D
OUT = os.path.join(HERE, "..", "frames"); os.makedirs(OUT, exist_ok=True)
D.OUT = OUT
W, H = D.W, D.H
svg, save, grad, head, body, figure, back_figure, fog = D.svg, D.save, D.grad, D.head, D.body, D.figure, D.back_figure, D.fog
her, mama, crooked_smile = S2.her, S4.mama, S2.crooked_smile
YELLOW, SCARF, GREEN, HSKIN = D.YELLOW, S2.SCARF, S4.GREEN, D.HSKIN
RED_MARK = "#c8463c"
WARM = "#d8bba2"
BRIGHT = ["#e0b13a", "#c8463c", "#4f7fc0", "#5fa05a", "#9a5fb0", "#e07a3a", "#3aa0a0"]

def capture(mod, fn):
    """Вызвать функцию кадра из другой серии и забрать SVG-строку вместо сохранения."""
    out = {}
    old = mod.save; mod.save = lambda name, s: out.__setitem__("s", s)
    try: fn()
    finally: mod.save = old
    return out["s"]

def hero_head_smile(x, y, r):
    """Открытая широкая улыбка героя (поверх лица без рта)."""
    my = y + r*.5
    s = f'<path d="M{x-r*.42},{my-r*.06} q{r*.42},{r*.5} {r*.84},0 q{-r*.42},{r*.16} {-r*.84},0z" fill="#5a3a36"/>'
    s += f'<path d="M{x-r*.36},{my-r*.02} q{r*.36},{r*.12} {r*.72},0 v{r*.07} q{-r*.36},{r*.08} {-r*.72},0z" fill="#f2efe6"/>'
    s += f'<path d="M{x-r*.48},{my-r*.12} q{r*.06},{r*.02} {r*.08},{r*.08} M{x+r*.48},{my-r*.12} q{-r*.06},{r*.02} {-r*.08},{r*.08}" stroke="#6d5a54" stroke-width="{r*.03:.1f}" fill="none"/>'
    return s

# ---------------------------------------------------------------- 1–4: рассвет, телефон, блокнот
def s01_rassvet():
    d = grad("dawn", "#b9a7b0", "#e6cfc0")
    b = f'<rect width="{W}" height="{H}" fill="url(#dawn)"/>'
    b += '<circle cx="820" cy="980" r="120" fill="#f6dcc0" opacity=".7" filter="url(#blur30)"/>'
    b += D.panel_houses(1150, seed=7, col="#8f8f98", lit=.04)
    b += fog(4, 6, 900, 1250, .35, "#e9dcd6")
    b += f'<rect y="1150" width="{W}" height="770" fill="#7c7f80"/>'
    b += '<rect x="200" y="1390" width="680" height="34" fill="#7b5a43"/><rect x="200" y="1300" width="680" height="24" fill="#7b5a43"/>'
    b += '<rect x="230" y="1424" width="20" height="110" fill="#5a4031"/><rect x="830" y="1424" width="20" height="110" fill="#5a4031"/>'
    b += '<rect x="200" y="1386" width="680" height="8" fill="#eef2f4" opacity=".8"/>'  # иней
    random.seed(201)
    b += figure(540, 1080, 1.8, hero=True, eyes="hero", mouth="flat", look=.4)
    b += '<rect x="610" y="1330" width="60" height="100" rx="10" fill="#15171a"/><rect x="616" y="1338" width="48" height="84" rx="6" fill="#9fc6e8" opacity=".7"/>'
    b += '<circle cx="640" cy="1380" r="80" fill="#bfe3f2" opacity=".15" filter="url(#blur30)"/>'
    save("01_rassvet", svg(b, "<defs>" + d + "</defs>"))

def phone_base(screen_on=True):
    b = f'<rect width="{W}" height="{H}" fill="#9a8f92"/>'
    b += '<rect width="1080" height="1920" fill="#e6cfc0" opacity=".25"/>'
    b += '<path d="M220,1920 q-40,-400 80,-560 l140,-40 q60,10 40,80 l-40,140 q120,-30 180,20 l40,360z" fill="#b9bab1"/>'
    b += f'<path d="M180,1920 q-20,-300 60,-420 l90,40 q-40,140 -20,380z" fill="{YELLOW}"/>'
    b += '<rect x="270" y="380" width="540" height="1100" rx="64" fill="#15171a"/>'
    b += f'<rect x="294" y="410" width="492" height="1040" rx="46" fill="{"#232a33" if screen_on else "#07080a"}"/>'
    return b

def s02_tel():
    b = phone_base()
    b += '<text x="540" y="560" text-anchor="middle" font-family="DejaVu Sans" font-size="110" fill="#e9edf2">7:52</text>'
    b += '<rect x="660" y="440" width="70" height="30" rx="6" fill="none" stroke="#e9edf2" stroke-width="4"/><rect x="664" y="444" width="5" height="22" fill="#e0443e"/>'
    b += '<text x="645" y="465" text-anchor="end" font-family="DejaVu Sans" font-size="24" fill="#e0443e">3%</text>'
    y = 660
    b += f'<rect x="318" y="{y}" width="444" height="155" rx="28" fill="#e9ecef" opacity=".96"/>'
    b += f'<circle cx="376" cy="{y+56}" r="30" fill="#e78b8b"/><text x="376" y="{y+68}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#fff">М</text>'
    b += f'<text x="422" y="{y+50}" font-family="DejaVu Sans" font-weight="bold" font-size="28" fill="#1c1f26">Мама</text>'
    b += f'<text x="422" y="{y+100}" font-family="DejaVu Sans" font-size="27" fill="#1c1f26">Приходи домой. Мы ждём</text>'
    b += f'<path d="M720,{y+120} c-10,-18 -36,-12 -30,7 c3,12 20,22 30,30 c10,-8 27,-18 30,-30 c6,-19 -20,-25 -30,-7z" fill="#e0443e"/>'
    save("02_tel", svg(b))

def s03_ekran():
    b = phone_base(screen_on=False)
    b += '<clipPath id="scr"><rect x="294" y="410" width="492" height="1040" rx="46"/></clipPath>'
    random.seed(203)
    b += f'<g clip-path="url(#scr)" opacity=".22">{figure(540, 880, 3.0, hero=True, eyes="hero", mouth="flat")}</g>'
    b += '<polygon points="294,410 420,410 294,700" fill="#fff" opacity=".05"/>'
    save("03_ekran", svg(b))

def s04_pravilo7():
    b = f'<rect width="{W}" height="{H}" fill="#7c7f80"/>'
    b += '<g transform="rotate(-3 540 920)"><rect x="130" y="300" width="820" height="1240" rx="14" fill="#efe9d6"/>'
    for y in range(470, 1520, 80): b += f'<line x1="150" y1="{y}" x2="930" y2="{y}" stroke="#bcc8d6" stroke-width="3"/>'
    b += '<line x1="240" y1="300" x2="240" y2="1540" stroke="#e0a3a0" stroke-width="4"/>'
    old = ["5. НЕ ХОДИ К ТЕМ, КОГО ЛЮБИШЬ", "6. НОЧЬЮ НЕ ВКЛЮЧАЙ СВЕТ"]
    for k, t in enumerate(old):
        b += f'<text x="260" y="{460 + k*80}" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="30" fill="#3c5a3a" opacity=".55">{t}</text>'
    for k, t in enumerate(["7. НЕ ЗНАЕШЬ,", "ЧТО ДЕЛАТЬ —", "ДЕЛАЙ КАК ВСЕ."]):
        b += f'<text x="{260 if k == 0 else 310}" y="{820 + k*130}" font-family="DejaVu Sans" font-weight="bold" font-style="oblique" font-size="64" fill="#2f5a2c">{t}</text>'
    b += '</g>'
    b += f'<path d="M0,1700 q200,-80 320,-260 l60,30 q-80,200 -220,330 h-160z" fill="{YELLOW}"/><circle cx="340" cy="1450" r="48" fill="{HSKIN}"/>'
    save("04_pravilo7", svg(b))

# ---------------------------------------------------------------- 5–9: метро, офис, копия
def s05_metro():
    s = capture(D, D.s05)
    hero = body(560, 1640 + 70*1.3, 1.3, YELLOW) + f'<circle cx="560" cy="1640" r="{62*1.3}" fill="#2b2a2d"/>'
    s = s.replace(f'<rect width="{W}" height="{H}" filter="url(#grain)"', hero + f'<rect width="{W}" height="{H}" filter="url(#grain)"', 1)
    save("05_metro", s)

def s06_ofis():
    b = D.office(False)
    # копия за «твоим» столом (третий от левого края): жёлтая спина
    b += body(670, 1080 + 70*.8, .8, YELLOW) + f'<circle cx="670" cy="1080" r="{62*.8}" fill="#2b2a2d"/>'
    save("06_ofis", svg(b))

def kopiya(x, y, s):
    g = figure(x, y, s, col=YELLOW, skin="#a9aea4", eyes="stare", mouth="none")
    g = g.replace('fill="#a9aea4"/>', 'fill="#a9aea4"/>', 1)
    g += f'<path d="M{x-50*s},{y+70*s} q{50*s},{50*s} {100*s},0" stroke="#d9a51e" stroke-width="{12*s}" fill="none"/>'
    g += crooked_smile(x, y, 62*s)
    return g

def s07_kopiya():
    b = D.office(False).split('<rect y="1240"')[0]
    b += '<rect y="1240" width="1080" height="680" fill="#8e918d"/>'
    random.seed(207)
    b += kopiya(500, 980, 3.6)
    b += figure(980, 900, 2.8, col="#30343c", eyes="empty", mouth="open", tilt=-10)  # начальник склонился
    b += '<rect width="1080" height="1920" fill="#000" opacity=".08"/>'
    save("07_kopiya", svg(b))

def office_front(state):
    """Офис лицом к нам: ряды столов. state: back | turned | smile1 | smile2"""
    b = f'<rect width="{W}" height="{H}" fill="#a9aca8"/>'
    b += '<rect y="0" width="1080" height="160" fill="#c6c8c3"/>'
    for x in range(60, 1080, 250): b += f'<rect x="{x}" y="60" width="180" height="24" fill="#f2f4ee"/>'
    random.seed(211)
    rows = [(760, .9, (140, 400, 680, 940)), (1080, 1.2, (180, 540, 900)), (1460, 1.7, (150, 930))]
    smile_set = {"smile1": {(0, 3), (2, 0)}, "smile2": "all"}.get(state, set())
    k = 0
    for ri, (y, s, xs) in enumerate(rows):
        for ci, x in enumerate(xs):
            col = random.choice(D.CLOTH); skin = random.choice(D.ZSKIN)
            sm = smile_set == "all" or (ri, ci) in smile_set
            if state == "back":
                b += f'<rect x="{x-80*s}" y="{y-150*s}" width="{160*s}" height="{110*s}" rx="6" fill="#2e3236"/>'
                b += back_figure(x, y, s, col=col)
            elif sm:
                if state == "smile2": col = BRIGHT[k % len(BRIGHT)]; skin = WARM
                b += figure(x, y, s, col=col, skin=skin, eyes="hero", mouth="smile", look=random.uniform(-.5, .5))
            else:
                b += figure(x, y, s, col=col, skin=skin, eyes="stare", mouth="flat")
            # столы перед ними
            b += f'<rect x="{x-150*s}" y="{y+150*s}" width="{300*s}" height="{24*s}" fill="#6e6a62"/>'
            k += 1
    # копия стоит в проходе
    if state != "back":
        b += kopiya(540, 1430, 1.5)
    if state == "smile2":
        b += '<rect width="1080" height="1920" fill="#f2d78a" opacity=".08"/>'
    return b

def s08(): save("08a_ofis_spinoy", svg(office_front("back"))); save("08b_ofis_golovy", svg(office_front("turned")))

def s09_uho():
    b = f'<rect width="{W}" height="{H}" fill="#9a9d99"/>'
    b += f'<g opacity=".5" filter="url(#blur6)">{office_front("turned")}</g>'
    random.seed(209)
    b += kopiya(620, 820, 6.2)
    b += '<rect width="1080" height="1920" fill="#000" opacity=".12"/>'
    save("09_uho", svg(b))

# ---------------------------------------------------------------- 10–13: вдох, улыбка, живые
def hero_close(state):
    b = f'<rect width="{W}" height="{H}" fill="#a3a6a2"/>'
    b += f'<g opacity=".45" filter="url(#blur6)">{office_front("turned")}</g>'
    random.seed(81)
    if state == "vdoh":
        b += figure(540, 980, 5.0, hero=True, eyes="closed", mouth="flat")
    else:
        b += figure(540, 980, 5.0, hero=True, eyes="hero", mouth="none", look=0)
        b += hero_head_smile(540, 980, 62*5.0)
        b += '<circle cx="540" cy="980" r="520" fill="#f2c230" opacity=".08" filter="url(#blur60)"/>'
    return b

def s10(): save("10a_vdoh", svg(hero_close("vdoh"))); save("10b_ulybka", svg(hero_close("smile")))

def ugol(smile):
    b = f'<rect width="{W}" height="{H}" fill="#a9aca8"/>'
    b += '<rect x="0" y="0" width="1080" height="700" fill="#b6b8b3"/><rect x="700" y="200" width="300" height="380" fill="#c9d0d4" stroke="#8d9192" stroke-width="10"/>'
    b += '<rect x="80" y="1250" width="920" height="40" fill="#6e6a62"/>'
    b += '<rect x="560" y="900" width="380" height="300" rx="10" fill="#2e3236"/><rect x="580" y="920" width="340" height="250" fill="#9fb3bd" opacity=".85"/>'
    b += her(330, 900, 2.8, eyes="hero", mouth="smile" if smile else "flat", look=1, scarf=False).replace(S2.COAT, "#7d8a9c")
    if smile: b += '<circle cx="330" cy="900" r="300" fill="#f2d78a" opacity=".1" filter="url(#blur60)"/>'
    return b

def s11(): save("11a_ugol", svg(ugol(False))); save("11b_ugol_ulybka", svg(ugol(True)))

def s12(): save("12a_ulybki", svg(office_front("smile1"))); save("12b_ulybki_vse", svg(office_front("smile2")))

def s13_pyatyatsya():
    b = f'<rect width="{W}" height="{H}" fill="#b0b2ad"/>'
    b += '<rect width="1080" height="1920" fill="#f2d78a" opacity=".08"/>'
    random.seed(213)
    # живые по краям, тёплые
    for k, (x, y, s) in enumerate([(90, 900, 1.6), (990, 920, 1.6), (120, 1450, 2.2), (960, 1470, 2.2)]):
        b += figure(x, y, s, col=BRIGHT[k], skin=WARM, eyes="hero", mouth="smile", look=(1 if x < 540 else -1))
    # копия и начальник в центре, пятятся, глаза мечутся
    b += figure(680, 820, 1.9, col="#30343c", eyes="stare", mouth="open", tilt=8)
    b += kopiya(430, 900, 2.0)
    save("13_pyatyatsya", svg(b))

# ---------------------------------------------------------------- 14–16: город, мама, конец
def city_top(ncolor):
    s = capture(D, D.s02)
    random.seed(301)
    dots = ''
    for _ in range(ncolor):
        x = random.uniform(0, W); y = random.uniform(0, H)
        # на улицах: вдоль сетки кварталов
        if random.random() < .5: x = -40 + 260*random.randint(0, 4) + random.uniform(0, 30)
        else: y = -40 + 300*random.randint(0, 6) + random.uniform(0, 30)
        c = random.choice(BRIGHT)
        dots += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="10" fill="{c}"/>'
    glow = '<circle cx="534" cy="1166" r="26" fill="#f2c230" opacity=".35" filter="url(#glow)"/>'
    s = s.replace(glow, dots + glow, 1)
    if ncolor > 300:
        s = s.replace(f'<rect width="{W}" height="{H}" filter="url(#grain)"', f'<rect width="{W}" height="{H}" fill="#f2d78a" opacity=".1"/><rect width="{W}" height="{H}" filter="url(#grain)"', 1)
    return s

def s14():
    for n, k in [(0, "a"), (90, "b"), (900, "c")]: save(f"14{k}_gorod", city_top(n))

def s15_mama():
    d = grad("morn", "#c9d3dc", "#f0e2cc")
    b = f'<rect width="{W}" height="{H}" fill="url(#morn)"/>'
    b += D.panel_houses(1050, seed=31, col="#a9adb2", lit=0)
    b += f'<rect y="1050" width="{W}" height="870" fill="#8a8d90"/>'
    b += '<rect x="120" y="640" width="840" height="460" fill="#6a707c"/><rect x="160" y="760" width="760" height="340" fill="#e8dcae" opacity=".85"/>'
    b += '<rect x="120" y="610" width="840" height="70" fill="#4a505c"/>'
    b += '<text x="540" y="662" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="48" fill="#eef1f4" letter-spacing="10">МЕТРО</text>'
    random.seed(215)
    for k, (x, y, s) in enumerate([(110, 1180, 1.2), (980, 1170, 1.2), (260, 1260, 1.35), (840, 1250, 1.35)]):
        b += figure(x, y, s, col=BRIGHT[(k+2) % len(BRIGHT)], skin=WARM, eyes="hero", mouth="smile", look=(1 if x < 540 else -1))
    g = mama(540, 1120, 2.6, eyes="hero", mouth="smile", tears=False)
    b += g.replace(S4.MSKIN, WARM)
    # красный шарф в руке
    b += f'<path d="M660,1500 q60,-20 90,40 q20,120 -10,260 h-50 q20,-130 0,-240 q-10,-40 -30,-60z" fill="{SCARF}"/>'
    b += f'<circle cx="680" cy="1500" r="36" fill="{WARM}"/>'
    b += '<circle cx="540" cy="1100" r="520" fill="#f6dca8" opacity=".14" filter="url(#blur60)"/>'
    save("15_mama", svg(b, "<defs>" + d + "</defs>"))

def s16_konec():
    b = f'<rect width="{W}" height="{H}" fill="#141618"/>'
    b += fog(91, 8, 600, 1400, .12, "#6c7378")
    b += f'<g opacity=".2">{D.city_towers(1300, seed=1, light=True)}</g>'
    b += '<text x="540" y="880" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="150" fill="#e8e4d8" letter-spacing="6">ЖИВОЙ</text>'
    b += '<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="110" fill="#f2c230" letter-spacing="6">В МОСКВЕ</text>'
    b += '<rect x="390" y="1110" width="300" height="4" fill="#8a8f92"/>'
    b += '<text x="540" y="1210" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="64" fill="#e8e4d8" letter-spacing="16">КОНЕЦ</text>'
    for k, c in enumerate([YELLOW, GREEN, SCARF]):
        b += f'<rect x="{390 + k*105}" y="1260" width="90" height="8" fill="{c}"/>'
    save("16_konec", svg(b))

if __name__ == "__main__":
    for f in [s01_rassvet, s02_tel, s03_ekran, s04_pravilo7, s05_metro, s06_ofis, s07_kopiya, s08, s09_uho,
              s10, s11, s12, s13_pyatyatsya, s14, s15_mama, s16_konec]:
        f(); print("ok", f.__name__)
    subprocess.run(["node", os.path.join(ROOT, "tools", "render.js"), OUT], check=True)
