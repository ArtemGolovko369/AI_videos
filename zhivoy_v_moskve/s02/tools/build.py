"""Сборка серии 2 «Не один».
python3 s02/tools/build.py            → s02/out/zhivoy_v_moskve_s02.mp4
python3 s02/tools/build.py --still 12 → один кадр для проверки
Нужны: s02/frames/*.png (s02/tools/draw.py), s02/audio/voice.mp3, s02/audio/words.json + phrases.json
(python3 tools/align.py s02), audio/music.wav из серии 1.
"""
import json, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
P = lambda *a: os.path.join(ROOT, *a)
W, H, FPS, SR = 1080, 1920, 30, 48000

# ---------------------------------------------------------------- время
# паузы, вставленные в дорожку голоса: (момент исходной озвучки, длительность)
INSERTS = [(19.9, 0.7),    # перед «Колёса снова стучат» — стук возвращается
           (50.6, 2.4),    # после «Отчё-ё-ёт» — стук в стену и стон соседа
           (59.6, 1.3)]    # перед «А в углу вагона…» — колёса замолкают
def T(t): return t + sum(d for a, d in INSERTS if t >= a)
WALL_T = T(50.6) - 2.4                 # начало вставки со стуком
SMILE_T = T(61.15)                     # «улыбается» — кадр с улыбкой зомби
VOICE_END = T(63.4)
TITLE_T = VOICE_END + 2.4
TOTAL = TITLE_T + 6.0

# (кадр, старт, z0, z1, центр0, центр1, тряска)
SHOTS = [
    ("01_golovy",        0.0,      1.05, 1.15, (540, 1100), (540, 1080), .3),
    ("02_ulybka",        T(3.35),  1.15, 1.25, (540, 1080), (540, 1150), 0),
    ("03_pustoy",        T(10.7),  1.15, 1.2,  (540, 1080), (540, 1060), 0),
    ("03_zevok",         T(14.5),  1.15, 1.25, (540, 1080), (540, 1100), 0),
    ("04a_otvorot",      T(15.6),  1.1,  1.05, (540, 1100), (540, 1080), 0),
    ("04b_otvorot",      T(18.95), 1.05, 1.02, (540, 1080), (540, 1060), 0),
    ("04c_vagon",        T(20.0),  1.02, 1.08, (540, 1060), (540, 1020), 0),
    ("05_steklo",        T(23.0),  1.0,  1.7,  (540, 900),  (610, 860), 0),
    ("06_ona",           T(27.1),  1.0,  1.12, (540, 950),  (540, 1100), 0),
    ("07_stanciya",      T(31.45), 1.0,  1.0,  (540, 960),  (540, 960), 0),
    ("07_stanciya",      T(34.2),  1.0,  2.0,  (540, 960),  (785, 1560), 0),
    ("08_chek",          T(36.2),  1.0,  1.12, (540, 900),  (540, 880), 0),
    ("09_zerkalo",       T(43.45), 1.0,  1.18, (540, 900),  (540, 800), 0),
    ("09b_stena",        WALL_T,   1.0,  1.08, (540, 960),  (540, 960), 0),
    ("10_utro",          T(53.65), 1.0,  1.35, (540, 960),  (800, 1000), 0),
    ("10b_telefon",      T(56.85), 1.0,  1.12, (540, 920),  (540, 900), 0),
    ("10_utro",          T(59.7),  1.6,  2.0,  (330, 1000), (300, 1000), 0),
    ("10c_ulybka_zombi", SMILE_T,  1.25, 1.0,  (560, 1050), (560, 960), .25),
    ("11_zastavka",      TITLE_T,  1.0,  1.06, (540, 1000), (540, 980), 0),
]
XFADE = {"04c_vagon": .5, "05_steklo": .5, "07_stanciya": .4, "08_chek": .4, "09_zerkalo": .6,
         "10_utro": .5}

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
    if shake and t - t0 < shake:
        k = 1 - (t - t0)/shake; cx += random.uniform(-14, 14)*k; cy += random.uniform(-14, 14)*k
    # тряска кадра со стеной на стуках
    if name == "09b_stena":
        for kt in (WALL_T + .25, WALL_T + .6):
            if 0 <= t - kt < .2: cx += random.uniform(-10, 10); cy += random.uniform(-10, 10)
    w, h = W/z, H/z
    x0 = min(max(cx - w/2, 0), W - w); y0 = min(max(cy - h/2, 0), H - h)
    return img(name).resize((W, H), Image.BICUBIC, box=(x0, y0, x0+w, y0+h))

def shot_index(t):
    i = 0
    for k, s in enumerate(SHOTS):
        if t >= s[1]: i = k
    return i

# ---------------------------------------------------------------- субтитры
words = [[T(a), T(b), w] for a, b, w in json.load(open(P("audio", "words.json")))]
phrases = json.load(open(P("audio", "phrases.json")))
blocks = []; cur = []; wi = 0
for a, b, txt in phrases:
    n = len(txt.split()); cur += words[wi:wi+n]; wi += n
    if txt.rstrip()[-1] not in "—,:": blocks.append(cur); cur = []
if cur: blocks.append(cur)

RED, YEL, ZGR = (226, 66, 58), (242, 194, 48), (186, 200, 170)
def accent(prev, w, nxt):
    u = w.upper().strip("«»,.:;!?…—"); p = prev.upper().strip("«»,.:;!?…—"); x = nxt.upper().strip("«»,.:;!?…—")
    if u == "ТЕБЯ" and p == "НА": return RED
    if u == "НА" and x == "ТЕБЯ": return RED
    if (u == "ВСЁ" and x == "ЕЩЁ") or (u == "ЕЩЁ" and p == "ВСЁ"): return RED
    if u in ("КРАСНЫЙ", "ТВОЕЙ"): return RED
    if (u == "ПЕРВЫЙ" and x == "ВАГОН") or (u == "ВАГОН" and p == "ПЕРВЫЙ"): return YEL
    if u.startswith("ОТЧЁ"): return ZGR
    return None

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 66)
FONT_Z = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
SUB_Y = int(H*0.70)
SUB_Y_LOW = {"06_ona", "08_chek", "10b_telefon"}   # кадры, где субтитры опускаем ниже предмета

def layout(block):
    toks = [w[2].upper() for w in block]; lines = [[]]; lw = 0; sp = FONT.getlength(" ")
    for k, tk in enumerate(toks):
        tw = FONT.getlength(tk)
        if lines[-1] and lw + sp + tw > W - 120: lines.append([]); lw = 0
        lw += (sp if lines[-1] else 0) + tw; lines[-1].append(k)
    return toks, lines

def draw_subs(frame, t, low=False):
    blk = None
    for b in blocks:
        if b[0][0] - .05 <= t <= b[-1][1] + .35: blk = b
    if blk is None: return frame
    toks, lines = layout(blk)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    lh = 84; y = (int(H*.84) if low else SUB_Y) - (len(lines)*lh)//2; a_in = min(1, (t - blk[0][0] + .05)/.15)
    for ln in lines:
        x = (W - FONT.getlength(" ".join(toks[k] for k in ln)))/2
        for k in ln:
            wd = blk[k]
            col = accent(blk[k-1][2] if k else "", wd[2], blk[k+1][2] if k+1 < len(blk) else "") or (255, 255, 255)
            lit = t >= wd[0]; al = int(255*a_in*(1 if lit else .42))
            jx = random.uniform(-3, 3) if (lit and col == ZGR) else 0
            d.text((x + jx, y), toks[k], font=FONT, fill=(col if lit else (235, 235, 235)) + (al,),
                   stroke_width=6, stroke_fill=(15, 15, 18, int(al*.9)))
            x += FONT.getlength(toks[k] + " ")
        y += lh
    frame.paste(ov, (0, 0), ov); return frame

def draw_moan(frame, t):
    """«М-М-М-М…» из-за стены во время вставки."""
    u = t - (WALL_T + .95)
    if not (0 <= u <= 1.5): return frame
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a = int(255*min(1, u/.15)*min(1, (1.5-u)/.3)); txt = "М-М-М-М…"
    x = (W - FONT_Z.getlength(txt))/2 + random.uniform(-4, 4); y = int(H*.30) + random.uniform(-4, 4)
    d.text((x, y), txt, font=FONT_Z, fill=ZGR + (a,), stroke_width=8, stroke_fill=(20, 22, 18, a))
    frame.paste(ov, (0, 0), ov); return frame

def frame_at(t):
    i = shot_index(t); name, t0 = SHOTS[i][0], SHOTS[i][1]
    f = render_shot(i, t)
    xf = XFADE.get(name, 0) if not (i and SHOTS[i-1][0] == name) else 0
    if i > 0 and xf and t - t0 < xf:
        f = Image.blend(render_shot(i-1, t), f, ease((t - t0)/xf))
    if name == "11_zastavka":
        u = t - t0
        if u < .6: f = Image.blend(Image.new("RGB", (W, H)), f, u/.6)
        if TOTAL - t < .5: f = Image.blend(Image.new("RGB", (W, H)), f, max(0, (TOTAL - t)/.5))
    else:
        f = draw_subs(f, t, name in SUB_Y_LOW); f = draw_moan(f, t)
    return f

# ---------------------------------------------------------------- звук
def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()

def build_audio(out):
    n = int(TOTAL*SR) + SR; rng = np.random.default_rng(2); tt = np.arange(n)/SR
    voice = load(P("audio", "voice.mp3")); music = load(os.path.join(ROOT, "..", "audio", "music.wav"))
    v = np.zeros(n, np.float32); cuts = [0.0] + [a for a, _ in INSERTS] + [len(voice)/SR]
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = voice[int(a*SR):int(b*SR)]; o = int(T(a)*SR); v[o:o+len(seg)] += seg[:max(0, n-o)]
    def lowpass(x, k): return np.convolve(x, np.ones(k)/k, "same").astype(np.float32)
    # музыка: тихий дрон, пропадает в тишине перед улыбкой, возвращается ударом
    m = np.resize(music, n).astype(np.float32); q = 10**(-17/20)
    env = np.full(n, q, np.float32); env[:SR] = np.linspace(0, q, SR)
    def ramp(t0, t1, g0, g1): i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(g0, g1, i1-i0)
    ramp(T(59.6) - 1.3, T(59.6) - 1.0, q, 0); env[int((T(59.6)-1.0)*SR):int(SMILE_T*SR)] = 0
    ramp(SMILE_T, SMILE_T+.5, 0, q*1.6); env[int((SMILE_T+.5)*SR):] = q*1.6
    ramp(TOTAL-1.2, TOTAL, q*1.6, 0); env[int(TOTAL*SR):] = 0
    m *= env
    sfx = np.zeros(n, np.float32)
    click = lowpass(rng.standard_normal(int(.06*SR)).astype(np.float32), 30)*np.exp(-np.linspace(0, 6, int(.06*SR))).astype(np.float32)*1.4
    rumble = lowpass(rng.standard_normal(n).astype(np.float32), 200)*.35
    def wheels(t0, t1):
        tk = t0
        while tk < t1:
            for off in (0, .16):
                i = int((tk+off)*SR); sfx[i:i+len(click)] += click[:max(0, n-i)]
            tk += 1.05
        i0, i1 = int(t0*SR), int(t1*SR); g = np.ones(i1-i0, np.float32)
        r = min(SR//2, (i1-i0)//3); g[:r] = np.linspace(0, 1, r); g[-r//2:] = np.linspace(1, 0, r//2)
        sfx[i0:i1] += rumble[i0:i1]*g
    wheels(T(19.9) - .55, T(31.4))          # стук возвращается под «Колёса снова стучат»
    wheels(T(53.6), T(59.6) - 1.0)          # утренний вагон, обрывается перед финалом
    # тормоза на станции: шипение
    i0 = int(T(31.3)*SR); L = int(1.2*SR)
    sfx[i0:i0+L] += (rng.standard_normal(L)*np.exp(-np.linspace(0, 3, L))*.12).astype(np.float32)
    # стук в стену ×2 и стон соседа
    def thud(t0, f=70, amp=.6):
        i = int(t0*SR); L = int(.35*SR); x = np.arange(L)/SR
        sfx[i:i+L] += (np.sin(2*np.pi*f*x)*np.exp(-x*18)*amp).astype(np.float32)
    thud(WALL_T + .25); thud(WALL_T + .6)
    i0, i1 = int((WALL_T + .95)*SR), int((WALL_T + 2.35)*SR); x = tt[i0:i1]
    moan = (np.sin(2*np.pi*(88 + 7*np.sin(2*np.pi*.9*x))*x) + .4*np.sin(2*np.pi*176*x))*np.sin(np.linspace(0, np.pi, i1-i0))*.11
    sfx[i0:i1] += lowpass(moan.astype(np.float32), 8)
    # низкие удары: хук и улыбка зомби
    def boom(t0, f=42, amp=.55, dec=2.5):
        i = int(t0*SR); L = int(dec*SR); x = np.arange(L)/SR
        sfx[i:i+L] += (np.sin(2*np.pi*f*x*(1-.25*x/dec))*np.exp(-x*2.2)*amp).astype(np.float32)[:max(0, n-i)]
    boom(0.05, 44, .35); boom(SMILE_T); boom(TITLE_T + .1, 38, .45, 3.0)
    mix = np.clip((v + m + sfx*.9)[:int(TOTAL*SR)], -1, 1)
    tmp = P("out", "_mix.f32"); mix.astype(np.float32).tofile(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", out], check=True)
    os.remove(tmp)

def main():
    os.makedirs(P("out"), exist_ok=True)
    wav = P("out", "_audio.wav"); build_audio(wav)
    out = P("out", "zhivoy_v_moskve_s02.mp4")
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
        t = float(sys.argv[sys.argv.index("--still")+1]); frame_at(t).save(P("out", f"still_{t:05.1f}.png"))
    else:
        main()
