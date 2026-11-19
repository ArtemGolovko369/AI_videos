"""Синтезирует фон и звуковые эффекты по сценарию и сводит их с озвучкой.
Вход: tools/timeline.json, audio/voice_placed.npy. Выход: audio/mix.wav"""
import json, os, re, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SR = 44100
TL = json.load(open(os.path.join(HERE, "timeline.json"), encoding="utf-8"))
voice = np.load(os.path.join(ROOT, "audio/voice_placed.npy"))
N = len(voice)
music = np.zeros(N, np.float32); sfx = np.zeros(N, np.float32)
rs = np.random.default_rng(7)
SC = {s["id"]: s for s in TL["scenes"]}

def word(sc, w, n=1):
    s = SC[sc]; k = 0; w = w.strip("«»")
    for v in TL["voice"]:
        if not (s["start"] - .01 <= v["at"] <= s["end"]): continue
        for x in v["words"]:
            if re.sub(r'[«».,:?!—…]', '', x["w"]).lower().startswith(w.lower()):
                k += 1
                if k == n: return x["s"]
    raise KeyError(w)
def vend(sc):
    s = SC[sc]; return max(v["end"] for v in TL["voice"] if s["start"] - .01 <= v["at"] <= s["end"])

def add(buf, t, x, g=1.0):
    i = int(t * SR)
    if i >= N or i + len(x) <= 0: return
    if i < 0: x = x[-i:]; i = 0
    x = x[:N - i]; buf[i:i + len(x)] += g * x.astype(np.float32)
def tt(d): return np.arange(int(d * SR)) / SR
def env(d, a=.01, r=.2):
    t = tt(d); e = np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)); return np.clip(e, 0, 1)
def lp(x, k):  # простой фильтр низких частот (скользящее среднее k отсчётов, дважды)
    if k <= 1: return x
    c = np.ones(k) / k; return np.convolve(np.convolve(x, c, 'same'), c, 'same')
def noise(d): return rs.standard_normal(int(d * SR)).astype(np.float32)
def tone(f, d, dec=3.0, harm=(1, .5, .25)):
    t = tt(d); x = sum(a * np.sin(2 * np.pi * f * (i + 1) * t) for i, a in enumerate(harm)); return x * np.exp(-t * dec)
def nf(n): return 440 * 2 ** ((n - 69) / 12)

def P(a, b):
    n = max(len(a), len(b)); o = np.zeros(n, np.float32); o[:len(a)] += a; o[:len(b)] += b; return o

# --- элементы
click = lambda: tone(2200, .04, 80, (1,)) + .5 * lp(noise(.04), 2) * np.exp(-tt(.04) * 120)
def creak(d=1.2):
    t = tt(d); f = 180 + 60 * np.sin(2 * np.pi * .7 * t); ph = np.cumsum(f) / SR * 2 * np.pi
    x = np.sign(np.sin(ph)) * (.5 + .5 * np.sin(2 * np.pi * 23 * t)); return lp(x, 6) * env(d, .1, .4) * .25
def wind(d, k=40): x = lp(noise(d), k); x /= np.abs(x).max() + 1e-9; lfo = .6 + .4 * np.sin(2 * np.pi * .13 * tt(d) + 1); return x * lfo * env(d, 1.5, 1.5)
def thump(f=55, d=.25): t = tt(d); return np.sin(2 * np.pi * f * t * np.exp(-t * 6)) * np.exp(-t * 14)
def heartbeat(t0, t1, bpm=80, g=.6):
    t = t0
    while t < t1: add(sfx, t, thump(50), g); add(sfx, t + .22, thump(45), g * .7); t += 60 / bpm
def hat(): return lp(noise(.05), 1) * np.exp(-tt(.05) * 90) * .3
def boom(): t = tt(2.5); return (np.sin(2 * np.pi * 40 * t * np.exp(-t * .8)) * np.exp(-t * 1.8) + .3 * lp(noise(2.5), 30) * np.exp(-t * 3))
def whoosh(d=.6): x = noise(d); k = np.linspace(40, 3, len(x)).astype(int); y = np.array([0.0]); x = lp(x, 8) * np.sin(np.pi * tt(d) / d) ** 2; return x * .5
def ping(f=1320): return tone(f, .35, 12, (1, .3)) * .5
def bell(f): return tone(f, 2.5, 1.6, (1, 0, .4, 0, .2)) * .4
def piano(f, d=2.2): return tone(f, d, 2.2, (1, .45, .2, .1)) * env(d, .005, .3) * .5
def pad(f, d, g=.12):
    t = tt(d); x = sum(np.sin(2 * np.pi * f * m * t + m) for m in (1, 1.5, 2, 1.005)) / 4; return x * env(d, 1.2, 1.5) * g

# --- общий дрон
T = N / SR; t = tt(T)
drone = (np.sin(2 * np.pi * 55 * t) + .6 * np.sin(2 * np.pi * 82.4 * t + 1) + .3 * np.sin(2 * np.pi * 110.3 * t)) * (.5 + .5 * np.sin(2 * np.pi * .05 * t))
music += .05 * drone

# 1. заставка
add(sfx, .9, click(), .8); add(sfx, 1.5, creak(1.6), .7); add(music, 0, wind(SC[1]["end"] + .5, 80), .08)
# 2. рождение: ветер и колыбельная (музыкальная шкатулка)
s = SC[2]; add(music, s["start"], wind(s["end"] - s["start"], 50), .18)
mel = [76, 79, 81, 79, 76, 74, 72, 74, 76, 72, 71, 72]
for i, n in enumerate(mel * 2):
    tt0 = s["start"] + .4 + i * .55
    if tt0 < s["end"] - .3: add(music, tt0, tone(nf(n), 1.2, 3.5, (1, 0, .3)), .07)
# 3. стук колёс на карте
s = SC[3]; t0 = word(3, "Вскоре")
x = t0
while x < s["end"]:
    add(sfx, x, P(thump(140, .08), .3 * hat()), .35); add(sfx, x + .14, thump(130, .08), .3); x += .75
# 4. мел, звонок, аккорды
s = SC[4]
for i in range(10): add(sfx, s["start"] + .3 + i * .45, lp(noise(.18), 2) * env(.18, .02, .05) * .08)
tb = word(4, "Учится"); add(sfx, tb - .3, (np.sin(2 * np.pi * 1000 * tt(1.0)) * (np.sin(2 * np.pi * 20 * tt(1.0)) > 0)) * env(1.0, .01, .2) * .05)
tm = word(4, "золотой")
for n in (60, 64, 67, 72): add(music, tm - .1, piano(nf(n), 2.5), .35)
td = word(4, "Потом")
for n in (62, 66, 69, 74): add(music, td, pad(nf(n), 3.0, .5), .5)
# 5. лёгкий бит
s = SC[5]; bpm = 112; b = 60 / bpm; x = s["start"] + .3; k = 0
while x < s["end"] + 2.5:
    fade = 1 - np.clip((x - s["end"]) / 2.5, 0, 1)
    if k % 4 in (0, 2): add(music, x, thump(60, .2), .45 * fade)
    if k % 4 in (1, 3): add(music, x, lp(noise(.12), 3) * np.exp(-tt(.12) * 30) * .4, .5 * fade)
    add(music, x + b / 2, hat(), .5 * fade); add(music, x, hat(), .3 * fade)
    if k % 8 == 0:
        for n in (57, 60, 64): add(music, x, pad(nf(n), b * 8, .25), .5 * fade)
    x += b; k += 1
for w in ("Обзоры", "Рецепты", "Лайфхаки", "«Погнали", "«Сто"): add(sfx, word(5, w) - .05, ping(990), .5)
# 6. одинокие клики
s = SC[6]; tc = word(6, "появляется") + .2; add(sfx, tc, click(), .9)
ve = vend(6)
for i in range(6): add(sfx, tc + .6 + i * (ve - tc) / 6, click(), .5)
# 7. удар и гул
s = SC[7]; tg = word(7, "ГостБастер") - .25; add(sfx, tg, boom(), .9); add(music, tg, pad(nf(38), s["end"] - tg + 1, .6), .6)
add(sfx, word(7, "нужно") - .1, click(), .6)
# 8. шаги, скрип, сердцебиение, резкий обрыв
s = SC[8]; ve = vend(8)
for i in range(10): add(sfx, s["start"] + .3 + i * .5, lp(noise(.12), 2) * np.exp(-tt(.12) * 25) * .25)
add(sfx, word(8, "Заброшенное"), creak(1.5), .8); heartbeat(word(8, "Фонарик"), ve, 92, .55)
add(sfx, word(8, "Фонарик") - .05, click(), .7)
# 9. ветер, ставни, ворона
s = SC[9]; add(music, s["start"], wind(s["end"] - s["start"], 30), .2)
for x in (s["start"] + 2.5, s["start"] + 4.1, word(9, "Едет") + 1.5): add(sfx, x, thump(90, .15) + .4 * lp(noise(.15), 2) * np.exp(-tt(.15) * 30), .5)
def crow():
    d = .35; tq = tt(d); f = 700 - 300 * tq / d; x = np.sign(np.sin(np.cumsum(f) / SR * 2 * np.pi)) * env(d, .02, .1); return lp(x, 4) * .15
for x in (word(9, "чешский"), word(9, "чешский") + .5): add(sfx, x, crow(), .6)
# 10. поток уведомлений, потом всё замирает
s = SC[10]; ve = vend(10); x = s["start"] + .4; gap = .9
while x < ve + .2:
    add(sfx, x, ping(1100 + rs.integers(0, 6) * 110), .35); x += gap; gap = max(.07, gap * .86)
# 11. «вжух» и аплодисменты
s = SC[11]; add(sfx, word(11, "появляется") + .5, thump(120, .3) * .5 + lp(noise(.3), 3) * np.exp(-tt(.3) * 12) * .3, .7)
add(sfx, word(11, "телевидение") - .5, whoosh(.7), .8)
def applause(d=2.2):
    x = np.zeros(int(d * SR), np.float32)
    for _ in range(int(d * 90)):
        i = rs.integers(0, len(x) - 2000); x[i:i + 600] += lp(noise(600 / SR), 2) * np.exp(-tt(600 / SR) * 200)
    return x * env(d, .2, .8) * .4
for w in ("«Чёрный", "«Импровизации"): add(sfx, word(11, w) - .2, applause(), .7)
for n in (60, 65, 69): add(music, word(11, "телевидение"), pad(nf(n), s["end"] - word(11, "телевидение"), .3), .5)
# 12. пещера, дверь бункера, гудок корабля, «динь»
s = SC[12]
tw = word(12, "пещерах"); [add(sfx, tw + i * .35, tone(1800 - i * 200, .4, 9, (1,)) * .3, .5 * .6 ** i) for i in range(4)]
add(sfx, word(12, "бункерах") - .1, P(sum(tone(f, 1.2, 4, (1,)) for f in (233, 377, 611, 987)) * .2, thump(70, .3)), .8)
th = word(12, "кораблях") - .1; d = 1.6; f = 98
add(sfx, th, lp(sum(np.sin(2 * np.pi * f * m * tt(d)) / m for m in range(1, 8)) * env(d, .1, .4), 3) * .3, .8)
ve = vend(12); add(sfx, ve - .2, bell(nf(84)), .8)
for n in (55, 62, 67): add(music, word(12, "апрелю"), pad(nf(n), s["end"] - word(12, "апрелю") + .5, .3), .45)
# 13. фортепиано и колокольчики
s = SC[13]; prog = [(57, 64, 69), (53, 60, 65), (48, 55, 64), (55, 62, 67)]
x = s["start"] + .3; k = 0
while x < s["end"] + 1:
    ch = prog[k % 4]
    for j, n in enumerate(ch + (ch[1] + 12,)): add(music, x + j * .28, piano(nf(n), 2.4), .3)
    x += 2.4; k += 1
tr = word(13, "Третьего")
for i, n in enumerate((84, 88, 91, 96)): add(sfx, tr + .6 + i * .12, bell(nf(n)), .35)
# 14. музыка поднимается
s = SC[14]
for n, g in ((45, .5), (52, .45), (57, .4), (64, .35), (69, .3)):
    d = s["end"] - s["start"] + 1.5; add(music, s["start"], pad(nf(n), d, .5) * np.linspace(.3, 1.4, int(d * SR)), g)
# 15. финал: щелчок — фонарик гаснет, последняя нота, тишина
s = SC[15]; v15 = [v for v in TL["voice"] if v["at"] >= s["start"] - .01]
e1 = v15[0]["end"]; e2 = v15[1]["end"]
add(sfx, e1 + 1.0, click(), .8)
for n in (57, 64, 69, 73, 76): add(music, e2 + .5, piano(nf(n), 4.5), .32)
add(music, s["start"], pad(nf(45), s["end"] - s["start"], .3), .4)

# --- резкий обрыв в конце сцены 8 и замирание в сцене 10
for sc, pad_s in ((8, .05), (10, .2)):
    a = int((vend(sc) + pad_s) * SR); b = int(SC[sc]["end"] * SR)
    music[a:b] *= 0 if sc == 8 else 0.15; sfx[a:b] = 0 if sc == 8 else sfx[a:b] * 0
# тишина в самом конце
a = int((SC[15]["end"] - .3) * SR); music[a:] = 0; sfx[a:] = 0

# --- приглушение музыки под голосом
envv = np.abs(voice); k = int(.25 * SR); envv = np.convolve(envv, np.ones(k) / k, 'same')
duck = 1 - .45 * np.clip(envv / (envv.max() * .15 + 1e-9), 0, 1)
fade_all = np.ones(N, np.float32); fl = int(1.6 * SR); e = int(SC[15]["end"] * SR); fade_all[max(0, e - fl):e] = np.linspace(1, 0, min(fl, e))
v = voice / (np.abs(voice).max() + 1e-9) * .85
mix = v + (music * duck * .9 + sfx * .8) * fade_all
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
st = np.stack([mix, mix], 1)
raw = os.path.join(ROOT, "audio/mix_raw.f32")
st.astype(np.float32).tofile(raw)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
                "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", str(SR), os.path.join(ROOT, "audio/mix.wav")], check=True)
os.remove(raw)
print("ok", N / SR)
