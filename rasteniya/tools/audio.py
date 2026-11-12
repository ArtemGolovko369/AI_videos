"""Звуковая дорожка: голос + синтезированный эмбиент и эффекты (без сторонних сэмплов).
Пишет out/mix.wav. Таймкоды берутся из tools/render.py (якоря по словам)."""
import os, subprocess, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render as R

SR = 48000; N = int(R.END * SR) + SR
rng = np.random.default_rng(7)
mix_bed = np.zeros(N, np.float32); mix_fx = np.zeros(N, np.float32)

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = ((f >= lo) & (f <= hi)).astype(np.float32)
    # soft edges
    m = np.convolve(m, np.ones(64) / 64, "same"); return np.fft.irfft(X * m, len(x)).astype(np.float32)
def noise(sec): return rng.standard_normal(int(round(sec * SR))).astype(np.float32)
def env(n, a, r, shape=1.0):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-3)) * np.clip((n / SR - t) / max(r, 1e-3), 0, 1)
    return (e ** shape).astype(np.float32)
def put(buf, t, x, g=1.0):
    i = int(t * SR); j = min(N, i + len(x))
    if j > i: buf[i:j] += x[:j - i] * g
def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
def ramp(t, pts):  # piecewise-linear gain
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts]).astype(np.float32)

T = np.arange(N) / SR
A = R.A
# ---- drone bed: low minor pad, slowly breathing, grows to the end, drops to silence on «Мир стал серым»
pad = np.zeros(N, np.float32)
for f, g in [(55, .5), (82.41, .35), (110, .3), (130.81, .18), (164.81, .1)]:
    lfo = 1 + .25 * np.sin(2 * np.pi * T / (7 + f % 5))
    pad += g * np.sin(2 * np.pi * f * T + .3 * np.sin(2 * np.pi * .1 * T)) * lfo
air = band(noise(N / SR), 200, 900) * .25
bed = norm(pad + air)
bed *= ramp(T, [(0, 0), (2, .35), (A["d3"], .4), (A["d7"], .5), (A["d12"], .6), (A["ktomu"], .65), (A["d20"], .8),
                (A["mir"] - .2, .85), (A["mir"] + .6, 0.0), (A["rostok"] - .5, 0)])
mix_bed += bed * .16
# ---- hope chord at the sprout + final chord in the outro
def chord(freqs, sec, a=1.5, r=2.5):
    t = np.arange(int(sec * SR)) / SR
    x = sum(np.sin(2 * np.pi * f * t) * (1 + .3 * np.sin(2 * np.pi * .3 * t + f)) for f in freqs)
    x += .3 * sum(np.sin(2 * np.pi * 2 * f * t) for f in freqs)
    return norm(x) * env(len(t), a, r)
put(mix_bed, A["rostok"] - .2, chord([220, 277.18, 329.63, 440], A["shtory"] - A["rostok"] + 1.2, 2.0, 1.2), .14)
put(mix_bed, A["shtory"], chord([110, 164.81, 220, 261.63], 2.5, .3, 2.0), .10)  # turns darker as curtain closes
put(mix_bed, R.OUT_T, chord([110, 220, 277.18, 329.63, 440, 554.37], R.END - R.OUT_T, .6, 2.0), .16)

# ---- effects
def whoosh(sec=.7):
    x = noise(sec); n = len(x); out = np.zeros(n, np.float32); k = 8
    for i in range(k):  # rising band sweep
        s, e = i * n // k, (i + 1) * n // k; f = 300 * (1 + i)
        out[s:e] = band(x, f, f * 2.2)[s:e]
    return norm(out) * env(n, sec * .6, sec * .4, 1.5)
def click(): x = band(noise(.03), 1500, 6000); return norm(x) * env(len(x), .001, .028, 2)
def buzz(sec, f):
    t = np.arange(int(sec * SR)) / SR; x = np.sign(np.sin(2 * np.pi * f * t)) * .5 + np.sin(2 * np.pi * f * 2 * t) * .3
    return band(x.astype(np.float32), 80, 1200)

put(mix_fx, A["propal"] + .1, whoosh(1.0), .18)
for tt, _ in R.DAYS[1:]: put(mix_fx, tt, click(), .35)
for k in range(2): put(mix_fx, A["novosti"] + .1 + k * .35, buzz(.22, 150) * env(int(.22 * SR), .01, .05), .12)
murmur = band(noise(4.5), 200, 800) * (1 + .5 * np.sin(np.arange(int(4.5 * SR)) / SR * 2 * np.pi * 3)).astype(np.float32)
put(mix_fx, A["uchenye1"], norm(murmur) * env(len(murmur), .8, 1.5), .05)
# wind: grows during grass scene, again at day 20
w = band(noise(A["d5"] - A["d3"] + 1), 150, 700); w *= ramp(np.arange(len(w)) / SR, [(0, .2), (A["veter"] - A["d3"], .3), (A["veter"] - A["d3"] + 1.5, 1), (len(w) / SR - 1, .6), (len(w) / SR, 0)])
put(mix_fx, A["d3"], norm(w), .13)
w2 = band(noise(A["vecher"] - A["d20"] + .5), 120, 600)
put(mix_fx, A["d20"], norm(w2) * env(len(w2), 1.0, 1.0), .10)
# bee buzz, fading
t4 = A["d7"] - A["d5"]; tt = np.arange(int(t4 * SR)) / SR
bee = np.sin(2 * np.pi * (230 * tt + 3 * np.sin(2 * np.pi * 6 * tt))) + .4 * np.sin(2 * np.pi * (460 * tt + 6 * np.sin(2 * np.pi * 6 * tt)))
put(mix_fx, A["d5"], bee.astype(np.float32) * np.interp(tt, [0, .5, 4, t4], [0, 1, .6, 0]).astype(np.float32), .035)
# cicadas on the hot street, then thunder + rain on «ливня»
tc = np.arange(int((A["livnya"] - A["d7"]) * SR)) / SR
cic = band(noise(len(tc) / SR), 4000, 7000) * (.6 + .4 * np.sin(2 * np.pi * 9 * tc)).astype(np.float32)
put(mix_fx, A["d7"], norm(cic) * env(len(tc), 1, .5), .05)
th = band(noise(3.5), 25, 180); put(mix_fx, A["livnya"], norm(th) * env(len(th), .02, 3.3, 2), .5)
rn = band(noise(A["d9"] - A["livnya"] + .3), 1500, 9000); put(mix_fx, A["livnya"] + .1, norm(rn) * env(len(rn), .4, .5), .09)
for k in ("pshen", "ris", "kuk"): put(mix_fx, A[k] - .05, whoosh(.45), .12)
crowd = band(noise(A["okaz"] - A["vsego3"]), 150, 900); put(mix_fx, A["vsego3"], norm(crowd) * env(len(crowd), 1.5, 1.0), .05)
# distant moo
tm = np.arange(int(1.4 * SR)) / SR; f0 = 140 - 25 * tm
moo = band((np.sign(np.sin(2 * np.pi * np.cumsum(f0) / SR))).astype(np.float32), 100, 900) * env(len(tm), .3, .6)
put(mix_fx, A["korovy"] + .3, norm(moo), .06)
# low rumble over the forests / globe
ru = band(noise(A["co2"] - A["d12"]), 30, 120); put(mix_fx, A["d12"], norm(ru) * np.linspace(.3, 1, len(ru)).astype(np.float32) * env(len(ru), 1, 1), .14)
# ticking over the thermometer
for k in range(int((A["vse"] - A["co2"]))): put(mix_fx, A["co2"] + .3 + k, click(), .14)
# plankton shimmer
ts = np.arange(int(3.5 * SR)) / SR
sh = sum(np.sin(2 * np.pi * f * ts) * np.clip(np.sin(2 * np.pi * (ts * .7 + f / 997)), 0, 1) ** 4 for f in (1318.5, 1567.98, 1760, 2093))
put(mix_fx, A["ktomu"] + 1.2, (norm(sh) * env(len(ts), .8, 1.5)).astype(np.float32), .035)
# fridge hum
tf = np.arange(int((A["apteka"] - A["zadoh"]) * SR)) / SR
hum = (np.sin(2 * np.pi * 50 * tf) + .5 * np.sin(2 * np.pi * 100 * tf) + .2 * np.sin(2 * np.pi * 150 * tf)).astype(np.float32)
put(mix_fx, A["zadoh"], hum * env(len(tf), .4, .5), .06)
# engine idle at the gas station
te = np.arange(int((A["grib"] - A["zapr"]) * SR)) / SR
eng = band((np.sin(2 * np.pi * 38 * te) * (1 + .5 * np.sin(2 * np.pi * 12 * te))).astype(np.float32) + .3 * rng.standard_normal(len(te)).astype(np.float32), 30, 300)
put(mix_fx, A["zapr"], norm(eng) * env(len(te), .6, .6), .10)
# wet rustle (rot)
wr = band(noise(A["pir"] - A["grib"] + 1), 300, 2500) * (np.abs(np.sin(np.arange(int((A["pir"] - A["grib"] + 1) * SR)) / SR * 2 * np.pi * 1.3)) ** 3).astype(np.float32)
put(mix_fx, A["grib"], norm(wr) * env(len(wr), .5, 1.2), .05)
put(mix_fx, A["propala"] + .3, whoosh(.9), .14)
# water drops on «полил»
for k in range(6):
    td = np.arange(int(.12 * SR)) / SR; f = 900 - 2500 * td
    put(mix_fx, A["polil"] + .1 + k * .18, (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(td), .002, .11, 2)).astype(np.float32), .06)
# sparkle on the sprout
for k, f in enumerate([1760, 2217.46, 2637, 3520]):
    tb = np.arange(int(1.2 * SR)) / SR
    put(mix_fx, A["rostok"] + k * .09, (np.sin(2 * np.pi * f * tb) * np.exp(-tb * 4)).astype(np.float32), .04)
# curtain
cu = band(noise(A["shtory_end"] - A["shtory"] + .5), 400, 4000); put(mix_fx, A["shtory"] + .1, norm(cu) * env(len(cu), .2, .4), .10)

# ---- voice
voice = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(R.ROOT, "audio/voice.mp3"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                                     capture_output=True, check=True).stdout, np.float32)
v = np.zeros(N, np.float32); v[:len(voice)] = voice
v = v / (np.max(np.abs(v)) + 1e-9) * .9
mix = v + mix_bed + mix_fx
mix = mix[:int(R.END * SR)]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
os.makedirs(R.OUT, exist_ok=True)
raw = os.path.join(R.OUT, "_mix.f32")
mix.astype(np.float32).tofile(raw)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", raw,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", os.path.join(R.OUT, "mix.wav")], check=True)
os.remove(raw); print("audio ok")
