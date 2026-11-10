"""Звук ролика «Что если исчезнет вся трава?»."""
import numpy as np
from core import SR, place, write_wav, brown
from sfx import *  # noqa


def build(path, total, G):
    n = int(total * SR) + SR
    bus = np.zeros(n)
    t = np.arange(n) / SR
    sc = dict(G["SCENES"])
    tc = G["T_CLICK"]
    # музыка/эмбиент: светлый аккорд до щелчка, потом тревожный гул
    warm = sum(np.sin(2 * np.pi * f * t) for f in (261.6, 329.6, 392.0)) / 3
    bus += warm * 0.05 * (t < tc)
    drone = 0.5 * np.sin(2 * np.pi * 46 * t) + 0.35 * np.sin(2 * np.pi * 69.3 * t + np.sin(t * 0.5))
    pad = sum(np.sin(2 * np.pi * f * t) for f in (110, 130.8, 164.8)) / 3
    rise = np.clip((t - tc) / 3, 0, 1)
    bus += (drone * 0.10 + pad * 0.03) * rise
    bus += brown(n / SR, 2) * 0.05 * rise
    # 1. парк
    for k in range(7):
        place(bus, chirp(k), 0.05 + k * 0.13 + (k % 3) * 0.05, 0.12)
    place(bus, pop(), 0.1, 0.3)
    place(bus, click(), tc, 0.9)
    place(bus, boom(1.5), tc, 0.5)
    place(bus, whoosh(0.5, 1), tc - 0.05, 0.3)
    place(bus, murmur(sc["fields"] - sc["brown"], 3), sc["brown"], 0.12)
    for k in range(6):
        place(bus, thump(), sc["brown"] + 0.5 + k * 0.9, 0.12)
    # 2. поля
    sf = G["get_scene"](2)
    for st in sf.starts:
        place(bus, whoosh(1.3, int(st)), st, 0.35)
    for _, ts, _, _ in sf.stamps:
        place(bus, thump(), ts, 0.6)
        place(bus, tick(), ts, 0.3)
    # 3. машина
    car = G["get_scene"](3)
    place(bus, ping(1760, 0.4), car.t0 + 0.3, 0.25)
    place(bus, ping(2349, 0.5), car.t0 + 0.45, 0.25)
    tt = car.t_freeze
    while tt < sc["shop"]:
        place(bus, heartbeat(), tt, 0.6)
        tt += 0.85
    # 4. магазин
    sh = G["get_scene"](4)
    place(bus, murmur(sc["road"] - sc["shop"], 5), sc["shop"], 0.2)
    place(bus, whoosh(0.35, 3), sh.t_grab, 0.3)
    place(bus, whoosh(0.4, 4), sh.t_snatch, 0.45)
    place(bus, thump(), sh.t_snatch + 0.1, 0.5)
    place(bus, kaching(), sc["price"] + 1.0, 0.45)
    place(bus, thump(), sc["price"] + 1.0, 0.5)
    # 5. буря, сель, корова
    rd = G["get_scene"](7)
    wind = brown(sc["flat"] - sc["road"], 9)
    tw = np.arange(len(wind)) / SR
    env = np.clip(tw / 4.0, 0, 1) ** 2 * np.clip((sc["flat"] - sc["road"] - tw) / 2.0, 0, 1)
    env = np.maximum(env * 0.9, 0.25 * np.clip(tw / 2, 0, 1))
    place(bus, wind * env, sc["road"], 0.7)
    place(bus, boom(2.5), sc["mud"] + 0.3, 0.5)
    place(bus, moo(), sc["cow"] + 0.4, 0.25)
    # 6. квартира
    fl = G["get_scene"](11)
    tt = sc["flat"]
    while tt < sc["clock"]:
        place(bus, tick(), tt, 0.12)
        tt += 1.0
    for k, mt in enumerate(fl.mark_t):
        place(bus, scratch(0.3, k), mt, 0.12)
    # 7. часы и кусты
    for ts in (55.4, 56.4):
        place(bus, tick(), ts, 0.7)
        place(bus, thump(), ts, 0.3)
    place(bus, boom(2.0), 57.4, 0.7)
    place(bus, bell(5), 57.4, 0.25)
    bu = G["get_scene"](13)
    for x, y, b, dl in bu.bushes:
        place(bus, pop(), bu.t0 + dl, 0.35)
    place(bus, tremolo(3.0), sc["petal"], 0.05)
    # финал
    place(bus, boom(3.0), sc["end"] + 2.3, 0.6)
    # голос, нарезанный по группам фраз
    voice = load(G["VOICE"])
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.9
    for s0, s1, dst in G["CLIPS"]:
        clip = voice[int(s0 * SR): int(s1 * SR)].copy()
        fl_ = min(len(clip), int(0.02 * SR))
        clip[:fl_] *= np.linspace(0, 1, fl_)
        clip[-fl_:] *= np.linspace(1, 0, fl_)
        place(bus, clip, dst, 1.0)
    bus *= np.clip((total - t) / 0.5, 0, 1)
    bus = np.tanh(bus * 1.1) / np.tanh(1.1)
    bus = bus / (np.abs(bus).max() + 1e-9) * 0.95
    write_wav(path, bus[: int(total * SR)])
    return path
