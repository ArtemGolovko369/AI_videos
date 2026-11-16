"""Кадры серии 5 «Вера». Использует помощники серий 1–4.
Запуск: python3 s05/tools/draw.py → s05/frames/*.png
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
YELLOW, SCARF, COAT, HER_SKIN, GREEN = D.YELLOW, S2.SCARF, S2.COAT, S2.HER_SKIN, S4.GREEN
RED_MARK = "#c8463c"
WARM = "#d8bba2"            # кожа живых (на старых фото и во флешбэке)

def table_front():
    return '<rect x="0" y="1300" width="1080" height="70" fill="#c9b48a"/><rect x="0" y="1370" width="1080" height="550" fill="#4a4136"/>'

def kitchen_mama(mouth):
    b = S4.kitchen_bg(table=False)
    b += '<rect width="1080" height="1920" fill="#000" opacity=".12"/>'
    b += mama(540, 860, 2.9, eyes="hero", mouth=mouth, tears=False, look=-.3)
    b += table_front()
    b += '<rect x="140" y="1250" width="220" height="70" rx="6" fill="#6b7d6a"/><text x="250" y="1296" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#efe9d6">ПРАВИЛА</text>'
    b += '<rect x="780" y="1240" width="90" height="70" rx="8" fill="#e9e2c4"/>'
    return b

def s02(): save("02_mama", svg(kitchen_mama("flat"))); save("02b_mama_rot", svg(kitchen_mama("open")))

def s03_flashback():
    b = S3.kamorka_bg()
    random.seed(161)
    # шестеро живых за столом, смеются
    for k, x in enumerate((130, 300, 470, 640, 810)):
        b += figure(x, 1010, 1.25, col=random.choice(["#6b7da3", "#a35d4f", "#5d7a62", "#8a6fa3", "#c08a4a"]), skin=WARM, eyes="closed", mouth="smile")
    b += table_front().replace('y="1300"', 'y="1330"').replace('y="1370"', 'y="1400"')
    b += figure(980, 1050, 1.35, col="#55606e", skin=WARM, eyes="hero", mouth="open")
    # Вера в углу с блокнотом, смотрит
    b += her(180, 700, 1.0, eyes="hero", look=1, scarf=False)
    b += '<rect x="230" y="830" width="80" height="100" fill="#efe9d6" transform="rotate(-10 270 880)"/>'
    save("03_flashback", svg(b))

def wall_n(ncross):
    """Стена из серии 3, но с ncross крестиками."""
    b = f'<rect width="{W}" height="{H}" fill="#5c564d"/>'
    b += '<circle cx="540" cy="600" r="600" fill="#f2d78a" opacity=".1" filter="url(#blur60)"/>'
    random.seed(151)
    pos = [(230, 420), (540, 400), (850, 430), (230, 800), (540, 790), (850, 810), (380, 1190)]
    for k, (x, y) in enumerate(pos):
        rot = random.uniform(-6, 6)
        g = f'<g transform="rotate({rot:.1f} {x} {y})"><rect x="{x-120}" y="{y-150}" width="240" height="300" fill="#f1efe6"/>'
        g += f'<rect x="{x-100}" y="{y-130}" width="200" height="210" fill="#8c9496"/>'
        g += f'<clipPath id="ph{k}"><rect x="{x-100}" y="{y-130}" width="200" height="210"/></clipPath><g clip-path="url(#ph{k})">'
        if k == 6: g += her(x, y - 40, .95, eyes="hero", scarf=True)
        else: g += figure(x, y - 40, .95, col=random.choice(D.CLOTH), skin=WARM, eyes="hero", look=random.uniform(-1, 1))
        g += f'</g><rect x="{x-100}" y="{y+80}" width="200" height="60" fill="#f1efe6"/><circle cx="{x}" cy="{y-150}" r="10" fill="{RED_MARK}"/></g>'
        b += g
        if k < ncross:
            b += f'<path d="M{x-110},{y-120} L{x+110},{y+120} M{x+110},{y-120} L{x-110},{y+120}" stroke="{RED_MARK}" stroke-width="14" stroke-linecap="round" opacity=".9"/>'
    b += '<rect y="1500" width="1080" height="420" fill="#3f3a34"/>'
    return b

def s04():
    for n in (0, 2, 4, 6): save(f"04_stena{n}", svg(wall_n(n)))

def s05_foto():
    b = S4.kitchen_bg(table=False) + '<rect width="1080" height="1920" fill="#000" opacity=".35"/>'
    b += '<g transform="rotate(-4 540 900)"><rect x="170" y="440" width="740" height="860" fill="#f3efe2"/>'
    b += '<rect x="210" y="480" width="660" height="640" fill="#b7a98c"/>'
    b += '<clipPath id="ft"><rect x="210" y="480" width="660" height="640"/></clipPath><g clip-path="url(#ft)">'
    b += '<rect x="210" y="480" width="660" height="300" fill="#c9bb9c"/>'
    # мама (моложе, тёплая кожа) и Вера в красном шарфе, обе живые, улыбаются
    g = mama(380, 760, 1.9, eyes="hero", mouth="smile")
    g = g.replace(S4.MSKIN, WARM).replace(S4.MHAIR, "#6d5a4a")
    b += g
    v = her(700, 760, 1.9, eyes="hero", mouth="smile", scarf=True).replace(HER_SKIN, WARM)
    b += v + '</g>'
    b += '<text x="540" y="1220" text-anchor="middle" font-family="DejaVu Sans" font-style="oblique" font-size="44" fill="#4a4a4a">мы с Верой · 2023</text></g>'
    # мамина рука держит фото
    b += f'<path d="M0,1600 q200,-60 300,-280 l60,30 q-60,220 -200,360 h-160z" fill="{GREEN}"/>'
    b += f'<path d="M300,1320 q30,-60 90,-50 q30,30 0,60 q-50,30 -90,20z" fill="{S4.MSKIN}"/>'
    save("05_foto", svg(b))

def phone_vera(n):
    b = f'<rect width="{W}" height="{H}" fill="#3a332b"/>'
    b += '<rect y="0" width="1080" height="1920" fill="#c9b48a" opacity=".25"/>'  # стол сверху
    b += '<circle cx="540" cy="900" r="520" fill="#f3d27a" opacity=".1" filter="url(#blur60)"/>'
    b += '<rect x="270" y="380" width="540" height="1100" rx="64" fill="#15171a"/><rect x="294" y="410" width="492" height="1040" rx="46" fill="#232a33"/>'
    b += '<text x="540" y="560" text-anchor="middle" font-family="DejaVu Sans" font-size="110" fill="#e9edf2">23:12</text>'
    msgs = [("Ты где? Я волнуюсь", "23:12"), ("Вижу свет на девятом", "23:12")]
    for k in range(n):
        y = 640 + k*175; txt, tm = msgs[k]
        b += f'<rect x="318" y="{y}" width="444" height="155" rx="28" fill="#e9ecef" opacity=".96"/>'
        b += f'<circle cx="376" cy="{y+56}" r="30" fill="{SCARF}"/><text x="376" y="{y+68}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="30" fill="#fff">В</text>'
        b += f'<text x="422" y="{y+50}" font-family="DejaVu Sans" font-weight="bold" font-size="28" fill="#1c1f26">Вера</text>'
        b += f'<text x="740" y="{y+50}" text-anchor="end" font-family="DejaVu Sans" font-size="22" fill="#7a818a">{tm}</text>'
        b += f'<text x="422" y="{y+100}" font-family="DejaVu Sans" font-size="28" fill="#1c1f26">{txt}</text>'
    return b

def s07(): save("07_vera1", svg(phone_vera(1))); save("07_vera2", svg(phone_vera(2)))

def s08_switch():
    b = f'<rect width="{W}" height="{H}" fill="#7a705f"/>'
    for y in range(0, H, 60):
        for x in range(0, W, 60): b += f'<rect x="{x+2}" y="{y+2}" width="56" height="56" fill="#857a68"/>'
    b += '<circle cx="540" cy="700" r="600" fill="#f3d27a" opacity=".15" filter="url(#blur60)"/>'
    b += '<rect x="410" y="700" width="260" height="380" rx="24" fill="#efece4"/><rect x="480" y="780" width="120" height="220" rx="14" fill="#dedad0"/>'
    b += '<rect x="490" y="790" width="100" height="100" rx="10" fill="#f8f6f0"/>'
    b += f'<path d="M1080,1500 q-250,-60 -380,-330 l50,-40 q150,220 330,280z" fill="{GREEN}"/>'
    b += f'<path d="M700,1170 q-90,-60 -110,-200 q20,-30 50,0 l40,110 q20,60 60,60z" fill="{S4.MSKIN}"/>'
    save("08_switch", svg(b))

def s08_dark():
    b = S4.kitchen_bg(table=False)
    b += '<rect width="1080" height="1920" fill="#05070c" opacity=".88"/>'
    b += '<rect x="40" y="420" width="300" height="300" fill="#2c3a5a" opacity=".6"/>'  # окно светлее комнаты
    save("08b_temno", svg(b))

def s09_vniz():
    """Вид из окна вниз: ночной тротуар, головы сверху, одна смотрит вверх."""
    b = f'<rect width="{W}" height="{H}" fill="#2f343d"/>'
    b += '<rect x="0" y="0" width="1080" height="420" fill="#1d2129"/>'  # дорога
    for x in range(40, 1080, 240): b += f'<rect x="{x}" y="200" width="130" height="18" fill="#5a5f66"/>'
    b += '<rect x="0" y="420" width="1080" height="16" fill="#4a4f58"/>'  # бордюр
    for y in range(560, 1920, 160): b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#2a2e36" stroke-width="4"/>'
    b += '<circle cx="700" cy="1200" r="420" fill="#f2d78a" opacity=".2" filter="url(#blur60)"/>'
    random.seed(171)
    def top(x, y, s=1, col="#3d424c", hair="#3a3a3c"):
        return (f'<ellipse cx="{x}" cy="{y}" rx="{70*s}" ry="{38*s}" fill="{col}"/>'
                f'<circle cx="{x}" cy="{y-8*s}" r="{30*s}" fill="{hair}"/>')
    pts = []
    while len(pts) < 30:
        x = random.randint(70, 1010); y = random.randint(520, 1860)
        if abs(x - 700) < 190 and abs(y - 1220) < 190: continue
        if any(abs(x-a) < 130 and abs(y-c) < 90 for a, c in pts): continue
        pts.append((x, y))
    for x, y in pts:
        b += top(x, y, random.uniform(1.0, 1.3), random.choice(["#3d424c", "#454a55", "#4c4f57"]), random.choice(["#3a3a3c", "#57534d", "#77736c"]))
    # Вера: запрокинула голову, лицо вверх
    x, y, k = 700, 1220, 1.7
    b += f'<g transform="translate({x} {y}) scale({k}) translate({-x} {-y})">'
    b += f'<ellipse cx="{x}" cy="{y+24}" rx="82" ry="44" fill="{COAT}"/>'
    b += f'<ellipse cx="{x}" cy="{y+4}" rx="54" ry="30" fill="{SCARF}"/>'
    b += f'<circle cx="{x}" cy="{y-14}" r="38" fill="{HER_SKIN}"/>'
    b += f'<path d="M{x-40},{y-14} a40,40 0 0 0 80,0 q-10,30 -40,34 q-30,-4 -40,-34z" fill="#2a2628"/>'
    b += f'<circle cx="{x-13}" cy="{y-24}" r="6" fill="#eef0e8"/><circle cx="{x+13}" cy="{y-24}" r="6" fill="#eef0e8"/><circle cx="{x-13}" cy="{y-24}" r="2.6" fill="#222"/><circle cx="{x+13}" cy="{y-24}" r="2.6" fill="#222"/>'
    b += f'<path d="M{x-6},{y-6} h12" stroke="#5d625a" stroke-width="3" stroke-linecap="round"/></g>'
    b += f'<circle cx="{x}" cy="{y}" r="200" fill="{SCARF}" opacity=".07" filter="url(#blur30)"/>'
    # рама окна (взгляд из тёмной кухни)
    b += '<rect x="0" y="0" width="1080" height="1920" fill="none" stroke="#0b0d12" stroke-width="60"/>'
    b += '<rect x="520" y="0" width="30" height="460" fill="#0b0d12"/><rect x="0" y="440" width="1080" height="28" fill="#0b0d12"/>'
    b += '<rect width="1080" height="1920" fill="#0b0d14" opacity=".15"/>'
    save("09_vniz", svg(b))

def s10_ulybka():
    b = f'<rect width="{W}" height="{H}" fill="#151922"/>'
    b += '<circle cx="540" cy="200" r="520" fill="#f2d78a" opacity=".22" filter="url(#blur60)"/>'  # фонарь сверху
    b += f'<g opacity=".35">{D.panel_houses(700, seed=42, col="#2a2f3b", lit=.15)}</g>'.replace('#e8d79a', '#efcf7c').replace('#6e7378', '#1e222b')
    b += her(540, 920, 4.6, eyes="hero", mouth="none", look=0, scarf=True)
    # идеальная улыбка: ровная, симметричная, мягкая
    r = 62*4.6; my = 920 + r*.55
    b += f'<path d="M{540-r*.34},{my-r*.04} q{r*.34},{r*.26} {r*.68},0" stroke="#5d4a44" stroke-width="{r*.055:.1f}" stroke-linecap="round" fill="none"/>'
    b += f'<path d="M{540-r*.38},{my-r*.08} q{r*.03},{r*.04} {r*.06},{r*.06} M{540+r*.38},{my-r*.08} q{-r*.03},{r*.04} {-r*.06},{r*.06}" stroke="#7a6a64" stroke-width="{r*.03:.1f}" fill="none"/>'
    # тёплый блик в глазах (свет фонаря)
    b += '<rect width="1080" height="1920" fill="#000" opacity=".08"/>'
    save("10_ulybka", svg(b))

def s10_bez():
    b = f'<rect width="{W}" height="{H}" fill="#151922"/>'
    b += '<circle cx="540" cy="200" r="520" fill="#f2d78a" opacity=".22" filter="url(#blur60)"/>'
    b += f'<g opacity=".35">{D.panel_houses(700, seed=42, col="#2a2f3b", lit=.15)}</g>'.replace('#e8d79a', '#efcf7c').replace('#6e7378', '#1e222b')
    b += her(540, 920, 4.6, eyes="hero", mouth="flat", look=0, scarf=True)
    b += '<rect width="1080" height="1920" fill="#000" opacity=".08"/>'
    save("10_bez", svg(b))

def s11():
    b = f'<rect width="{W}" height="{H}" fill="#121416"/>'
    b += fog(91, 8, 600, 1400, .12, "#6c7378")
    b += f'<g opacity=".18">{D.city_towers(1300, seed=1)}</g>'
    b += '<text x="540" y="880" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="150" fill="#e8e4d8" letter-spacing="6">ЖИВОЙ</text>'
    b += '<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="110" fill="#f2c230" letter-spacing="6">В МОСКВЕ</text>'
    b += '<rect x="390" y="1110" width="300" height="4" fill="#8a8f92"/>'
    b += '<text x="540" y="1200" text-anchor="middle" font-family="DejaVu Sans" font-size="48" fill="#a9aeb1" letter-spacing="14">СЕРИЯ 5</text>'
    b += f'<rect x="420" y="1250" width="240" height="8" fill="{SCARF}"/>'
    save("11_zastavka", svg(b))

if __name__ == "__main__":
    for f in [s02, s03_flashback, s04, s05_foto, s07, s08_switch, s08_dark, s09_vniz, s10_bez, s10_ulybka, s11]:
        f(); print("ok", f.__name__)
    subprocess.run(["node", os.path.join(ROOT, "tools", "render.js"), D.OUT], check=True)
    for src, dst in [("s04/frames/12_stranica", "01_stranica"), ("s02/frames/05_steklo", "06a_steklo"),
                     ("s02/frames/08_chek", "06b_chek"), ("s03/frames/06d_bloknot", "06c_bloknot"),
                     ("s03/frames/08b_stena8", "06d_stena8")]:
        shutil.copy(os.path.join(ROOT, src + ".png"), os.path.join(D.OUT, dst + ".png"))
