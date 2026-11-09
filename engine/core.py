"""Минимальный движок для вертикальных TikTok-роликов в стиле репозитория.

Статичные слои рисуются один раз (с суперсэмплингом для гладкого контура),
а покадрово добавляются: камера (Ken Burns / тряска), частицы, свет, HUD, субтитры.
"""
import math
import os
import random
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
SS = 2                      # суперсэмплинг статичных слоёв
MX, MY = 108, 192           # запас слоя вокруг кадра (для наездов и тряски)
LW, LH = W + 2 * MX, H + 2 * MY

INK = (20, 17, 28)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_COND = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"

_font_cache = {}


def font(size, path=FONT_BOLD):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_back(t, s=1.7):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def mix(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- canvas
class Canvas:
    """Рисование в координатах кадра (1080x1920) на увеличенном холсте."""

    def __init__(self, x0=-MX, y0=-MY, w=LW, h=LH, ss=SS, bg=(0, 0, 0, 0)):
        self.x0, self.y0, self.w, self.h, self.ss = x0, y0, w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), bg)
        self.d = ImageDraw.Draw(self.img)

    def P(self, x, y):
        return ((x - self.x0) * self.ss, (y - self.y0) * self.ss)

    def pts(self, pts):
        return [self.P(x, y) for x, y in pts]

    def box(self, x1, y1, x2, y2):
        a, b = self.P(x1, y1), self.P(x2, y2)
        return [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]

    def poly(self, pts, fill, outline=INK, w=6):
        self.d.polygon(self.pts(pts), fill=fill)
        if outline and w:
            p = self.pts(pts)
            self.d.line(p + [p[0]], fill=outline, width=int(w * self.ss), joint="curve")

    def line(self, pts, fill=INK, w=6):
        self.d.line(self.pts(pts), fill=fill, width=int(w * self.ss), joint="curve")

    def ellipse(self, x1, y1, x2, y2, fill, outline=INK, w=6):
        self.d.ellipse(self.box(x1, y1, x2, y2), fill=fill,
                       outline=outline if w else None, width=int(w * self.ss))

    def circle(self, cx, cy, r, fill, outline=INK, w=6):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, fill, outline, w)

    def rect(self, x1, y1, x2, y2, fill, outline=INK, w=6, r=0):
        b = self.box(x1, y1, x2, y2)
        if r:
            self.d.rounded_rectangle(b, radius=r * self.ss, fill=fill,
                                     outline=outline if w else None, width=int(w * self.ss))
        else:
            self.d.rectangle(b, fill=fill, outline=outline if w else None, width=int(w * self.ss))

    def text(self, x, y, s, size, fill, anchor="mm", path=FONT_BOLD, stroke=0, stroke_fill=INK):
        self.d.text(self.P(x, y), s, font=font(int(size * self.ss), path), fill=fill, anchor=anchor,
                    stroke_width=int(stroke * self.ss), stroke_fill=stroke_fill)

    def vgrad(self, x1, y1, x2, y2, c1, c2):
        b = [int(v) for v in self.box(x1, y1, x2, y2)]
        h = max(1, b[3] - b[1])
        for i in range(h):
            col = mix(c1, c2, i / h)
            self.d.line([(b[0], b[1] + i), (b[2], b[1] + i)], fill=col + (255,))

    def paste(self, other, x=0, y=0):
        """Наложить другой Canvas (того же ss) так, чтобы его (x0,y0) совпало с x+x0,y+y0."""
        ox, oy = self.P(other.x0 + x, other.y0 + y)
        self.img.alpha_composite(other.img, (int(ox), int(oy)))

    def done(self, blur=0):
        im = self.img.resize((self.w, self.h), Image.LANCZOS)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        return im


def paper_grain(img, amount=10, seed=1):
    """Лёгкая бумажная текстура поверх статичного слоя."""
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.int16)
    n = rng.normal(0, amount, a.shape[:2])[..., None]
    a[..., :3] = np.clip(a[..., :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- frame helpers
def camera(layer, zoom=1.0, cx=W / 2, cy=H / 2, shake=0.0, t=0.0):
    """Вырезать кадр из увеличенного слоя: наезд, сдвиг, тряска."""
    if shake:
        cx += shake * (math.sin(t * 71.3) + 0.5 * math.sin(t * 133.1))
        cy += shake * (math.cos(t * 59.7) + 0.5 * math.sin(t * 97.3))
    hw, hh = W / 2 / zoom, H / 2 / zoom
    cx = clamp(cx, hw - MX, W + MX - hw)
    cy = clamp(cy, hh - MY, H + MY - hh)
    box = (cx - hw + MX, cy - hh + MY, cx + hw + MX, cy + hh + MY)
    return layer.resize((W, H), Image.BILINEAR, box=box)


def put(frame, sprite, x, y, alpha=1.0, scale=1.0, sx=1.0, sy=1.0, anchor="bottom"):
    """Наложить спрайт (RGBA) с якорем снизу-по-центру или по центру."""
    if sprite is None or alpha <= 0.01:
        return
    sw, sh = sprite.size
    fx, fy = scale * sx, scale * sy
    if abs(fx - 1) > 1e-3 or abs(fy - 1) > 1e-3:
        sprite = sprite.resize((max(1, int(sw * fx)), max(1, int(sh * fy))), Image.BILINEAR)
    if alpha < 0.999:
        a = sprite.getchannel("A").point(lambda v: int(v * alpha))
        sprite = sprite.copy()
        sprite.putalpha(a)
    sw, sh = sprite.size
    px = int(x - sw / 2)
    py = int(y - sh) if anchor == "bottom" else int(y - sh / 2)
    frame.alpha_composite(sprite, (px, py)) if (0 <= px and 0 <= py and px + sw <= frame.width
                                                 and py + sh <= frame.height) else _safe_paste(frame, sprite, px, py)


def _safe_paste(frame, sprite, px, py):
    x1, y1 = max(0, px), max(0, py)
    x2, y2 = min(frame.width, px + sprite.width), min(frame.height, py + sprite.height)
    if x2 <= x1 or y2 <= y1:
        return
    crop = sprite.crop((x1 - px, y1 - py, x2 - px, y2 - py))
    frame.alpha_composite(crop, (x1, y1))


def with_alpha(img, alpha):
    if alpha >= 0.999:
        return img
    out = img.copy()
    out.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return out


def radial(size, color, inner=0.0, power=1.6):
    """Мягкое круглое свечение RGBA."""
    w, h = size
    y, x = np.mgrid[0:h, 0:w]
    r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    a = np.clip((1 - r) / (1 - inner), 0, 1) ** power
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = color[:3]
    arr[..., 3] = (a * (color[3] if len(color) > 3 else 255)).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def vignette(strength=0.6):
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
    a = np.clip((r - 0.45) / 0.65, 0, 1) ** 1.5 * 255 * strength
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 0:3] = (8, 6, 14)
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def grain_frames(n=4, amount=14):
    rng = np.random.default_rng(7)
    out = []
    for _ in range(n):
        v = rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        a = rng.integers(0, amount, (H // 2, W // 2), dtype=np.uint8)
        arr = np.stack([v, v, v, a], -1)
        out.append(Image.fromarray(arr, "RGBA").resize((W, H), Image.NEAREST))
    return out


def darkness(frame, alpha, color=(4, 4, 10)):
    if alpha <= 0.005:
        return
    ov = Image.new("RGBA", (W, H), color + (int(255 * clamp(alpha)),))
    frame.alpha_composite(ov)


def flash(frame, alpha, color=(255, 255, 255)):
    darkness(frame, alpha, color)


# ---------------------------------------------------------------- particles
class Ash:
    """Пепел: медленно падающие хлопья с покачиванием."""

    def __init__(self, n=120, seed=3, color=(150, 140, 135), size=(2, 6), speed=(40, 110),
                 region=(0, 0, W, H), glow=False):
        r = random.Random(seed)
        self.p = [(r.uniform(region[0], region[2]), r.uniform(0, 1), r.uniform(*size),
                   r.uniform(*speed), r.uniform(0, 6.28), r.uniform(0.4, 1.0)) for _ in range(n)]
        self.color, self.region, self.glow = color, region, glow

    def draw(self, frame, t, alpha=1.0, wind=20):
        if alpha <= 0.01:
            return
        x0, y0, x1, y1 = self.region
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        hgt = y1 - y0
        for (x, ph, s, sp, wob, br) in self.p:
            y = y0 + ((ph * hgt + sp * t) % hgt)
            xx = x + wind * t * 0.3 + 14 * math.sin(t * 1.3 + wob)
            xx = x0 + (xx - x0) % (x1 - x0)
            a = int(255 * alpha * br)
            if self.glow and math.sin(t * 6 + wob * 3) > 0.92:
                d.line([(xx - s * 3, y), (xx + s * 3, y)], fill=(255, 250, 230, a), width=2)
                d.line([(xx, y - s * 3), (xx, y + s * 3)], fill=(255, 250, 230, a), width=2)
            d.ellipse([xx - s, y - s * 0.7, xx + s, y + s * 0.7], fill=self.color + (a,))
        frame.alpha_composite(ov)


# ---------------------------------------------------------------- text
def text_w(s, f):
    return f.getlength(s)


def wrap_words(words, f, maxw):
    lines, cur = [], []
    for w in words:
        test = " ".join([x[0] for x in cur] + [w[0]])
        if cur and text_w(test, f) > maxw:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def draw_words(frame, words, y, size=76, maxw=940, alpha_fn=None):
    """words: [(text, color, alpha)]. Белые заглавные с обводкой и тенью, по центру."""
    f = font(size)
    lines = wrap_words(words, f, maxw)
    lh = int(size * 1.18)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    top = y - (len(lines) - 1) * lh / 2
    sp = text_w(" ", f)
    for i, line in enumerate(lines):
        tw = sum(text_w(w[0], f) for w in line) + sp * (len(line) - 1)
        x = W / 2 - tw / 2
        yy = top + i * lh
        for (s, col, a) in line:
            if a > 0.01:
                A = int(255 * a)
                ds.text((x + 4, yy + 7), s, font=f, fill=(0, 0, 0, int(A * 0.7)), anchor="lm")
                d.text((x, yy), s, font=f, fill=col + (A,), anchor="lm", stroke_width=7,
                       stroke_fill=(12, 10, 18, A))
            x += text_w(s, f) + sp
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    frame.alpha_composite(sh)
    frame.alpha_composite(ov)


# ---------------------------------------------------------------- timing
def speech_segments(audio, noise="-38dB", d=0.22):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af",
                          f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    dur = audio_duration(audio)
    segs, cur = [], 0.0
    for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if s - cur > 0.05:
            segs.append((cur, s))
        cur = e
    if dur - cur > 0.1:
        segs.append((cur, dur))
    return segs


def audio_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip())


def _speech_len(s):
    return len(re.sub(r"[^\wёЁ]", "", s)) + 0.4 * s.count(" ")


def align(phrases, segs):
    """DP: последовательно раздать речевые сегменты фразам (min ошибки длительности)."""
    P, S = len(phrases), len(segs)
    lens = [_speech_len(p) for p in phrases]
    total_speech = sum(e - s for s, e in segs)
    rate = total_speech / sum(lens)
    INF = 1e18
    dp = [[INF] * (S + 1) for _ in range(P + 1)]
    bk = [[0] * (S + 1) for _ in range(P + 1)]
    dp[0][0] = 0
    for i in range(1, P + 1):
        for j in range(1, S + 1):
            for k in range(i - 1, j):
                if dp[i - 1][k] >= INF:
                    continue
                dur = sum(e - s for s, e in segs[k:j])
                c = dp[i - 1][k] + (dur - rate * lens[i - 1]) ** 2 / max(0.3, rate * lens[i - 1])
                if c < dp[i][j]:
                    dp[i][j], bk[i][j] = c, k
    res, j = [], S
    for i in range(P, 0, -1):
        k = bk[i][j]
        res.append(segs[k:j])
        j = k
    res.reverse()
    return res


def word_times(phrase, segs):
    """Время появления каждого слова фразы (пропорционально длине, по речевым кускам)."""
    words = phrase.split()
    L = [max(1.0, _speech_len(w)) for w in words]
    tot = sum(L)
    dur = sum(e - s for s, e in segs)
    times, acc = [], 0.0
    for l in L:
        pos = acc / tot * dur
        acc += l
        # отобразить pos (время речи) на абсолютное время с учётом пауз
        for s, e in segs:
            if pos <= (e - s) + 1e-6:
                times.append(s + pos)
                break
            pos -= (e - s)
        else:
            times.append(segs[-1][1])
    return words, times


# ---------------------------------------------------------------- encoding
def encoder(path, fps=FPS):
    return subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
                             "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", path],
                            stdin=subprocess.PIPE)


# ---------------------------------------------------------------- audio synth
SR = 44100


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def lowpass(x, a):
    """Однополюсный ФНЧ, a in (0,1): чем меньше — тем глуше."""
    y = np.empty_like(x)
    acc = 0.0
    # векторизованно через cumulative не выйдет, используем быстрый цикл блоками
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def brown(dur, seed=0):
    rng = np.random.default_rng(seed)
    x = np.cumsum(rng.normal(0, 1, int(dur * SR)))
    x -= np.convolve(x, np.ones(2000) / 2000, mode="same")
    return x / (np.abs(x).max() + 1e-9)


def env(n, a, r, sus=None):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    if ai:
        e[:ai] = np.linspace(0, 1, ai)
    if ri:
        e[-ri:] *= np.linspace(1, 0, ri)
    return e


def place(buf, snd, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(snd))
    buf[i:j] += snd[: j - i] * gain


def write_wav(path, x):
    import wave
    x = np.clip(x, -1, 1)
    data = (x * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
