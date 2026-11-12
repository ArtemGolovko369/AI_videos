"""Сборка ролика «Что если… исчезнут растения».

Нужны: frames/*.png (tools/variants.py), audio/voice.mp3, audio/words.json (tools/align.py).
Запуск:  python3 tools/render.py            — полный рендер в out/rasteniya.mp4
         python3 tools/render.py --still 36.5 60 152   — отдельные кадры в out/still_*.png
"""
import json, math, os, random, subprocess, sys, re
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
FR, OUT = os.path.join(ROOT, "frames"), os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
J = json.load(open(os.path.join(ROOT, "audio/words.json")))
WORDS = J["words"]; VOICE = J["duration"]
OUTRO = 5.0
END = VOICE + 0.6 + OUTRO

def clean(w): return re.sub(r"[^\wё-]", "", w.lower())
def at(prefix, after=0.0, end=False):
    for w in WORDS:
        if w["t0"] >= after - 1e-6 and clean(w["w"]).startswith(prefix):
            return w["t1"] if end else w["t0"]
    raise KeyError(prefix)

def ease(p): p = min(1, max(0, p)); return p * p * (3 - 2 * p)
def eob(p):  # ease-out-back
    p = min(1, max(0, p)); c = 1.7; return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2

# ---------------------------------------------------------------- timeline
A = {}  # anchors
A["propal"] = at("пропал"); A["novosti"] = at("днём"); A["uchenye1"] = at("учёные")
A["d3"] = at("день", 17); A["veter"] = at("ветер"); A["d5"] = at("день", 28); A["tri4"] = at("три", 35)
A["d7"] = at("день", 42); A["18"] = at("больше", 50); A["livnya"] = at("ливня"); A["d9"] = at("день", 58)
A["pshen"] = at("пшеница"); A["ris"] = at("рис"); A["kuk"] = at("кукуруза"); A["vsego3"] = at("всего")
A["okaz"] = at("оказалось"); A["korovy"] = at("коровы"); A["d12"] = at("день", 84); A["sux"] = at("в", 90)
A["co2"] = at("растения", 98); A["vse"] = at("все", 109); A["ktomu"] = at("к", 116); A["zadoh"] = at("задохнуться", 122)
A["apteka"] = at("в", 126.5); A["zapr"] = at("а", 131); A["grib"] = at("сначала"); A["pir"] = at("но", 145)
A["d20"] = at("день", 148); A["propala"] = at("пропала", 150); A["mir"] = at("мир", 153); A["vecher"] = at("вечером")
A["polil"] = at("полил"); A["utrom"] = at("а", 158); A["rostok"] = at("росток"); A["odno"] = at("одно", 162)
A["shtory"] = at("я", 168); A["shtory_end"] = at("шторы", 168, end=True)
OUT_T = VOICE + 0.6

# shot: img, t0, cam (z0, z1, (cx0,cy0), (cx1,cy1)), swaps [(t, img, dur, mode)], fx
SHOTS = [
    dict(img="A__01_kaktus", t0=0.0, cam=(1.12, 1.24, (540, 1000), (540, 1050)), swaps=[(A["propal"] + 0.15, "01_kaktus", 0.9, "fade")], fx=["sparkle_out"]),
    dict(img="01_kaktus", t0=A["propal"] + 3.4, cam=(1.25, 1.42, (540, 1060), (540, 1100))),
    dict(img="02_novosti", t0=A["novosti"], cam=(1.0, 1.12, (540, 960), (540, 900))),
    dict(img="02_novosti", t0=A["uchenye1"], cam=(1.35, 1.45, (540, 1060), (540, 1100))),
    dict(img="03_trava", t0=A["d3"], cam=(1.18, 1.1, (430, 980), (650, 980)), fx=["dust"]),
    dict(img="03_trava", t0=A["veter"] - 1.3, cam=(1.0, 1.06, (540, 960), (540, 900)), fx=["dust", "dust_storm"]),
    dict(img="04_cvety", t0=A["d5"], cam=(1.0, 1.15, (540, 960), (560, 980))),
    dict(img="04_cvety", t0=A["tri4"], cam=(1.55, 1.7, (600, 940), (590, 940))),
    dict(img="05_derevya", t0=A["d7"], cam=(1.12, 1.02, (540, 1100), (540, 960)), fx=["haze"]),
    dict(img="05_derevya", t0=A["18"] - 3.2, cam=(1.3, 1.4, (540, 1250), (540, 1300)), fx=["haze", "rain"]),
    dict(img="06_zerno", t0=A["d9"], cam=(1.3, 1.3, (540, 740), (540, 1080)), fx=["bump3"]),
    dict(img="06_zerno", t0=A["vsego3"], cam=(1.05, 1.15, (540, 1100), (540, 1300))),
    dict(img="07_korova", t0=A["okaz"], cam=(1.0, 1.1, (540, 1000), (560, 1150)), suby=720),
    dict(img="07_korova", t0=A["korovy"], cam=(1.35, 1.5, (640, 1300), (650, 1320)), suby=700),
    dict(img="08_lesa", t0=A["d12"], cam=(1.0, 1.12, (540, 960), (540, 960)), fx=["greenfade_lesa"]),
    dict(img="08_lesa", t0=A["sux"], cam=(1.25, 1.35, (520, 880), (520, 860)), fx=["greenfade_lesa"]),
    dict(img="09_zhara", t0=A["co2"], cam=(1.0, 1.15, (540, 960), (640, 1150)), fx=["haze"]),
    dict(img="09_zhara", t0=A["vse"], cam=(1.25, 1.1, (500, 900), (500, 960)), fx=["haze"]),
    dict(img="08_lesa", t0=A["ktomu"], cam=(1.1, 1.22, (540, 960), (540, 960)), fx=["greenfade_lesa_done", "plankton"]),
    dict(img="10_holodilnik", t0=A["zadoh"], cam=(1.0, 1.1, (540, 960), (500, 1000)), fx=["fridge"]),
    dict(img="C__06_zerno", t0=A["apteka"], cam=(1.25, 1.1, (540, 600), (540, 760))),
    dict(img="11_zapravka", t0=A["zapr"], cam=(1.35, 1.0, (600, 1000), (540, 960))),
    dict(img="12_gnienie", t0=A["grib"], cam=(1.15, 1.3, (540, 1450), (540, 1470)), fx=["rot_fade"]),
    dict(img="13_poslednyaya_travinka", t0=A["d20"], cam=(1.0, 1.15, (540, 960), (540, 900)), suby=760, swaps=[(A["propala"] + 0.35, "B__13_poslednyaya_travinka", 0.8, "fade")], fx=["wind_dust"]),
    dict(img="14_seryy_gorod", t0=A["mir"], cam=(1.25, 1.0, (540, 1000), (540, 960)), fx=["wind_dust"]),
    dict(img="A__15_rostok", t0=A["vecher"], cam=(1.0, 1.2, (540, 960), (700, 1000)),
         swaps=[(A["rostok"] - 0.2, "B__15_rostok", 1.0, "fade"), (A["shtory"] + 0.1, "15_rostok", A["shtory_end"] - A["shtory"] + 0.3, "wipe")],
         fx=["drops", "glow"]),
    dict(img="16_zastavka", t0=OUT_T, cam=(1.0, 1.05, (540, 960), (540, 960)), fx=["outro"]),
]
for i, s in enumerate(SHOTS):
    s["t1"] = SHOTS[i + 1]["t0"] if i + 1 < len(SHOTS) else END
    s.setdefault("swaps", []); s.setdefault("fx", [])
XF = 0.3  # crossfade

DAYS = [(0, 1), (A["d3"], 3), (A["d5"], 5), (A["d7"], 7), (A["d9"], 9), (A["d12"], 12), (A["co2"], 14), (A["vse"], 15),
        (A["apteka"], 17), (A["grib"], 18), (A["d20"], 20), (A["utrom"], 21)]
GREEN = [(0, 1.0), (A["d3"], .85), (A["d5"], .7), (A["d7"], .55), (A["d9"], .4), (A["d12"], .25), (A["co2"], .2),
         (A["vse"], .12), (A["grib"], .05), (A["d20"], 0.0), (A["rostok"], 1.0)]
PLATES = [
    (A["tri4"], at("нечего", 40, True) + .2, "75%", "культур зависят от опылителей", "IPBES"),
    (at("восемнадцать") - .2, A["livnya"] - .4, "−18 °C", "в тени деревьев", ""),
    (A["vsego3"], at("час", 67, True) + .3, "3 культуры", "≈ 50% калорий", ""),
    (at("восьмидесяти") - .1, at("растения", 73, True) + 1.0, "82%", "калорий — растения", ""),
    (at("семидесяти") - .1, at("деревья", 93, True) + .3, "до 70%", "дождей — от деревьев", ""),
    (at("четверти", 99) - .1, at("мы", 104, True) + .4, "¼–⅓", "наших выбросов CO₂", ""),
]
def lv(table, t):
    v = table[0][1]
    for t0, x in table:
        if t >= t0: v = x
    return v

# ---------------------------------------------------------------- images
@lru_cache(maxsize=None)
def img(name):
    return np.asarray(Image.open(os.path.join(FR, name + ".png")).convert("RGB"), dtype=np.float32)

@lru_cache(maxsize=None)
def green_mask(name):
    a = img(name); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.clip((g - np.maximum(r, b) - 6) / 30, 0, 1)
    return m[..., None]

@lru_cache(maxsize=64)
def degreen(name, q):  # q: 0..20, share of green left
    a = img(name)
    if q >= 20: return a
    l = (a @ np.array([.3, .59, .11], np.float32))[..., None]
    grey = np.concatenate([l + 6, l, l - 4], -1)
    k = green_mask(name) * (1 - q / 20)
    return a * (1 - k) + grey * k

def camera(arr, z, cx, cy):
    z = max(z, 1.0)
    hw, hh = W / (2 * z), H / (2 * z)
    cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    out = im.transform((W, H), Image.AFFINE, (1 / z, 0, cx - hw, 0, 1 / z, cy - hh), resample=Image.BILINEAR)
    return np.asarray(out, dtype=np.float32)

def rng_for(key): return random.Random(key)

# ---------------------------------------------------------------- shot render
def shot_frame(s, t):
    p = (t - s["t0"]) / max(0.5, s["t1"] - s["t0"] + XF)
    z0, z1, c0, c1 = s["cam"]; e = ease(p) * .85 + p * .15
    z = z0 + (z1 - z0) * e; cx = c0[0] + (c1[0] - c0[0]) * e; cy = c0[1] + (c1[1] - c0[1]) * e
    if "bump3" in s["fx"]:
        for k in ("pshen", "ris", "kuk"):
            d = t - A[k]
            if 0 <= d < .5: z += .06 * math.sin(math.pi * d / .5)
    # base image with swaps
    name = s["img"]

    def src(n):
        if "greenfade_lesa" in s["fx"]:
            q = round(20 * (1 - ease((t - A["d12"]) / 9.0)))
            return degreen(n, q)
        if "greenfade_lesa_done" in s["fx"]: return degreen(n, 0)
        return img(n)
    arr = src(name)
    for (ts, n2, dur, mode) in s["swaps"]:
        if t >= ts:
            k = ease((t - ts) / dur)
            b = src(n2)
            if mode == "fade": arr = arr * (1 - k) + b * k
            else:  # soft wipe left→right (curtain)
                x = np.arange(W, dtype=np.float32)
                edge = -120 + (W + 240) * k
                m = np.clip((edge - x) / 120 + .5, 0, 1)[None, :, None]
                arr = arr * (1 - m) + b * m
    if "rot_fade" in s["fx"]:
        k = ease((t - A["pir"]) / 2.5) * .55
        if k > 0:
            l = (arr @ np.array([.3, .59, .11], np.float32))[..., None]
            flat = np.full_like(arr, 0) + (l * .4 + 120 * .6)
            arr = arr * (1 - k) + flat * k
    fr = camera(arr, z, cx, cy)
    # haze: per-row horizontal wobble in lower 55%
    if "haze" in s["fx"]:
        y0 = int(H * .45); rows = np.arange(y0, H)
        sh = (np.sin(rows * .045 + t * 5.0) * 2.5 * ((rows - y0) / (H - y0))).astype(int)
        cols = (np.arange(W)[None, :] - sh[:, None]) % W
        fr[y0:] = fr[rows[:, None], cols]
    return fr

def particles(s, t, fr):
    lay = None
    def L():
        nonlocal lay
        if lay is None: lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        return lay
    fx = s["fx"]; lt = t - s["t0"]
    if "sparkle_out" in fx and t >= A["propal"]:
        d = ImageDraw.Draw(L()); r = rng_for(1); k = t - A["propal"]
        for i in range(40):
            x = 540 + r.uniform(-140, 140); y = r.uniform(780, 1050); dl = r.uniform(0, .8); life = r.uniform(1.2, 2.4)
            q = (k - dl) / life
            if 0 < q < 1:
                yy = y - q * r.uniform(80, 220); a = int(220 * math.sin(math.pi * q)); rr = r.uniform(3, 8)
                d.ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=(170, 235, 160, a))
    if "dust" in fx:
        d = ImageDraw.Draw(L()); r = rng_for(3)
        storm = ease((t - A["veter"]) / 1.5) if "dust_storm" in fx else 0
        n = 50 + int(120 * storm)
        for i in range(n):
            sp = r.uniform(60, 220) * (1 + 2.5 * storm); y = r.uniform(300, 1900); ph = r.uniform(0, W + 200)
            x = (ph + t * sp) % (W + 200) - 100; yy = y + 30 * math.sin(t * .8 + i)
            rr = r.uniform(2, 6); d.ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=(196, 150, 100, int(r.uniform(60, 150))))
        if storm > 0:
            veil = Image.new("RGBA", (W, H), (190, 140, 95, int(110 * storm))); L().alpha_composite(veil)
    if "wind_dust" in fx:
        d = ImageDraw.Draw(L()); r = rng_for(13)
        for i in range(40):
            sp = r.uniform(80, 200); y = r.uniform(400, 1900); x = (r.uniform(0, W + 200) + t * sp) % (W + 200) - 100
            rr = r.uniform(1.5, 4); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(180, 178, 172, int(r.uniform(50, 120))))
    if "rain" in fx and t >= A["livnya"]:
        k = t - A["livnya"]; d = ImageDraw.Draw(L()); r = rng_for(5)
        if k < .15: L().alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - k / .15)))))
        L().alpha_composite(Image.new("RGBA", (W, H), (40, 45, 60, int(90 * min(1, k / .4)))))
        for i in range(160):
            x0 = r.uniform(-200, W); sp = r.uniform(1800, 2600); y = (r.uniform(0, H) + t * sp) % (H + 100) - 50
            x = x0 + y * .18; d.line([x, y, x + 10, y + 55], fill=(200, 210, 230, 120), width=2)
    if "bee" in fx:
        # tiny wing shimmer near bee
        pass
    if "plankton" in fx:
        d = ImageDraw.Draw(L()); r = rng_for(8)
        k = ease((t - (A["ktomu"] + 1.2)) / 2.0)
        for i in range(140):
            a = r.uniform(0, 2 * math.pi); rad = 390 * math.sqrt(r.random())
            x = 540 + rad * math.cos(a); y = 960 + rad * math.sin(a)
            tw = .5 + .5 * math.sin(t * r.uniform(1.5, 4) + i)
            al = int(220 * k * tw); rr = r.uniform(2, 5)
            d.ellipse([x - rr * 2.5, y - rr * 2.5, x + rr * 2.5, y + rr * 2.5], fill=(80, 220, 255, al // 4))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(170, 245, 255, al))
    if "drops" in fx:
        d = ImageDraw.Draw(L()); k = t - A["polil"]
        for i in range(6):
            q = (k - i * .18) / .45
            if 0 < q < 1:
                x = 735 + (i % 3 - 1) * 14; y = 760 + q * 280; d.ellipse([x - 6, y - 10, x + 6, y + 10], fill=(150, 190, 220, 200))
    if "glow" in fx and t >= A["rostok"] - .2:
        k = ease((t - A["rostok"] + .2) / 1.0); pulse = 1 + .15 * math.sin(2 * math.pi * (t - A["rostok"]) / 1.8)
        # curtain covers left part after wipe; glow stays at the plant
        g = glow_sprite(); sz = int(560 * pulse); gs = g.resize((sz, sz), Image.BILINEAR)
        a = np.asarray(gs, np.float32) / 255 * k
        x0, y0 = 740 - sz // 2, 950 - sz // 2
        fr[y0:y0 + sz, x0:x0 + sz] += a[..., None] * np.array([90, 200, 90], np.float32) * .55
        d = ImageDraw.Draw(L()); r = rng_for(15)
        for i in range(18):
            ph = r.uniform(0, 3); q = ((t + ph) % 3) / 3; x = 740 + r.uniform(-110, 110); y = 1030 - q * 260
            rr = r.uniform(2, 5); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(200, 255, 190, int(200 * k * math.sin(math.pi * q))))
    if "fridge" in fx:
        f = 1 + .04 * math.sin(t * 9) * (1 if int(t * 3) % 7 == 0 else 0)
        fr *= f
    if "outro" in fx:
        d = ImageDraw.Draw(L()); r = rng_for(16)
        for i in range(50):
            x = r.uniform(0, W); y = (r.uniform(0, H) - t * r.uniform(10, 30)) % H; rr = r.uniform(1, 3)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(220, 230, 220, int(r.uniform(40, 140))))
    return lay

@lru_cache(maxsize=1)
def glow_sprite():
    n = 256; y, x = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]; g = np.clip(1 - np.sqrt(x * x + y * y), 0, 1) ** 2.2
    return Image.fromarray((g * 255).astype(np.uint8))

# ---------------------------------------------------------------- HUD
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
@lru_cache(maxsize=None)
def font(path, size): return ImageFont.truetype(path, size)

def day_badge(lay, t):
    if t >= OUT_T: return
    cur = lv(DAYS, t); prev = None; k = 1.0
    for i, (t0, n) in enumerate(DAYS):
        if i and t0 <= t < t0 + .4: prev = DAYS[i - 1][1]; k = ease((t - t0) / .4)
    fa = 1.0 if t > .4 else ease(t / .4)
    box = Image.new("RGBA", (320, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
    d.rounded_rectangle([0, 0, 319, 95], 22, fill=(22, 24, 30, int(200 * fa)))
    f = font(FONT_MONO, 52); d.text((26, 18), "ДЕНЬ", font=f, fill=(235, 232, 222, int(255 * fa)))
    num = Image.new("RGBA", (130, 96), (0, 0, 0, 0)); dn = ImageDraw.Draw(num)
    col = (255, 214, 92, int(255 * fa))
    if prev is not None:
        dn.text((4, 18 - 70 * k), str(prev), font=f, fill=(255, 214, 92, int(255 * (1 - k))))
        dn.text((4, 18 + 70 * (1 - k)), str(cur), font=f, fill=(255, 214, 92, int(255 * k)))
    else: dn.text((4, 18), str(cur), font=f, fill=col)
    box.alpha_composite(num, (182, 0))
    lay.alpha_composite(box, ((W - 320) // 2, 110))

@lru_cache(maxsize=None)
def plate_img(big, small, src):
    f1, f2, f3 = font(FONT_SANS, 92), font(FONT_SANS, 40), font(FONT_SANS, 28)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = max(tmp.textlength(big, f1), tmp.textlength(small, f2)) + 90
    h = 210 + (40 if src else 0)
    im = Image.new("RGBA", (int(w), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(20, 22, 28, 215), outline=(255, 214, 92, 180), width=3)
    d.text((w / 2, 28), big, font=f1, fill=(255, 214, 92, 255), anchor="ma")
    d.text((w / 2, 140), small, font=f2, fill=(245, 243, 236, 255), anchor="ma")
    if src: d.text((w / 2, 200), src, font=f3, fill=(170, 170, 170, 255), anchor="ma")
    return im

def plates(lay, t):
    for (t0, t1, big, small, src) in PLATES:
        if t0 <= t < t1 + .25:
            im = plate_img(big, small, src)
            sc = eob((t - t0) / .3) if t < t0 + .3 else 1.0
            a = 1.0 if t < t1 else 1 - (t - t1) / .25
            if sc <= .02: continue
            pw, ph = int(im.width * sc), int(im.height * sc)
            p = im.resize((pw, ph), Image.BILINEAR)
            if a < 1: p.putalpha(p.getchannel("A").point(lambda v: int(v * a)))
            ang = math.sin((t - t0) * 2 * math.pi / 2.5) * 1.2
            p = p.rotate(ang, resample=Image.BILINEAR, expand=True)
            lay.alpha_composite(p, ((W - p.width) // 2, 300 - (p.height - ph) // 2 + (210 - ph) // 2))

# ---------------------------------------------------------------- karaoke subtitles
PLANT = ("кактус", "фикус", "фиалк", "трав", "газон", "сорняк", "мох", "цвет", "деревь", "пшениц", "рис", "кукуруз",
         "растен", "растител", "лес", "травинк", "росток", "ив", "семен", "поле")
NUM = ("третий", "пятый", "седьмой", "девятый", "двенадцатый", "двадцатый", "три", "четверт", "восемнадцат", "половин",
       "восьмидесят", "процент", "семидесят", "трет", "тысяч", "шест", "миллион")
def wclass(w):
    c = clean(w)
    if c in ("ив", "ивы") or any(c.startswith(p) for p in PLANT if p != "ив"): return "plant"
    if any(c.startswith(p) for p in NUM): return "num"
    return ""

def make_phrases():
    segs, cur, ln = [], [], 0
    for i, w in enumerate(WORDS):
        cur.append(i); ln += len(w["w"]) + 1
        if w["s"] >= 2 or i == len(WORDS) - 1 or (w["s"] == 1 and ln > 18):
            segs.append(cur); cur, ln = [], 0
    ph = []
    for sg in segs:  # split long segments into n parts minimising the longest part
        Ls = [len(WORDS[i]["w"]) + 1 for i in sg]; tot = sum(Ls); n = min(len(sg), math.ceil(tot / 38))
        best = None
        import itertools
        for cuts in itertools.combinations(range(1, len(sg)), n - 1):
            b = (0,) + cuts + (len(sg),); m = max(sum(Ls[b[k]:b[k + 1]]) for k in range(n))
            if best is None or m < best[0]: best = (m, b)
        b = best[1]; ph += [sg[b[k]:b[k + 1]] for k in range(n)]
    return ph
PHRASES = make_phrases()

def sub_layout(idx, f):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10))); sp = tmp.textlength(" ", f)
    lines, cur, cw = [], [], 0
    for i in idx:
        tw = tmp.textlength(WORDS[i]["w"].upper(), f)
        if cur and cw + sp + tw > 960: lines.append((cur, cw)); cur, cw = [], 0
        cur.append((i, tw)); cw += (sp if len(cur) > 1 else 0) + tw
    lines.append((cur, cw)); return lines, sp

def subtitles(lay, t):
    if t >= OUT_T: return
    s = SHOTS[shot_at(t)]; f = font(FONT_SERIF, 70); lh = 90
    for pi, idx in enumerate(PHRASES):
        t0 = WORDS[idx[0]]["t0"] - .12
        nxt = WORDS[PHRASES[pi + 1][0]]["t0"] - .12 if pi + 1 < len(PHRASES) else OUT_T
        t1 = min(nxt, WORDS[idx[-1]]["t1"] + .7)
        if not (t0 <= t < t1): continue
        prev_end = (min(t0, WORDS[PHRASES[pi - 1][-1]]["t1"] + .7)) if pi else -9
        fin = 1 if t0 - prev_end < .05 else (t - t0) / .15   # back-to-back phrases switch without a dip
        fout = 1 if t1 >= nxt - 1e-6 and nxt - WORDS[idx[-1]]["t1"] < .7 else (t1 - t) / .15
        fa = max(0, min(1, fin, fout))
        lines, sp = sub_layout(idx, f)
        if max(cw for _, cw in lines) > 1010:
            f2 = font(FONT_SERIF, int(70 * 1000 / max(cw for _, cw in lines))); lines, sp = sub_layout(idx, f2); f = f2
        y = s.get("suby", 1470) - len(lines) * lh / 2
        d = ImageDraw.Draw(lay)
        gl = lv(GREEN, t)
        for words, cw in lines:
            x = (W - cw) / 2
            for i, tw in words:
                w = WORDS[i]; lit = min(1, max(0, (t - w["t0"]) / .08))
                a = fa
                cl = wclass(w["w"])
                if cl == "plant":
                    g = 1.0 if clean(w["w"]).startswith("росток") or t >= A["rostok"] else gl
                    base = np.array([255, 255, 255]); green = np.array([110, 215, 100]); grey = np.array([150, 150, 145])
                    col = green * g + grey * (1 - g); col = col * lit + base * (1 - lit) * .9 + col * (1 - lit) * .1
                elif cl == "num": col = np.array([255, 214, 92]) * lit + np.array([255, 255, 255]) * (1 - lit)
                else: col = np.array([255, 255, 255])
                col = col * (.55 + .45 * lit) + np.array([120, 120, 120]) * (1 - lit) * .45
                fill = tuple(int(v) for v in col) + (int(255 * a),)
                d.text((x + 3, y + 5), w["w"].upper(), font=f, fill=(0, 0, 0, int(110 * a)))
                d.text((x, y), w["w"].upper(), font=f, fill=fill, stroke_width=5, stroke_fill=(18, 18, 22, int(230 * a)))
                x += tw + sp
            y += lh

@lru_cache(maxsize=1)
def band():
    y = np.arange(H, dtype=np.float32); a = np.clip((y - 1200) / 300, 0, 1) * np.clip((1850 - y) / 200, 0, 1) * 70
    im = np.zeros((H, W, 4), np.uint8); im[..., 3] = a[:, None].astype(np.uint8)
    return Image.fromarray(im, "RGBA")

# ---------------------------------------------------------------- compose
def shot_at(t):
    for i, s in enumerate(SHOTS):
        if s["t0"] <= t < s["t1"]: return i
    return len(SHOTS) - 1

def frame(t):
    i = shot_at(t); s = SHOTS[i]
    fr = shot_frame(s, t); lay = particles(s, t, fr)
    if lay is not None: fr = composite(fr, lay)
    if i > 0 and t < s["t0"] + XF:  # crossfade from previous shot (continues moving)
        ps = SHOTS[i - 1]; pf = shot_frame(ps, t); pl = particles(ps, t, pf)
        if pl is not None: pf = composite(pf, pl)
        dur = .6 if s["img"] == "16_zastavka" else XF
        k = ease((t - s["t0"]) / dur)
        if s["img"] == "16_zastavka":  # dip to black
            fr = pf * max(0, 1 - 2 * k) if k < .5 else fr * (2 * k - 1)
        else: fr = pf * (1 - k) + fr * k
    if s["img"] == "16_zastavka" and t > s["t0"] + XF: fr = fr * min(1, (t - s["t0"]) / .6)
    if t > END - .5: fr = fr * max(0, (END - t) / .5)
    hud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < OUT_T: hud.alpha_composite(band())
    day_badge(hud, t); plates(hud, t); subtitles(hud, t)
    return composite(fr, hud)

def composite(fr, lay):
    a = np.asarray(lay, np.float32); al = a[..., 3:4] / 255
    return fr * (1 - al) + a[..., :3] * al

def render_chunk(args):
    ci, f0, f1 = args
    path = os.path.join(OUT, f"_chunk{ci:02d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for n in range(f0, f1):
        p.stdin.write(np.clip(frame(n / FPS), 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait(); return path

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if "--still" in sys.argv:
        for a in sys.argv[sys.argv.index("--still") + 1:]:
            Image.fromarray(np.clip(frame(float(a)), 0, 255).astype(np.uint8)).save(os.path.join(OUT, f"still_{float(a):06.2f}.png"))
        sys.exit()
    N = int(END * FPS); C = 8; step = math.ceil(N / C)
    jobs = [(c, c * step, min(N, (c + 1) * step)) for c in range(C)]
    with Pool(int(os.environ.get("JOBS", os.cpu_count()))) as pool:
        parts = pool.map(render_chunk, jobs)
    lst = os.path.join(OUT, "_list.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(OUT, "_video.mp4")], check=True)
    print("video ok", END)
