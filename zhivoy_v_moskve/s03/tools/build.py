"""Сборка серии 3 «Правила».
python3 s03/tools/build.py            → s03/out/zhivoy_v_moskve_s03.mp4
python3 s03/tools/build.py --still 12 → один кадр
Нужны: s03/frames (s03/tools/draw.py), s03/audio/voice.mp3 + vera.mp3, words/phrases.json
(python3 tools/align.py s03), audio/music.wav из серии 1.
"""
import json, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
P = lambda *a: os.path.join(ROOT, *a)
W, H, FPS, SR = 1080, 1920, 30, 48000

# ---------------------------------------------------------------- реплики Веры (куски vera.mp3)
# (момент вставки в исходную озвучку, начало и конец куска в vera.mp3, текст по предложениям с их временем внутри куска)
VERA = [
    (6.95,  0.00, 0.95, [(0.00, 0.83, "Не беги.")]),
    (22.15, 1.15, 2.40, [(0.09, 1.08, "Меня зовут Вера.")]),
    (32.55, 2.60, 8.10, [(0.08, 1.33, "Они учатся у нас."), (1.73, 3.70, "Каждый раз, когда ты делаешь что-то живое,"),
                         (3.70, 5.33, "кто-то запоминает.")]),
    (39.42, 8.30, 9.65, [(0.07, 1.19, "Нас было семеро.")]),
]
PAD = 0.5
INSERTS = [(at, (b - a) + PAD) for at, a, b, _ in VERA]
def T(t): return t + sum(d for a, d in INSERTS if t >= a)
NARR_END = T(50.05)
FINAL_VERA_T = NARR_END + 1.3                    # «Когда ты последний раз слышал её голос?»
FINAL_VERA = (9.85, 12.36, [(0.08, 2.43, "Когда ты последний раз слышал её голос?")])
TITLE_T = FINAL_VERA_T + (FINAL_VERA[1] - FINAL_VERA[0]) + 1.8
TOTAL = TITLE_T + 6.0
def vera_start(i): return T(VERA[i][0]) - INSERTS[i][1] + 0.2   # реплика начинается через 0,2 с после паузы

# (кадр, старт, z0, z1, центр0, центр1, тряска)
SHOTS = [
    ("01_idet",          0.0,      1.0,  1.3,  (560, 960),  (560, 900), .3),
    ("02_lokot",         T(3.4),   1.0,  1.1,  (540, 1100), (480, 1140), 0),
    ("03_platforma",     T(7.15),  1.0,  1.25, (540, 1200), (560, 1050), 0),
    ("04_dver",          T(13.4),  1.0,  1.15, (540, 960),  (600, 900), 0),
    ("05_kamorka",       T(17.95), 1.0,  1.1,  (480, 1100), (420, 1080), 0),
    ("05b_vera",         T(19.4),  1.0,  1.12, (540, 960),  (540, 920), 0),
    ("06a_bloknot",      T(22.3) if False else T(22.3), 1.0, 1.04, (540, 900), (540, 880), 0),
    ("06b_bloknot",      T(25.75), 1.04, 1.06, (540, 880),  (540, 900), 0),
    ("06c_bloknot",      T(26.8),  1.06, 1.08, (540, 900),  (540, 940), 0),
    ("06d_bloknot",      T(29.0),  1.1,  1.25, (540, 960),  (520, 1080), 0),
    ("05b_vera",         T(32.45), 1.05, 1.2,  (540, 940),  (540, 900), 0),
    ("07_ulybka_zombi",  T(32.75), 1.25, 1.05, (560, 1000), (560, 960), .25),
    ("08a_stena",        T(35.75), 1.0,  1.2,  (540, 800),  (430, 1100), 0),
    ("08b_stena8",       T(39.5),  1.2,  1.6,  (540, 1100), (700, 1200), 0),
    ("09_tel1",          T(42.45), 1.0,  1.06, (540, 900),  (540, 880), 0),
    ("09_tel2",          T(45.85), 1.06, 1.08, (540, 880),  (540, 900), .15),
    ("09_tel3",          T(46.8),  1.08, 1.10, (540, 900),  (540, 920), .15),
    ("09_tel5",          T(47.6),  1.10, 1.22, (540, 920),  (540, 960), .2),
    ("05b_vera",         NARR_END + .6, 1.15, 1.35, (540, 940), (540, 900), 0),
    ("11_zastavka",      TITLE_T,  1.0,  1.06, (540, 1000), (540, 980), 0),
]
XFADE = {"03_platforma": .5, "04_dver": .4, "05_kamorka": .4, "06a_bloknot": .4, "08a_stena": .5, "09_tel1": .4}

imgs = {}
def img(name):
    if name not in imgs: imgs[name] = Image.open(P("frames", name + ".png")).convert("RGB")
    return imgs[name]
def ease(x): return x*x*(3-2*x)

# огибающая голоса Веры по кадрам — для липсинка
vera_env = None
def talking(t):
    k = int(t*FPS)
    return vera_env is not None and 0 <= k < len(vera_env) and vera_env[k] > 0.035

def render_shot(i, t):
    name, t0, z0, z1, c0, c1, shake = SHOTS[i]
    t1 = SHOTS[i+1][1] if i+1 < len(SHOTS) else TOTAL
    e = ease(min(max((t - t0)/max(t1 - t0, .01), 0), 1))
    z = z0 + (z1-z0)*e; cx = c0[0] + (c1[0]-c0[0])*e; cy = c0[1] + (c1[1]-c0[1])*e
    if shake and t - t0 < shake:
        k = 1 - (t - t0)/shake; cx += random.uniform(-14, 14)*k; cy += random.uniform(-14, 14)*k
    w, h = W/z, H/z
    x0 = min(max(cx - w/2, 0), W - w); y0 = min(max(cy - h/2, 0), H - h)
    src = "05c_vera_rot" if (name == "05b_vera" and talking(t)) else name
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
def vera_block(t0, s, e, txt):
    ws = txt.split(); ln = [len(w) + 2 for w in ws]; tt = t0 + s; out = []
    for w, l in zip(ws, ln):
        d = (e - s)*l/sum(ln); out.append([tt, tt + d, w, "v"]); tt += d
    return out
for i, (at, a, b, sents) in enumerate(VERA):
    for s, e, txt in sents: blocks.append(vera_block(vera_start(i), s, e, txt))
for s, e, txt in FINAL_VERA[2]: blocks.append(vera_block(FINAL_VERA_T, s, e, txt))
blocks.sort(key=lambda b: b[0][0])

RED, YEL, VERA_C = (226, 66, 58), (242, 194, 48), (243, 205, 198)
def accent(prev, w, nxt):
    u = w.upper().strip("«»,.:;!?…—"); p = prev.upper().strip("«»,.:;!?…—"); x = nxt.upper().strip("«»,.:;!?…—")
    if u in ("ТВОЕЙ", "ТВОЮ"): return RED
    if (u == "ТОЛЬКО" and x == "ЖИВЫЕ") or (u == "ЖИВЫЕ" and p == "ТОЛЬКО"): return RED
    if u == "ЖИВЫМИ": return YEL
    if u in ("УСТУПАЙ", "МЕСТО") or (u == "НЕ" and x == "УСТУПАЙ"): return RED
    if u == "ВОСЬМОЙ": return RED
    return None

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 66)
FONT_V = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf", 70)
SUB_Y = int(H*0.70)
SUB_Y_LOW = {"06a_bloknot", "06b_bloknot", "06c_bloknot", "06d_bloknot", "09_tel1", "09_tel2", "09_tel3", "09_tel5"}

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
    vera = blk[0][3] == "v"; font = FONT_V if vera else FONT
    toks, lines = layout(blk, font)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    lh = 84; y = (int(H*.84) if low else SUB_Y) - (len(lines)*lh)//2; a_in = min(1, (t - blk[0][0] + .05)/.15)
    for ln in lines:
        x = (W - font.getlength(" ".join(toks[k] for k in ln)))/2
        for k in ln:
            wd = blk[k]
            col = (VERA_C if vera else None) or accent(blk[k-1][2] if k else "", wd[2], blk[k+1][2] if k+1 < len(blk) else "") or (255, 255, 255)
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
    # финальный крупный план: лампа мигает
    if i == len(SHOTS) - 2:
        u = t - t0
        if any(a <= u < a + .12 for a in (1.0, 1.35, 1.5, 3.4)) or u > 4.3:
            f = ImageEnhance.Brightness(f).enhance(.35 if u <= 4.3 else max(.1, 1 - (u - 4.3)*.9))
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

def build_audio(out):
    global vera_env
    n = int(TOTAL*SR) + SR; rng = np.random.default_rng(3); tt = np.arange(n)/SR
    voice = load(P("audio", "voice.mp3")); vera = load(P("audio", "vera.mp3"))
    music = load(os.path.join(ROOT, "..", "audio", "music.wav"))
    v = np.zeros(n, np.float32); vv = np.zeros(n, np.float32)
    cuts = [0.0] + [a for a, _ in INSERTS] + [len(voice)/SR]
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = voice[int(a*SR):int(b*SR)]; o = int(T(a)*SR); v[o:o+len(seg)] += seg[:max(0, n-o)]
    for i, (at, a, b, _) in enumerate(VERA):
        seg = vera[int(a*SR):int(b*SR)]; o = int(vera_start(i)*SR); vv[o:o+len(seg)] += seg
    seg = vera[int(FINAL_VERA[0]*SR):int(FINAL_VERA[1]*SR)]; o = int(FINAL_VERA_T*SR); vv[o:o+len(seg)] += seg
    hop = SR//FPS
    vera_env = np.array([np.sqrt(np.mean(vv[k*hop:(k+1)*hop]**2)) for k in range(n//hop)])
    def lowpass(x, k): return np.convolve(x, np.ones(k)/k, "same").astype(np.float32)
    # музыка
    m = np.resize(music, n).astype(np.float32); q = 10**(-27/20)   # музыка тише голоса (было −18)
    env = np.full(n, q, np.float32); env[:SR] = np.linspace(0, q, SR)
    def ramp(t0, t1, g0, g1): i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(g0, g1, i1-i0)
    ramp(NARR_END + .3, NARR_END + .6, q, 0); env[int((NARR_END+.6)*SR):int(TITLE_T*SR)] = 0
    ramp(TITLE_T, TITLE_T + .4, 0, q*1.6); env[int((TITLE_T+.4)*SR):] = q*1.6
    ramp(TOTAL - 1.2, TOTAL, q*1.6, 0); env[int(TOTAL*SR):] = 0
    m *= env
    sfx = np.zeros(n, np.float32)
    def add(t0, x): i = int(t0*SR); sfx[i:i+len(x)] += x[:max(0, n-i)]
    def noise(d, k=30): return lowpass(rng.standard_normal(int(d*SR)).astype(np.float32), k)
    # вагон в начале: гул и колёса
    click = noise(.06)*np.exp(-np.linspace(0, 6, int(.06*SR))).astype(np.float32)*1.4
    tk = 0.3
    while tk < T(3.4):
        add(tk, click); add(tk + .16, click); tk += 1.05
    i1 = int(T(3.4)*SR); sfx[:i1] += noise(T(3.4), 200)*.35
    add(T(3.4), noise(1.0, 6)*np.exp(-np.linspace(0, 3, SR)).astype(np.float32)*.15)   # шипение дверей
    # платформа: шарканье толпы
    i0, i1 = int(T(7.15)*SR), int(T(13.4)*SR); crowd = noise((i1-i0)/SR, 60)*.25
    for k in range(40):
        p = rng.integers(0, len(crowd) - SR//4); crowd[p:p+SR//4] += noise(.25, 12)*np.hanning(SR//4).astype(np.float32)*.25
    g = np.ones(i1-i0, np.float32); g[:SR//2] = np.linspace(0, 1, SR//2); g[-SR//2:] = np.linspace(1, 0, SR//2)
    sfx[i0:i1] += crowd*g
    # ключ и замок
    def thud(t0, f, amp, dec=18):
        L = int(.3*SR); x = np.arange(L)/SR; add(t0, (np.sin(2*np.pi*f*x)*np.exp(-x*dec)*amp).astype(np.float32))
    add(T(14.8), noise(.08, 3)*.3); add(T(14.95), noise(.06, 3)*.25)
    thud(T(15.55), 140, .5, 30); add(T(15.55), noise(.05, 2)*.35)
    # каморка: гудение лампы
    i0 = int(T(17.95)*SR); i1 = int(TITLE_T*SR)
    sfx[i0:i1] += (np.sin(2*np.pi*100*tt[i0:i1])*.012 + np.sin(2*np.pi*200*tt[i0:i1])*.006).astype(np.float32)
    # ручка пишет правила
    for t0 in (T(24.6), T(25.75), T(26.8), T(29.0)):
        L = int(.7*SR); sc = noise(.7, 4)*(0.5 + 0.5*np.sin(2*np.pi*9*np.arange(L)/SR)).astype(np.float32)*.12
        add(t0, sc)
    # маркер «8»
    add(T(39.6), noise(.35, 3)*.2); add(T(40.1), noise(.3, 3)*.2)
    # удар на улыбке зомби
    def boom(t0, f=42, amp=.55, dec=2.5):
        L = int(dec*SR); x = np.arange(L)/SR
        add(t0, (np.sin(2*np.pi*f*x*(1-.25*x/dec))*np.exp(-x*2.2)*amp).astype(np.float32))
    boom(0.05, 44, .35); boom(T(32.75), 40, .5); boom(TITLE_T + .1, 38, .45, 3.0)
    # вибрация телефона: сначала одиночные, потом всё чаще, потом обрыв
    def buzz(t0, d=.35):
        L = int(d*SR); x = np.arange(L)/SR
        sq = np.sign(np.sin(2*np.pi*170*x)).astype(np.float32)*.05
        add(t0, lowpass(sq, 6)*np.minimum(1, np.minimum(x/.02, (d - x)/.03)).astype(np.float32))
    for t0 in (T(42.45), T(42.95), T(45.85), T(46.8), T(47.6)): buzz(t0)
    tk, gap = T(48.4), .5
    while tk < NARR_END + .5:
        buzz(tk, .22); tk += gap; gap = max(.25, gap*.85)
    # мигание лампы — потрескивание
    for a in (1.0, 1.35, 1.5, 3.4): add(NARR_END + .6 + a, noise(.1, 2)*.18)
    # приглушение фона под голосом: −6 дБ, атака/отпускание ~0,25 с
    speech = v + vv*0.95
    act = (np.convolve(np.abs(speech), np.ones(SR//10)/(SR//10), "same") > 0.02).astype(np.float32)
    act = np.convolve(act, np.ones(SR//4)/(SR//4), "same")
    duck = 1 - 0.5*act
    mix = np.clip((speech + (m + sfx*.3)*duck)[:int(TOTAL*SR)], -1, 1)   # шумы −9,5 дБ (было ×0.9)
    tmp = P("out", "_mix.f32"); mix.astype(np.float32).tofile(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", out], check=True)
    os.remove(tmp)

def main():
    os.makedirs(P("out"), exist_ok=True)
    wav = P("out", "_audio.wav"); build_audio(wav)
    out = P("out", "zhivoy_v_moskve_s03.mp4")
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
        build_audio(P("out", "_tmp.wav")); os.remove(P("out", "_tmp.wav"))
        for a in sys.argv[sys.argv.index("--still")+1:]:
            t = float(a); frame_at(t).save(P("out", f"still_{t:05.1f}.png"))
    else:
        main()
