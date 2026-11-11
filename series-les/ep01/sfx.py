"""Синтез фона и звуковых эффектов серии 1 (numpy, без чужих записей → CC0, автор — проект).
Пишет audio/sfx/{bed,fire,fx}.wav длиной во весь ролик.
Времена событий — в секундах озвучки (v), переводятся во время ролика так же, как в timeline.js.
"""
import numpy as np, wave, os

SR = 48000
LEAD = 0.8
INSERTS = [(25.40, 0.6), (79.20, 0.8)]
TITLE_V, TITLE_LEN = 80.6, 5.6


def v2t(v):
    t = v + LEAD
    for p, d in INSERTS:
        if v > p:
            t += d
    return t


TOTAL = v2t(TITLE_V) + TITLE_LEN
N = int(TOTAL * SR)
rs = np.random.default_rng(7)
tt = np.arange(N) / SR


def lp(x, a):  # однополюсный фильтр нижних частот
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y


def lp_fast(x, cutoff):
    # фильтр через FFT (быстро для длинных сигналов)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def bp_fast(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / np.sqrt(1 + (f / hi) ** 4)) * (1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4))
    return np.fft.irfft(X, len(x))


def env_curve(points):
    """кусочно-линейная огибающая по [(t, gain)] во времени ролика"""
    ts, gs = zip(*points)
    return np.interp(tt, ts, gs)


def add(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def save(name, x):
    x = np.clip(x, -1, 1)
    os.makedirs('audio/sfx', exist_ok=True)
    with wave.open(f'audio/sfx/{name}.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


# ---------- 1. ФОН: низкий гул + ветер + мокрый снег снаружи ----------
drone = (np.sin(2 * np.pi * 55 * tt + 0.3 * np.sin(2 * np.pi * 0.07 * tt)) * 0.5
         + np.sin(2 * np.pi * 55.6 * tt) * 0.35
         + np.sin(2 * np.pi * 82.4 * tt + np.sin(2 * np.pi * 0.05 * tt)) * 0.22
         + np.sin(2 * np.pi * 110.3 * tt) * 0.08)
drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * tt)
rumble = lp_fast(rs.standard_normal(N), 120) * 2.5
wind_raw = bp_fast(rs.standard_normal(N), 250, 900)
gust = 0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * tt + 1) * np.sin(2 * np.pi * 0.047 * tt)
wind = wind_raw * (0.35 + 0.65 * np.clip(gust, 0, 1))
sleet = bp_fast(rs.standard_normal(N), 2500, 9000) * 0.6

# громкость слоёв по сценам (время ролика)
outside = env_curve([(0, 0), (v2t(4.4), 0), (v2t(4.8), 1), (v2t(17.9), 1), (v2t(18.4), 0), (TOTAL, 0)])
inside_wind = 0.35 * (1 - outside)
# нарастание гула к финалу, тишина перед «И улыбался», затем заставка
dr_env = env_curve([(0, 0), (0.6, 0.7), (v2t(40), 0.8), (v2t(69), 1.0), (v2t(75.5), 1.25), (v2t(79.0), 1.3),
                    (v2t(79.25), 0.15), (v2t(79.45), 0.15), (v2t(80.3), 0.9), (v2t(TITLE_V) + 1, 0.6), (TOTAL - 1.5, 0.5), (TOTAL, 0)])
bed = (drone * 0.55 + rumble * 0.5) * dr_env + wind * (outside * 1.0 + inside_wind) * dr_env.clip(0, 1) + sleet * outside * 0.5
save('bed', bed)

# ---------- 2. ТРЕСК КОСТРА ----------
def crackle(n, density, seed):
    r = np.random.default_rng(seed)
    out = np.zeros(n)
    k = int(n / SR * density)
    for _ in range(k):
        i = r.integers(0, n - 2000)
        L = r.integers(80, 900)
        burst = r.standard_normal(L) * np.exp(-np.arange(L) / (L / 5)) * (0.3 + r.random() ** 3 * 1.7)
        out[i:i + L] += burst
    out = out - lp_fast(out, 700)            # убрать низ у щелчков
    hiss = bp_fast(r.standard_normal(n), 400, 3000) * 0.08
    roar = lp_fast(r.standard_normal(n), 300) * 0.9 * (0.8 + 0.2 * np.sin(np.arange(n) / SR * 2 * np.pi * 0.6))
    return out + hiss + roar

fire_sig = crackle(N, 14, 3)
fire_env = env_curve([(0, 0), (v2t(35.4), 0), (v2t(35.9), 1.0), (v2t(43.6), 1.0), (v2t(44.3), 0.45),  # печь, потом палка в подвале
                      (v2t(71.6), 0.45), (v2t(72.2), 0), (v2t(TITLE_V) - 0.2, 0), (v2t(TITLE_V) + 0.8, 1.0), (TOTAL - 1.0, 1.0), (TOTAL, 0)])
save('fire', fire_sig * fire_env)

# ---------- 3. ЭФФЕКТЫ ----------
fx = np.zeros(N)

def match_strike(fail=False):
    L = int(0.35 * SR); x = np.arange(L) / SR
    scratch = bp_fast(rs.standard_normal(L), 1500, 7000) * np.exp(-x / 0.05) * 1.2
    flare = bp_fast(rs.standard_normal(L), 300, 3000) * (np.exp(-x / (0.05 if fail else 0.18)) * (1 - np.exp(-x / 0.02))) * 0.8
    return scratch + flare

def thud(f=60, dur=0.6, noise=0.5):
    L = int(dur * SR); x = np.arange(L) / SR
    s = np.sin(2 * np.pi * f * x * (1 - 0.3 * x)) * np.exp(-x / (dur / 4))
    n = lp_fast(rs.standard_normal(L), 400) * np.exp(-x / (dur / 8)) * noise
    return s + n

def creak(dur=1.0, f0=180, f1=120):
    L = int(dur * SR); x = np.arange(L) / SR
    f = np.linspace(f0, f1, L) * (1 + 0.08 * np.sin(2 * np.pi * 7 * x))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    stick = (np.sin(2 * np.pi * 23 * x) > 0.2).astype(float) * 0.6 + 0.4  # «прерывистость» скрипа
    s = bp_fast(saw * stick, 300, 2500)
    return s * np.sin(np.pi * x / dur) ** 0.6

def whoosh(dur=0.45):
    L = int(dur * SR); x = np.arange(L) / SR
    return bp_fast(rs.standard_normal(L), 300, 2500) * np.sin(np.pi * x / dur) ** 2

def hiss(dur=0.8):
    L = int(dur * SR); x = np.arange(L) / SR
    return bp_fast(rs.standard_normal(L), 2500, 9000) * np.exp(-x / 0.25)

def bloom(dur=1.2):
    L = int(dur * SR); x = np.arange(L) / SR
    s = sum(np.sin(2 * np.pi * f * x) for f in (220, 277, 330)) / 3
    return s * (1 - np.exp(-x / 0.08)) * np.exp(-x / 0.4)

def mix(*xs):
    out = np.zeros(max(len(x) for x in xs))
    for x in xs:
        out[:len(x)] += x
    return out

def wood_steps(n=1):
    return mix(thud(70, 0.5, 0.9), creak(0.35, 260, 200) * 0.25)

# чирк спички в начале
add(fx, match_strike(), v2t(-0.58), 0.55)
# шаги на чердаке
for s in (22.38, 23.33):
    add(fx, wood_steps(), v2t(s), 0.9)
# рывок камеры к люку + скрип приоткрытого люка
add(fx, whoosh(), v2t(25.5) + 0.0, 0.35)
add(fx, creak(1.2, 150, 110), v2t(25.9), 0.35)
add(fx, thud(45, 1.2, 0.3), v2t(28.4), 0.5)  # глухой удар на «открыта»
# спички: шесть гаснут, седьмая — загорается
for i, s in enumerate([32.55, 33.05, 33.55, 34.05, 34.55, 35.0, 35.4]):
    add(fx, match_strike(fail=i < 6), v2t(s), 0.45)
add(fx, whoosh(0.8) * 0.8, v2t(35.45), 0.4)  # «вспыхнуло»
# спуск по лестнице: скрип ступеней
for s in np.arange(44.4, 47.2, 0.55):
    add(fx, mix(creak(0.3, 230, 190) * 0.6, thud(90, 0.25, 0.4) * 0.5), v2t(s), 0.4)
for s in np.arange(47.7, 49.9, 0.55):
    add(fx, mix(creak(0.3, 250, 200) * 0.6, thud(90, 0.25, 0.4) * 0.5), v2t(s), 0.35)
# воспоминание
add(fx, bloom(), v2t(61.0), 0.35)
# крышка захлопнулась
add(fx, thud(50, 1.4, 1.2), v2t(69.95), 1.0)
add(fx, creak(0.25, 300, 220), v2t(69.88), 0.4)
# палка гаснет
add(fx, hiss(1.0), v2t(71.65), 0.35)
# чирк в темноте
add(fx, match_strike(), v2t(73.3), 0.55)
# крышка поднимается — долгий скрип
add(fx, creak(1.4, 140, 95), v2t(75.9), 0.5)
save('fx', fx)
print('TOTAL', round(TOTAL, 2))
