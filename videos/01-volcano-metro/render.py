"""Рендер ролика «Если извержение вулкана застало вас в метро».

python3 render.py            — полный рендер (видео + звук) в out/volcano_metro.mp4
python3 render.py --stills   — только контрольные кадры в out/stills/
"""
import math
import os
import random
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
sys.path.insert(0, HERE)

from core import *  # noqa
from characters import *  # noqa
from phrases import PHRASES

VOICE = os.path.join(HERE, "voice.mp3")
OUT = os.path.join(HERE, "out")

# ======================================================================= timing
SEGS = align(PHRASES, speech_segments(VOICE))
PH = [(s[0][0], s[-1][1]) for s in SEGS]          # начало/конец каждой фразы
WT = [word_times(p, s) for p, s in zip(PHRASES, SEGS)]
VOICE_END = PH[-1][1]


def ph_start(i):
    return PH[i][0]


def word_t(i, stem):
    words, times = WT[i]
    for w, t in zip(words, times):
        if stem in w.lower():
            return t
    return PH[i][0]


def cut(i):
    return PH[i][0] - 0.25


# сцены: (имя, начало)
SCENES = [
    ("hook", 0.0), ("sky", cut(1)), ("train", cut(2)), ("child", cut(4)), ("phone", cut(5)),
    ("cloth", cut(9)), ("leader", cut(12)), ("door", cut(15)), ("gas", cut(17)), ("hush", cut(20)),
    ("gate", cut(23)), ("rescue", cut(25)), ("ghost", cut(26)), ("final", VOICE_END + 0.35),
]
TOTAL = SCENES[-1][1] + 5.2
XF = 0.45                                   # длительность растворения
BLACK_DIP = {"rescue"}                      # вход через затемнение


def scene_at(t):
    idx = 0
    for i, (_, s) in enumerate(SCENES):
        if t >= s:
            idx = i
    return idx


# ======================================================================= palette
NIGHT = (22, 26, 40)
WALL = (50, 56, 72)
WALL_D = (38, 42, 56)
TILE = (60, 84, 90)
TILE_L = (46, 66, 72)
FLOOR = (36, 38, 48)
ORANGE = (255, 130, 42)
ORANGE_L = (255, 186, 90)
RED = (204, 54, 38)
LAVA = (255, 100, 26)
SAFE_YEL = (255, 222, 120)

VIG = vignette(0.65)
VIG_STRONG = vignette(1.0)
GRAIN = grain_frames()


def scr(x, y, z, cx, cy):
    return ((x - cx) * z + W / 2, (y - cy) * z + H / 2)


def finish(frame, t, vig=VIG):
    frame.alpha_composite(vig)
    frame.alpha_composite(GRAIN[int(t * 8) % len(GRAIN)])
    return frame


def blink_at(t, seed=0, period=3.3):
    """Моргание ~100 мс каждые 2-5 сек."""
    r = random.Random(seed)
    tt = 0.0
    while tt < TOTAL:
        tt += r.uniform(2.0, 4.5)
        if tt <= t < tt + 0.11:
            return True
    return False


def tiles(c, x1, y1, x2, y2, col, line, step=60):
    c.rect(x1, y1, x2, y2, col, w=0)
    y = y1
    while y <= y2:
        c.line([(x1, y), (x2, y)], line, 3)
        y += step
    row = 0
    y = y1
    while y < y2:
        off = (step / 2) * (row % 2)
        x = x1 + off
        while x <= x2:
            c.line([(x, y), (x, min(y + step, y2))], line, 3)
            x += step * 2
        y += step
        row += 1


# ======================================================================= scenes
class Scene:
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1

    def frame(self, t):
        raise NotImplementedError


# ---------------------------------------------------------------- 1. HOOK
class Hook(Scene):
    EX = (330, 470, 750, 760)   # проём выхода

    def __init__(self, *a):
        super().__init__(*a)
        x1, y1, x2, y2 = self.EX
        c = Canvas()
        # небо в проёме
        c.vgrad(x1, y1, x2, y2, (255, 190, 90), (255, 110, 34))
        c.poly([(x1 + 30, y2), (510, 560), (560, 552), (x2 - 10, y2)], (92, 36, 40), w=5)   # вулкан
        c.ellipse(500, 540, 570, 566, LAVA, w=0)
        for (bx, by, r) in [(535, 520, 40), (510, 480, 52), (570, 470, 48), (530, 420, 66), (600, 410, 56),
                            (470, 420, 50), (560, 360, 80), (450, 370, 60), (660, 370, 60)]:
            c.circle(bx, by, r, (70, 58, 66), w=4)
        for i, bx in enumerate(range(x1, x2, 48)):
            hh = [60, 100, 40, 80, 120, 50, 90, 70, 110][i % 9]
            c.rect(bx, y2 - hh, bx + 44, y2, (50, 30, 44), w=4)
        # потолок
        c.poly([(-MX, -MY), (W + MX, -MY), (x2, y1), (x1, y1)], (30, 32, 46))
        for k in range(1, 6):
            f = (k / 6) ** 1.6
            ya = lerp(y1, -MY, f)
            xa, xb = lerp(x1, -MX, f) + 40 * f, lerp(x2, W + MX, f) - 40 * f
            c.line([(lerp(xa, xb, 0.35), ya), (lerp(xa, xb, 0.65), ya)], (230, 220, 190), 6 + 10 * f)
        # стены
        c.poly([(-MX, -MY), (x1, y1), (x1, y2), (-MX, H + MY)], WALL)
        c.poly([(W + MX, -MY), (x2, y1), (x2, y2), (W + MX, H + MY)], WALL_D)
        for k in range(1, 9):
            f = (k / 9) ** 1.5
            xa = lerp(x1, -MX, f)
            c.line([(xa, lerp(y1, -MY, f)), (xa, lerp(y2, H + MY, f))], (40, 44, 58), 4)
            xb = lerp(x2, W + MX, f)
            c.line([(xb, lerp(y1, -MY, f)), (xb, lerp(y2, H + MY, f))], (30, 32, 44), 4)
        # лестница
        c.poly([(x1, y2), (x2, y2), (W + MX, H + MY), (-MX, H + MY)], (58, 60, 72))
        N = 22
        for k in range(N):
            fa, fb = (k / N) ** 1.7, ((k + 0.45) / N) ** 1.7
            ya, yb = lerp(y2, H + MY, fa), lerp(y2, H + MY, fb)
            pts = [(lerp(x1, -MX, fa), ya), (lerp(x2, W + MX, fa), ya), (lerp(x2, W + MX, fb), yb),
                   (lerp(x1, -MX, fb), yb)]
            c.poly(pts, (44, 46, 58), w=0)
        c.line([(x1 + 10, y2), (-MX + 140, H + MY)], (140, 120, 100), 10)
        c.line([(x2 - 10, y2), (W + MX - 140, H + MY)], (120, 100, 90), 10)
        self.bg = paper_grain(c.done())
        g = radial((1100, 1100), ORANGE + (170,), power=1.4)
        self.glow = g
        self.you = adult("back")
        self.kid = girl("back")
        self.ash = Ash(140, seed=5, color=(170, 150, 140), speed=(60, 160))
        r = random.Random(11)
        self.crowd = [(r.uniform(0.05, 0.95), r.uniform(0, 1), r.uniform(0.18, 0.32), r.uniform(0, 6),
                       r.random() < 0.4) for _ in range(26)]

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.09, ease_io(lt / (self.t1 - self.t0)))
        sh = 16 * max(0, 1 - lt / 0.9)
        f = camera(self.bg, z, 540, 900, sh, t)
        x1, y1, x2, y2 = self.EX
        gx, gy = scr(540, 615, z, 540, 900)
        pulse = 0.75 + 0.25 * math.sin(t * 5.3) * math.sin(t * 2.1)
        put(f, with_alpha(self.glow, pulse), gx, gy, anchor="center", scale=z)
        # толпа бежит вверх к выходу
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        items = []
        for (lx, p0, sp, ph, up) in self.crowd:
            p = (p0 - sp * lt) % 1.0                    # 1 — внизу, 0 — у выхода
            fy = p ** 1.7
            yy = lerp(y2, 1700, fy)
            xx = lerp(lerp(x1 + 20, x2 - 20, lx), lerp(-60, 1140, lx), fy)
            hh = lerp(60, 520, fy)
            items.append((yy, xx, hh, ph, up))
        for yy, xx, hh, ph, up in sorted(items):
            sx, sy = scr(xx, yy, z, 540, 900)
            silhouette(d, sx, sy, hh * z, (24, 20, 30, 235), ph=ph + t * 14, arms_up=up)
        f.alpha_composite(ov)
        self.ash.draw(f, t, 0.85, wind=30)
        # вы и ребёнок стоят — не бегут
        bx, by = scr(430, 2010, z, 540, 900)
        put(f, self.you, bx, by, scale=z * 1.25)
        kx, ky = scr(680, 2000, z, 540, 900)
        put(f, self.kid, kx, ky, scale=z * 1.3)
        return finish(f, t)


# ---------------------------------------------------------------- 2. SKY
class Sky(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, 460, (28, 30, 44), w=0)
        tiles(c, -MX, 460, W + MX, 1340, TILE, TILE_L, 64)
        c.rect(-MX, 1340, W + MX, H + MY, FLOOR, w=0)
        c.rect(-MX, 1640, W + MX, 1680, (190, 160, 60), w=0)
        c.rect(-MX, 440, W + MX, 470, (24, 26, 36), w=0)
        # вывеска
        c.rect(250, 640, 830, 760, (30, 52, 104), w=8, r=10)
        c.text(540, 700, "ПЕПЕЛЬНАЯ", 70, (240, 240, 240))
        # решётки вентиляции
        self.grates = [(170, 330), (760, 1010)]
        for gx1, gx2 in self.grates:
            c.rect(gx1, 360, gx2, 430, (255, 150, 60), w=8)
            for x in range(int(gx1) + 20, int(gx2), 30):
                c.line([(x, 362), (x, 428)], (60, 40, 40), 8)
        # скамейка
        c.rect(120, 1260, 460, 1300, (120, 84, 60), w=6)
        c.rect(140, 1300, 170, 1360, (60, 60, 70), w=5)
        c.rect(410, 1300, 440, 1360, (60, 60, 70), w=5)
        self.bg = paper_grain(c.done())
        # лучи света сверху
        s = Canvas(ss=1)
        for gx1, gx2 in self.grates:
            s.poly([(gx1, 430), (gx2, 430), (gx2 + 240, 1700), (gx1 - 160, 1700)], ORANGE + (120,), outline=None)
        self.shafts = s.done(blur=30)
        self.kid = girl("back")
        self.you = adult("back")
        self.ash = Ash(160, seed=9, color=(230, 150, 90), speed=(50, 120), glow=True)
        r = random.Random(4)
        self.people = [(r.uniform(-60, 1140), r.uniform(1380, 1600), r.uniform(300, 420)) for _ in range(6)]

    def frame(self, t):
        lt = t - self.t0
        k = ease_io(lt / (self.t1 - self.t0 + XF))
        cx = lerp(470, 610, k)
        z = 1.05
        f = camera(self.bg, z, cx, 960)
        a = 0.65 + 0.35 * math.sin(t * 3.1) * math.sin(t * 1.7 + 1)
        sh = camera(self.shafts, z, cx, 960)
        f.alpha_composite(with_alpha(sh, clamp(a)))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for (px, py, hh) in self.people:
            sx, sy = scr(px, py, z, cx, 960)
            silhouette(d, sx, sy, hh * z, (26, 22, 34, 230), ph=1.0, arms_up=False)
        f.alpha_composite(ov)
        sx, sy = scr(600, 1560, z, cx, 960)
        put(f, self.you, sx, sy, scale=0.62 * z)
        sx, sy = scr(700, 1560, z, cx, 960)
        put(f, self.kid, sx, sy, scale=0.62 * z)
        self.ash.draw(f, t, 0.9, wind=10)
        return finish(f, t)


# ---------------------------------------------------------------- 3. TRAIN
def car_interior(dark=False):
    c = Canvas()
    c.rect(-MX, -MY, W + MX, H + MY, (178, 182, 172), w=0)
    c.rect(-MX, -MY, W + MX, 320, (150, 154, 146), w=0)
    for x in (60, 620):
        c.rect(x, 250, x + 420, 284, (250, 246, 220), w=6, r=8)
    # окна
    for x in (-60, 370, 800):
        c.rect(x, 470, x + 360, 900, (14, 16, 24), w=10, r=30)
        c.line([(x + 20, 610), (x + 340, 640)], (40, 40, 50), 5)
        c.line([(x + 20, 700), (x + 340, 720)], (34, 34, 44), 4)
    # сиденья
    c.rect(-MX, 1000, W + MX, 1070, (70, 96, 150), w=6)
    c.rect(-MX, 1070, W + MX, 1200, (56, 78, 126), w=6)
    c.rect(-MX, 1200, W + MX, H + MY, (110, 108, 104), w=0)
    for x in (160, 920):
        c.rect(x - 14, -MY, x + 14, H + MY, (200, 200, 196), w=5)
    return paper_grain(c.done())


class Train(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        self.bg = car_interior()
        self.you = adult("front", worried=True)
        self.you_b = adult("front", worried=True, blink=True)
        self.kid = girl("front")
        self.kid_b = girl("front", blink=True)
        self.t_blink = word_t(3, "мигнул")
        self.t_off = word_t(3, "погас")
        self.emerg = radial((700, 700), (255, 40, 30, 150))

    def light(self, t):
        if t < self.t_blink:
            return 1.0
        if t >= self.t_off:
            return 0.0
        k = (t - self.t_blink) / max(0.3, self.t_off - self.t_blink)
        return 1.0 if (int(k * 7) % 2 == 1) else 0.15

    def frame(self, t):
        lt = t - self.t0
        sh = 22 * max(0, 1 - lt / 0.7)
        z = lerp(1.02, 1.08, lt / (self.t1 - self.t0))
        f = camera(self.bg, z, 540, 960, sh, t)
        sway = math.sin(lt * 6) * 4 * max(0, 1 - lt)
        put(f, self.you_b if blink_at(t, 1) else self.you, *scr(420 + sway, 1500, z, 540, 960), scale=z * 1.15)
        put(f, self.kid_b if blink_at(t, 2) else self.kid, *scr(640 + sway, 1500, z, 540, 960), scale=z * 1.15)
        L = self.light(t)
        darkness(f, 0.9 * (1 - L))
        if L < 0.5:
            pa = 0.5 + 0.5 * math.sin(t * 4)
            put(f, with_alpha(self.emerg, pa), 980, 300, anchor="center")
        return finish(f, t)


# ---------------------------------------------------------------- 4. CHILD (фонарик)
class Child(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        self.bg = car_interior()
        self.kid = girl("front", hand_up=True)
        self.kid_b = girl("front", hand_up=True, blink=True)
        # рука взрослого слева
        c = Canvas(ss=2)
        c.poly([(-MX, 1260), (-MX, 1420), (330, 1060), (290, 1010)], JACKET)
        c.circle(318, 1020, 34, SKIN)
        self.arm = c.done()
        # конус фонаря
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.polygon([(1150, 2000), (980, 2000), (250, 620), (860, 560)], fill=255)
        d.ellipse([200, 420, 900, 1300], fill=255)
        self.cone = m.filter(ImageFilter.GaussianBlur(60))
        self.t_click = self.t0 + 0.35

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.07, ease_io(lt / (self.t1 - self.t0)))
        f = camera(self.bg, z, 540, 900)
        put(f, self.kid_b if blink_at(t, 3) else self.kid, *scr(600, 1720, z, 540, 900), scale=z * 2.0)
        f.alpha_composite(camera(self.arm, z, 540, 900))
        on = t >= self.t_click and not (self.t_click + 0.08 < t < self.t_click + 0.16)
        dark = Image.new("RGBA", (W, H), (4, 4, 10, 245))
        if on:
            inv = self.cone.point(lambda v: 255 - int(v * 0.97))
            a = Image.eval(inv, lambda v: int(v * 245 / 255))
            dark.putalpha(a)
            warm = Image.new("RGBA", (W, H), (255, 220, 140, 0))
            warm.putalpha(self.cone.point(lambda v: int(v * 0.16)))
            f.alpha_composite(warm)
        f.alpha_composite(dark)
        return finish(f, t)


# ---------------------------------------------------------------- 5. PHONE + MAP
class Phone(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        tiles(c, -MX, -MY, W + MX, H + MY, TILE, TILE_L, 64)
        c.rect(-MX, 1500, W + MX, H + MY, FLOOR, w=0)
        # аварийный телефон
        c.rect(70, 620, 380, 1110, (196, 46, 40), w=8, r=16)
        c.rect(110, 680, 340, 760, (240, 236, 220), w=5, r=6)
        c.text(225, 720, "SOS", 46, RED)
        c.rect(120, 800, 330, 900, (30, 30, 34), w=6, r=40)           # трубка
        c.rect(150, 790, 300, 830, (30, 30, 34), w=0)
        c.line([(225, 900), (215, 960), (240, 1000), (220, 1050)], (30, 30, 34), 8)
        c.text(225, 1080, "ЭКСТРЕННАЯ СВЯЗЬ", 22, (255, 230, 220))
        # схема линии
        c.rect(430, 560, 1050, 1100, (232, 228, 214), w=10, r=10)
        c.text(740, 610, "ЛИНИЯ 3 · СХЕМА", 30, (40, 40, 50))
        self.route = [(480, 1000), (600, 1000), (680, 900), (680, 760), (800, 700), (1000, 700)]
        c.line(self.route, (40, 150, 90), 22)
        st = [("ДЕПО", 480, 1000), ("ПАРКОВАЯ", 600, 1000), ("ПЕПЕЛЬНАЯ", 680, 830), ("ЗАВОДСКАЯ", 800, 700),
              ("СЕВЕРНАЯ", 1000, 700)]
        for name, x, y in st:
            c.circle(x, y, 18, (250, 250, 250), w=6)
            c.text(x, y + 44 if y > 900 else y - 44, name, 22, (40, 40, 50))
        self.here = (680, 830)
        c.text(560, 830, "ВЫ ЗДЕСЬ", 22, RED)
        # аварийные выходы
        for x, y in [(640, 950), (740, 735)]:
            c.rect(x - 22, y - 16, x + 22, y + 16, (40, 160, 80), w=4, r=4)
            c.text(x, y, "↑", 24, (255, 255, 255))
        self.bg = paper_grain(c.done())
        self.spot = radial((1500, 1500), (0, 0, 0, 255), power=1.2)

    def cam(self, t):
        a, b = (225, 860, 1.25), (740, 840, 1.35)
        t7, t8 = ph_start(7), ph_start(8)
        mid = (480, 840, 1.0)
        if t < ph_start(6) + 1.2:
            k = ease_io((t - self.t0) / 2.5)
            return tuple(lerp(m, x, k * 0.6) for m, x in zip(mid, a))
        if t < t8 - 0.3:
            k = ease_io((t - (ph_start(6) + 1.2)) / 1.2)
            st = tuple(lerp(m, x, 0.6) for m, x in zip(mid, a))
            return tuple(lerp(s, e, k) for s, e in zip(st, b))
        k = ease_io((t - (t8 - 0.3)) / 0.9)
        return tuple(lerp(s, e, k) for s, e in zip(b, a))

    def frame(self, t):
        cx, cy, z = self.cam(t)
        f = camera(self.bg, z, cx, cy)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        # огонёк бежит по маршруту к ближайшему выходу
        L = self.route
        seglen = [math.dist(L[i], L[i + 1]) for i in range(len(L) - 1)]
        tot = sum(seglen)
        pos = ((t * 260) % tot)
        for i, sl in enumerate(seglen):
            if pos <= sl:
                px = lerp(L[i][0], L[i + 1][0], pos / sl)
                py = lerp(L[i][1], L[i + 1][1], pos / sl)
                break
            pos -= sl
        sx, sy = scr(px, py, z, cx, cy)
        r = 16 * z
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 240, 120, 230))
        hx, hy = scr(*self.here, z, cx, cy)
        pr = (26 + 12 * (0.5 + 0.5 * math.sin(t * 8))) * z
        d.ellipse([hx - pr, hy - pr, hx + pr, hy + pr], outline=(230, 40, 40, 255), width=int(6 * z))
        lx, ly = scr(225, 640, z, cx, cy)
        if math.sin(t * 9) > 0:
            d.ellipse([lx - 18 * z, ly - 18 * z, lx + 18 * z, ly + 18 * z], fill=(255, 70, 50, 255))
        f.alpha_composite(ov)
        # темнота + луч фонаря по центру
        dk = Image.new("RGBA", (W, H), (4, 4, 10, 0))
        spot = self.spot.resize((1700, 1700))
        m = Image.new("L", (W, H), 225)
        inv = spot.getchannel("A").point(lambda v: 225 - int(v * 225 / 255))
        m.paste(inv, (W // 2 - 850, H // 2 - 900))
        dk.putalpha(m)
        f.alpha_composite(dk)
        return finish(f, t)


# ---------------------------------------------------------------- 6. CLOTH
class Cloth(Scene):
    def build(self, blink):
        c = Canvas()
        c.vgrad(-MX, -MY, W + MX, H + MY, (36, 40, 56), (20, 22, 32))
        for i in range(6):
            c.rect(-MX + i * 240, 1300, -MX + i * 240 + 180, 1340, (50, 56, 72), w=0)
        # плечи и капюшон
        c.poly([(120, 1700), (960, 1700), (1140, H + MY), (-60, H + MY)], YEL)
        c.circle(540, 900, 380, YEL, w=8)
        c.circle(540, 900, 380 - 60, YEL_D, w=0)
        c.ellipse(260, 640, 820, 1180, SKIN, w=8)
        c.poly([(268, 820), (300, 700), (420, 630), (660, 630), (780, 700), (812, 820), (760, 800),
                (700, 740), (600, 780), (500, 730), (400, 790), (330, 770)], GHAIR, w=8)
        ey = 860
        if blink:
            c.line([(400, ey), (470, ey)], INK, 10)
            c.line([(610, ey), (680, ey)], INK, 10)
        else:
            c.circle(436, ey, 34, INK, w=0)
            c.circle(644, ey, 34, INK, w=0)
            c.circle(448, ey - 12, 10, (255, 255, 255), w=0)
            c.circle(656, ey - 12, 10, (255, 255, 255), w=0)
        c.line([(390, 800), (470, 784)], INK, 7)
        c.line([(610, 784), (690, 800)], INK, 7)
        # мокрая ткань на лице
        c.poly([(330, 930), (760, 920), (740, 1110), (560, 1150), (350, 1100)], (150, 196, 226), w=8)
        for (x, y, r) in [(420, 990, 30), (600, 1040, 40), (690, 970, 22), (500, 1090, 26)]:
            c.circle(x, y, r, (110, 160, 200), w=0)
        c.line([(360, 960), (740, 950)], (120, 170, 210), 5)
        # рука взрослого
        c.poly([(W + MX, 1200), (W + MX, 1420), (780, 1110), (760, 1020)], JACKET)
        c.ellipse(700, 960, 830, 1100, SKIN, w=8)
        # бутылка сверху
        c.poly([(820, 220), (900, 260), (760, 560), (680, 520)], (170, 210, 230), w=8)
        c.poly([(680, 520), (760, 560), (720, 600), (660, 580)], (60, 120, 200), w=6)
        return paper_grain(c.done())

    def __init__(self, *a):
        super().__init__(*a)
        self.bg = self.build(False)
        self.bg_b = self.build(True)
        self.ash = Ash(220, seed=21, color=(190, 190, 200), size=(2, 5), speed=(30, 90), glow=True)
        self.t_glass = ph_start(11)

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.1, ease_io(lt / (self.t1 - self.t0)))
        f = camera(self.bg_b if blink_at(t, 4) else self.bg, z, 540, 960)
        if t < self.t_glass:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            for i in range(6):
                ph = (lt * 1.6 + i / 6) % 1
                x, y = scr(700 - 20 * ph, 590 + ph * 360, z, 540, 960)
                r = 10 * z
                d.ellipse([x - r, y - r * 1.4, x + r, y + r], fill=(130, 190, 240, 230))
            f.alpha_composite(ov)
        dens = 0.55 + 0.45 * ease_io((t - self.t_glass) / 0.8)
        self.ash.draw(f, t, dens, wind=40)
        return finish(f, t)


# ---------------------------------------------------------------- 7. LEADER
class Leader(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, 520, (28, 30, 44), w=0)
        tiles(c, -MX, 520, W + MX, 1200, (52, 70, 78), (40, 56, 62), 64)
        c.rect(-MX, 1200, W + MX, H + MY, FLOOR, w=0)
        self.bg = paper_grain(c.done())
        self.ldr = leader()
        self.glow = radial((900, 900), (255, 200, 110, 200), power=1.5)
        self.you = adult("back")
        self.kid = girl("back")
        r = random.Random(17)
        self.crowd = []
        for i in range(14):
            sx, sy = r.uniform(40, 1040), r.uniform(1250, 1820)
            row = i // 2
            side = -1 if i % 2 == 0 else 1
            tx = 540 + side * (130 + 40 * row)
            ty = 1500 + 46 * row
            self.crowd.append((sx, sy, tx, ty, r.uniform(0, 6), r.uniform(0, 0.8)))
        self.t_follow = ph_start(14)

    def frame(self, t):
        lt = t - self.t0
        z = 1.02
        f = camera(self.bg, z, 540, 960)
        gp = 0.8 + 0.2 * math.sin(t * 2.4)
        put(f, with_alpha(self.glow, gp), 750, 950, anchor="center")
        put(f, self.ldr, 540, 1480, scale=1.05)
        k_all = (t - self.t_follow) / 2.0
        items = []
        for (sx, sy, tx, ty, ph, dl) in self.crowd:
            k = ease_io(k_all - dl * 0.6) if t > self.t_follow else 0
            x, y = lerp(sx, tx, k), lerp(sy, ty, k)
            jitter = (1 - k) * 10 * math.sin(t * 9 + ph)
            hh = lerp(320, 520, (y - 1200) / 700)
            items.append((y, x + jitter, hh, ph, k))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for y, x, hh, ph, k in sorted(items):
            col = mix((22, 20, 30), (60, 52, 46), k * 0.6) + (235,)
            silhouette(d, x, y, hh, col, panic=1 - k, ph=ph + t * (12 if k < 0.9 else 4))
        f.alpha_composite(ov)
        k0 = ease_io((t - self.t_follow + 0.3) / 1.4) if t > self.t_follow - 0.3 else 0
        put(f, self.you, lerp(200, 380, k0), lerp(1960, 1880, k0), scale=0.95)
        put(f, self.kid, lerp(330, 470, k0), lerp(1960, 1890, k0), scale=0.95)
        return finish(f, t)


# ---------------------------------------------------------------- 8. DOOR
class Door(Scene):
    D = (130, 720, 470, 1380)

    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (30, 30, 40), w=0)
        # главный тоннель справа (опасный)
        c.poly([(540, 400), (W + MX, 260), (W + MX, H + MY), (540, 1500)], (60, 40, 40), w=0)
        for k, col in enumerate([(120, 60, 40), (190, 80, 36), (255, 120, 40), (255, 180, 90)]):
            x1, x2, y1, y2 = 600 + k * 45, 1060 - k * 45, 700 + k * 40, 1140 - k * 8
            c.rect(x1, y1 + (x2 - x1) / 2, x2, y2, col, w=6 if k == 0 else 0)
            c.ellipse(x1, y1, x2, y1 + (x2 - x1), col, w=6 if k == 0 else 0)
        for i in range(10):
            f = i / 10
            c.line([(lerp(810, W + MX, f ** 1.5), lerp(1120, H + MY, f ** 1.5)),
                    (lerp(860, W + MX, f ** 1.5) + 200 * f, lerp(1120, H + MY, f ** 1.5))], (90, 70, 60), 6)
        c.line([(760, 1120), (300 + 600, H + MY)], (150, 140, 130), 10)
        c.line([(860, 1120), (W + MX + 200, H + MY)], (150, 140, 130), 10)
        # левая стена с дверью
        c.poly([(-MX, -MY), (540, 400), (540, 1500), (-MX, H + MY)], (68, 72, 84))
        x1, y1, x2, y2 = self.D
        c.rect(x1 - 20, y1 - 20, x2 + 20, y2, (40, 42, 50), w=8)
        c.rect(x1, y1, x2, y2, (10, 10, 14), w=6)
        c.rect(x1 - 30, y1 - 140, x2 + 30, y1 - 50, (40, 150, 80), w=6, r=8)
        c.text((x1 + x2) / 2, y1 - 95, "СЛУЖЕБНЫЙ ПРОХОД", 28, (255, 255, 255))
        c.line([(-MX, 1560), (540, 1500)], (100, 100, 110), 8)
        self.bg = paper_grain(c.done())
        self.you = adult("back", arm_out=True)
        self.kid = girl("back")
        self.smoke = [(random.Random(i).uniform(560, 1100), random.Random(i + 50).uniform(500, 1300),
                       random.Random(i + 99).uniform(80, 200)) for i in range(14)]
        self.t_open = self.t0 + 0.5

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.12, ease_io(lt / (self.t1 - self.t0)))
        cx, cy = lerp(540, 420, ease_io(lt / 4)), 1050
        f = camera(self.bg, z, cx, cy)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for (sx, sy, r) in self.smoke:
            x = sx + 30 * math.sin(t * 0.7 + sy)
            y = sy - (t * 40 + sx) % 300
            px, py = scr(x, y, z, cx, cy)
            d.ellipse([px - r * z, py - r * z, px + r * z, py + r * z], fill=(90, 70, 70, 70))
        ov = ov.filter(ImageFilter.GaussianBlur(14))
        f.alpha_composite(ov)
        # дверь открывается
        x1, y1, x2, y2 = self.D
        k = ease_out((t - self.t_open) / 1.2)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        dw = (x2 - x1) * (1 - 0.8 * k)
        pts = [(x2 - dw, y1 - 30 * k), (x2, y1), (x2, y2), (x2 - dw, y2 + 30 * k)]
        sp = [scr(x, y, z, cx, cy) for x, y in pts]
        d.polygon(sp, fill=(120, 124, 132, 255), outline=(20, 17, 28, 255), width=int(6 * z))
        hx, hy = scr(x2 - dw + 30, (y1 + y2) / 2, z, cx, cy)
        d.ellipse([hx - 12 * z, hy - 12 * z, hx + 12 * z, hy + 12 * z], fill=(220, 200, 100, 255))
        if k > 0.2:
            bx, by = scr(560, 1560, z, cx, cy)
            tx1, ty1 = scr(x1 + 10, y1 + 80, z, cx, cy)
            tx2, ty2 = scr(x2 - dw - 10, y2 - 40, z, cx, cy)
            d.polygon([(bx, by), (tx1, ty1), (tx2, ty2)], fill=(255, 230, 150, int(90 * k)))
        f.alpha_composite(ov)
        wk = ease_io(lt / (self.t1 - self.t0))
        put(f, self.you, lerp(600, 520, wk), lerp(2060, 1990, wk), scale=1.15 - 0.1 * wk)
        put(f, self.kid, lerp(800, 700, wk), lerp(2060, 1990, wk), scale=1.15 - 0.1 * wk)
        return finish(f, t)


# ---------------------------------------------------------------- 9. GAS (схема-разрез)
class Gas(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.vgrad(-MX, -MY, W + MX, 480, (255, 150, 60), (230, 90, 40))
        c.poly([(700, 480), (880, 300), (940, 300), (1150, 480)], (90, 36, 40), w=6)
        c.rect(-MX, 480, W + MX, H + MY, (66, 50, 44), w=0)
        for y in (700, 1000, 1500, 1800):
            c.line([(-MX, y), (W + MX, y + 40)], (80, 62, 54), 10)
        for x in range(-60, 640, 110):
            c.rect(x, 380, x + 90, 480, (50, 30, 44), w=5)
        # нижний (опасный) тоннель с провалом
        self.low = [(-MX, 1000), (200, 1000), (420, 1340), (660, 1340), (880, 1000), (W + MX, 1000)]
        self.up = [(-MX, 760), (W + MX, 760)]
        c.line(self.low, (24, 22, 28), 190)
        c.line(self.low, (120, 112, 104), 150)
        c.line(self.up, (24, 22, 28), 130)
        c.line(self.up, (150, 140, 128), 96)
        c.text(260, 640, "СЛУЖЕБНЫЙ ХОД", 34, (255, 255, 255), stroke=5)
        self.bg = paper_grain(c.done())
        m = Canvas(ss=1, bg=(0, 0, 0, 0))
        m.line(self.low, (255, 255, 255), 150)
        self.mask = m.done().getchannel("A")
        self.you = adult("front", worried=False)
        self.kid = girl("front")
        self.skull = font(120)

    def frame(self, t):
        lt = t - self.t0
        z, cx, cy = 1.0, 540, 960
        f = camera(self.bg, z, cx, cy)
        # газ заполняет низину
        lvl = lerp(1430, 1170, ease_io(lt / 3.5))
        gas = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
        d = ImageDraw.Draw(gas)
        pts = [(x, lvl + MY + 14 * math.sin(x / 60 + t * 3)) for x in range(0, LW + 30, 30)]
        d.polygon(pts + [(LW, LH), (0, LH)], fill=(120, 210, 80, 200))
        gm = Image.new("L", (LW, LH), 0)
        gm.paste(gas.getchannel("A"), (0, 0), self.mask)
        gas.putalpha(gm)
        f.alpha_composite(camera(gas, z, cx, cy))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        if lt > 1.2:
            a = int(255 * clamp((lt - 1.2) / 0.3))
            d.text((540, 1250), "☠", font=self.skull, fill=(30, 40, 20, a), anchor="mm")
        # красный крест на спуске
        k = ease_back((t - ph_start(18)) / 0.25)
        if t > ph_start(18):
            r = 70 * k
            for sx, sy in [(330, 1180)]:
                d.line([(sx - r, sy - r), (sx + r, sy + r)], fill=(230, 40, 40, 255), width=22)
                d.line([(sx - r, sy + r), (sx + r, sy - r)], fill=(230, 40, 40, 255), width=22)
        # стрелка вверх
        bob = 10 * math.sin(t * 5)
        d.polygon([(860, 560 + bob), (920, 640 + bob), (885, 640 + bob), (885, 700 + bob), (835, 700 + bob),
                   (835, 640 + bob), (800, 640 + bob)], fill=(255, 214, 64, 255), outline=(20, 17, 28, 255))
        f.alpha_composite(ov)
        wk = lt / (self.t1 - self.t0)
        put(f, self.you, lerp(420, 640, wk), 800, scale=0.4)
        put(f, self.kid, lerp(500, 720, wk), 800, scale=0.4)
        return finish(f, t)


# ---------------------------------------------------------------- 10. HUSH
class Hush(Scene):
    def build(self, blink):
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (54, 56, 64), w=0)
        for y in (500, 560):
            c.line([(-MX, y), (W + MX, y)], (90, 84, 76), 26)
            c.line([(-MX, y), (W + MX, y)], INK, 4)
        c.rect(-MX, 1500, W + MX, H + MY, (40, 40, 48), w=0)
        c.rect(860, 360, 960, 440, (255, 220, 140), w=6, r=10)
        for x in (875, 905, 935):
            c.line([(x, 360), (x, 440)], (60, 60, 60), 4)
        # девочка крупно: плащ, голова, рука с пальцем у губ, фонарик
        cx, cy = 540, 980
        c.poly([(330, 1220), (750, 1220), (900, H + MY), (180, H + MY)], YEL)
        c.line([(540, 1230), (540, H + MY)], YEL_D, 6)
        c.circle(cx, cy, 300, YEL, w=8)
        c.ellipse(cx - 220, cy - 230, cx + 220, cy + 250, SKIN, w=8)
        c.poly([(cx - 226, cy - 60), (cx - 180, cy - 190), (cx - 60, cy - 240), (cx + 100, cy - 240),
                (cx + 200, cy - 180), (cx + 226, cy - 60), (cx + 170, cy - 100), (cx + 90, cy - 160),
                (cx, cy - 110), (cx - 100, cy - 170), (cx - 170, cy - 90)], GHAIR, w=8)
        ey = cy + 10
        if blink:
            c.line([(cx - 120, ey), (cx - 60, ey)], INK, 9)
            c.line([(cx + 60, ey), (cx + 120, ey)], INK, 9)
        else:
            c.circle(cx - 88, ey, 28, INK, w=0)
            c.circle(cx + 88, ey, 28, INK, w=0)
            c.circle(cx - 78, ey - 10, 9, (255, 255, 255), w=0)
            c.circle(cx + 98, ey - 10, 9, (255, 255, 255), w=0)
        c.circle(cx - 150, cy + 90, 26, BLUSH, w=0)
        c.circle(cx + 150, cy + 90, 26, BLUSH, w=0)
        c.ellipse(cx - 30, cy + 140, cx + 30, cy + 160, (170, 70, 70), w=5)
        # рука у губ
        c.poly([(320, 1500), (420, 1470), (520, 1240), (470, 1210)], YEL)
        c.ellipse(cx - 50, cy + 160, cx + 20, cy + 260, SKIN, w=7)
        c.rect(cx - 18, cy + 60, cx + 6, cy + 190, SKIN, w=6, r=12)
        # фонарик в другой руке
        c.poly([(760, 1500), (860, 1560), (900, 1420), (820, 1380)], YEL)
        c.rect(800, 1300, 900, 1420, (60, 64, 80), w=7, r=10)
        c.rect(790, 1270, 910, 1310, (200, 200, 210), w=7, r=8)
        c.ellipse(840, 1380, 920, 1450, SKIN, w=7)
        return paper_grain(c.done())

    def __init__(self, *a):
        super().__init__(*a)
        self.bg = self.build(False)
        self.bg_b = self.build(True)
        s = Canvas(ss=1)
        s.poly([(800, 1290), (910, 1290), (1250, 600), (700, 420)], SAFE_YEL + (90,), outline=None)
        self.beam = s.done(blur=24)
        self.t_count = word_t(22, "считать")

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.06, ease_io(lt / (self.t1 - self.t0)))
        f = camera(self.bg_b if blink_at(t, 6) else self.bg, z, 540, 1000)
        f.alpha_composite(with_alpha(camera(self.beam, z, 540, 1000), 0.8 + 0.2 * math.sin(t * 7)))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        if ph_start(21) - 0.1 < t < self.t_count:
            a = clamp((t - ph_start(21)) / 0.3)
            d.text((260, 900), "ТСС…", font=font(64), fill=(255, 255, 255, int(220 * a)), anchor="mm",
                   stroke_width=6, stroke_fill=(20, 17, 28, int(220 * a)))
        if t >= self.t_count:
            n = int((t - self.t_count) / 0.55) + 1
            for i in range(max(1, n - 2), n + 1):
                age = t - self.t_count - (i - 1) * 0.55
                s = ease_back(age / 0.2)
                a = clamp(1 - (age - 0.6) / 0.6)
                x = 200 + (i % 3) * 30
                y = 880 - age * 120
                d.text((x, y), str(i), font=font(int(90 * s) + 1), fill=(255, 222, 80, int(255 * a)), anchor="mm",
                       stroke_width=7, stroke_fill=(20, 17, 28, int(255 * a)))
        f.alpha_composite(ov)
        return finish(f, t)


# ---------------------------------------------------------------- 11. GATE
class Gate(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (44, 44, 52), w=0)
        c.ellipse(40, 300, 1040, 1300, (70, 70, 78), w=10)
        c.rect(40, 800, 1040, 1650, (70, 70, 78), w=0)
        c.line([(40, 800), (40, 1650)], INK, 10)
        c.line([(1040, 800), (1040, 1650)], INK, 10)
        c.ellipse(100, 360, 980, 1240, (96, 100, 108), w=8)
        c.rect(100, 800, 980, 1600, (96, 100, 108), w=0)
        c.line([(100, 800), (100, 1600)], INK, 8)
        c.line([(980, 800), (980, 1600)], INK, 8)
        c.line([(540, 365), (540, 1600)], INK, 10)
        for x in (150, 930):
            for y in range(480, 1580, 90):
                c.circle(x, y, 10, (130, 134, 140), w=4)
        c.circle(540, 1000, 130, (130, 60, 50), w=10)
        for a in range(0, 360, 45):
            c.line([(540, 1000), (540 + 130 * math.cos(math.radians(a)), 1000 + 130 * math.sin(math.radians(a)))],
                   (90, 40, 34), 12)
        c.circle(540, 1000, 30, (90, 40, 34), w=6)
        for i in range(12):
            x = 100 + i * 74
            c.poly([(x, 1520), (x + 37, 1520), (x + 74, 1600), (x + 37, 1600)], (240, 196, 40), w=0)
        c.rect(100, 1520, 980, 1600, None, w=6)
        c.rect(330, 1680, 750, 1760, (200, 196, 180), w=6, r=6)
        c.text(540, 1720, "ГЕРМОЗАТВОР", 40, (30, 30, 36))
        c.rect(-MX, 1650, W + MX, H + MY, (36, 36, 44), w=0)
        c.rect(330, 1680, 750, 1760, (200, 196, 180), w=6, r=6)
        c.text(540, 1720, "ГЕРМОЗАТВОР", 40, (30, 30, 36))
        self.bg = paper_grain(c.done())
        s = Canvas(ss=1)
        s.rect(528, 365, 552, 1600, (255, 70, 30, 255), outline=None, w=0)
        self.seam = s.done(blur=18)
        self.dust = Ash(90, seed=31, color=(150, 140, 130), size=(2, 4), speed=(120, 220), region=(0, 0, W, H))

    def frame(self, t):
        lt = t - self.t0
        dur = self.t1 - self.t0
        z = lerp(1.0, 1.14, ease_io(lt / dur))
        rumble = max(0, math.sin(lt * 2.2)) ** 6
        f = camera(self.bg, z, 540, 1000, 10 * rumble * (1 - lt / dur), t)
        a = clamp((0.6 + 0.4 * math.sin(t * 3.5)) * (1 - 0.6 * lt / dur))
        f.alpha_composite(with_alpha(camera(self.seam, z, 540, 1000), a))
        f.alpha_composite(with_alpha(camera(self.seam, z, 540, 1000), a))
        self.dust.draw(f, t, 0.3 + 0.7 * rumble, wind=0)
        v = VIG if lt < dur * 0.5 else VIG_STRONG
        return finish(f, t, v)


# ---------------------------------------------------------------- 12. RESCUE
class Rescue(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (16, 16, 22), w=0)
        c.rect(-MX, 1350, W + MX, H + MY, (60, 60, 62), w=0)
        for i in range(30):
            r = random.Random(i)
            x, y = r.uniform(-MX, W + MX), r.uniform(1380, H + MY)
            c.ellipse(x - 80, y - 14, x + 80, y + 14, (90, 90, 92), w=0)
        tiles(c, -MX, 500, W + MX, 1350, (34, 40, 44), (26, 30, 34), 64)
        self.bg = paper_grain(c.done())
        self.res = rescuer("front")
        self.ash = Ash(80, seed=41, color=(160, 160, 160), size=(1, 3), speed=(20, 50))

    def frame(self, t):
        lt = t - self.t0
        z = 1.0
        f = camera(self.bg, z, 540, 960)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for (x0, ang0, sp) in [(330, -0.4, 1.3), (760, 0.5, -1.1)]:
            ang = ang0 + 0.5 * math.sin(lt * sp)
            sx, sy = x0, 860
            L = 1500
            a1, a2 = ang - 0.18, ang + 0.18
            d.polygon([(sx, sy), (sx + L * math.sin(a1), sy + L * math.cos(a1)),
                       (sx + L * math.sin(a2), sy + L * math.cos(a2))], fill=(255, 250, 220, 70))
        ov = ov.filter(ImageFilter.GaussianBlur(16))
        f.alpha_composite(ov)
        step = lt * 1.6
        for x0, ph in [(330, 0), (760, 1.6)]:
            bob = abs(math.sin(step * math.pi + ph)) * 10
            put(f, self.res, x0, 1720 - bob, scale=1.2 + 0.03 * lt)
        self.ash.draw(f, t, 0.7, wind=0)
        return finish(f, t, VIG_STRONG)


# ---------------------------------------------------------------- 13-14. GHOST
class Ghost(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (20, 22, 28), w=0)
        tiles(c, -MX, 300, W + MX, 1400, (40, 48, 54), (30, 36, 40), 64)
        c.rect(-MX, 1400, W + MX, H + MY, (62, 62, 64), w=0)
        self.bg = paper_grain(c.done())
        # меловые отметки — 31 день
        m = Canvas()
        for g in range(6):
            gx, gy = 120 + (g % 3) * 170, 560 + (g // 3) * 170
            n = 5 if g < 6 else 1
            for k in range(min(5, 31 - g * 5)):
                if k < 4:
                    m.line([(gx + k * 28, gy), (gx + k * 28 + 6, gy + 110)], (230, 230, 220), 7)
                else:
                    m.line([(gx - 14, gy + 80), (gx + 110, gy + 20)], (230, 230, 220), 7)
        m.line([(120, 920), (126, 1030)], (230, 230, 220), 7)
        m.text(800, 640, "МЫ ЖДЁМ", 44, (230, 230, 220))
        self.chalk = m.done()
        self.you = adult("front", ghost=True, worried=False)
        self.kid = girl("front", ghost=True)
        self.you_b = adult("front", ghost=True, worried=False, blink=True)
        self.res = rescuer("back")
        s = Canvas(ss=1)
        s.poly([(200, 1500), (250, 1440), (1100, 600), (1100, 1500)], (255, 250, 220, 110), outline=None)
        self.beam = s.done(blur=30)
        self.t_none = word_t(27, "никто")

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.12, ease_io(lt / (self.t1 - self.t0)))
        cx, cy = 640, 1040
        layer = self.bg.copy()
        ca = 0.25 + 0.75 * ease_io((t - self.t_none) / 0.8)
        layer.alpha_composite(with_alpha(self.chalk, ca))
        ga = 1.0 - 0.8 * ease_io((t - self.t_none + 0.2) / 1.6)
        sp = self.you_b if blink_at(t, 9) else self.you
        put(layer, sp, 700 + MX, 1560 + MY, alpha=ga, scale=1.05)
        put(layer, self.kid, 880 + MX, 1560 + MY, alpha=ga, scale=1.05)
        layer.alpha_composite(self.beam)
        f = camera(layer, z, cx, cy)
        put(f, self.res, *scr(210, 2250, z, cx, cy), scale=z * 1.6)
        return finish(f, t, VIG_STRONG)


# ---------------------------------------------------------------- 15. FINAL
class Final(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (12, 12, 20), w=0)
        # фонарик
        c.rect(470, 520, 610, 820, (60, 64, 80), w=8, r=16)
        c.rect(450, 470, 630, 540, (200, 200, 210), w=8, r=10)
        c.ellipse(470, 476, 610, 532, SAFE_YEL, w=6)
        c.rect(500, 600, 580, 640, (240, 190, 50), w=5, r=6)
        self.bg = c.done()
        self.glow = radial((900, 900), SAFE_YEL + (160,), power=1.6)
        self.ash = Ash(70, seed=51, color=(150, 140, 135), size=(1, 3), speed=(20, 50))

    def frame(self, t):
        lt = t - self.t0
        f = camera(self.bg, 1.0)
        put(f, with_alpha(self.glow, 0.7 + 0.3 * math.sin(t * 3)), 540, 500, anchor="center")
        self.ash.draw(f, t, 0.6, wind=0)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        a = clamp(lt / 0.4)
        A = int(255 * a)
        fq = font(78)
        d.text((540, 1000), "А ВЫ БЫ ПОШЛИ", font=fq, fill=(255, 255, 255, A), anchor="mm", stroke_width=7,
               stroke_fill=(10, 10, 16, A))
        d.text((540, 1095), "ЗА ТОЛПОЙ?", font=fq, fill=(255, 214, 64, A), anchor="mm", stroke_width=7,
               stroke_fill=(10, 10, 16, A))
        for i, (label, col, x) in enumerate([("ДА", (230, 60, 50), 340), ("НЕТ", (60, 200, 90), 740)]):
            k = clamp((lt - 0.6 - i * 0.35) / 0.35)
            if k <= 0:
                continue
            y = 1290 + 12 * (1 - ease_out(k))
            pulse = 0.5 + 0.5 * math.sin(t * 4 + i * 1.5)
            Ak = int(255 * k)
            bw, bh = 300, 110
            d.rounded_rectangle([x - bw / 2 - 6, y - bh / 2 - 6, x + bw / 2 + 6, y + bh / 2 + 6], radius=60,
                                outline=col + (int(Ak * 0.35 * pulse),), width=10)
            d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=55,
                                fill=(22, 22, 32, Ak), outline=col + (Ak,), width=7)
            d.text((x, y), label, font=font(56), fill=(255, 255, 255, Ak), anchor="mm")
        k = clamp((lt - 1.6) / 0.5)
        d.text((540, 1470), "РЕШАТЬ ВАМ.", font=font(48), fill=(220, 220, 230, int(255 * k)), anchor="mm")
        f.alpha_composite(ov)
        return finish(f, t)


CLASSES = dict(hook=Hook, sky=Sky, train=Train, child=Child, phone=Phone, cloth=Cloth, leader=Leader, door=Door,
               gas=Gas, hush=Hush, gate=Gate, rescue=Rescue, ghost=Ghost, final=Final)
_cache = {}


def get_scene(i):
    if i not in _cache:
        name, t0 = SCENES[i]
        t1 = SCENES[i + 1][1] if i + 1 < len(SCENES) else TOTAL
        _cache[i] = CLASSES[name](t0, t1)
    return _cache[i]


# ======================================================================= HUD
HUD_TIMES = {"hook": "14:07", "sky": "14:07", "train": "14:09", "child": "14:10", "phone": "14:12",
             "cloth": "14:15", "leader": "14:21", "door": "14:34", "gas": "14:52", "hush": "15:20",
             "gate": "16:03", "rescue": "??:??", "ghost": "??:??"}
HUD_BADGE = {"hook": "ТРЕВОГА", "sky": "ТРЕВОГА", "train": "ТРЕВОГА", "child": "ТРЕВОГА",
             "phone": "СОВЕТ 1/6", "cloth": "СОВЕТ 2/6", "leader": "СОВЕТ 3/6", "door": "СОВЕТ 4/6",
             "gas": "СОВЕТ 5/6", "hush": "СОВЕТ 6/6", "gate": "ГЛАВНОЕ", "rescue": "ДЕНЬ 31", "ghost": "ДЕНЬ 31"}
BADGE_START = {"phone": ph_start(5), "cloth": ph_start(9), "leader": ph_start(12), "door": ph_start(15),
               "gas": ph_start(17), "hush": ph_start(20), "gate": ph_start(23)}


def hud_state(t):
    i = scene_at(t)
    name = SCENES[i][0]
    if name == "final":
        return None
    badge, since = HUD_BADGE[name], SCENES[i][1]
    if name in BADGE_START and t < BADGE_START[name]:
        badge, since = HUD_BADGE[SCENES[i - 1][0]], SCENES[i - 1][1]
        if SCENES[i - 1][0] in BADGE_START:
            since = BADGE_START[SCENES[i - 1][0]]
    elif name in BADGE_START:
        since = BADGE_START[name]
    elif name == "ghost":
        since = SCENES[i - 1][1]
    return HUD_TIMES[name], badge, since, SCENES[i][1], name


def draw_hud(frame, t):
    st = hud_state(t)
    if not st:
        return
    tm, badge, b_since, s_since, name = st
    ov = Image.new("RGBA", (W, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    glitch = t - s_since < 0.18 and s_since > 0
    fm = font(66, FONT_MONO)
    d.rounded_rectangle([390, 70, 690, 160], radius=20, fill=(12, 12, 20, 200), outline=(255, 255, 255, 40),
                        width=2)
    dy = random.Random(int(t * 30)).randint(-10, 10) if glitch else 0
    col = (255, 90, 70) if tm.startswith("?") else (240, 240, 240)
    d.text((540, 116 + dy), tm, font=fm, fill=col + ((120 if glitch else 255),), anchor="mm")
    line = "СТАНЦИЯ «ПЕПЕЛЬНАЯ» · ЛИНИЯ 3" if name not in ("rescue", "ghost") else "СТАНЦИЯ «ПЕПЕЛЬНАЯ» · ЗАКРЫТА"
    d.text((540, 196), line, font=font(28), fill=(230, 230, 236, 220), anchor="mm",
           stroke_width=3, stroke_fill=(0, 0, 0, 160))
    age = t - b_since
    s = 1.0 + 0.4 * (1 - ease_out(age / 0.18)) if age < 0.18 else 1.0
    fb = font(int(30 * s))
    bw = fb.getlength(badge) + 40 * s
    bc = (200, 150, 30) if badge == "ГЛАВНОЕ" else (176, 40, 40)
    if badge.startswith("ДЕНЬ") and age < 0.6 and int(age * 10) % 2 == 0:
        bc = (255, 60, 60)
    d.rounded_rectangle([540 - bw / 2, 248 - 26 * s, 540 + bw / 2, 248 + 26 * s], radius=int(14 * s),
                        fill=bc + (235,))
    d.text((540, 249), badge, font=fb, fill=(255, 255, 255, 255), anchor="mm")
    frame.alpha_composite(ov, (0, 0))


# ======================================================================= SUBTITLES
Y, R, O = (255, 214, 64), (240, 64, 52), (255, 150, 60)
HL = {0: {"извержение": R, "не": Y, "бегите": Y}, 1: {"оранжевым": O}, 3: {"погас": R}, 4: {"ребёнок": Y},
      5: {"первое": Y}, 7: {"карта": Y}, 8: {"голос": Y}, 9: {"второе": Y}, 10: {"ткань": Y},
      11: {"стекло": R}, 12: {"третье": Y}, 13: {"паникует": Y}, 15: {"четвёртое": Y},
      16: {"служебными": Y}, 17: {"пятое": Y}, 18: {"низины": R}, 19: {"газы": R, "видно": R},
      20: {"шестое": Y}, 21: {"тишину": Y}, 22: {"дело": Y}, 23: {"главное": Y}, 24: {"надолго": Y},
      25: {"месяц": Y}, 27: {"никто": R, "выжил": R, "выжил.": R}}


def build_chunks():
    chunks = []
    for i, (words, times) in enumerate(WT):
        n = len(words)
        k = max(1, math.ceil(n / 5))
        size = math.ceil(n / k)
        pairs = list(zip(words, times))
        groups = [pairs[j:j + size] for j in range(0, n, size)]
        for g in groups:
            chunks.append((i, g))
    out = []
    for k, (i, g) in enumerate(chunks):
        start = g[0][1] - 0.05
        nxt = chunks[k + 1][1][0][1] - 0.05 if k + 1 < len(chunks) else VOICE_END + 0.6
        end = min(nxt, PH[i][1] + 0.6)
        out.append((i, g, start, end))
    return out


CHUNKS = build_chunks()


def draw_subs(frame, t):
    for (i, g, s, e) in CHUNKS:
        if s <= t < e:
            words = []
            for w, wt in g:
                a = clamp((t - wt + 0.05) / 0.12)
                key = w.lower().strip(".,:!?…«»")
                col = HL.get(i, {}).get(key, (255, 255, 255))
                words.append((w.upper(), col, a))
            fade = clamp((e - t) / 0.12)
            words = [(a, b, c * fade) for a, b, c in words]
            draw_words(frame, words, 1330, size=74, maxw=930)
            return


# ======================================================================= compose
def render_frame(t):
    i = scene_at(t)
    sc = get_scene(i)
    f = sc.frame(t)
    if i > 0:
        name = SCENES[i][0]
        b = SCENES[i][1]
        if name in BLACK_DIP:
            k = clamp((t - b) / 0.6)
            darkness(f, 1 - k)
        elif t - b < XF / 2:
            prev = get_scene(i - 1).frame(t)
            k = 0.5 + (t - b) / XF
            f = Image.blend(prev, f, ease_io(k))
    if i + 1 < len(SCENES):
        b = SCENES[i + 1][1]
        nname = SCENES[i + 1][0]
        if nname in BLACK_DIP and b - t < 0.6:
            darkness(f, 1 - (b - t) / 0.6)
        elif nname not in BLACK_DIP and b - t < XF / 2:
            nxt = get_scene(i + 1).frame(t)
            k = 0.5 - (b - t) / XF
            f = Image.blend(f, nxt, ease_io(k))
    if t > TOTAL - 0.5:
        darkness(f, (t - (TOTAL - 0.5)) / 0.5)
    draw_hud(f, t)
    draw_subs(f, t)
    return f.convert("RGB")


def render_range(args):
    a, b, path = args
    enc = encoder(path)
    for n in range(a, b):
        enc.stdin.write(render_frame(n / FPS).tobytes())
    enc.stdin.close()
    enc.wait()
    return path


def stills():
    os.makedirs(os.path.join(OUT, "stills"), exist_ok=True)
    for i, (name, t0) in enumerate(SCENES):
        t1 = SCENES[i + 1][1] if i + 1 < len(SCENES) else TOTAL
        t = (t0 + t1) / 2 + (0.6 if name == "ghost" else 0)
        render_frame(t).save(os.path.join(OUT, "stills", f"{i:02d}_{name}.jpg"), quality=88)
        print(name, round(t, 2))


def main():
    os.makedirs(OUT, exist_ok=True)
    nfr = int(TOTAL * FPS)
    parts = 4
    step = math.ceil(nfr / parts)
    jobs = [(k * step, min(nfr, (k + 1) * step), os.path.join(OUT, f"part{k}.mp4")) for k in range(parts)]
    with Pool(parts) as p:
        files = p.map(render_range, jobs)
    lst = os.path.join(OUT, "parts.txt")
    with open(lst, "w") as fh:
        for fp in files:
            fh.write(f"file '{fp}'\n")
    import sound
    wav = sound.build(os.path.join(OUT, "mix.wav"), TOTAL, globals())
    final = os.path.join(OUT, "volcano_metro.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final],
                   check=True)
    for fp in files:
        os.remove(fp)
    os.remove(lst)
    print("done", final, TOTAL)


if __name__ == "__main__":
    if "--stills" in sys.argv:
        stills()
    else:
        main()
