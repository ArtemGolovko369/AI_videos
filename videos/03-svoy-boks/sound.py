"""Звук «Свой бокс»: синтезированная музыка + редкие эффекты + голос, финальная громкость −14 LUFS.

python3 sound.py  → out/mix.wav и готовый svoy_boks.mp4 (нужен out/video.mp4 от art/render.js)
Все звуки и музыка синтезированы этим кодом (numpy), чужих записей нет.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from core import SR, place, write_wav  # noqa
from sfx import load, ping, click, T  # noqa

TM = json.load(open(os.path.join(HERE, "timing.json")))
META = json.load(open(os.path.join(HERE, "out", "meta.json")))
TOTAL = META["TOTAL"]
OUT = os.path.join(HERE, "out")


def wt(i, stem):
    for w, t in TM[i]["words"]:
        if stem in w.lower():
            return t
    return TM[i]["start"]


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- музыка
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
# аккорды (MIDI): светлая часть, кризис, светлый финал
WARM = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]          # C Am F G
CRISIS = [[45, 52, 57, 60], [41, 48, 53, 57], [38, 50, 53, 57], [40, 52, 56, 59]]        # Am F Dm E
BRIGHT = [[41, 53, 57, 60], [43, 55, 59, 62], [48, 55, 60, 64], [48, 55, 64, 67]]        # F G C C(add)


def pad_note(f, d):
    t = T(d)
    x = sum(np.sin(2 * np.pi * f * k * t + k) / (k * k) for k in (1, 2, 3))
    x += 0.5 * np.sin(2 * np.pi * f * 1.003 * t)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
    return x * env


def pluck(f, d=0.9):
    t = T(d)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 5) * np.minimum(1, t * 200)


def music(n):
    bus = np.zeros(n)
    crisis_a, crisis_b = TM[7]["start"] - 0.3, TM[14]["start"] - 0.3
    bright_a = TM[16]["start"] - 0.3
    t, k = 0.0, 0
    while t < n / SR:
        if crisis_a <= t < crisis_b:
            prog, arp_every, octv, gain = CRISIS, 2, 0, 0.7
        elif t >= bright_a:
            prog, arp_every, octv, gain = BRIGHT, 1, 12, 1.0
        else:
            prog, arp_every, octv, gain = WARM, 1, 0, 0.9
        chord = prog[k % 4]
        for nn in chord:
            place(bus, pad_note(midi(nn), BAR + 0.8) * 0.16 * gain, t)
        for j in range(8):
            if j % arp_every:
                continue
            nn = chord[1 + (j % 3)] + 12 + octv
            place(bus, pluck(midi(nn)) * 0.12 * gain, t + j * BEAT / 2)
        t += BAR
        k += 1
    return bus


# ---------------------------------------------------------------- эффекты
def notif():
    return 0.6 * ping(1568, 0.35) + 0.6 * np.concatenate([np.zeros(int(0.09 * SR)), ping(2093, 0.4)])[: int(0.35 * SR)]


def doorbell():
    out = np.zeros(int(1.6 * SR))
    for i, f in enumerate((1318.5, 1046.5)):
        x = ping(f, 1.2) + 0.4 * ping(f * 2.01, 1.2)
        place(out, x, i * 0.35)
    return out


def kaching():
    out = np.zeros(int(1.2 * SR))
    place(out, click()[: int(0.03 * SR)], 0, 0.6)
    place(out, ping(2637, 1.0) + 0.6 * ping(3520, 1.0), 0.06)
    return out


def ring():
    t = T(0.9)
    x = (np.sin(2 * np.pi * 880 * t) + np.sin(2 * np.pi * 1100 * t)) * (np.sin(2 * np.pi * 20 * t) > 0) * 0.5
    out = np.zeros(int(2.2 * SR))
    place(out, x, 0)
    place(out, x, 1.2)
    return out


def rms(x):
    x = x[np.abs(x) > 1e-4]
    return np.sqrt(np.mean(x ** 2)) if len(x) else 1e-9


def build():
    n = int(TOTAL * SR)
    t = np.arange(n) / SR
    voice = np.zeros(n)
    v = load(os.path.join(HERE, "voice_fast.wav"))
    voice[: min(n, len(v))] = v[:n]
    voice /= np.abs(voice).max() + 1e-9
    mus = music(n)
    # музыка на 19 дБ тише голоса (по RMS звучащих участков), мягкий вход и выход
    mus *= rms(voice) / rms(mus) * 10 ** (-19 / 20)
    mus *= np.clip(t / 1.0, 0, 1) * np.clip((TOTAL - t) / 1.5, 0, 1)
    end_t = META["END_T"]
    mus *= np.where(t > end_t, 1 + 1.5 * np.clip((t - end_t) / 0.8, 0, 1), 1)   # в финальной карточке музыка чуть громче
    fx = np.zeros(n)
    place(fx, notif(), wt(1, "пятьсот"), 0.22)
    place(fx, doorbell(), wt(10, "приехал"), 0.18)
    place(fx, kaching(), wt(11, "выручка"), 0.2)
    place(fx, ring(), TM[15]["start"] - 0.15, 0.08)
    place(fx, kaching(), wt(14, "брата"), 0.14)
    mix = voice + mus + fx
    mix /= np.abs(mix).max() + 1e-9
    path = os.path.join(OUT, "mix.wav")
    write_wav(path, mix * 0.9)
    return path


def loudnorm(src, video, dst):
    """Двухпроходная нормализация к −14 LUFS, true peak −1.5 dBTP."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"): r.rindex("}") + 1])
    af = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
          "measured_thresh={input_thresh}:offset={target_offset}:linear=true").format(**m)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-i", src, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-r", "30",
                    "-af", af + ",aresample=48000", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", dst], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", dst, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    print("итоговая громкость:", re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1], "LUFS")


if __name__ == "__main__":
    mix = build()
    loudnorm(mix, os.path.join(OUT, "video.mp4"), os.path.join(HERE, "svoy_boks.mp4"))
