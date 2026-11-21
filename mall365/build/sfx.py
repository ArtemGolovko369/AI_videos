"""Синтез звуков и дрона по build/sfx.json, сведение с голосом -> build/mix.wav"""
import json, os, wave
import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
rs = np.random.default_rng(7)
tl = json.load(open(f'{ROOT}/build/timeline.json'))
DUR = tl['duration']
N = int(DUR * SR) + SR

def T(d): return np.arange(int(d * SR)) / SR
def env(d, a=.003, r=.1):
    t = T(d); e = np.minimum(1, t / a) * np.exp(-t / r); return e
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, hz, o=2): return sosfilt(butter(o, hz, 'low', fs=SR, output='sos'), x)
def hp(x, hz, o=2): return sosfilt(butter(o, hz, 'high', fs=SR, output='sos'), x)
def noise(d): return rs.standard_normal(int(d * SR))
def norm(x, peak=1.0): m = np.abs(x).max(); return x / m * peak if m > 0 else x

def thump(f0=70, d=.25, drop=.5, r=.08):
    t = T(d); fr = f0 * (1 - drop * np.minimum(1, t / d)); ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * env(d, .002, r)
def metal(d=.5, base=2200, n=6, r=.15):
    t = T(d); x = np.zeros_like(t)
    for _ in range(n): f = base * (1 + rs.random() * 1.8); x += np.sin(2 * np.pi * f * t + rs.random() * 6) * np.exp(-t / (r * (.5 + rs.random())))
    return x / n
def S_step(): return norm(lp(thump(90, .2, .6, .045) + .25 * lp(noise(.2), 900) * env(.2, .001, .02), 1500), .9)
def S_keys():
    out = np.zeros(int(.9 * SR))
    for k in range(7):
        s = int(rs.random() * .6 * SR); m = metal(.3, 3000 + rs.random() * 2500, 5, .05)
        out[s:s + len(m)] += m[:len(out) - s] * (.5 + rs.random() * .5)
    return norm(hp(out, 1500), .7)
def S_boom():
    d = 2.2; x = thump(55, d, .55, .7) + .4 * lp(noise(d), 200) * env(d, .002, .3)
    return norm(lp(x, 400), 1)
def S_click(): return norm(hp(noise(.03), 2000) * env(.03, .0005, .004), .8)
def S_buzz():
    t = T(.5); x = np.sign(np.sin(2 * np.pi * 100 * t)) * .3 + np.sin(2 * np.pi * 200 * t) * .3
    return norm(lp(x, 1200) * env(.5, .01, .3) * (rs.random(len(t)) > .02), .5)
def S_slam():
    d = 1.4; x = thump(60, d, .4, .25) + .6 * metal(d, 400, 6, .35) + .3 * lp(noise(d), 1500) * env(d, .001, .05)
    return norm(x, 1)
def S_knock(): return norm(bp(thump(180, .18, .3, .03) + .4 * noise(.18) * env(.18, .001, .01), 120, 2500), .9)
def S_pop():
    t = T(.09); fr = 380 + 700 * t / .09; return norm(np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(.09, .002, .03), .6)
def S_error():
    t = T(.5); x = np.sin(2 * np.pi * 220 * t) * (t < .2) + np.sin(2 * np.pi * 165 * t) * (t >= .25)
    return norm(lp(np.sign(x) * .5, 1800) * env(.5, .005, .6), .45)
def S_pencil(d=1.5):
    t = T(d); am = (np.sin(2 * np.pi * 7 * t + np.sin(2 * np.pi * 1.3 * t) * 2) > -.2).astype(float)
    am = lp(am, 40); x = bp(noise(d), 2500, 7000) * am * np.minimum(1, t / .05) * np.minimum(1, (d - t) / .1)
    return norm(x, .35)
def S_ratchet():
    out = np.zeros(int(1.0 * SR))
    for i in range(14): s = int(i * .065 * SR); c = bp(noise(.02), 1500, 6000) * env(.02, .0005, .004); out[s:s + len(c)] += c
    return norm(out, .7)
def S_grate():
    d = 1.3; x = bp(noise(d), 300, 3000) * (.6 + .4 * np.sin(2 * np.pi * 23 * T(d))) + .5 * metal(d, 700, 8, .6)
    return norm(x * np.minimum(1, T(d) / .1) * np.minimum(1, (d - T(d)) / .3), .7)
def S_clack(): return norm(bp(noise(.05), 800, 4000) * env(.05, .0005, .008) + .4 * thump(300, .05, .2, .01), .6)
def S_chime():
    out = np.zeros(int(1.6 * SR))
    for i, f in enumerate([660, 880, 1320]):
        s = int(i * .09 * SR); t = np.arange(len(out) - s) / SR
        out[s:s + len(t)] += np.sin(2 * np.pi * f * t) * np.exp(-t / .4) + .3 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t / .2)
    return norm(out, .45)
def S_heart():
    out = np.zeros(int(.6 * SR)); a = thump(55, .25, .3, .07); out[:len(a)] += a; s = int(.2 * SR); out[s:s + len(a)] += .7 * a
    return norm(lp(out, 300), 1)
def S_tick(): return norm(hp(noise(.02), 3000) * env(.02, .0003, .003) + .5 * np.sin(2 * np.pi * 2500 * T(.02)) * env(.02, .0003, .004), .55)
def S_bells():
    d = 2.0; out = np.zeros(int(d * SR))
    for k in range(10):
        s = int(rs.random() * 1.0 * SR); t = np.arange(len(out) - s) / SR; f = 1800 + rs.random() * 1400
        out[s:] += (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t / .35) * (.4 + .6 * rs.random())
    return norm(out, .7)
def S_drop(): return norm(lp(thump(120, .3, .7, .06) + .3 * noise(.3) * env(.3, .002, .04), 900), .6)
def S_page():
    d = .32; t = T(d); x = bp(noise(d), 1200, 8000) * np.sin(np.pi * t / d) ** 2
    return norm(x, .5)
def S_stamp():
    a = lp(thump(110, .25, .5, .05), 800)
    b = .3 * bp(noise(.08), 500, 3000) * env(.08, .001, .015)
    a[:len(b)] += b
    return norm(a, .8)
def S_alarm():
    t = T(.6); x = np.sin(2 * np.pi * 90 * t) + .5 * np.sin(2 * np.pi * 135 * t)
    return norm(lp(x * env(.6, .01, .25), 500), .8)

GEN = {k[2:]: v for k, v in globals().items() if k.startswith('S_')}

# ---- дрон ----
t = np.arange(N) / SR
lfo = .5 + .5 * np.sin(2 * np.pi * t / 9)
drone = (np.sin(2 * np.pi * 55 * t) + .7 * np.sin(2 * np.pi * 55.4 * t) + .5 * np.sin(2 * np.pi * 82.6 * t) * lfo + .25 * np.sin(2 * np.pi * 110.3 * t))
drone += 1.2 * lp(rs.standard_normal(N), 180)
air = .25 * bp(rs.standard_normal(N), 400, 1800) * (.5 + .5 * np.sin(2 * np.pi * t / 13))
drone = norm(drone + air, 1)
L = tl['lines']
def S(i): return L[i]['t0']
w13 = [w['t0'] for p in L[21]['phrases'] for w in p['words'] if w['w'].startswith('ТРИНАДЦАТЬ')][0]
# огибающая дрона: тише на названии/схемах, обрыв перед «тринадцать», затухание в финале
denv = np.interp(t, [0, 1.5, S(1) - .1, S(1), S(2), 60, S(13), S(15), S(16), S(19), w13 - 1.5, w13 - .05, w13 + .05, w13 + 1.5, S(22), DUR - 3, DUR],
                    [0, .9, 1.0, .5, .7, .75, 1.0, 1.1, .7, .95, .9, .0, .0, .8, .75, .4, 0])
drone *= denv

sfx = np.zeros(N)
for e in json.load(open(f'{ROOT}/build/sfx.json')):
    fn = GEN[e['type']]
    x = fn(e['d']) if 'd' in e else fn()
    s = int(e['t'] * SR); x = x[:max(0, N - s)]
    sfx[s:s + len(x)] += x * e['g']

def read_wav(p):
    with wave.open(p) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
voice = read_wav(f'{ROOT}/build/narration.wav'); voice = np.pad(voice, (0, N - len(voice)))
voice = voice / np.sqrt(np.mean(voice[np.abs(voice) > .01] ** 2)) * .12  # RMS речи ≈ -18 dBFS
# лёгкий ducking дрона и звуков под голос
venv = lp(np.abs(voice), 8, 1); duck = 1 - .45 * np.clip(venv / .08, 0, 1)
mix = voice + .055 * drone * duck + .16 * sfx * (1 - .3 * np.clip(venv / .08, 0, 1))
mix = mix[:int(DUR * SR)]
mix = np.tanh(mix * 1.1) / 1.1
st = np.stack([mix, mix], 1)
with wave.open(f'{ROOT}/build/mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok', mix.shape[0] / SR, 'peak', np.abs(mix).max())
