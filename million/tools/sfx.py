"""Synthesised sound effects track, timed to the scene events."""
import numpy as np, json, os, wave
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR = 44100
rng = np.random.default_rng(1)
tm = json.load(open(f"{ROOT}/build/timing.json"))
L = [l["s"] for l in tm["lines"]]
DUR = L[10] + tm["lines"][10]["d"] + 2.2
END = L[10] + tm["lines"][10]["d"] + 1.0

def env(n, a=0.003, d=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a)
    if d: e *= np.exp(-t / d)
    return e
def lp(x, k):  # crude low-pass (moving average)
    return np.convolve(x, np.ones(k) / k, mode="same")
def sweep(f0, f1, dur):
    n = int(dur * SR); f = np.geomspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph), n

def pop():
    s, n = sweep(1100, 280, .09); return s * env(n, .002, .03) * .8
def click():
    n = int(.02 * SR); x = rng.standard_normal(n); x = x - lp(x, 6); return x * env(n, .001, .004) * .5
def tick():
    n = int(.03 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * 2600 * t) * env(n, .001, .006) * .45
def whoosh(d=.35):
    n = int(d * SR); x = rng.standard_normal(n); x = lp(x, 9) - lp(x, 40)
    t = np.linspace(0, 1, n); return x * np.sin(np.pi * t) ** 2 * 1.6
def boom():
    s, n = sweep(120, 38, .7); x = rng.standard_normal(n); x = lp(x, 60)
    return (s * 1.0 + x * 2.0) * env(n, .002, .18) * .9
def cash():
    n = int(.8 * SR); t = np.arange(n) / SR
    b = (np.sin(2 * np.pi * 1975 * t) + .6 * np.sin(2 * np.pi * 2637 * t) + .3 * np.sin(2 * np.pi * 3951 * t)) * env(n, .002, .22)
    b2 = np.zeros(n); k = int(.09 * SR); b2[k:] = b[:n - k] * .8
    c = np.zeros(n); c[:int(.02*SR)] = click()[:int(.02*SR)] * 2
    return (b + b2) * .3 + c
def alarm(d=.9):
    n = int(d * SR); t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * 2100 * t)) * .5 + np.sin(2 * np.pi * 2100 * t) * .5
    gate = ((t * 16) % 1 < .55).astype(float)
    return lp(x, 3) * gate * .22
def train(d=2.5):
    n = int(d * SR); x = np.cumsum(rng.standard_normal(n)); x -= lp(x, 2000); x /= np.abs(x).max() + 1e-9
    t = np.arange(n) / SR; clack = np.zeros(n)
    for c in np.arange(.2, d, .45):
        i = int(c * SR); m = min(n - i, int(.05 * SR)); clack[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (SR * .01))
    e = np.minimum(1, t / .3) * np.minimum(1, (d - t) / .4)
    return (x * .7 + lp(clack, 4) * .5) * e * .6
def trombone():
    out = []
    for f, d in [(233, .32), (220, .32), (208, .32), (196, 1.0)]:
        n = int(d * SR); t = np.arange(n) / SR
        vib = 1 + (0.03 * np.sin(2 * np.pi * 6 * t) if d > .5 else 0)
        ph = 2 * np.pi * np.cumsum(f * vib * np.ones(n)) / SR
        x = sum(np.sin(k * ph) / k for k in range(1, 8))
        out.append(lp(x, 5) * env(n, .02) * np.minimum(1, (d - t) / .05) * .25)
    return np.concatenate(out)
def sparkle():
    s, n = sweep(2500, 6000, .35); return s * env(n, .002, .1) * .25
def flip():
    n = int(.09 * SR); x = rng.standard_normal(n); x = lp(x, 3) - lp(x, 25); t = np.linspace(0, 1, n)
    return x * np.sin(np.pi * t) * .9

ev = []
A = lambda t, f, g=1.0: ev.append((t, f, g))
import re
def at(li, pre, k=0):
    n = 0
    for w in tm["words"]:
        if w["line"] != li: continue
        c = re.sub(r"[«»:;,.!?—]", "", w["w"]).lower()
        if c.startswith(pre):
            if n >= k: return w["s"]
            n += 1
    return L[li]
TQ = at(1, "что") - .1
cuts = [L[1], TQ, L[2], L[3], L[4], at(4, "никаких"), L[5], at(5, "дождь") - .15, at(5, "мороз") - .15, at(5, "воскресенье") - .15,
        at(5, "тридцать") - .15, L[6], L[7], at(7, "вкладе"), L[8], L[9], L[10], END]
for c in cuts: A(c - .12, whoosh(), .6)
A(.05, cash(), .9); A(.3, pop())
A(L[1] + .05, pop()); A(at(1, "три"), pop()); A(at(1, "год"), pop())
A(at(1, "семь"), alarm(.9), .8); A(at(1, "сгорел"), boom(), .7)
A(TQ + .2, boom(), .9)
A(L[2] + .2, click()); A(L[2] + .2, tick()); A(L[2] + .4, pop()); A(at(2, "вставать"), pop())
A(at(3, "три"), pop()); A(at(3, "умножить"), pop())
A(at(3, "миллион"), boom(), .8)
for k in range(12): A(at(3, "миллион") + k * .1, tick(), .6)
A(at(3, "больше"), cash(), .9)
A(at(4, "вклад"), pop()); A(at(4, "сто"), cash(), .8); A(at(4, "никаких"), pop()); A(at(4, "никаких") + .4, boom(), .7)
for w in ["дождь", "мороз", "воскресенье", "тридцать"]:
    A(at(5, w) - .15, pop()); A(at(5, w) + .2, cash(), .45)
A(at(5, "тридцать") - .1, sparkle())
A(at(6, "проспала"), pop()); A(at(6, "болела"), pop())
t0c = at(6, "проспала"); span = max(.5, at(6, "сгорело") - t0c)
for j in range(14): A(t0c + j * span / 14, click(), .9)
A(at(6, "сгорело"), pop()); A(at(6, "минус"), trombone(), .8); A(at(6, "минус"), boom(), .6)
A(L[7] + .1, pop()); A(at(7, "мотоцикл") - .2, pop()); A(at(7, "мотоцикл"), train(1.2), .6); A(at(7, "мотоцикл") + .2, sparkle())
A(at(7, "триста"), boom(), .8)
for k in range(8): A(at(7, "вкладе") + k * .1, tick(), .6)
A(at(7, "проценты") + .3, cash(), .8)
A(L[8] + .2, boom(), .7)
for k in range(10): A(at(8, "семьсот") + k * .1, tick(), .5)
A(at(8, "гараже"), pop()); A(at(8, "ноябрь"), trombone(), .7)
for k in range(10): A(at(8, "вики") + k * .1, tick(), .5)
A(at(8, "вики") + 1.0, cash(), .9); A(at(8, "она"), pop())
A(L[9] + .1, boom(), .8); A(at(9, "не"), pop()); A(at(9, "ты"), boom())
A(L[10] + .3, boom(), .8); A(L[10] + .7, pop()); A(L[10] + 1.0, pop()); A(L[10] + 1.8, pop()); A(L[10] + 1.8, sparkle())
A(END + .05, pop())
out = np.zeros(int(DUR * SR) + SR)
for t, x, gn in ev:
    i = max(0, int(t * SR)); out[i:i + len(x)] += x[:len(out) - i] * gn
out = np.clip(out * .8, -1, 1)
st = np.stack([out, out], 1)
with wave.open(f"{ROOT}/build/sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("sfx events:", len(ev), "dur", round(DUR, 2))
