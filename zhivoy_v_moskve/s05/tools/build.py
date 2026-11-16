"""Сборка серии 5 «Вера».
python3 s05/tools/build.py               → s05/out/zhivoy_v_moskve_s05.mp4
python3 s05/tools/build.py --still 12 30 → отдельные кадры
Нужны: s05/frames (s05/tools/draw.py), s05/audio/voice.mp3 + mama.mp3 + vera.mp3,
words/phrases.json (python3 tools/align.py s05), audio/music.wav из серии 1.
"""
import json, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
P = lambda *a: os.path.join(ROOT, *a)
W, H, FPS, SR = 1080, 1920, 30, 48000

# ---------------------------------------------------------------- реплики мамы (m) и Веры (v)
# вставка: (момент в озвучке рассказчика, длительность паузы,
#           [(кто, сдвиг в паузе, начало куска, конец куска, [(s, e, текст)])])
INSERTS = [
    (3.35, 2.0, [("m", .25, 0.00, 1.30, [(0.00, 1.20, "Её больше нет.")])]),
    (7.15, 5.5, [("m", .25, 1.65, 6.45, [(0.06, 1.24, "Нас было семеро."), (1.68, 3.05, "Вера пришла последней."),
                                          (3.37, 4.71, "Самая внимательная.")])]),
    (12.2, 9.4, [("m", .30, 6.70, 9.85, [(0.06, 2.20, "А потом наши начали пропадать."), (2.44, 3.04, "По одному.")]),
                 ("m", 4.75, 10.15, 14.25, [(0.07, 1.35, "Шарф я ей подарила."), (1.68, 3.99, "В тот вечер, когда она перестала дышать.")])]),
    (26.4, 10.6, [("v", .70, 0.00, 1.90, [(0.00, 1.80, "Ты где? Я волнуюсь.")]),
                  ("v", 3.60, 2.25, 3.80, [(0.08, 1.41, "Вижу свет на девятом.")]),
                  ("m", 6.90, 14.50, 17.80, [(0.09, 0.98, "Правило шесть."), (1.30, 3.16, "Ночью не включай свет.")])]),
]
def T(t): return t + sum(d for a, d, _ in INSERTS if t >= a)
def ins_start(i): return T(INSERTS[i][0]) - INSERTS[i][1]
I3, I4 = ins_start(2), ins_start(3)
CLICK_T = I4 + 6.35
SMILE_T = T(31.6)
NARR_END = T(34.74)
TITLE_T = NARR_END + 2.4
TOTAL = TITLE_T + 6.0

# (кадр, старт, z0, z1, центр0, центр1, тряска)
SHOTS = [
    ("01_stranica",  0.0,       1.25, 1.55, (540, 860),  (540, 1080), 0),
    ("02_mama",      T(3.55),   1.0,  1.12, (540, 1000), (540, 940), 0),
    ("03_flashback", T(7.4),    1.0,  1.45, (540, 1000), (300, 860), 0),
    ("04_stena0",    I3,        1.0,  1.04, (540, 900),  (540, 880), 0),
    ("04_stena2",    I3 + 1.3,  1.04, 1.06, (540, 880),  (540, 880), .1),
    ("04_stena4",    I3 + 2.45, 1.06, 1.08, (540, 880),  (540, 880), .1),
    ("04_stena6",    I3 + 3.2,  1.08, 1.12, (540, 880),  (540, 880), .1),
    ("05_foto",      I3 + 4.3,  1.0,  1.5,  (540, 900),  (690, 780), 0),
    ("06a_steklo",   T(16.5),   1.4,  1.6,  (610, 860),  (610, 860), 0),
    ("06b_chek",     T(17.75),  1.1,  1.15, (540, 900),  (540, 900), 0),
    ("06c_bloknot",  T(18.3),   1.1,  1.15, (540, 900),  (540, 900), 0),
    ("06d_stena8",   T(19.2),   1.3,  1.9,  (540, 1000), (700, 1200), 0),
    ("10_bez",       T(21.45),  1.0,  1.15, (540, 980),  (540, 940), 0),
    ("07_vera1",     T(24.6),   1.0,  1.05, (540, 900),  (540, 880), 0),
    ("07_vera2",     I4 + 3.35, 1.05, 1.12, (540, 880),  (540, 900), .25),
    ("08_switch",    I4 + 5.7,  1.0,  1.1,  (540, 960),  (560, 920), 0),
    ("08b_temno",    CLICK_T,   1.0,  1.05, (540, 960),  (540, 960), 0),
    ("09_vniz",      T(26.5),   1.0,  1.75, (540, 1000), (700, 1180), 0),
    ("10_bez",       T(30.0),   1.05, 1.15, (540, 980),  (540, 950), 0),
    ("10_ulybka",    SMILE_T,   1.15, 1.35, (540, 950),  (540, 1000), 0),
    ("11_zastavka",  TITLE_T,   1.0,  1.06, (540, 1000), (540, 980), 0),
]
XFADE = {"02_mama": .4, "03_flashback": .7, "04_stena0": .4, "05_foto": .6, "09_vniz": .6, "07_vera1": .4, "10_bez": .5}
SEPIA = {"03_flashback", "04_stena0", "04_stena2", "04_stena4", "04_stena6"}
MEMORY = {"06a_steklo", "06b_chek", "06c_bloknot", "06d_stena8"}

imgs = {}
def img(name):
    if name not in imgs:
        im = Image.open(P("frames", name + ".png")).convert("RGB")
        if name in SEPIA:   # флешбэк: выцветшая сепия
            g = ImageOps.grayscale(im)
            im = Image.blend(ImageOps.colorize(g, (40, 30, 22), (236, 214, 178)), im, .18)
            im = ImageEnhance.Contrast(im).enhance(.85)
        if name in MEMORY:  # воспоминание: почти без цвета
            im = ImageEnhance.Color(im).enhance(.35)
        imgs[name] = im
    return imgs[name]
def ease(x): return x*x*(3-2*x)

mama_env = None
def talking(t):
    k = int(t*FPS)
    return mama_env is not None and 0 <= k < len(mama_env) and mama_env[k] > 0.035

def render_shot(i, t):
    name, t0, z0, z1, c0, c1, shake = SHOTS[i]
    t1 = SHOTS[i+1][1] if i+1 < len(SHOTS) else TOTAL
    e = ease(min(max((t - t0)/max(t1 - t0, .01), 0), 1))
    z = z0 + (z1-z0)*e; cx = c0[0] + (c1[0]-c0[0])*e; cy = c0[1] + (c1[1]-c0[1])*e
    if shake and t - t0 < shake:
        k = 1 - (t - t0)/shake; cx += random.uniform(-12, 12)*k; cy += random.uniform(-12, 12)*k
    w, h = W/z, H/z
    x0 = min(max(cx - w/2, 0), W - w); y0 = min(max(cy - h/2, 0), H - h)
    src = "02b_mama_rot" if (name == "02_mama" and talking(t)) else name
    return img(src).resize((W, H), Image.BICUBIC, box=(x0, y0, x0+w, y0+h))

def shot_index(t):
    i = 0
    for k, s in enumerate(SHOTS):
        if t >= s[1]: i = k
    return i

VIG = None
def vignette():
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:H, 0:W]; r = np.sqrt(((x - W/2)/(W/2))**2 + ((y - H/2)/(H/2))**2)
        VIG = Image.fromarray((np.clip((r - .55)/.6, 0, 1)*200).astype(np.uint8))
    return VIG

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
    for who, off, a, b, sents in pieces:
        for s, e, txt in sents: blocks.append(line_block(ins_start(i) + off, s, e, txt, who))
blocks.sort(key=lambda b: b[0][0])

RED, YEL = (226, 66, 58), (242, 194, 48)
COLOR = {"m": (202, 228, 190), "v": (243, 205, 198)}
def clean(w): return w.upper().strip("«»,.:;!?…—")
def accent(prev, w, nxt, who):
    u, p, x = clean(w), clean(prev), clean(nxt)
    if who == "m":
        if (u == "БОЛЬШЕ" and x == "НЕТ") or (u == "НЕТ" and p == "БОЛЬШЕ"): return RED
        return COLOR["m"]
    if who == "v":
        if (u == "НА" and x == "ДЕВЯТОМ") or u == "ДЕВЯТОМ": return RED
        return COLOR["v"]
    if u in ("ТРИ", "ГОДА", "НАЗАД"): return RED
    if (u == "НИЧЕГО" and x == "НЕ") or (u == "НЕ" and p == "НИЧЕГО") or (u == "ЗАБЫЛА" and p == "НЕ"): return RED
    if u in ("ИЗУЧАЛА", "ВОСЕМЬ"): return RED
    if u in ("ЛУЧШЕ", "УМЕЕШЬ") or (u == "ЧЕМ" and p == "ЛУЧШЕ") or (u == "ТЫ" and p == "УМЕЕШЬ"): return RED
    if u == "ВЕРА": return YEL
    return None

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 66)
FONT_I = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf", 70)
SUB_Y = int(H*0.70)
SUB_Y_LOW = {"01_stranica", "05_foto", "06b_chek", "06c_bloknot", "07_vera1", "07_vera2", "09_vniz", "10_bez", "10_ulybka"}

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
    if name in SEPIA:
        f.paste((20, 14, 8), (0, 0, W, H), vignette())
    if name in MEMORY and t - t0 < .1:   # вспышка воспоминания
        f = Image.blend(f, Image.new("RGB", (W, H), (255, 255, 255)), .7*(1 - (t - t0)/.1))
    if name == "10_ulybka" and t > NARR_END + 1.2:      # уход в темноту перед заставкой
        f = ImageEnhance.Brightness(f).enhance(max(0, 1 - (t - NARR_END - 1.2)/1.2))
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
    global mama_env
    n = int(TOTAL*SR) + SR; rng = np.random.default_rng(5); tt = np.arange(n)/SR
    voice = load(P("audio", "voice.mp3")); src = {"m": load(P("audio", "mama.mp3")), "v": load(P("audio", "vera.mp3"))}
    music = load(os.path.join(ROOT, "..", "audio", "music.wav"))
    v = np.zeros(n, np.float32); tr = {"m": np.zeros(n, np.float32), "v": np.zeros(n, np.float32)}
    cuts = [0.0] + [a for a, _, _ in INSERTS] + [len(voice)/SR]
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = voice[int(a*SR):int(b*SR)]; o = int(T(a)*SR); v[o:o+len(seg)] += seg[:max(0, n-o)]
    for i, (at, dur, pieces) in enumerate(INSERTS):
        for who, off, a, b, _ in pieces:
            seg = src[who][int(a*SR):int(b*SR)]; o = int((ins_start(i) + off)*SR); tr[who][o:o+len(seg)] += seg
    hop = SR//FPS
    mama_env = np.array([np.sqrt(np.mean(tr["m"][k*hop:(k+1)*hop]**2)) for k in range(n//hop)])
    def lowpass(x, k): return np.convolve(x, np.ones(k)/k, "same").astype(np.float32)
    # музыка: тихо; пропадает в темноте после щелчка, возвращается на заставке
    m = np.resize(music, n).astype(np.float32); q = 10**(-27/20)
    env = np.full(n, q, np.float32); env[:SR] = np.linspace(0, q, SR)
    def ramp(t0, t1, g0, g1): i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(g0, g1, i1-i0)
    env[int(CLICK_T*SR):int(TITLE_T*SR)] = 0
    ramp(TITLE_T, TITLE_T + .4, 0, q*1.6); env[int((TITLE_T+.4)*SR):] = q*1.6
    ramp(TOTAL - 1.2, TOTAL, q*1.6, 0); env[int(TOTAL*SR):] = 0
    m *= env
    sfx = np.zeros(n, np.float32)
    def add(t0, x): i = int(t0*SR); sfx[i:i+len(x)] += x[:max(0, n-i)]
    def noise(d, k=30): return lowpass(rng.standard_normal(int(d*SR)).astype(np.float32), k)
    # кухня: холодильник до щелчка выключателя
    i0, i1 = 0, int(CLICK_T*SR)
    sfx[i0:i1] += (np.sin(2*np.pi*50*tt[i0:i1])*.03 + np.sin(2*np.pi*100*tt[i0:i1])*.015).astype(np.float32)
    # флешбэк: шипение старой плёнки
    i0, i1 = int(T(7.4)*SR), int((I3 + 4.3)*SR)
    hiss = (rng.standard_normal(i1-i0)*.035).astype(np.float32); hiss -= lowpass(hiss, 20)
    g = np.ones(i1-i0, np.float32); g[:SR//2] = np.linspace(0, 1, SR//2); g[-SR//2:] = np.linspace(1, 0, SR//2)
    sfx[i0:i1] += hiss*g
    # маркер: крестики
    for t0 in (I3 + 1.3, I3 + 1.45, I3 + 2.45, I3 + 2.6, I3 + 3.2, I3 + 3.35):
        add(t0, noise(.12, 3)*.22)
    add(I3 + 4.3, noise(.4, 5)*np.hanning(int(.4*SR)).astype(np.float32)*.25)   # фото из ящика
    # вспышки воспоминаний: «вжух»
    for t0 in (T(16.5), T(17.75), T(18.3), T(19.2)):
        L = int(.35*SR); x = np.linspace(0, 1, L)
        add(t0 - .1, (noise(.35, 8)*np.sin(np.pi*x)**2*.3).astype(np.float32))
    # вибрация на сообщениях Веры
    def buzz(t0, d=.35):
        L = int(d*SR); x = np.arange(L)/SR
        sq = np.sign(np.sin(2*np.pi*170*x)).astype(np.float32)*.05
        add(t0, lowpass(sq, 6)*np.minimum(1, np.minimum(x/.02, (d - x)/.03)).astype(np.float32))
    buzz(I4 + .2); buzz(I4 + 3.35)
    # щелчок выключателя
    add(CLICK_T, noise(.04, 1)*.5); add(CLICK_T + .02, noise(.03, 2)*.3)
    # ночная улица за окном: тихий ветер
    i0, i1 = int(T(26.5)*SR), int(TITLE_T*SR)
    wind = lowpass(rng.standard_normal(i1-i0).astype(np.float32), 500)*1.2
    g = np.ones(i1-i0, np.float32); g[:SR] = np.linspace(0, 1, SR); g[-SR:] = np.linspace(1, 0, SR)
    sfx[i0:i1] += wind*g
    # удары
    def boom(t0, f=42, amp=.55, dec=2.5):
        L = int(dec*SR); x = np.arange(L)/SR
        add(t0, (np.sin(2*np.pi*f*x*(1-.25*x/dec))*np.exp(-x*2.2)*amp).astype(np.float32))
    boom(0.05, 44, .3); boom(NARR_END + .5, 40, .55); boom(TITLE_T + .1, 38, .45, 3.0)
    # сведение: фон тихо + приглушение под голосом
    speech = v + tr["m"]*.95 + tr["v"]*.95
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
    out = P("out", "zhivoy_v_moskve_s05.mp4")
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
