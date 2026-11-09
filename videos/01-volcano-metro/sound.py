"""Звук: голос + эмбиент + SFX, синтезировано кодом (numpy)."""
import math
import subprocess
import numpy as np
from core import SR, place, write_wav, brown


def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def T(d):
    return np.arange(int(d * SR)) / SR


def boom(d=3.0):
    t = T(d)
    x = brown(d, 1) * np.exp(-t * 1.6) + 0.8 * np.sin(2 * np.pi * (34 - 8 * t) * t) * np.exp(-t * 1.2)
    return x


def click():
    t = T(0.03)
    return np.random.default_rng(2).normal(0, 1, len(t)) * np.exp(-t * 300)


def thump():
    t = T(0.3)
    return np.sin(2 * np.pi * 70 * t) * np.exp(-t * 18) + 0.3 * click()[:len(t)].sum() * 0


def tick():
    t = T(0.04)
    return np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 160)


def drip():
    t = T(0.09)
    f = 1500 - 7000 * t
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 50)


def ping(f, d=1.2):
    t = T(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 5)


def bell(d=6.0):
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * 196 * r * t) * np.exp(-t * dc)
            for r, a, dc in [(0.5, 0.6, 0.6), (1, 1, 0.8), (1.19, 0.5, 1.1), (1.5, 0.4, 1.3), (2.0, 0.35, 1.6),
                             (2.74, 0.2, 2.2)])
    return x / 2.5


def screech(d=1.3):
    t = T(d)
    f = 2300 - 500 * t + 40 * np.sin(2 * np.pi * 9 * t)
    env = np.minimum(1, t * 10) * np.exp(-t * 1.5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env


def creak(d=1.2):
    t = T(d)
    f = 260 - 90 * t + 25 * np.sin(2 * np.pi * 13 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4
    return x * np.minimum(1, t * 8) * np.exp(-t * 1.2)


def step():
    t = T(0.18)
    return (brown(0.18, 5) * 0.8 + np.sin(2 * np.pi * 55 * t)) * np.exp(-t * 25)


def build(path, total, G):
    n = int(total * SR) + SR
    bus = np.zeros(n)
    voice = load(G["VOICE"])
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.9
    t = np.arange(n) / SR
    # эмбиент: низкий гул + минорный пэд
    drone = (0.5 * np.sin(2 * np.pi * 41 * t) + 0.4 * np.sin(2 * np.pi * 55 * t + np.sin(t * 0.3))) \
        * (0.6 + 0.4 * np.sin(t * 0.4))
    drone += 0.6 * brown(n / SR, 3)
    pad = sum(np.sin(2 * np.pi * f * t) for f in (110, 130.8, 164.8)) / 3
    sc = dict((nm, t0) for nm, t0 in G["SCENES"])
    amb = np.full(n, 0.10)
    amb[: int(sc["sky"] * SR)] = 0.18
    amb[int(sc["gate"] * SR): int(sc["rescue"] * SR)] = 0.2
    bus += drone * amb + pad * 0.035 * np.clip((t - 2) / 4, 0, 1)
    # события
    place(bus, boom(), 0.0, 0.55)
    place(bus, screech(), sc["train"] + 0.05, 0.05)
    place(bus, boom(1.0) * 0.5, sc["train"] + 0.05, 0.3)
    tr = G["get_scene"](2)
    tt = tr.t_blink
    while tt < tr.t_off:
        if tr.light(tt) < 0.5:
            place(bus, np.sin(2 * np.pi * 120 * T(0.05)) * 0.5, tt, 0.15)
        tt += 0.05
    place(bus, thump(), tr.t_off, 0.6)
    place(bus, click(), G["get_scene"](3).t_click, 0.5)
    place(bus, click(), G["get_scene"](3).t_click + 0.16, 0.4)
    for nm, ts in G["BADGE_START"].items():
        place(bus, thump(), ts, 0.5)
        place(bus, tick(), ts, 0.3)
    cl = G["get_scene"](5)
    tt = cl.t0 + 0.3
    while tt < cl.t_glass:
        place(bus, drip(), tt, 0.25)
        tt += 0.62
    rng = np.random.default_rng(8)
    for k in range(7):
        place(bus, ping(rng.uniform(2500, 4200)), cl.t_glass + k * 0.35 + rng.uniform(0, 0.15), 0.06)
    dr = G["get_scene"](7)
    place(bus, creak(), dr.t_open, 0.12)
    gs = G["get_scene"](8)
    hiss = np.random.default_rng(4).normal(0, 1, int((gs.t1 - gs.t0) * SR))
    hiss = np.convolve(hiss, np.ones(8) / 8, "same") * np.minimum(1, T(gs.t1 - gs.t0) / 1.5)
    place(bus, hiss, gs.t0, 0.035)
    hs = G["get_scene"](9)
    k = 0
    while hs.t_count + k * 0.55 < hs.t1:
        place(bus, tick(), hs.t_count + k * 0.55, 0.25)
        k += 1
    gt = G["get_scene"](10)
    for k in range(6):
        ts = gt.t0 + (math.pi / 2 + 2 * math.pi * k) / 2.2
        if ts < gt.t1:
            place(bus, boom(1.5), ts - 0.4, 0.25)
    rs = G["get_scene"](11)
    tt = rs.t0 + 0.3
    while tt < sc["ghost"] + 1.5:
        place(bus, step(), tt, 0.3)
        tt += 0.62
    t_none = G["get_scene"](12).t_none
    tt = rs.t0
    while tt < t_none:
        place(bus, tick(), tt, 0.25)
        tt += 1.0
    place(bus, bell(), G["word_t"](27, "выжил") + 0.15, 0.5)
    # голос поверх
    bus[: len(voice)] += voice
    fade = np.clip((total - t) / 0.6, 0, 1)
    bus *= fade
    bus = np.tanh(bus * 1.1) / np.tanh(1.1)
    bus = bus / (np.abs(bus).max() + 1e-9) * 0.95
    write_wav(path, bus[: int(total * SR)])
    return path
