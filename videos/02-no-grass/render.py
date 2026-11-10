"""Рендер ролика «Что если исчезнет вся трава?».

python3 render.py --stills   — контрольные кадры в out/stills/
python3 render.py            — полный рендер в out/no_grass.mp4
"""
import math
import os
import random
import subprocess
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
_spoken = list(PHRASES)
_spoken[0] = "В четырнадцать ноль-ноль на Земле исчезла вся трава."
SEGS0 = align(_spoken, speech_segments(VOICE))
# группы фраз и момент, когда группа звучит в ролике
GROUPS = [([0], 1.5), ([1, 2], 5.2), ([3, 4], 10.6), ([5], 21.4), ([6, 7], 33.6), ([8, 9], 46.2), ([10, 11], 58.6)]
CLIPS = []          # (src_start, src_end, dst_start)
SEGS = [None] * len(PHRASES)
for idx, target in GROUPS:
    s0 = SEGS0[idx[0]][0][0]
    s1 = SEGS0[idx[-1]][-1][1]
    off = target - s0
    CLIPS.append((max(0, s0 - 0.03), s1 + 0.12, target - (s0 - max(0, s0 - 0.03))))
    for i in idx:
        SEGS[i] = [(a + off, b + off) for a, b in SEGS0[i]]
PH = [(s[0][0], s[-1][1]) for s in SEGS]
WT = [word_times(p, s) for p, s in zip(PHRASES, SEGS)]


def ph_start(i):
    return PH[i][0]


def word_t(i, stem):
    words, times = WT[i]
    for w, t in zip(words, times):
        if stem in w.lower():
            return t
    return PH[i][0]


T_CLICK = 1.0
SCENES = [("park", 0.0), ("brown", 4.6), ("fields", 10.2), ("car", 15.4), ("shop", 20.8), ("price", 26.4),
          ("door", 28.8), ("road", 32.4), ("hug", 38.2), ("mud", 41.2), ("cow", 43.6), ("flat", 45.8),
          ("clock", 55.2), ("bushes", 57.5), ("turn", 60.6), ("petal", 62.6), ("end", 65.6)]
TOTAL = 70.6
XF = 0.4
HARD_CUT = {"price", "door", "clock", "bushes", "petal"}


def scene_at(t):
    idx = 0
    for i, (_, s) in enumerate(SCENES):
        if t >= s:
            idx = i
    return idx


VIG = vignette(0.55)
VIG_STRONG = vignette(0.95)
GRAIN = grain_frames()

SKY_T, SKY_B = (140, 196, 236), (214, 234, 240)
HAZE_T, HAZE_B = (196, 176, 150), (226, 206, 176)
GRASS = (112, 180, 78)
GRASS_D = (84, 148, 60)
DIRT = (142, 106, 74)
DIRT_D = (116, 84, 58)
TREE = (62, 122, 72)
TREE_D = (46, 96, 56)
GREEN_GLOW = (120, 255, 120)


def scr(x, y, z, cx, cy):
    return ((x - cx) * z + W / 2, (y - cy) * z + H / 2)


def finish(frame, t, vig=VIG):
    frame.alpha_composite(vig)
    frame.alpha_composite(GRAIN[int(t * 8) % len(GRAIN)])
    return frame


def blink_at(t, seed=0):
    r = random.Random(seed)
    tt = 0.0
    while tt < TOTAL:
        tt += r.uniform(2.0, 4.5)
        if tt <= t < tt + 0.11:
            return True
    return False


def sky(c, top=-MY, bot=1000, hazy=False):
    c.vgrad(-MX, top, W + MX, bot, *(HAZE_T, HAZE_B) if hazy else (SKY_T, SKY_B))


def trees(c, y, seed=1, n=9, scale=1.0, col=TREE):
    r = random.Random(seed)
    for i in range(n):
        x = -60 + i * (1200 / n) + r.uniform(-30, 30)
        s = scale * r.uniform(0.8, 1.2)
        c.rect(x - 12 * s, y - 90 * s, x + 12 * s, y, (96, 70, 50), w=4)
        for dx, dy, rr in [(0, -150, 80), (-50, -110, 60), (50, -110, 60)]:
            c.circle(x + dx * s, y + dy * s, rr * s, col, w=5)


def ground(c, y, green, seed=3):
    r = random.Random(seed)
    c.rect(-MX, y, W + MX, H + MY, GRASS if green else DIRT, w=0)
    for _ in range(260):
        x = r.uniform(-MX, W + MX)
        yy = r.uniform(y + 20, H + MY)
        s = 0.5 + (yy - y) / 1000
        if green:
            c.line([(x - 10 * s, yy), (x - 4 * s, yy - 22 * s), (x, yy), (x + 6 * s, yy - 26 * s), (x + 10 * s, yy)],
                   GRASS_D, 4)
        else:
            if r.random() < 0.5:
                c.line([(x, yy), (x + 30 * s, yy + 6 * s), (x + 50 * s, yy - 4 * s)], DIRT_D, 3)
            else:
                c.ellipse(x - 8 * s, yy - 5 * s, x + 8 * s, yy + 5 * s, DIRT_D, w=0)


def bubble(frame, x, y, text, k):
    if k <= 0:
        return
    s = ease_back(k)
    f = font(int(54 * s) + 1)
    tw = f.getlength(text)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    bw, bh = tw + 60 * s, 100 * s
    d.polygon([(x - 20 * s, y + bh / 2 - 6), (x + 30 * s, y + bh / 2 - 6), (x + 10 * s, y + bh / 2 + 40 * s)],
              fill=(255, 255, 255, 255), outline=INK + (255,))
    d.rounded_rectangle([x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2], radius=int(40 * s), fill=(255, 255, 255, 255),
                        outline=INK + (255,), width=6)
    d.text((x, y), text, font=f, fill=INK + (255,), anchor="mm")
    frame.alpha_composite(ov)


def stamp(frame, x, y, text, k, fill=(255, 214, 64), fg=INK, rot=-4, size=72):
    if k <= 0:
        return
    s = 1.5 - 0.5 * ease_out(k / 0.6) if k < 0.6 else 1.0
    f = font(size)
    tw = f.getlength(text)
    im = Image.new("RGBA", (int(tw + 90), size + 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, im.width - 6, im.height - 6], fill=fill + (255,), outline=INK + (255,), width=7)
    d.text((im.width / 2, im.height / 2), text, font=f, fill=fg + (255,), anchor="mm")
    im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    put(frame, im, x, y, scale=s, anchor="center", alpha=clamp(k * 4))


# ======================================================================= scenes
class Scene:
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1


class Park(Scene):
    BL = [(250, 1400), (830, 1400), (940, 1720), (140, 1720)]

    def __init__(self, *a):
        super().__init__(*a)
        self.layers = []
        for green in (True, False):
            c = Canvas()
            sky(c, bot=1050)
            trees(c, 1050, seed=2)
            ground(c, 1040, green)
            self.layers.append(paper_grain(c.done()))
        b = Canvas()
        q = self.BL
        n, m = 7, 5
        for i in range(n):
            for j in range(m):
                def P(u, v):
                    top = (lerp(q[0][0], q[1][0], u), q[0][1])
                    bot = (lerp(q[3][0], q[2][0], u), q[3][1])
                    return (lerp(top[0], bot[0], v), lerp(top[1], bot[1], v))
                pts = [P(i / n, j / m), P((i + 1) / n, j / m), P((i + 1) / n, (j + 1) / m), P(i / n, (j + 1) / m)]
                b.poly(pts, (220, 70, 66) if (i + j) % 2 == 0 else (246, 240, 230), w=0)
        b.poly(q, None, w=7)
        b.rect(760, 1440, 880, 1520, (190, 140, 80), w=6, r=10)
        b.line([(770, 1450), (800, 1400), (840, 1400), (870, 1450)], (150, 104, 60), 6)
        b.circle(700, 1500, 26, (230, 60, 50), w=5)
        self.blanket = b.done()
        self.art = [artyom("sit", "smile"), artyom("sit", "shock")]
        self.art_b = artyom("sit", "smile", blink=True)
        self.son = sonya("stand", "out")
        self.son_b = sonya("stand", "out", blink=True)
        self.dust = Ash(60, seed=4, color=(170, 140, 110), size=(4, 10), speed=(-60, -20), region=(100, 1300, 1000, 1800))

    def frame(self, t):
        lt = t - self.t0
        after = t >= T_CLICK
        drop = 26 * ease_out((t - T_CLICK) / 0.25) if after else 0
        sh = 18 * max(0, 1 - (t - T_CLICK) / 0.5) if after else 0
        z = lerp(1.0, 1.08, ease_io(lt / (self.t1 - self.t0)))
        cx, cy = 540, 1150
        f = camera(self.layers[1 if after else 0], z, cx, cy, sh, t)
        f.alpha_composite(camera(self.blanket, z, cx, cy - drop, sh, t))
        ax, ay = scr(420, 1640 + drop, z, cx, cy)
        put(f, self.art_b if (blink_at(t, 1) and not after) else self.art[1 if after else 0], ax, ay, scale=z * 1.25)
        sx, sy = scr(800, 1700 + drop, z, cx, cy)
        put(f, self.son_b if blink_at(t, 2) else self.son, sx, sy, scale=z * 1.3)
        if after and t < T_CLICK + 1.5:
            self.dust.draw(f, t - T_CLICK, 1 - (t - T_CLICK) / 1.5, wind=60)
        bx, by = scr(860, 990, z, cx, cy)
        if t < T_CLICK + 0.4:
            bubble(f, bx, by, "Это тебе!", clamp((t - 0.1) / 0.25) * clamp((T_CLICK + 0.4 - t) / 0.15))
        if T_CLICK <= t < T_CLICK + 0.08:
            flash(f, 0.8)
        return finish(f, t)


class Brown(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        sky(c, bot=980, hazy=True)
        trees(c, 980, seed=5, n=11, scale=0.8)
        ground(c, 970, False, seed=8)
        r = random.Random(3)
        self.blankets = []
        for i in range(5):
            x, y = r.uniform(60, 1020), r.uniform(1050, 1250)
            col = [(90, 140, 210), (230, 180, 60), (200, 90, 140), (120, 200, 180), (240, 140, 80)][i]
            c.poly([(x - 90, y), (x + 90, y), (x + 110, y + 50), (x - 110, y + 50)], col, w=4)
            self.blankets.append((x, y + 30, r.uniform(0, 0.8)))
        self.bg = paper_grain(c.done())
        self.art = [artyom("stand", "worried", look=lk) for lk in (-1, 0, 1)]
        self.art_b = artyom("stand", "worried", blink=True)
        self.son = sonya("stand", "hold", expr="sad", look=0)
        self.son_b = sonya("stand", "hold", expr="sad", blink=True)
        self.dust = Ash(80, seed=12, color=(176, 146, 112), size=(2, 6), speed=(10, 40))

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.04, 1.0, ease_io(lt / (self.t1 - self.t0)))
        cx = lerp(520, 560, lt / 6)
        f = camera(self.bg, z, cx, 1150)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for (x, y, dl) in self.blankets:
            k = ease_out((lt - dl) / 0.5)
            hh = lerp(110, 200, k)
            jump = abs(math.sin((lt - dl) * 6)) * 20 * k
            sx, sy = scr(x, y - jump, z, cx, 1150)
            silhouette(d, sx, sy, hh * z, (60, 46, 50, 240), ph=lt * 6 + x, arms_up=k > 0.5 and (x > 500))
        # мяч катится по голой земле
        bx = lerp(-60, 1150, lt / 5.5)
        sx, sy = scr(bx, 1330, z, cx, 1150)
        r = 34 * z
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(250, 250, 250, 255), outline=INK + (255,), width=5)
        a = bx / 34
        for k in range(3):
            aa = a + k * 2.1
            px, py = sx + r * 0.5 * math.cos(aa), sy + r * 0.5 * math.sin(aa)
            d.ellipse([px - r * 0.25, py - r * 0.25, px + r * 0.25, py + r * 0.25], fill=INK + (255,))
        f.alpha_composite(ov)
        look = [0, -1, -1, 1, 1, 0, 0][int(lt / 0.9) % 7]
        ax, ay = scr(400, 1960, z, cx, 1150)
        put(f, self.art_b if blink_at(t, 3) else self.art[look + 1], ax, ay, scale=z * 1.35)
        sx, sy = scr(700, 1960, z, cx, 1150)
        put(f, self.son_b if blink_at(t, 4) else self.son, sx, sy, scale=z * 1.45)
        self.dust.draw(f, t, 0.6, wind=80)
        return finish(f, t)


class Fields(Scene):
    BANDS = [(-MY, 720, "wheat"), (720, 1380, "rice"), (1380, H + MY, "corn")]

    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        r = random.Random(1)
        for y1, y2, kind in self.BANDS:
            if kind == "wheat":
                c.rect(-MX, y1, W + MX, y2, (228, 188, 92), w=0)
                for y in range(int(y1), int(y2), 26):
                    for x in range(-MX, W + MX, 34):
                        xx = x + r.uniform(-6, 6) + (y % 52) / 2
                        c.line([(xx, y), (xx + 6, y + 14)], (196, 150, 60), 4)
            elif kind == "rice":
                c.rect(-MX, y1, W + MX, y2, (98, 172, 88), w=0)
                for k in range(9):
                    yy = y1 + k * 76
                    pts = [(x, yy + 26 * math.sin(x / 170 + k)) for x in range(-MX, W + MX + 40, 40)]
                    c.line(pts, (150, 210, 230), 10)
                    c.line([(p[0], p[1] + 14) for p in pts], (70, 140, 66), 6)
            else:
                c.rect(-MX, y1, W + MX, y2, (54, 128, 58), w=0)
                for x in range(-MX, W + MX, 60):
                    for y in range(int(y1) + 20, int(y2), 50):
                        c.line([(x - 18, y + 12), (x, y), (x + 18, y + 12)], (100, 176, 80), 5)
            c.line([(-MX, y2), (W + MX, y2)], (80, 70, 50), 10)
        self.fields = paper_grain(c.done())
        d = Canvas()
        d.rect(-MX, -MY, W + MX, H + MY, DIRT, w=0)
        for y in range(-MY, H + MY, 40):
            d.line([(-MX, y), (W + MX, y + 8)], DIRT_D, 5)
        for y1, y2, kind in self.BANDS:
            d.line([(-MX, y2), (W + MX, y2)], (90, 66, 46), 10)
        self.dirt = paper_grain(d.done())
        self.starts = [ph_start(3) - 0.2, word_t(4, "рис") - 0.1, word_t(4, "кукуруз") - 0.1]
        self.stamps = [("ХЛЕБ.", word_t(3, "пшениц"), 400, -5), ("РИС.", word_t(4, "рис"), 560, 4),
                       ("САХАР.", word_t(4, "сахар"), 720, -3), ("— ВСЁ", word_t(4, "тоже"), 900, 2)]

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.06, lt / (self.t1 - self.t0))
        f = camera(self.fields, z, 540, 960)
        dirt = camera(self.dirt, z, 540, 960)
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        for (y1, y2, kind), st in zip(self.BANDS, self.starts):
            p = clamp((t - st) / 1.3)
            if p <= 0:
                continue
            a, b = scr(0, y1, z, 540, 960)[1], scr(0, y2, z, 540, 960)[1]
            front = -100 + p * (W + 300)
            pts = [(-10, a)]
            for k in range(13):
                yy = lerp(a, b, k / 12)
                pts.append((front + 40 * math.sin(k * 1.3 + t * 4), yy))
            pts.append((-10, b))
            d.polygon(pts, fill=255)
        f.paste(dirt, (0, 0), m.filter(ImageFilter.GaussianBlur(6)))
        for text, ts, y, rot in self.stamps:
            stamp(f, 540, y, text, (t - ts) / 0.5 if t >= ts else 0,
                  fill=(240, 70, 56) if "ВСЁ" in text else (255, 214, 64),
                  fg=(255, 255, 255) if "ВСЁ" in text else INK, rot=rot, size=78)
        return finish(f, t)


class Car(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (40, 40, 48), w=0)
        c.rect(-MX, 200, 260, 1000, (196, 176, 150), w=10, r=30)      # боковое окно
        c.rect(-MX, 700, 260, 1000, DIRT, w=0)
        c.rect(300, 340, 980, 1500, (58, 58, 66), w=8, r=60)          # подголовник/кресло
        c.rect(420, 160, 860, 360, (58, 58, 66), w=8, r=40)
        self.bg = paper_grain(c.done())
        self.art = [artyom("stand", e, res=2) for e in ("neutral", "shock")]
        self.art_b = artyom("stand", "neutral", res=2, blink=True)
        p = Canvas(-260, -470, 520, 940, ss=2)
        p.rect(-250, -460, 250, 460, (24, 24, 30), w=8, r=50)
        p.rect(-220, -400, 220, 420, (236, 238, 244), w=0, r=14)
        p.rect(-220, -400, 220, -310, (210, 40, 40), w=0)
        p.text(0, -355, "СРОЧНО", 46, (255, 255, 255))
        p.rect(-190, -280, 190, -60, DIRT, w=4, r=8)
        for x in range(-180, 190, 40):
            p.line([(x, -200), (x + 30, -190)], DIRT_D, 4)
        self.phone = p.done()
        self.news = "ВО ВСЁМ МИРЕ ИСЧЕЗЛИ ПШЕНИЦА, РИС И КУКУРУЗА"
        self.t_freeze = self.t0 + 1.8

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.12, ease_io(lt / (self.t1 - self.t0)))
        f = camera(self.bg, z, 540, 960)
        sp = self.art[1] if t > self.t_freeze else (self.art_b if blink_at(t, 5) else self.art[0])
        ax, ay = scr(640, 2380, z, 540, 960)
        put(f, sp, ax, ay, scale=z * 1.05)
        cool = Image.new("RGBA", (W, H), (80, 140, 255, 40))
        f.alpha_composite(cool)
        ph = self.phone.copy()
        d = ImageDraw.Draw(ph)
        n = int(clamp((lt - 0.3) / 1.6) * len(self.news))
        words, lines, cur = self.news[:n].split(" "), [], ""
        fnt = font(40)
        for w in words:
            if fnt.getlength(cur + " " + w) > 400:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        for i, ln in enumerate(lines):
            d.text((50, 470 + i * 54), ln, font=fnt, fill=(20, 20, 26, 255))
        if int(t * 2) % 2 == 0 and n < len(self.news):
            d.text((50 + fnt.getlength(lines[-1]), 470 + (len(lines) - 1) * 54), "|", font=fnt, fill=(20, 20, 26, 255))
        put(f, ph.rotate(8, expand=True, resample=Image.BICUBIC), 330, 2050 + 60 * (1 - ease_out(lt / 0.5)))
        return finish(f, t, VIG_STRONG)


class Shop(Scene):
    SH = [520, 800, 1080, 1360]

    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (214, 216, 210), w=0)
        c.rect(300, 330, 780, 430, (230, 120, 40), w=6, r=10)
        c.text(540, 380, "ХЛЕБ · МУКА · КРУПЫ", 36, (255, 255, 255))
        c.rect(-MX, 470, W + MX, 1500, (232, 232, 228), w=8)
        for y in self.SH:
            c.rect(-MX, y, W + MX, y + 30, (150, 150, 156), w=5)
            for x in range(-40, 1120, 230):
                c.rect(x, y + 30, x + 90, y + 66, (255, 230, 80), w=3)
        for x, y in [(80, 520), (140, 520), (900, 800), (300, 1360)]:
            c.rect(x, y - 110, x + 60, y, (200, 80, 60), w=5, r=8)
        c.rect(-MX, 1500, W + MX, H + MY, (176, 176, 172), w=0)
        self.bg = paper_grain(c.done())
        b = Canvas(-90, -230, 180, 240)
        b.poly([(-80, -200), (80, -200), (86, 0), (-86, 0)], (248, 246, 240))
        b.poly([(-80, -200), (80, -200), (64, -226), (-64, -226)], (230, 228, 220), w=5)
        b.text(0, -130, "МУКА", 40, (60, 60, 70))
        for k in range(4):
            b.line([(-10 + k * 8, -90), (-20 + k * 8, -40)], (220, 170, 60), 6)
        self.bag = b.done()
        self.art = artyom("back", arm="out")
        a = Canvas()
        a.poly([(W + MX, 1240), (W + MX, 1340), (700, 1300), (700, 1230)], (60, 50, 60))
        a.circle(690, 1265, 34, (220, 180, 150))
        self.thief = a.done()
        self.t_grab, self.t_snatch = self.t0 + 1.0, self.t0 + 2.8

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.05, lt / (self.t1 - self.t0))
        sh = 16 * max(0, 1 - (t - self.t_snatch) / 0.4) if t > self.t_snatch else 0
        f = camera(self.bg, z, 540, 1000, sh, t)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for i, (x, ph) in enumerate([(80, 0), (1000, 1), (180, 2), (900, 3)]):
            sx, sy = scr(x + 20 * math.sin(t * 3 + ph), 2000 + 60 * (i // 2), z, 540, 1000)
            silhouette(d, sx, sy, 760 * z, (50, 46, 56, 255), ph=t * 8 + ph, arms_up=i % 2 == 0)
        f.alpha_composite(ov)
        shelf = (600, 1080)
        hand = (650, 1520)
        if t < self.t_grab:
            pos = shelf
        elif t < self.t_snatch:
            pos = tuple(lerp(a, b, ease_out((t - self.t_grab) / 0.5)) for a, b in zip(shelf, hand))
        else:
            k = ease_io((t - self.t_snatch - 0.25) / 0.45)
            pos = tuple(lerp(a, b, k) for a, b in zip(hand, (1350, 1300)))
        ax, ay = scr(300, 2280, z, 540, 1000)
        put(f, self.art, ax, ay, scale=z * 1.65)
        put(f, self.bag, *scr(pos[0], pos[1] + 30, z, 540, 1000), scale=z)
        if t > self.t_snatch - 0.3:
            k = ease_out((t - self.t_snatch + 0.3) / 0.3) - ease_io((t - self.t_snatch - 0.25) / 0.45)
            ox = (1 - clamp(k)) * 700
            f.alpha_composite(camera(self.thief, z, 540 - ox, 1000 - 60 + (pos[1] - 1300) * 0))
        return finish(f, t)


class Price(Scene):
    def frame(self, t):
        lt = t - self.t0
        f = Image.new("RGBA", (W, H), (60, 60, 66, 255))
        d = ImageDraw.Draw(f)
        d.rectangle([0, 1180, W, 1260], fill=(150, 150, 156, 255))
        s = 1.0 + 0.04 * lt
        tag = Image.new("RGBA", (760, 480), (0, 0, 0, 0))
        g = ImageDraw.Draw(tag)
        g.rounded_rectangle([8, 8, 752, 472], radius=24, fill=(255, 226, 70, 255), outline=INK + (255,), width=10)
        g.text((380, 80), "МУКА ПШЕНИЧНАЯ, 1 КГ", font=font(40), fill=INK + (255,), anchor="mm")
        g.text((380, 250), "99 ₽", font=font(170), fill=INK + (255,), anchor="mm")
        k = clamp((lt - 0.4) / 0.35)
        if k > 0:
            g.line([(110, 300), (110 + 540 * k, 200)], fill=(220, 30, 30, 255), width=22)
        put(f, tag.rotate(-3, expand=True, resample=Image.BICUBIC), 540, 960, scale=s, anchor="center")
        if lt > 1.0:
            stamp(f, 600, 1330, "990 ₽", (lt - 1.0) / 0.4, fill=(230, 40, 36), fg=(255, 255, 255), rot=-9, size=150)
        return finish(f, t)


class Door(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (120, 116, 112), w=0)
        c.rect(60, 300, 1020, 1520, (60, 64, 72), w=10)
        c.rect(90, 340, 530, 1500, (168, 200, 214), w=6)
        c.rect(550, 340, 990, 1500, (168, 200, 214), w=6)
        c.rect(400, 200, 680, 280, (40, 150, 80), w=6, r=8)
        c.text(540, 240, "ВХОД", 46, (255, 255, 255))
        c.rect(-MX, 1520, W + MX, H + MY, (150, 146, 140), w=0)
        self.bg = paper_grain(c.done())
        g = Canvas(ss=1)
        for x, y in [(90, 340), (550, 340)]:
            g.rect(x, y, x + 440, 1500, (255, 255, 255, 60), outline=None, w=0)
            g.line([(x + 40, y + 900), (x + 300, y + 200)], (255, 255, 255, 120), 18)
        self.glass = g.done()
        self.son = sonya("stand", "hold", expr="sad", res=2)
        self.son_b = sonya("stand", "hold", expr="sad", blink=True, res=2)

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.08, ease_io(lt / (self.t1 - self.t0)))
        f = camera(self.bg, z, 540, 1000)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for i in range(9):
            x = 120 + i * 105 + 30 * math.sin(t * 4 + i)
            sx, sy = scr(x, 1500, z, 540, 1000)
            silhouette(d, sx, sy, 520 * z, (40, 40, 52, 200), ph=t * 10 + i, arms_up=i % 3 == 0)
        f.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
        f.alpha_composite(camera(self.glass, z, 540, 1000))
        sx, sy = scr(540, 2080, z, 540, 1000)
        put(f, self.son_b if blink_at(t, 7) else self.son, sx, sy, scale=z * 0.82)
        return finish(f, t)


class Road(Scene):
    HZ = 900

    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.vgrad(-MX, -MY, W + MX, self.HZ, (206, 150, 96), (232, 196, 150))
        c.rect(-MX, self.HZ, W + MX, H + MY, DIRT, w=0)
        for k in range(12):
            y = self.HZ + (k / 12) ** 1.8 * 1300
            c.line([(-MX, y), (W + MX, y)], DIRT_D, 4)
        c.poly([(500, self.HZ), (580, self.HZ), (W + MX + 200, H + MY), (-MX - 200, H + MY)], (80, 80, 86), w=0)
        self.bg = paper_grain(c.done())
        w = Canvas(-100, -1400, 1300, 1450, ss=1)
        r = random.Random(3)
        for i in range(70):
            x = r.uniform(-60, 1180)
            y = r.uniform(-1350, -40)
            rr = r.uniform(90, 200)
            col = mix((120, 70, 40), (190, 110, 60), r.random())
            w.circle(x, y, rr, col, w=0)
        w.rect(-100, -300, 1200, 50, (130, 76, 44), w=0)
        self.wall = w.done(blur=3)
        k = Canvas(-170, -220, 340, 240)
        k.rect(-150, -150, 150, -30, (170, 50, 46), w=7, r=26)
        k.poly([(-110, -150), (110, -150), (90, -210), (-90, -210)], (170, 50, 46), w=7)
        k.poly([(-90, -150), (90, -150), (74, -196), (-74, -196)], (60, 80, 100), w=5)
        k.rect(-140, -110, -100, -84, (255, 90, 70), w=4)
        k.rect(100, -110, 140, -84, (255, 90, 70), w=4)
        k.rect(-50, -100, 50, -70, (240, 240, 230), w=4)
        k.rect(-140, -40, -90, 0, (30, 30, 34), w=4, r=8)
        k.rect(90, -40, 140, 0, (30, 30, 34), w=4, r=8)
        self.car = k.done()
        self.t_engulf = self.t0 + 4.0
        self.streak = Ash(160, seed=17, color=(150, 90, 50), size=(3, 8), speed=(10, 30))

    def frame(self, t):
        lt = t - self.t0
        sh = 6 * clamp((t - self.t_engulf + 1) / 1)
        f = camera(self.bg, 1.0, 540, 960, sh, t)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for k in range(10):
            p = ((k / 10) + lt * 0.6) % 1
            y = self.HZ + p ** 2.2 * 1100
            hw = lerp(2, 20, p)
            hl = lerp(6, 120, p)
            d.rectangle([540 - hw, y, 540 + hw, y + hl], fill=(240, 220, 120, 255))
        f.alpha_composite(ov)
        h = lerp(0.12, 1.25, ease_io(lt / 4.6))
        wall = self.wall.resize((int(self.wall.width * lerp(1, 1.3, lt / 6)), int(self.wall.height * h)))
        put(f, wall, 540, self.HZ + 60 + 500 * ease_io((lt - 2) / 3), anchor="bottom")
        bob = 4 * math.sin(lt * 18)
        put(f, self.car, 540, 1720 + bob, scale=1.6)
        dk = clamp((t - self.t_engulf) / 1.2)
        if dk > 0:
            darkness(f, 0.7 * dk, (110, 56, 26))
            self.streak.draw(f, t, dk, wind=2600)
        return finish(f, t, VIG_STRONG)


class Hug(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (46, 36, 34), w=0)
        c.rect(-MX + 40, 240, 1100, 980, (190, 100, 50), w=12, r=40)
        c.rect(-MX, 1400, W + MX, H + MY, (40, 34, 36), w=0)
        self.bg = paper_grain(c.done())
        self.art = artyom("stand", "worried", arm="hug", res=2)
        self.son = sonya("stand", "hold", expr="sad", res=2)
        self.son_b = sonya("stand", "hold", expr="sad", blink=True, res=2)
        self.streak = Ash(140, seed=21, color=(120, 60, 30), size=(4, 10), speed=(-20, 20), region=(0, 200, W, 980))

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.04, 1.12, lt / (self.t1 - self.t0))
        f = camera(self.bg, z, 540, 1000, 4, t)
        self.streak.draw(f, t, 1.0, wind=3500)
        ax, ay = scr(400, 2140, z, 540, 1000)
        put(f, self.art, ax, ay, scale=z * 0.9)
        sx, sy = scr(690, 2140, z, 540, 1000)
        put(f, self.son_b if blink_at(t, 8) else self.son, sx, sy, scale=z * 0.82)
        darkness(f, 0.3, (120, 60, 20))
        return finish(f, t, VIG_STRONG)


class Mud(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.vgrad(-MX, -MY, W + MX, H + MY, (120, 120, 130), (176, 166, 156))
        c.poly([(-MX, 300), (W + MX, 1500), (W + MX, H + MY), (-MX, H + MY)], DIRT)
        c.poly([(-MX, 900), (W + MX, 1800), (W + MX, H + MY), (-MX, H + MY)], DIRT_D, w=0)
        self.bg = paper_grain(c.done())
        h = Canvas(-170, -330, 340, 350)
        h.rect(-130, -200, 130, 0, (232, 214, 180), w=7)
        h.poly([(-160, -190), (0, -310), (160, -190)], (180, 60, 50))
        h.rect(-90, -150, -30, -90, (120, 170, 210), w=5)
        h.rect(30, -150, 90, -90, (120, 170, 210), w=5)
        h.rect(-24, -80, 24, 0, (120, 80, 50), w=5)
        self.house = h.done()
        self.t_slide = self.t0 + 0.5
        self.rain = Ash(120, seed=7, color=(160, 170, 190), size=(1, 2), speed=(900, 1300))

    def frame(self, t):
        lt = t - self.t0
        f = camera(self.bg, 1.04, 540, 960, 8 * clamp(lt - 0.6), t)
        self.rain.draw(f, t, 0.6, wind=-200)
        def sy(x):
            return 300 + (x + MX) * (1200 / (W + 2 * MX))
        k = ease_in = clamp((lt - 0.9) / 1.4) ** 2
        hx = lerp(520, 900, k)
        put(f, self.house.rotate(-8 - 40 * k, expand=True, resample=Image.BICUBIC), hx, sy(hx) + 40, scale=1.3)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        front = lerp(-200, 1250, ease_io((lt - 0.1) / 1.9))
        xs = list(range(-MX, int(front), 30))
        if len(xs) > 1:
            top = [(x, sy(x) - 70 - 25 * math.sin(x / 45 + t * 9)) for x in xs]
            bot = [(x, sy(x) + 60) for x in reversed(xs)]
            d.polygon(top + bot, fill=(112, 76, 48, 255), outline=INK + (255,))
            for k2 in range(0, len(top) - 2, 3):
                x, y = top[k2]
                d.line([(x, y + 25), (x + 40, sy(x + 40) - 30)], fill=(150, 108, 72, 255), width=6)
        f.alpha_composite(ov)
        return finish(f, t)


class Cow(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        sky(c, bot=1000, hazy=True)
        ground(c, 1000, False, seed=13)
        c.line([(860, 1010), (870, 760), (820, 660)], (90, 70, 56), 14)
        c.line([(868, 820), (930, 740)], (90, 70, 56), 10)
        c.rect(-MX, 1100, 360, 1120, (120, 100, 80), w=4)
        for x in range(-60, 360, 110):
            c.rect(x, 1040, x + 14, 1180, (120, 100, 80), w=4)
        self.bg = paper_grain(c.done())
        self.cow = cow()
        self.dust = Ash(120, seed=31, color=(190, 160, 120), size=(2, 6), speed=(5, 20))

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.08, lt / (self.t1 - self.t0))
        f = camera(self.bg, z, 540, 1100)
        put(f, self.cow, *scr(540, 1500, z, 540, 1100), scale=z * 1.35)
        self.dust.draw(f, t, 0.8, wind=900)
        return finish(f, t)


def jar_canvas(c, x, y, s=1.0, petal_skip=None):
    """Банка с водой и одуванчиком; (x,y) — дно банки по центру."""
    c.rect(x - 70 * s, y - 220 * s, x + 70 * s, y, (190, 220, 235), w=6 * s, r=20 * s)
    c.rect(x - 66 * s, y - 150 * s, x + 66 * s, y - 4 * s, (150, 196, 224), w=0, r=16 * s)
    c.rect(x - 78 * s, y - 236 * s, x + 78 * s, y - 210 * s, (170, 200, 214), w=5 * s, r=8 * s)
    c.line([(x - 40 * s, y - 190 * s), (x - 40 * s, y - 40 * s)], (240, 250, 255), 8 * s)
    dandelion(c, x, y - 330 * s, 1.15 * s, skip=petal_skip)


class Flat(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (58, 54, 66), w=0)
        for x in range(-MX, W + MX, 70):
            c.line([(x, -MY), (x, 1500)], (64, 60, 72), 18)
        c.rect(640, 380, 1010, 920, (170, 140, 110), w=12)
        c.line([(640, 650), (1010, 650)], (60, 54, 60), 10)
        c.line([(825, 380), (825, 920)], (60, 54, 60), 10)
        for (a, b) in [((660, 400), (990, 900)), ((990, 400), (660, 900))]:
            c.line([a, b], (226, 216, 190), 22)
        c.rect(-MX, 1500, W + MX, H + MY, (40, 36, 44), w=0)
        c.rect(600, 1470, 1120, 1510, (110, 80, 60), w=6)
        c.rect(630, 1510, 660, 1800, (90, 66, 50), w=5)
        c.rect(1060, 1510, 1090, 1800, (90, 66, 50), w=5)
        jar_canvas(c, 830, 1470, 1.0)
        self.bg = paper_grain(c.done())
        self.glow = radial((700, 700), GREEN_GLOW + (110,), power=1.6)
        self.son = sonya("back", "up")
        self.marks = [(250 + i * 30, 880) for i in range(7)]
        self.mark_t = [self.t0 + 0.6 + i * 1.15 for i in range(7)]

    def frame(self, t):
        lt = t - self.t0
        k = ease_io((lt - 4.5) / 4.5)
        z = lerp(1.0, 1.35, k)
        cx, cy = lerp(540, 780, k), lerp(1000, 1250, k)
        f = camera(self.bg, z, cx, cy)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for (mx, my), mt in zip(self.marks, self.mark_t):
            p = clamp((t - mt) / 0.3)
            if p > 0:
                a, b = scr(mx, my, z, cx, cy), scr(mx + 4, my + 110 * p, z, cx, cy)
                d.line([a, b], fill=(240, 240, 232, 255), width=int(8 * z))
        f.alpha_composite(ov)
        cur = sum(1 for mt in self.mark_t if t >= mt)
        hx = self.marks[min(6, cur)][0] if cur < 7 else self.marks[6][0] + 60
        sx, sy = scr(hx - 150, 1720, z, cx, cy)
        put(f, self.son, sx, sy + 6 * math.sin(t * 9), scale=z * 1.5)
        gx, gy = scr(830, 1150, z, cx, cy)
        put(f, with_alpha(self.glow, 0.75 + 0.25 * math.sin(t * 2)), gx, gy, anchor="center", scale=z)
        return finish(f, t, VIG_STRONG)


class Clock(Scene):
    def frame(self, t):
        lt = t - self.t0
        f = Image.new("RGBA", (W, H), (10, 10, 16, 255))
        if t >= 57.4:
            txt, col = "14:00:00", (255, 255, 255)
        else:
            txt, col = f"13:59:{min(59, 58 + int(t - 55.4))}", (255, 70, 60)
        s = 1.0 + 0.06 * (1 - ((t - 55.4) % 1.0)) ** 4
        put(f, radial((1000, 500), col + (70,)), 540, 960, anchor="center")
        im = Image.new("RGBA", (1000, 260), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((500, 130), txt, font=font(170, FONT_MONO), fill=col + (255,), anchor="mm")
        put(f, im, 540, 960, scale=s, anchor="center")
        if 57.4 <= t < 57.5:
            flash(f, 0.6)
        return finish(f, t, VIG_STRONG)


class Bushes(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        sky(c, bot=700, hazy=True)
        c.rect(-MX, 300, 200, 700, (170, 150, 140), w=6)
        c.rect(860, 260, W + MX, 700, (160, 144, 136), w=6)
        for x in range(-60, 200, 60):
            for y in range(340, 680, 80):
                c.rect(x, y, x + 34, y + 44, (90, 90, 100), w=3)
        ground(c, 700, False, seed=21)
        c.rect(380, 900, 700, 1000, (200, 60, 50), w=6)          # горка
        c.line([(420, 1000), (420, 1150)], (80, 80, 90), 10)
        c.line([(660, 1000), (660, 1150)], (80, 80, 90), 10)
        c.line([(700, 920), (880, 1150)], (200, 200, 60), 18)
        trees(c, 780, seed=9, n=3, scale=1.4)
        self.bg = paper_grain(c.done())
        r = random.Random(5)
        self.bushes = []
        for i in range(9):
            x, y = r.uniform(20, 1060), r.uniform(1150, 1500)
            b = Canvas(-130, -150, 260, 170)
            for dx, dy, rr in [(0, -60, 70), (-60, -40, 55), (60, -40, 55), (0, -20, 60)]:
                b.circle(dx, dy, rr, mix((70, 150, 70), (90, 170, 80), r.random()), w=5)
            self.bushes.append((x, y, b.done(), 0.4 + i * 0.05))
        w = Canvas()
        w.rect(-MX, -MY, W + MX, 120, (40, 36, 44), w=0)
        w.rect(-MX, 1700, W + MX, H + MY, (40, 36, 44), w=0)
        w.rect(-MX, -MY, 60, H + MY, (40, 36, 44), w=0)
        w.rect(1020, -MY, W + MX, H + MY, (40, 36, 44), w=0)
        w.rect(510, 120, 570, 1700, (40, 36, 44), w=0)
        for (a, b) in [((80, 140), (1000, 1680)), ((1000, 140), (80, 1680))]:
            w.line([a, b], (226, 216, 190, 220), 26)
        self.win = w.done()
        self.puff = radial((300, 300), (200, 170, 130, 230), power=1.2)

    def frame(self, t):
        lt = t - self.t0
        f = camera(self.bg, 1.0)
        for x, y, b, dl in self.bushes:
            if lt < dl:
                put(f, b, x, y)
            elif lt < dl + 0.5:
                k = (lt - dl) / 0.5
                put(f, self.puff, x, y - 60, scale=0.6 + k, alpha=1 - k, anchor="center")
        f.alpha_composite(camera(self.win, 1.0))
        return finish(f, t, VIG_STRONG)


class Turn(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (48, 44, 56), w=0)
        for x in range(-MX, W + MX, 70):
            c.line([(x, -MY), (x, H + MY)], (54, 50, 62), 18)
        self.bg = paper_grain(c.done())
        self.art = [artyom("stand", "worried", look=lk, res=2) for lk in (1, 0, -1)]

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.1, lt / (self.t1 - self.t0))
        f = camera(self.bg, z, 540, 960)
        idx = 0 if lt < 0.6 else (1 if lt < 1.0 else 2)
        put(f, self.art[idx], 540 + (idx - 1) * -20, 2500, scale=z * 1.05)
        put(f, radial((600, 600), GREEN_GLOW + (60,)), 1050, 1300, anchor="center")
        return finish(f, t, VIG_STRONG)


class Petal(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (34, 32, 42), w=0)
        c.rect(-MX, 1700, W + MX, H + MY, (90, 64, 50), w=6)
        jar_canvas(c, 540, 1820, 3.0, petal_skip=3)
        self.bg = paper_grain(c.done())
        self.glow = radial((1100, 1100), GREEN_GLOW + (110,), power=1.6)
        # отдельный лепесток (индекс 3), центр цветка (540, 1820-990)
        p = Canvas(-60, -60, 120, 120, ss=2)
        p.ellipse(-39, -39, 39, 39, PETAL, w=9)
        self.petal = p.done()
        self.center = (540, 1820 - 330 * 3)
        a = 3 / 14 * 2 * math.pi
        self.pos = (self.center[0] + 26 * 3.45 * math.cos(a), self.center[1] + 26 * 3.45 * math.sin(a))

    def frame(self, t):
        lt = t - self.t0
        f = camera(self.bg, 1.0)
        put(f, with_alpha(self.glow, 0.8 + 0.2 * math.sin(t * 2)), *self.center, anchor="center")
        amp = 2 + 10 * ease_io(lt / 2.6)
        dx = amp * math.sin(t * 47)
        dy = amp * 0.6 * math.sin(t * 61) + 18 * ease_io((lt - 2.2) / 0.8)
        pt = self.petal.rotate(amp * math.sin(t * 53), resample=Image.BICUBIC)
        put(f, pt, self.pos[0] + dx, self.pos[1] + dy, anchor="center")
        return finish(f, t, VIG_STRONG)


class End(Scene):
    def __init__(self, *a):
        super().__init__(*a)
        c = Canvas()
        c.rect(-MX, -MY, W + MX, H + MY, (34, 32, 42), w=0)
        self.bg = c.done()
        self.son = sonya("stand", "down", expr="sad", look=0, res=3)
        self.son_b = sonya("stand", "down", expr="sad", blink=True, res=3)
        j = Canvas()
        dandelion(j, 540, 1640, 2.6)
        self.flower = j.done()
        self.glow = radial((1000, 1000), GREEN_GLOW + (90,), power=1.6)
        self.emoji = None
        try:
            ef = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
            im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((80, 80), "👇", font=ef, anchor="mm", embedded_color=True)
            self.emoji = im
        except Exception:
            pass

    def frame(self, t):
        lt = t - self.t0
        z = lerp(1.0, 1.1, lt / (self.t1 - self.t0))
        f = camera(self.bg, z)
        put(f, self.son_b if blink_at(t, 11) else self.son, 540, 2380 + 40 * lt, scale=z * 0.95)
        put(f, with_alpha(self.glow, 0.8), 540, 1640, anchor="center")
        f.alpha_composite(camera(self.flower, z, 540, 960))
        dk = ease_io((lt - 1.8) / 0.9)
        darkness(f, 0.82 * dk)
        k = clamp((lt - 2.3) / 0.4)
        if k > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            A = int(255 * k)
            d.text((540, 860), "ЧТО ИСЧЕЗНЕТ", font=font(88), fill=(255, 255, 255, A), anchor="mm", stroke_width=8,
                   stroke_fill=(10, 10, 16, A))
            d.text((540, 970), "СЛЕДУЮЩИМ?", font=font(88), fill=(255, 214, 64, A), anchor="mm", stroke_width=8,
                   stroke_fill=(10, 10, 16, A))
            f.alpha_composite(ov)
            if self.emoji is not None:
                put(f, self.emoji, 540, 1130 + 14 * math.sin(t * 6), anchor="center", alpha=k)
        return finish(f, t, VIG_STRONG)


CLASSES = dict(park=Park, brown=Brown, fields=Fields, car=Car, shop=Shop, price=Price, door=Door, road=Road, hug=Hug,
               mud=Mud, cow=Cow, flat=Flat, clock=Clock, bushes=Bushes, turn=Turn, petal=Petal, end=End)
_cache = {}


def get_scene(i):
    if i not in _cache:
        name, t0 = SCENES[i]
        t1 = SCENES[i + 1][1] if i + 1 < len(SCENES) else TOTAL
        _cache[i] = CLASSES[name](t0, t1)
    return _cache[i]


# ======================================================================= HUD
D1, D7, D8 = "СУББОТА · 16 МАЯ", "ПЯТНИЦА · 22 МАЯ", "СУББОТА · 23 МАЯ"
HUD = {"park": ("13:59", D1, "ДЕНЬ 1"), "brown": ("14:02", D1, "ДЕНЬ 1"), "fields": ("14:41", D1, "ДЕНЬ 1"),
       "car": ("15:08", D1, "ДЕНЬ 1"), "shop": ("17:03", D1, "ДЕНЬ 1"), "price": ("17:05", D1, "ДЕНЬ 1"),
       "door": ("17:06", D1, "ДЕНЬ 1"), "road": ("19:40", D1, "ДЕНЬ 1"), "hug": ("19:44", D1, "ДЕНЬ 1"),
       "mud": ("19:47", D1, "ДЕНЬ 1"), "cow": ("19:52", D1, "ДЕНЬ 1"), "flat": ("21:15", D7, "ДЕНЬ 7"),
       "bushes": ("14:00", D8, "ДЕНЬ 8"), "turn": ("14:00", D8, "ДЕНЬ 8"), "petal": ("14:01", D8, "ДЕНЬ 8")}


def draw_hud(frame, t):
    i = scene_at(t)
    name = SCENES[i][0]
    if name not in HUD:
        return
    tm, date, badge = HUD[name]
    since = SCENES[i][1]
    if name == "park" and t >= T_CLICK:
        tm, since = "14:00", T_CLICK
    ov = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    glitch = 0 < t - since < 0.18
    d.rounded_rectangle([390, 70, 690, 160], radius=20, fill=(12, 12, 20, 200), outline=(255, 255, 255, 40), width=2)
    dy = random.Random(int(t * 30)).randint(-10, 10) if glitch else 0
    d.text((540, 116 + dy), tm, font=font(66, FONT_MONO), fill=(240, 240, 240, 120 if glitch else 255), anchor="mm")
    d.text((540, 196), date, font=font(28), fill=(235, 235, 240, 225), anchor="mm", stroke_width=3,
           stroke_fill=(0, 0, 0, 160))
    fb = font(30)
    bw = fb.getlength(badge) + 40
    newday = badge != "ДЕНЬ 1" and t - SCENES[i][1] < 0.6 and int((t - SCENES[i][1]) * 10) % 2 == 0
    bc = (255, 70, 60) if newday else (176, 40, 40)
    d.rounded_rectangle([540 - bw / 2, 222, 540 + bw / 2, 274], radius=14, fill=bc + (235,))
    d.text((540, 249), badge, font=fb, fill=(255, 255, 255, 255), anchor="mm")
    frame.alpha_composite(ov, (0, 0))


# ======================================================================= SUBTITLES
Y, R, G = (255, 214, 64), (240, 64, 52), (120, 230, 100)
HL = {0: {"14:00": Y, "вся": Y, "трава": G}, 1: {"чудом": Y}, 2: {"смешным": Y}, 3: {"пшеница": Y, "трава": G},
      4: {"рис": Y, "кукуруза": Y, "сахар": Y, "тоже": R}, 5: {"хлеб": Y, "исчез": R}, 6: {"корни": Y, "землю": R},
      7: {"степи": Y, "небо": R}, 8: {"неделю": Y}, 9: {"поливала": G, "каждый": Y}, 10: {"неделю": Y, "кусты": R},
      11: {"расписание": R}}


def build_chunks():
    out = []
    flat = []
    for i, (words, times) in enumerate(WT):
        n = len(words)
        k = max(1, math.ceil(n / 5))
        size = math.ceil(n / k)
        pairs = list(zip(words, times))
        for j in range(0, n, size):
            flat.append((i, pairs[j:j + size]))
    for k, (i, g) in enumerate(flat):
        start = g[0][1] - 0.05
        nxt = flat[k + 1][1][0][1] - 0.05 if k + 1 < len(flat) else TOTAL
        out.append((i, g, start, min(nxt, PH[i][1] + 0.7)))
    return out


CHUNKS = build_chunks()


def draw_subs(frame, t):
    for (i, g, s, e) in CHUNKS:
        if s <= t < e:
            words = []
            for w, wt in g:
                a = clamp((t - wt + 0.05) / 0.12)
                key = w.lower().strip(".,:!?…«»—")
                words.append((w.upper(), HL.get(i, {}).get(key, (255, 255, 255)), a))
            fade = clamp((e - t) / 0.12)
            draw_words(frame, [(a, b, c * fade) for a, b, c in words], 1330, size=76, maxw=930)
            return


# ======================================================================= compose
def render_frame(t):
    i = scene_at(t)
    f = get_scene(i).frame(t)
    name = SCENES[i][0]
    if i > 0 and name not in HARD_CUT and t - SCENES[i][1] < XF / 2:
        prev = get_scene(i - 1).frame(t)
        f = Image.blend(prev, f, ease_io(0.5 + (t - SCENES[i][1]) / XF))
    if i + 1 < len(SCENES) and SCENES[i + 1][0] not in HARD_CUT and SCENES[i + 1][1] - t < XF / 2:
        nxt = get_scene(i + 1).frame(t)
        f = Image.blend(f, nxt, ease_io(0.5 - (SCENES[i + 1][1] - t) / XF))
    if t > TOTAL - 0.4:
        darkness(f, (t - (TOTAL - 0.4)) / 0.4)
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


def stills(times=None):
    os.makedirs(os.path.join(OUT, "stills"), exist_ok=True)
    for i, (name, t0) in enumerate(SCENES):
        t1 = SCENES[i + 1][1] if i + 1 < len(SCENES) else TOTAL
        t = t0 + (t1 - t0) * 0.6
        render_frame(t).save(os.path.join(OUT, "stills", f"{i:02d}_{name}.jpg"), quality=85)


def main():
    os.makedirs(OUT, exist_ok=True)
    nfr = int(TOTAL * FPS)
    parts = os.cpu_count() or 4
    step = math.ceil(nfr / parts)
    jobs = [(k * step, min(nfr, (k + 1) * step), os.path.join(OUT, f"part{k}.mp4")) for k in range(parts)]
    with Pool(parts) as p:
        files = p.map(render_range, jobs)
    lst = os.path.join(OUT, "parts.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{fp}'\n" for fp in files)
    import sound
    wav = sound.build(os.path.join(OUT, "mix.wav"), TOTAL, globals())
    final = os.path.join(HERE, "no_grass.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-tune", "grain", "-c:a", "aac", "-b:a",
                    "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("done", final)


if __name__ == "__main__":
    stills() if "--stills" in sys.argv else main()
