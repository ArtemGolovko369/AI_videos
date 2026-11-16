"""Сборка серии 6 «Стук».
python3 s06/tools/build.py               → s06/out/zhivoy_v_moskve_s06.mp4
python3 s06/tools/build.py --still 12 30 → отдельные кадры
Нужны: s06/frames (s06/tools/draw.py), s06/audio/voice.mp3 + mama.mp3 + vera.mp3,
words/phrases.json (python3 tools/align.py s06), audio/music.wav из серии 1.
"""
import json, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
P = lambda *a: os.path.join(ROOT, *a)
W, H, FPS, SR = 1080, 1920, 30, 48000

# ---------------------------------------------------------------- реплики: (кто, сдвиг в паузе, начало куска, конец куска, фильтр, [(s, e, текст)])
# фильтр: "door" — за дверью, "far" — глухо сверху, None — как есть
INSERTS = [
    (2.30, 5.30, [("v", 2.30, 0.00, 2.62, "door", [(0.00, 2.56, "Это я. Открой. Мне страшно.")])]),
    (5.10, 1.90, [("m", 0.20, 0.00, 1.40, None, [(0.00, 1.33, "Послушай, как она говорит.")])]),
    (12.20, 4.30, [("v", 0.30, 3.60, 7.16, "door", [(0.08, 1.33, "Я знаю, что ты там."), (1.87, 3.56, "Я слышу, как ты дышишь.")])]),
    (16.55, 3.90, [("m", 0.30, 2.05, 5.30, None, [(0.09, 0.73, "Балкон."), (0.90, 1.59, "Люк в полу."), (1.92, 3.13, "Спускайся до первого.")])]),
    (22.98, 1.70, [("m", 0.20, 5.72, 6.88, None, [(0.08, 1.04, "Я её задержу.")])]),
    (26.15, 2.80, [("m", 0.30, 7.45, 9.60, "far", [(0.12, 1.18, "Верочка. Заходи."), (1.35, 1.99, "Чай будешь?")])]),
    (36.95, 1.30, []),                                   # задержка дыхания на пятом
]
def T(t): return t + sum(d for a, d, _ in INSERTS if t >= a)
def ins_start(i): return T(INSERTS[i][0]) - INSERTS[i][1]
I1 = ins_start(0)
LIGHT_T = T(44.25)
WAVE_T = T(45.9)
NARR_END = T(50.83)
TITLE_T = NARR_END + 2.4
TOTAL = TITLE_T + 6.0

# (кадр, старт, z0, z1, центр0, центр1, тряска)
SHOTS = [
    ("01_lift5",      0.0,       1.0, 1.0, (540, 900), (540, 900), 0),
    ("01_lift6",      0.5,       1.0, 1.0, (540, 900), (540, 900), 0),
    ("01_lift7",      1.0,       1.0, 1.0, (540, 900), (540, 900), 0),
    ("01_lift8",      1.5,       1.0, 1.0, (540, 900), (540, 900), 0),
    ("01_lift9",      2.0,       1.0, 1.06, (540, 900), (540, 880), 0),
    ("02_dver",       I1 + .6,   1.0, 1.15, (540, 960), (540, 900), 0),
    ("03_ruka",       ins_start(1), 1.0, 1.1, (540, 1100), (500, 1120), 0),
    ("03_uho",        T(5.4),    1.0, 1.15, (540, 980), (480, 990), 0),
    ("04_vera_glazok", ins_start(2), 1.0, 1.15, (540, 900), (540, 880), 0),
    ("04b_chek",      T(12.5),   1.05, 1.15, (540, 900), (540, 800), 0),
    ("05_mama_temno", ins_start(3), 1.0, 1.08, (540, 960), (500, 940), 0),
    ("06_luk",        T(16.85),  1.0, 1.25, (540, 960), (540, 980), 0),
    ("05_mama_temno", ins_start(4), 1.1, 1.18, (540, 900), (540, 880), 0),
    ("06_spusk",      T(23.15),  1.7, 1.7, (700, 520), (700, 1450), 0),
    ("07_pyatyy",     T(29.6),   1.0, 1.2, (540, 900), (540, 800), 0),
    ("08_zemlya",     T(37.3),   1.15, 1.0, (540, 1250), (540, 1100), 0),
    ("09a_dom_temno", T(41.95),  1.2, 1.9, (540, 900), (470, 640), 0),
    ("09b_dom_svet",  LIGHT_T,   1.9, 2.0, (470, 640), (470, 640), 0),
    ("10_okno0",      T(45.5),   1.0, 1.12, (540, 1000), (540, 1050), 0),
    ("11_zastavka",   TITLE_T,   1.0, 1.06, (540, 1000), (540, 980), 0),
]
XFADE = {"02_dver": .4, "03_uho": .3, "04b_chek": .3, "06_luk": .4, "06_spusk": .5, "07_pyatyy": .5, "08_zemlya": .6, "09a_dom_temno": .5, "10_okno0": .4}
KNOCKS = [I1 + 1.5, I1 + 1.78, I1 + 2.06]

imgs = {}
def img(name):
    if name not in imgs: imgs[name] = Image.open(P("frames", name + ".png")).convert("RGB")
    return imgs[name]
def ease(x): return x*x*(3-2*x)

def render_shot(i, t):
    name, t0, z0, z1, c0, c1, shake = SHOTS[i]
    t1 = SHOTS[i+1][1] if i+1 < len(SHOTS) else TOTAL
    e = ease(min(max((t - t0)/max(t1 - t0, .01), 0), 1))
    z = z0 + (z1-z0)*e; cx = c0[0] + (c1[0]-c0[0])*e; cy = c0[1] + (c1[1]-c0[1])*e
    if name == "02_dver":
        for kt in KNOCKS:
            if 0 <= t - kt < .12: cx += random.uniform(-9, 9); cy += random.uniform(-9, 9)
    w, h = W/z, H/z
    x0 = min(max(cx - w/2, 0), W - w); y0 = min(max(cy - h/2, 0), H - h)
    src = name
    if name == "10_okno0" and t >= WAVE_T:   # синхронный взмах обеих
        src = "10_okno1" if int((t - WAVE_T)/.38) % 2 == 0 else "10_okno2"
    return img(src).resize((W, H), Image.BICUBIC, box=(x0, y0, x0+w, y0+h))

def shot_index(t):
    i = 0
    for k, s in enumerate(SHOTS):
        if t >= s[1]: i = k
    return i

# ---------------------------------------------------------------- субтитры
words = [[T(a), T(b), w, "n"] for a, b, w in json.load(open(P("audio", "words.json")))]
phrases = json.load(open(P("audio", "phrases.json")))
blocks = []; cur = []; wi = 0
for a, b, txt in phrases:
    n = len(txt.split()); cur += words[wi:wi+n]; wi += n
    if txt.rstrip()[-1] not in "—,:": blocks.append(cur); cur = []
if cur: blocks.append(cur)
def line_block(t0, s, e, txt, who):
    ws = txt.split(); ln = [len(w) + 2 for w in ws]; tt = t0 + s; out = []
    for w, l in zip(ws, ln):
        d = (e - s)*l/sum(ln); out.append([tt, tt + d, w, who]); tt += d
    return out
for i, (at, dur, pieces) in enumerate(INSERTS):
    for who, off, a, b, flt, sents in pieces:
        for s, e, txt in sents: blocks.append(line_block(ins_start(i) + off, s, e, txt, who))
blocks.sort(key=lambda b: b[0][0])

RED, YEL = (226, 66, 58), (242, 194, 48)
COLOR = {"m": (202, 228, 190), "v": (243, 205, 198)}
def clean(w): return w.upper().strip("«»,.:;!?…—")
def accent(prev, w, nxt, who):
    u, p, x = clean(w), clean(prev), clean(nxt)
    if u == "ДЫШИШЬ": return RED
    if who in COLOR: return COLOR[who]
    if u in ("НИ", "ОДНОГО", "ВДОХА") and (u != "НИ" or x == "ОДНОГО"): return RED
    if u in ("ВОСЬМОЙ", "СЕДЬМОЙ", "ШЕСТОЙ", "ПЯТЫЙ", "ЛЮК", "ДЕВЯТОМ"): return YEL
    if (u == "СЛИШКОМ" and x == "СПОКОЙНЫЙ") or u == "СПОКОЙНЫЙ": return RED
    if u in ("ОДНУ", "СЕКУНДУ") or (u == "В" and x == "ОДНУ") or (u in ("И", "ТУ", "ЖЕ") and p in ("ОДНУ", "И", "ТУ")): return RED
    return None

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 66)
FONT_I = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf", 70)
SUB_Y = int(H*0.70)
SUB_Y_LOW = {"03_uho", "04b_chek", "05_mama_temno", "09a_dom_temno", "09b_dom_svet", "10_okno0"}

def layout(block, font):
    toks = [w[2].upper() for w in block]; lines = [[]]; lw = 0; sp = font.getlength(" ")
    for k, tk in enumerate(toks):
        tw = font.getlength(tk)
        if lines[-1] and lw + sp + tw > W - 120: lines.append([]); lw = 0
        lw += (sp if lines[-1] else 0) + tw; lines[-1].append(k)
    return toks, lines

def draw_subs(frame, t, low=False):
    blk = None
    for b in blocks:
        if b[0][0] - .05 <= t <= b[-1][1] + .35: blk = b
    if blk is None: return frame
    who = blk[0][3]; font = FONT if who == "n" else FONT_I
    toks, lines = layout(blk, font)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    lh = 84; y = (int(H*.84) if low else SUB_Y) - (len(lines)*lh)//2; a_in = min(1, (t - blk[0][0] + .05)/.15)
    for ln in lines:
        x = (W - font.getlength(" ".join(toks[k] for k in ln)))/2
        for k in ln:
            wd = blk[k]
            col = accent(blk[k-1][2] if k else "", wd[2], blk[k+1][2] if k+1 < len(blk) else "", who) or (255, 255, 255)
            lit = t >= wd[0]; al = int(255*a_in*(1 if lit else .42))
            d.text((x, y), toks[k], font=font, fill=(col if lit else (235, 235, 235)) + (al,),
                   stroke_width=6, stroke_fill=(15, 15, 18, int(al*.9)))
            x += font.getlength(toks[k] + " ")
        y += lh
    frame.paste(ov, (0, 0), ov); return frame

def frame_at(t):
    i = shot_index(t); name, t0 = SHOTS[i][0], SHOTS[i][1]
    f = render_shot(i, t)
    xf = XFADE.get(name, 0) if not (i and SHOTS[i-1][0] == name) else 0
    if i > 0 and xf and t - t0 < xf:
        f = Image.blend(render_shot(i-1, t), f, ease((t - t0)/xf))
    if name == "10_okno0" and t > NARR_END + 1.0:
        f = ImageEnhance.Brightness(f).enhance(max(0, 1 - (t - NARR_END - 1.0)/1.4))
    if name == "11_zastavka":
        u = t - t0
        if u < .6: f = Image.blend(Image.new("RGB", (W, H)), f, u/.6)
        if TOTAL - t < .5: f = Image.blend(Image.new("RGB", (W, H)), f, max(0, (TOTAL - t)/.5))
    else:
        f = draw_subs(f, t, name in SUB_Y_LOW)
    return f

# ---------------------------------------------------------------- звук
def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()
def lowpass(x, k): return np.convolve(x, np.ones(k)/k, "same").astype(np.float32)

def build_audio(out):
    n = int(TOTAL*SR) + SR; rng = np.random.default_rng(6); tt = np.arange(n)/SR
    voice = load(P("audio", "voice.mp3")); src = {"m": load(P("audio", "mama.mp3")), "v": load(P("audio", "vera.mp3"))}
    music = load(os.path.join(ROOT, "..", "audio", "music.wav"))
    v = np.zeros(n, np.float32); lines = np.zeros(n, np.float32)
    cuts = [0.0] + [a for a, _, _ in INSERTS] + [len(voice)/SR]
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = voice[int(a*SR):int(b*SR)]; o = int(T(a)*SR); v[o:o+len(seg)] += seg[:max(0, n-o)]
    for i, (at, dur, pieces) in enumerate(INSERTS):
        for who, off, a, b, flt, _ in pieces:
            seg = src[who][int(a*SR):int(b*SR)].copy()
            if flt == "door": seg = lowpass(seg, 5)*1.15                      # за дверью: чуть глуше
            if flt == "far":  seg = lowpass(seg, 14)*1.3                      # сверху: глухо
            o = int((ins_start(i) + off)*SR); lines[o:o+len(seg)] += seg*.95
    # музыка: тихо; пропадает на пятом этаже и после света, возвращается на заставке
    m = np.resize(music, n).astype(np.float32); q = 10**(-27/20)
    env = np.full(n, q, np.float32); env[:SR] = np.linspace(0, q, SR)
    def ramp(t0, t1, g0, g1): i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(g0, g1, i1-i0)
    ramp(T(29.6), T(29.6) + .5, q, 0); env[int((T(29.6)+.5)*SR):int(T(37.3)*SR)] = 0; ramp(T(37.3), T(37.3) + 1, 0, q)
    ramp(LIGHT_T, LIGHT_T + .3, q, 0); env[int((LIGHT_T+.3)*SR):int(TITLE_T*SR)] = 0
    ramp(TITLE_T, TITLE_T + .4, 0, q*1.6); env[int((TITLE_T+.4)*SR):] = q*1.6
    ramp(TOTAL - 1.2, TOTAL, q*1.6, 0); env[int(TOTAL*SR):] = 0
    m *= env
    sfx = np.zeros(n, np.float32)
    def add(t0, x): i = int(t0*SR); sfx[i:i+len(x)] += x[:max(0, n-i)]
    def noise(d, k=30): return lowpass(rng.standard_normal(int(d*SR)).astype(np.float32), k)
    def ping(f, d, amp, dec=6):
        L = int(d*SR); x = np.arange(L)/SR; return (np.sin(2*np.pi*f*x)*np.exp(-x*dec)*amp).astype(np.float32)
    # лифт: гул и звонок
    i1 = int((I1 + .2)*SR); sfx[:i1] += (np.sin(2*np.pi*80*tt[:i1])*.03 + lowpass(rng.standard_normal(i1).astype(np.float32), 150)[:i1]*.25).astype(np.float32)
    for k in range(5): add(k*.5, ping(1200, .08, .05, 40))                       # щелчок табло
    add(I1 + .2, ping(880, 1.2, .12, 3)); add(I1 + .45, ping(660, 1.4, .12, 3))
    # шаги по площадке
    for k in range(4): add(I1 + .7 + k*.22, ping(90, .2, .35, 25) + noise(.2, 6)*.08)
    # стук в дверь
    for kt in KNOCKS: add(kt, ping(170, .25, .6, 30) + noise(.25, 3)*.15)
    # балкон: ветер, люк, ступени
    i0, i1 = int(T(16.85)*SR), int(T(29.6)*SR)
    wind = lowpass(rng.standard_normal(i1-i0).astype(np.float32), 400)*1.1
    g = np.ones(i1-i0, np.float32); g[:SR] = np.linspace(0, 1, SR); g[-SR//2:] = np.linspace(1, 0, SR//2)
    sfx[i0:i1] += wind*g
    clank = sum(ping(f, .8, .06, 7) for f in (420, 1130, 2210))
    add(T(16.9), clank)
    for k in range(9): add(T(23.2) + k*.65, ping(900 + 60*(k % 3), .15, .05, 25))   # ступени лестницы
    # тишина на пятом — ничего; земля: ночной город
    i0, i1 = int(T(37.3)*SR), int(TITLE_T*SR)
    city = lowpass(rng.standard_normal(i1-i0).astype(np.float32), 300)*.8
    g = np.ones(i1-i0, np.float32); g[:SR] = np.linspace(0, 1, SR); g[-SR:] = np.linspace(1, 0, SR)
    sfx[i0:i1] += city*g
    add(T(37.3), ping(70, .4, .5, 12))                                             # приземление
    add(LIGHT_T, noise(.03, 1)*.12)                                               # далёкий щелчок света
    # удары
    def boom(t0, f=42, amp=.55, dec=2.5):
        L = int(dec*SR); x = np.arange(L)/SR
        add(t0, (np.sin(2*np.pi*f*x*(1-.25*x/dec))*np.exp(-x*2.2)*amp).astype(np.float32))
    boom(LIGHT_T, 46, .3); boom(NARR_END + .4, 40, .55); boom(TITLE_T + .1, 38, .45, 3.0)
    # сведение: фон тихо + приглушение под голосом
    speech = v + lines
    act = (np.convolve(np.abs(speech), np.ones(SR//10)/(SR//10), "same") > 0.02).astype(np.float32)
    act = np.convolve(act, np.ones(SR//4)/(SR//4), "same")
    duck = 1 - 0.5*act
    mix = np.clip((speech + (m + sfx*.3)*duck)[:int(TOTAL*SR)], -1, 1)
    tmp = P("out", "_mix.f32"); mix.astype(np.float32).tofile(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", out], check=True)
    os.remove(tmp)

def main():
    os.makedirs(P("out"), exist_ok=True)
    wav = P("out", "_audio.wav"); build_audio(wav)
    out = P("out", "zhivoy_v_moskve_s06.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    nf = int(TOTAL*FPS); random.seed(5)
    for k in range(nf):
        ff.stdin.write(frame_at(k/FPS).tobytes())
        if k % 300 == 0: print(f"{k}/{nf}", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print("готово:", out, f"{TOTAL:.1f} c")

if __name__ == "__main__":
    if "--still" in sys.argv:
        os.makedirs(P("out"), exist_ok=True)
        for a in sys.argv[sys.argv.index("--still")+1:]:
            t = float(a); frame_at(t).save(P("out", f"still_{t:05.1f}.png"))
    else:
        main()
