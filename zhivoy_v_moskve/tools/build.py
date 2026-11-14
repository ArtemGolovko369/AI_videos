"""Сборка ролика «Живой в Москве», серия 1.
python3 tools/build.py [--preview]   → out/zhivoy_v_moskve_s01.mp4
Нужны: frames/*.png (tools/draw.py), audio/voice.mp3, audio/zombie_otchet.mp3, audio/music.wav,
audio/words.json (tools/align.py).
"""
import json, os, subprocess, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
W, H, FPS = 1080, 1920, 30
PREVIEW = "--preview" in sys.argv
SR = 48000

# ---------------------------------------------------------------- время
# Вставки в дорожку голоса: (момент в исходной озвучке, длительность паузы)
INS_ZOMBIE_AT, INS_ZOMBIE = 34.55, 2.5      # после «…поворачивается к тебе» — реплика «Отчё-ё-ёт…»
INS_SILENCE_AT, INS_SILENCE = 59.25, 1.6    # после «Совсем чуть-чуть» — тишина, колёса замолкают
def T(t):  # исходное время голоса → время ролика
    return t + (INS_ZOMBIE if t >= INS_ZOMBIE_AT else 0) + (INS_SILENCE if t >= INS_SILENCE_AT else 0)
ZOMBIE_T = T(INS_ZOMBIE_AT) - INS_ZOMBIE + 0.35
VOICE_END = T(61.65)
HEADS_T = T(60.75)          # «поворачивает» — все головы разом
TITLE_T = VOICE_END + 2.3
TOTAL = TITLE_T + 6.0

# ---------------------------------------------------------------- сцены
# (кадр, старт, z0, z1, (cx0,cy0), (cx1,cy1), shake)
SHOTS = [
    ("01_siti",      0.0,  1.00, 1.10, (540, 900), (560, 860), 0),
    ("02_sverhu",    T(3.95), 1.05, 1.9, (540, 1000), (534, 1166), 0),
    ("03_podezd",    T(7.55), 1.00, 1.12, (540, 960), (540, 900), 0),
    ("04_dvor",      T(12.2), 1.08, 1.08, (600, 1300), (480, 1300), 0),
    ("04b_sosed",    T(15.9), 1.00, 1.10, (540, 900), (540, 860), 0),
    ("05_metro",     T(19.95), 1.15, 1.02, (540, 1100), (540, 1000), 0),
    ("06_zazhat",    T(26.65), 1.00, 1.12, (540, 900), (540, 820), 0),
    ("07_ofis",      T(29.7), 1.00, 1.08, (540, 1100), (540, 1200), 0),
    ("07b_nachalnik", T(33.85), 1.05, 1.25, (540, 1300), (540, 1420), 0),
    ("08_kuryer",    T(35.05), 1.00, 1.10, (560, 960), (540, 900), 0),
    ("08b_probka",   T(39.25), 1.10, 1.00, (500, 1300), (580, 1250), 0),
    ("09_vitrina",   T(41.5), 1.00, 1.30, (540, 960), (540, 860), 0),
    ("10_vagon",     T(51.95), 1.00, 1.06, (540, 1100), (540, 1050), 0),
    ("10a_telefon",  T(53.95), 1.05, 1.18, (540, 900), (540, 880), 0),
    ("10b_lico",     T(56.55), 1.00, 1.06, (540, 1000), (540, 1020), 0),
    ("10b_ulybka",   T(57.35), 1.06, 1.22, (540, 1020), (540, 1150), 0),
    ("10_vagon",     T(59.45), 1.10, 1.10, (540, 1100), (540, 1100), 0),
    ("10c_golovy",   HEADS_T, 1.18, 1.05, (540, 1150), (540, 1100), 0.25),
    ("11_zastavka",  TITLE_T, 1.00, 1.06, (540, 1000), (540, 980), 0),
]
# мягкие растворения (сек) на входе в сцену; 0 = жёсткая склейка
XFADE = {"02_sverhu": .5, "03_podezd": .4, "04_dvor": .4, "05_metro": .4, "06_zazhat": .3, "07_ofis": .4,
         "08_kuryer": .3, "09_vitrina": .5, "10_vagon": .5, "10a_telefon": .3, "11_zastavka": 0}

imgs = {}
def img(name):
    if name not in imgs:
        imgs[name] = Image.open(P("frames", name + ".png")).convert("RGB")
    return imgs[name]

def ease(x): return x*x*(3-2*x)

def render_shot(i, t):
    name, t0, z0, z1, c0, c1, shake = SHOTS[i]
    t1 = SHOTS[i+1][1] if i+1 < len(SHOTS) else TOTAL
    u = min(max((t - t0) / max(t1 - t0, .01), 0), 1); e = ease(u)
    z = z0 + (z1 - z0)*e; cx = c0[0] + (c1[0]-c0[0])*e; cy = c0[1] + (c1[1]-c0[1])*e
    if shake and t - t0 < shake:
        k = 1 - (t - t0)/shake; cx += random.uniform(-14, 14)*k; cy += random.uniform(-14, 14)*k
    w, h = W/z, H/z
    x0 = min(max(cx - w/2, 0), W - w); y0 = min(max(cy - h/2, 0), H - h)
    return img(name).resize((W, H), Image.BICUBIC, box=(x0, y0, x0+w, y0+h))

def shot_index(t):
    i = 0
    for k, s in enumerate(SHOTS):
        if t >= s[1]: i = k
    return i

# ---------------------------------------------------------------- субтитры (караоке, стиль «Что если…»)
words = json.load(open(P("audio", "words.json")))
words = [[T(a), T(b), w] for a, b, w in words]
RED, YEL = (226, 66, 58), (242, 194, 48)
def accent(prev, w, nxt):
    u = w.upper().strip("«»,.:;!?…—")
    if u.startswith("ЗОМБИ"): return RED
    if u == "МОСКВЕ": return YEL
    if u == "ТОЛЬКО" or (u == "ТЫ" and prev.upper().startswith("ТОЛЬКО")): return YEL
    if u == "ПОКАЗЫВАЙ" or (u == "НЕ" and nxt.upper().startswith("ПОКАЗЫВАЙ")): return RED
    if u in ("ЛЮБЛЮ", "УЛЫБАЕШЬСЯ"): return YEL
    if u == "ЖИВОЙ" and prev.upper() == "ТЫ": return YEL
    return None
# блоки = фразы из align.py; фраза, оканчивающаяся на «—», «,» или «:», склеивается со следующей
phrases = json.load(open(P("audio", "phrases.json")))
blocks = []; cur = []; wi = 0
for a, b, txt in phrases:
    n = len(txt.split()); cur += words[wi:wi+n]; wi += n
    if txt.rstrip()[-1] not in "—,:": blocks.append(cur); cur = []
if cur: blocks.append(cur)

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 66)
FONT_Z = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
SUB_Y = int(H*0.70)
def layout(block):
    toks = [w[2].upper() for w in block]
    lines = [[]]; lw = 0; space = FONT.getlength(" ")
    for k, tk in enumerate(toks):
        tw = FONT.getlength(tk)
        if lines[-1] and lw + space + tw > W - 120: lines.append([]); lw = 0
        lw += (space if lines[-1] else 0) + tw; lines[-1].append(k)
    return toks, lines

def draw_subs(frame, t):
    # блок, который сейчас звучит (с хвостом 0.35 с)
    blk = None
    for b in blocks:
        if b[0][0] - 0.05 <= t <= b[-1][1] + 0.35: blk = b
    if blk is None: return frame
    toks, lines = layout(blk)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    lh = 84; y = SUB_Y - (len(lines)*lh)//2
    a_in = min(1, (t - blk[0][0] + 0.05)/0.15)
    for ln in lines:
        txt = " ".join(toks[k] for k in ln); x = (W - FONT.getlength(txt))/2
        for k in ln:
            wd = blk[k]; tk = toks[k]
            col = accent(blk[k-1][2] if k else "", wd[2], blk[k+1][2] if k+1 < len(blk) else "") or (255, 255, 255)
            lit = t >= wd[0]
            alpha = int(255*a_in*(1 if lit else .42))
            sc = col if lit else (235, 235, 235)
            d.text((x, y), tk, font=FONT, fill=sc + (alpha,), stroke_width=6, stroke_fill=(15, 15, 18, int(alpha*.9)))
            x += FONT.getlength(tk + " ")
        y += lh
    frame.paste(ov, (0, 0), ov)
    return frame

def draw_zombie_line(frame, t):
    u = t - ZOMBIE_T
    if not (0 <= u <= 2.2): return frame
    txt = "ОТЧЁ-Ё-ЁТ…"
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a = int(255*min(1, u/0.12)*min(1, (2.2-u)/0.3))
    x = (W - FONT_Z.getlength(txt))/2 + random.uniform(-5, 5); y = int(H*0.30) + random.uniform(-5, 5)
    d.text((x, y), txt, font=FONT_Z, fill=(186, 200, 170, a), stroke_width=8, stroke_fill=(20, 22, 18, a))
    frame.paste(ov, (0, 0), ov); return frame

def frame_at(t):
    i = shot_index(t); name, t0 = SHOTS[i][0], SHOTS[i][1]
    f = render_shot(i, t)
    xf = XFADE.get(name, 0) if not (i and SHOTS[i-1][0] == name) else 0
    if i > 0 and xf and t - t0 < xf:
        f = Image.blend(render_shot(i-1, t), f, ease((t - t0)/xf))
    # тишина в вагоне / финальные взгляды — лёгкое затемнение
    if name == "11_zastavka":
        u = t - t0
        if u < .6: f = Image.blend(Image.new("RGB", (W, H)), f, u/.6)
        if TOTAL - t < .5: f = Image.blend(Image.new("RGB", (W, H)), f, max(0, (TOTAL - t)/.5))
    else:
        f = draw_subs(f, t); f = draw_zombie_line(f, t)
    return f

# ---------------------------------------------------------------- звук
def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()

def build_audio(out):
    n = int(TOTAL*SR) + SR
    voice = load(P("audio", "voice.mp3")); zombie = load(P("audio", "zombie_otchet.mp3"))
    music = load(P("audio", "music.wav"))
    v = np.zeros(n, np.float32)
    a, b = int(INS_ZOMBIE_AT*SR), int(INS_SILENCE_AT*SR)
    v[:a] += voice[:a]
    o = a + int(INS_ZOMBIE*SR); v[o:o + (b - a)] += voice[a:b]
    o2 = int(T(INS_SILENCE_AT)*SR); rest = voice[b:]; v[o2:o2+len(rest)] += rest[:n-o2]
    # реплика зомби: ниже и медленнее не делаем — просто с лёгким «эхом»
    z = int(ZOMBIE_T*SR); zz = zombie*1.1
    v[z:z+len(zz)] += zz; d1 = int(.09*SR); v[z+d1:z+d1+len(zz)] += zz*.3
    rng = np.random.default_rng(1); tt = np.arange(n)/SR
    # музыка: тихо под голосом, выключается в тишине вагона, возвращается на взглядах
    m = np.zeros(n, np.float32); m[:min(n, len(music))] = music[:n]
    if len(music) < n: m[len(music):] = music[:n-len(music)]
    env = np.full(n, 10**(-17/20), np.float32)
    def ramp(t0, t1, g0, g1):
        i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(g0, g1, i1-i0)
    q = 10**(-17/20)
    env[:int(1.5*SR)] = np.linspace(0, q, int(1.5*SR))
    ramp(T(59.1), T(59.1)+.25, q, 0); env[int((T(59.1)+.25)*SR):int(HEADS_T*SR)] = 0
    ramp(HEADS_T, HEADS_T+.6, 0, q*1.6); env[int((HEADS_T+.6)*SR):] = q*1.6
    ramp(TOTAL-1.2, TOTAL, q*1.6, 0); env[int(TOTAL*SR):] = 0
    m *= env
    sfx = np.zeros(n, np.float32)
    def lowpass(x, k): return np.convolve(x, np.ones(k)/k, "same").astype(np.float32)
    # город/туман: ветер
    w = lowpass(rng.standard_normal(n).astype(np.float32), 400) * 0.6
    gate = np.zeros(n, np.float32); gate[:int(T(7.5)*SR)] = 1
    gate[:int(SR)] *= np.linspace(0, 1, SR); sfx += w*gate*0.5
    # метро: низкий гул
    s0, s1 = int(T(19.9)*SR), int(T(29.7)*SR)
    hum = (np.sin(2*np.pi*55*tt) + .5*np.sin(2*np.pi*110*tt)).astype(np.float32)*.02 + lowpass(rng.standard_normal(n).astype(np.float32), 120)*.15
    g = np.zeros(n, np.float32); g[s0:s1] = 1; g[s0:s0+SR] = np.linspace(0, 1, SR); g[s1-SR:s1] = np.linspace(1, 0, SR)
    sfx += hum*g
    # офис: тихий стон коллег (низкий тон с вибрато)
    s0, s1 = int(T(29.7)*SR), int(T(32.8)*SR)
    moan = np.sin(2*np.pi*(95 + 6*np.sin(2*np.pi*.7*tt))*tt).astype(np.float32)*.035
    g = np.zeros(n, np.float32); g[s0:s1] = np.sin(np.linspace(0, np.pi, s1-s0)); sfx += moan*g
    # вагон: стук колёс «та-дам… та-дам», замолкает перед тишиной
    s0, s1 = int(T(51.9)*SR), int((T(59.1)+.2)*SR)
    click = lowpass(rng.standard_normal(int(.06*SR)).astype(np.float32), 30)*np.exp(-np.linspace(0, 6, int(.06*SR))).astype(np.float32)*1.4
    tk = T(51.9)
    while tk < T(59.1):
        for off in (0, .16):
            i = int((tk+off)*SR); sfx[i:i+len(click)] += click[:max(0, n-i)]
        tk += 1.05
    rumble = lowpass(rng.standard_normal(n).astype(np.float32), 200)*.35
    g = np.zeros(n, np.float32); g[s0:s1] = 1; g[s0:s0+SR//2] = np.linspace(0, 1, SR//2); g[s1-int(.2*SR):s1] = np.linspace(1, 0, int(.2*SR))
    sfx += rumble*g
    # удар на «все повернулись» и на заставке
    def boom(t0, f=42, amp=.55, dec=2.5):
        i = int(t0*SR); L = int(dec*SR); x = np.arange(L)/SR
        bm = (np.sin(2*np.pi*f*x*(1 - .25*x/dec))*np.exp(-x*2.2)*amp).astype(np.float32)
        sfx[i:i+L] += bm[:max(0, n-i)]
    boom(HEADS_T); boom(TITLE_T + .1, 38, .45, 3.0)
    mix = v*1.0 + m + sfx*0.9
    mix = np.clip(mix[:int(TOTAL*SR)], -1, 1)
    tmp = P("out", "_mix.f32"); mix.astype(np.float32).tofile(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", out], check=True)
    os.remove(tmp)

# ---------------------------------------------------------------- рендер
def main():
    os.makedirs(P("out"), exist_ok=True)
    wav = P("out", "_audio.wav"); build_audio(wav)
    out = P("out", "zhivoy_v_moskve_s01" + ("_preview" if PREVIEW else "") + ".mp4")
    scale = ["-vf", "scale=540:960"] if PREVIEW else []
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", wav, *scale, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    nf = int(TOTAL*FPS); random.seed(5)
    for k in range(nf):
        ff.stdin.write(frame_at(k/FPS).tobytes())
        if k % 300 == 0: print(f"{k}/{nf}", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print("готово:", out, f"{TOTAL:.1f} c")

if __name__ == "__main__":
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still")+1]); frame_at(t).save(P("out", f"still_{t:05.1f}.png"))
    else:
        main()
