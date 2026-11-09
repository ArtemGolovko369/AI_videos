"""Assemble «Если землетрясение застало вас на даче» (style-01 time-loop drama).

Inputs : build/png/*.png (from scenes.py + render_scenes.js), voiceover.mp3
Output : earthquake-dacha.mp4 (1080x1920, 30 fps)

Timings come from pauses detected in the voiceover (ffmpeg silencedetect).
"""
import math
import random
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 30
W, H = 1080, 1920
SRC = "build/png"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VO_END = 88.03

DAYS = {1: "СУББОТА · 13 ИЮНЯ", 2: "ВОСКРЕСЕНЬЕ · 14 ИЮНЯ", 3: "ПОНЕДЕЛЬНИК · 15 ИЮНЯ",
        4: "ВТОРНИК · 16 ИЮНЯ", 5: "СРЕДА · 17 ИЮНЯ", 6: "ЧЕТВЕРГ · 18 ИЮНЯ"}

# (start, end, scene, camera, shake, clock, day)
# camera: (scale_from, scale_to, fx_from, fy_from, fx_to, fy_to)
IN = (1.0, 1.12, .5, .5, .5, .5)
OUT_ = (1.14, 1.0, .5, .5, .5, .5)
PAN_R = (1.12, 1.12, .42, .5, .58, .5)
PAN_UP = (1.12, 1.12, .5, .58, .5, .44)
SHOTS = [
    (0.00, 2.66, "hook_house", IN, 1.0, "03:17", 1),
    (2.66, 4.90, "jars_fall", (1.05, 1.15, .5, .5, .5, .55), 0.7, "03:17", 1),
    (4.90, 7.45, "hero_face", (1.0, 1.18, .5, .5, .5, .45), 0.08, "03:18", 1),
    (7.45, 8.65, "phone", IN, 0, "03:19", 1),
    (8.65, 10.15, "road_blocked", PAN_UP, 0, "03:22", 1),
    (10.15, 11.90, "strangers_wide", IN, 0, "03:25", 1),
    (11.90, 13.85, "woman_close", (1.0, 1.2, .5, .5, .5, .47), 0, "03:25", 1),
    (13.85, 15.90, "gate_wide", IN, 0, "03:31", 1),
    (15.90, 18.00, "gate_latch", (1.0, 1.15, .5, .5, .55, .47), 0, "03:31", 1),
    (18.00, 21.60, "yard_stuff", PAN_R, 0, "03:38", 1),
    (21.60, 24.30, "gate_open", (1.0, 1.25, .5, .5, .53, .6), 0, "03:44", 1),
    (24.30, 26.90, "well_water", IN, 0, "03:58", 1),
    (26.90, 29.10, "meds_pack", OUT_, 0, "04:06", 1),
    (29.10, 30.75, "pipe_burst", IN, 0.15, "04:11", 1),
    (30.75, 32.45, "pharmacy_sign", (1.0, 1.2, .5, .5, .62, .42), 0, "04:15", 1),
    (32.45, 35.20, "shed", IN, 0.05, "04:40", 1),
    (35.20, 37.60, "tools", PAN_R, 0, "04:52", 1),
    (37.60, 40.30, "tools_vs_money", OUT_, 0, "05:03", 1),
    (40.30, 43.00, "stove_close", IN, 0, "21:40", 1),
    (43.00, 45.00, "shelter_wide", (1.0, 1.15, .5, .5, .56, .6), 0, "21:52", 1),
    (45.00, 47.20, "vent", PAN_R, 0, "22:03", 1),
    (47.20, 49.00, "canister_gauge", IN, 0, "22:30", 1),
    (49.00, 51.30, "empty_road", (1.0, 1.15, .5, .5, .5, .55), 0, "22:47", 1),
    (51.30, 54.00, "water_glass", (1.0, 1.2, .5, .5, .5, .45), 0.03, "23:15", 1),
    (54.00, 56.15, "relaxed_group", PAN_R, 0, "23:21", 1),
    (56.15, 57.45, "boots", IN, 0, "23:34", 1),
    (57.45, 60.10, "pack_exit", (1.0, 1.15, .5, .5, .6, .5), 0, "23:40", 1),
    (60.10, 63.10, "watch_sleep", IN, 0, "00:52", 2),
    (63.10, 65.80, "assign", PAN_R, 0, "01:06", 2),
    (65.80, 68.10, "faces_fire", IN, 0, "01:30", 2),
    (68.10, 70.25, "strangers_wide", (1.15, 1.3, .5, .55, .5, .5), 0, "01:44", 2),
    (70.25, 72.60, "house_cracked_woman", IN, 0.03, "03:09", 2),
    (72.60, 74.95, "grab_shoulder", (1.0, 1.12, .45, .5, .5, .5), 0.05, "03:10", 2),
    (74.95, 77.60, "docs_inside", PAN_UP, 0.06, "03:12", 2),
    (77.60, 80.30, "walls_crack", IN, 0.12, "03:16", 2),
    (80.30, 82.50, "collapse", (1.1, 1.0, .5, .5, .5, .5), 1.0, "03:17", 2),
    (82.50, 85.15, "loop_watch", IN, 0.8, "03:17", 3),
    (85.15, 86.50, "loop_yard", IN, 0.8, "03:17", 4),
    (86.50, 88.10, "village_aerial", (1.25, 1.0, .5, .55, .5, .5), 0.6, "03:17", 5),
    (88.10, 91.60, "question", IN, 0, "03:16", 6),
    (91.60, 93.60, "endcard", IN, 0, None, None),
]
TOTAL = SHOTS[-1][1]
FADE_CUTS = {40.30, 60.10, 70.25, 82.50, 88.10, 91.60}   # dip-to-black transitions
SHOCKS = [(0.0, 3.2, 1.0), (2.7, 4.6, .6), (80.3, 82.6, 1.0), (82.5, 84.4, .9),
          (85.15, 86.6, .9), (86.5, 88.2, .7)]

# voiceover chunks between detected pauses: (start, end, text)
CHUNKS = [
    (0.00, 2.50, "Если землетрясение застало вас на даче —"),
    (2.83, 4.30, "считайте, что вам повезло."),
    (4.97, 7.24, "Первый толчок был только предупреждением."),
    (7.61, 8.43, "Связи нет."),
    (8.80, 9.89, "Дорогу засыпало."),
    (10.31, 13.37, "А рядом — люди, которых вы никогда раньше не видели."),
    (14.01, 14.50, "Первое:"),
    (14.89, 17.74, "закройте калитку и уберите всё со двора."),
    (18.22, 21.43, "Незакреплённые вещи при новом толчке станут ловушками —"),
    (21.76, 23.88, "а открытый двор приглашает чужих."),
    (24.45, 25.00, "Второе:"),
    (25.41, 28.82, "как только толчки стихнут, соберите воду и лекарства."),
    (29.37, 30.59, "Трубы могут лопнуть,"),
    (30.86, 32.01, "а аптеки рядом нет."),
    (32.61, 33.09, "Третье:"),
    (33.55, 37.31, "заберите из сарая инструменты и топливо — пока он ещё стоит."),
    (37.83, 39.87, "Лом и фонарь сейчас ценнее денег."),
    (40.47, 41.18, "Четвёртое:"),
    (41.66, 44.42, "держите печь или обогрев в одном месте —"),
    (44.85, 46.91, "и только там, где есть проветривание."),
    (47.40, 48.57, "Топливо экономьте:"),
    (48.92, 50.92, "никто не знает, когда приедет помощь."),
    (51.53, 52.00, "Пятое:"),
    (52.46, 55.77, "будьте готовы к новому толчку, даже когда всё стихло."),
    (56.34, 57.30, "Обувь на ногах,"),
    (57.56, 59.64, "рюкзак рядом, выход свободен."),
    (60.27, 60.90, "Шестое:"),
    (61.25, 62.87, "не спите все одновременно."),
    (63.24, 65.48, "И сразу договоритесь, кто что несёт."),
    (66.07, 69.98, "С незнакомцами правила лучше обсудить до того, как станет страшно."),
    (70.42, 71.20, "И главное:"),
    (71.52, 74.51, "не возвращайтесь в повреждённое здание за вещами."),
    (75.09, 77.38, "Ни за документами, ни за телефоном."),
    (77.81, 80.09, "Стены, которые выдержали первый толчок,"),
    (80.45, 81.97, "могут не выдержать второй."),
    (82.63, 84.92, "Новый толчок придёт ровно в то же время…"),
    (85.34, 86.29, "И потом снова…"),
    (86.63, 88.03, "Как будто по расписанию."),
]

YELLOW = ("ПЕРВОЕ", "ВТОРОЕ", "ТРЕТЬЕ", "ЧЕТВЁРТОЕ", "ПЯТОЕ", "ШЕСТОЕ", "КАЛИТКУ", "ВОДУ",
          "ЛЕКАРСТВА", "ИНСТРУМЕНТЫ", "ТОПЛИВО", "ПЕЧЬ", "ОДНОМ", "МЕСТЕ", "ПРОВЕТРИВАНИЕ",
          "ГОТОВЫ", "ОБУВЬ", "РЮКЗАК", "НЕ СПИТЕ", "СПИТЕ", "НЕСЁТ", "ЛОМ", "ФОНАРЬ", "ПОВЕЗЛО")
RED = ("ПРЕДУПРЕЖДЕНИЕМ", "ЛОВУШКАМИ", "ЧУЖИХ", "ВОЗВРАЩАЙТЕСЬ", "ПОВРЕЖДЁННОЕ",
       "ВТОРОЙ", "РАСПИСАНИЮ", "ТО", "ЖЕ", "ВРЕМЯ…", "СНОВА…", "СТРАШНО", "ЗЕМЛЕТРЯСЕНИЕ", "ГЛАВНОЕ")
COL = {"w": (255, 255, 255), "y": (255, 213, 74), "r": (255, 72, 60)}


def word_color(w):
    k = w.strip(",.:;—!?").upper()
    if k in RED:
        return "r"
    if k in YELLOW:
        return "y"
    return "w"


def subtitle_groups():
    """Split each chunk into 1–4 word groups, timed by character length."""
    out = []
    for s, e, text in CHUNKS:
        words = [w for w in text.replace("—", " ").split() if w]
        groups, cur = [], []
        for w in words:
            if cur and (len(cur) >= 3 or len(" ".join(cur + [w])) > 18):
                groups.append(cur)
                cur = []
            cur.append(w)
        if cur:
            if groups and len(cur) == 1 and len(cur[0]) <= 4 and len(" ".join(groups[-1] + cur)) <= 22:
                groups[-1] += cur
            else:
                groups.append(cur)
        # don't leave a short function word hanging at the end of a group
        for i in range(len(groups) - 1):
            while len(groups[i]) > 1 and len(groups[i][-1].strip(",")) <= 3 and not groups[i][-1].endswith(","):
                groups[i + 1].insert(0, groups[i].pop())
        total = sum(len(" ".join(g)) + 2 for g in groups)
        t = s
        for i, g in enumerate(groups):
            d = (e - s) * (len(" ".join(g)) + 2) / total
            end = e + 0.25 if i == len(groups) - 1 else t + d
            out.append((t, end, [w.strip(",.:;") if not w.endswith("…") else w for w in g]))
            t += d
    return out


# ---------------------------------------------------------------- overlays

def font(path, size):
    return ImageFont.truetype(path, size)


def draw_spaced(d, xy, text, fnt, fill, spacing):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + spacing


def spaced_width(d, text, fnt, spacing):
    return sum(d.textlength(c, font=fnt) + spacing for c in text) - spacing


def hud(clock, day, alarm=False):
    img = Image.new("RGBA", (W, 360), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f_clock, f_date, f_day = font(MONO, 96), font(BOLD, 30), font(BOLD, 30)
    tw = d.textlength(clock, font=f_clock)
    pw, ph = tw + 90, 132
    x0, y0 = (W - pw) / 2, 92
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), 30, fill=(10, 10, 22, 205),
                        outline=(255, 80, 70, 230) if alarm else (255, 255, 255, 40), width=4)
    d.text(((W - tw) / 2, y0 + 12), clock, font=f_clock, fill=(255, 92, 80) if alarm else (240, 240, 250))
    date = DAYS[day]
    dw = spaced_width(d, date, f_date, 5)
    draw_spaced(d, ((W - dw) / 2 + 2, y0 + ph + 20), date, f_date, (0, 0, 0, 160), 5)
    draw_spaced(d, ((W - dw) / 2, y0 + ph + 18), date, f_date, (235, 235, 245), 5)
    badge = f"ДЕНЬ {day}"
    bw = d.textlength(badge, font=f_day) + 44
    by = y0 + ph + 70
    d.rounded_rectangle(((W - bw) / 2, by, (W + bw) / 2, by + 50), 14, fill=(150, 34, 34, 225))
    d.text(((W - bw) / 2 + 22, by + 7), badge, font=f_day, fill=(255, 225, 220))
    return img


def subtitle(words):
    f = font(BOLD, 96)
    img = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    words = [w.upper() for w in words]
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        if cur and d.textlength(test, font=f) > W - 110:
            lines.append(cur)
            cur = []
        cur.append(w)
    lines.append(cur)
    if any(d.textlength(" ".join(l), font=f) > W - 110 for l in lines):
        f = font(BOLD, 78)
    lh = f.size * 1.18
    y = (420 - lh * len(lines)) / 2
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for line in lines:
        x = (W - d.textlength(" ".join(line), font=f)) / 2
        for w in line:
            sd.text((x + 6, y + 8), w, font=f, fill=(0, 0, 0, 170))
            d.text((x, y), w, font=f, fill=COL[word_color(w)], stroke_width=9, stroke_fill=(12, 10, 20))
            x += d.textlength(w + " ", font=f)
        y += lh
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(shadow, img)


def question_card():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fq, fb, fs = font(BOLD, 76), font(BOLD, 64), font(BOLD, 52)
    lines = ["ОСТАТЬСЯ НА ДАЧЕ", "С НЕЗНАКОМЦАМИ?"]
    y = 1080
    for l in lines:
        w = d.textlength(l, font=fq)
        d.text(((W - w) / 2, y), l, font=fq, fill=(255, 255, 255), stroke_width=7, stroke_fill=(10, 10, 20))
        y += 96
    for label, cx, col in (("ДА", 330, (70, 210, 110)), ("НЕТ", 750, (240, 70, 60))):
        d.rounded_rectangle((cx - 170, 1330, cx + 170, 1450), 60, fill=(16, 16, 28, 235), outline=col, width=8)
        w = d.textlength(label, font=fb)
        d.text((cx - w / 2, 1353), label, font=fb, fill=col)
    t = "РЕШАТЬ ВАМ."
    w = spaced_width(d, t, fs, 6)
    draw_spaced(d, ((W - w) / 2, 1540), t, fs, (235, 235, 245), 6)
    return img


def end_card():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f1, f2 = font(BOLD, 120), font(REG, 44)
    t = "ЧТО ЕСЛИ…"
    w = d.textlength(t, font=f1)
    d.text(((W - w) / 2, 820), t, font=f1, fill=(255, 213, 74), stroke_width=8, stroke_fill=(10, 10, 20))
    for i, l in enumerate(["Подпишись — следующая история", "в то же время."]):
        w = d.textlength(l, font=f2)
        d.text(((W - w) / 2, 1010 + i * 62), l, font=f2, fill=(225, 225, 235))
    return img


# ---------------------------------------------------------------- frames

def shake_offset(t, amp, seed):
    if amp <= 0:
        return 0, 0
    a = amp * 38
    return (a * (math.sin(t * 61 + seed) * .6 + math.sin(t * 23.3 + seed * 2) * .4),
            a * (math.sin(t * 53 + seed * 3) * .6 + math.sin(t * 31.7 + seed) * .4))


def ease(x):
    return x * x * (3 - 2 * x)


def render_video(path_noaudio):
    srcs = {}
    hud_cache = {}
    subs = [(s, e, subtitle(g)) for s, e, g in subtitle_groups()]
    qcard, ecard = question_card(), end_card()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "19", "-pix_fmt", "yuv420p", path_noaudio], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    si = 0
    for fi in range(n):
        t = fi / FPS
        while t >= SHOTS[si][1] and si < len(SHOTS) - 1:
            si += 1
        s, e, name, cam, shake, clock, day = SHOTS[si]
        if name not in srcs:
            srcs[name] = Image.open(f"{SRC}/{name}.png").convert("RGB")
        im = srcs[name]
        sw, sh = im.size
        p = ease((t - s) / (e - s))
        sc = cam[0] + (cam[1] - cam[0]) * p
        fx = cam[2] + (cam[4] - cam[2]) * p
        fy = cam[3] + (cam[5] - cam[3]) * p
        # local shake decays over the shot; big shocks follow SHOCKS envelope
        amp = shake * max(0.0, 1 - (t - s) / max(e - s, 0.01) * 0.6)
        for a, b, k in SHOCKS:
            if a <= t <= b:
                amp = max(amp, k * math.sin(math.pi * (t - a) / (b - a)) ** 0.6)
        cw, ch = sw / sc, sh / sc  # sc=1 shows the whole illustration
        dx, dy = shake_offset(t, amp, si)
        cx = min(max(fx * sw + dx, cw / 2), sw - cw / 2)
        cy = min(max(fy * sh + dy, ch / 2), sh - ch / 2)
        frame = im.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
        frame = frame.convert("RGBA")
        if clock:
            key = (clock, day, clock == "03:17")
            if key not in hud_cache:
                hud_cache[key] = hud(*key)
            frame.alpha_composite(hud_cache[key], (0, 0))
        if name == "question":
            frame.alpha_composite(qcard)
        if name == "endcard":
            frame.alpha_composite(ecard)
        for a, b, img in subs:
            if a <= t < b:
                frame.alpha_composite(img, (0, 1120))
                break
        rgb = frame.convert("RGB")
        # dip to black around marked cuts + flash on shocks
        fade = 1.0
        for c in FADE_CUTS:
            if abs(t - c) < 0.25:
                fade = min(fade, abs(t - c) / 0.25)
        if t > TOTAL - 0.5:
            fade = min(fade, (TOTAL - t) / 0.5)
        if fade < 1:
            rgb = Image.eval(rgb, lambda v, f=fade: int(v * f))
        ff.stdin.write(rgb.tobytes())
        if fi % 300 == 0:
            print(f"frame {fi}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()


# ---------------------------------------------------------------- audio

SR = 44100


def make_bed(path):
    n = int(TOTAL * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(1)
    # dark drone: two low sines with slow beating + filtered noise
    drone = 0.06 * np.sin(2 * np.pi * 49 * t) + 0.04 * np.sin(2 * np.pi * 73.6 * t + np.sin(t * .3))
    drone *= 0.7 + 0.3 * np.sin(2 * np.pi * t / 9)
    noise = rng.standard_normal(n).astype(np.float64)
    brown = np.cumsum(noise)
    brown -= np.convolve(brown, np.ones(4410) / 4410, mode="same")
    brown /= np.max(np.abs(brown)) + 1e-9
    bed = drone + 0.05 * brown
    # rumbles on shocks
    rum = np.zeros(n)
    for a, b, k in SHOCKS:
        i0, i1 = int(a * SR), min(int((b + 0.8) * SR), n)
        seg = brown[i0:i1] * 3.0
        env = np.sin(np.linspace(0, math.pi, i1 - i0)) ** 0.5
        rum[i0:i1] += k * 0.55 * np.clip(seg, -1, 1) * env
        rum[i0:i1] += k * 0.25 * np.sin(2 * np.pi * 31 * t[i0:i1]) * env
    # clock ticks in the finale + question card
    tick = np.zeros(n)
    tk = np.exp(-np.arange(int(.03 * SR)) / 250.0) * np.sin(2 * np.pi * 2200 * np.arange(int(.03 * SR)) / SR)
    for s in np.arange(82.5, 93.0, 1.0):
        i = int(s * SR)
        tick[i:i + len(tk)] += 0.18 * tk[: n - i]
    mix = bed * 0.55 + rum + tick
    fade = np.ones(n)
    fl = int(1.5 * SR)
    fade[-fl:] = np.linspace(1, 0, fl)
    fade[:int(.05 * SR)] = np.linspace(0, 1, int(.05 * SR))
    mix *= fade
    mix = np.clip(mix, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767 * 0.9).astype(np.int16).tobytes())


if __name__ == "__main__":
    import sys
    if "--subs" in sys.argv:
        for s, e, g in subtitle_groups():
            print(f"{s:6.2f}-{e:6.2f} {' '.join(g)}")
        sys.exit()
    render_video("build/video_noaudio.mp4")
    make_bed("build/bed.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "build/video_noaudio.mp4", "-i", "voiceover.mp3",
                    "-i", "build/bed.wav", "-filter_complex",
                    "[1:a]volume=1.0,apad[vo];[2:a]volume=0.55[bed];[vo][bed]amix=inputs=2:duration=shortest:normalize=0,"
                    "alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "earthquake-dacha.mp4"], check=True)
    print("done")
