"""Общие синтезированные звуковые эффекты (numpy)."""
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


def chirp(seed=0):
    r = np.random.default_rng(seed)
    d = r.uniform(0.08, 0.16)
    t = T(d)
    f0 = r.uniform(2800, 4200)
    f = f0 + r.uniform(800, 1600) * np.sin(np.pi * t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2


def whoosh(d=0.6, seed=0):
    t = T(d)
    n = np.random.default_rng(seed).normal(0, 1, len(t))
    n = np.convolve(n, np.ones(6) / 6, "same")
    return n * np.sin(np.pi * t / d) ** 2


def pop():
    t = T(0.12)
    f = 300 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)


def murmur(d, seed=0):
    t = T(d)
    x = brown(d, seed)
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t) * np.sin(2 * np.pi * 1.9 * t + 1)
    return x * mod


def kaching():
    return 0.6 * ping(2093, 0.8) + 0.5 * ping(2637, 0.8) + 0.4 * click()[:int(0.03 * SR)].sum() * 0


def moo(d=1.6):
    t = T(d)
    f = 150 - 40 * t / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 9))
    return x * np.minimum(1, t * 6) * np.minimum(1, (d - t) * 4) * 0.5


def heartbeat():
    t = T(0.5)
    b = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 30)
    out = b.copy()
    j = int(0.18 * SR)
    out[j:] += 0.7 * b[: len(out) - j]
    return out


def scratch(d=0.3, seed=0):
    t = T(d)
    n = np.random.default_rng(seed).normal(0, 1, len(t))
    n = n - np.convolve(n, np.ones(3) / 3, "same")
    return n * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) * np.minimum(1, (d - t) * 20)


def tremolo(d=3.0, f=1800):
    t = T(d)
    return np.sin(2 * np.pi * f * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t)) * (t / d)
