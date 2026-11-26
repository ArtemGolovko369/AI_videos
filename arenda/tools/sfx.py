"""Synthesised sound effects track, timed to the scene events."""
import numpy as np, json, os, wave
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR = 44100
rng = np.random.default_rng(1)
tm = json.load(open(f"{ROOT}/build/timing.json"))
L = [l["s"] for l in tm["lines"]]
DUR = L[10] + tm["lines"][10]["d"] + 2.2

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
cuts = [L[1], 7.30, L[2], L[3], L[4], L[5], L[6], L[7], L[8], L[9], L[10]]
for c in cuts: A(c - .12, whoosh(), .6)
for x in [.05, .35, 1.0]: A(x, pop())
A(2.0, cash(), .8)
for x in [.05, .3, 2.2]: A(L[1] + x, pop())
A(L[1] + .9, cash(), .8)
A(7.5, boom(), .9)
A(L[2] + .9, click()); A(L[2] + .9, tick()); A(L[2] + 1.2, pop()); A(L[2] + 4.3, pop()); A(L[2] + 4.35, cash(), .5)
A(L[3], alarm(), 1.0); A(L[3] + 1.95, pop()); A(L[3] + 3.45, boom(), .7); A(L[3] + 4.6, sparkle())
A(L[4] + .02, alarm(.6), .5); A(L[4] + 1.4, train(2.5), 1.0)
for x in [1.45, 2.2, 3.05, 4.0, 4.95]: A(L[4] + x, pop())
for x in [1.0, 2.3, 6.2, 7.6]: A(L[5] + x, pop())
A(L[5] + 3.9, boom(), .8)
for k in range(9): A(L[5] + 3.9 + k * .1, tick(), .7)
A(L[6] + .2, whoosh(.25), .5); A(L[6] + .2, cash(), .6); A(L[6] + 2.4, whoosh(.25), .5); A(L[6] + 2.45, click())
for k in range(6): A(L[6] + 3.6 + k * .1, tick(), .6)
A(L[6] + 5.5, pop()); A(L[6] + 8.0, boom()); A(L[6] + 8.02, cash(), .6)
A(L[7] + 2.9, trombone(), .9); A(L[7] + 3.9, pop())
A(L[8] + .4, pop())
for k in range(6): A(L[8] + 3.0 + k * .32, flip())
A(L[8] + 3.1, boom(), .6); A(L[8] + 5.45, pop()); A(L[8] + 6.6, cash()); A(L[8] + 6.6, boom(), .6); A(L[8] + 7.7, boom(), .7)
A(L[9] + .2, boom(), .7)
for x in [.4, 1.4, 3.2]: A(L[9] + x, pop())
A(L[9] + 3.9, boom()); A(L[9] + 3.92, cash(), .5)
A(L[10] + .4, boom()); A(L[10] + .8, pop()); A(L[10] + 1.1, pop()); A(L[10] + 2.9, pop()); A(L[10] + 2.9, sparkle())

out = np.zeros(int(DUR * SR) + SR)
for t, x, gn in ev:
    i = max(0, int(t * SR)); out[i:i + len(x)] += x[:len(out) - i] * gn
out = np.clip(out * .8, -1, 1)
st = np.stack([out, out], 1)
with wave.open(f"{ROOT}/build/sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("sfx events:", len(ev), "dur", round(DUR, 2))
