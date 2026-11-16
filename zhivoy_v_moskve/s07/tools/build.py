"""Сборка серии 7 (финал) «Живые».
python3 s07/tools/build.py               → s07/out/zhivoy_v_moskve_s07.mp4
python3 s07/tools/build.py --still 12 30 → отдельные кадры
Нужны: s07/frames (s07/tools/draw.py), s07/audio/voice.mp3 + mama.mp3 + zombie_otchet.mp3 (из серии 1),
words/phrases.json (python3 tools/align.py s07), audio/music.wav из серии 1.
"""
import json, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
P = lambda *a: os.path.join(ROOT, *a)
W, H, FPS, SR = 1080, 1920, 30, 48000

# ---------------------------------------------------------------- вставки в дорожку рассказчика
# (момент, длительность, [(кто, сдвиг, файл, начало, конец, [(s, e, текст)])]); кто: m — мама, b — начальник, "" — только звук
INSERTS = [
    (3.85, 2.6, [("m", .30, "mama", 0.00, 1.85, [(0.00, 0.88, "Приходи домой."), (1.14, 1.70, "Мы ждём.")])]),
    (34.45, 2.4, [("b", .20, "zombie_otchet", 0.00, 1.80, [])]),
    (44.20, 0.8, []),     # копия подходит
    (48.95, 1.4, []),     # громкий вдох
    (51.25, 1.2, []),     # тишина после улыбки
    (54.55, 1.0, []),     # вдох в углу
    (63.00, 0.8, []),     # перед финальной фразой — входит тёплый аккорд
]
def T(t): return t + sum(d for a, d, _ in INSERTS if t >= a)
def ins_start(i): return T(INSERTS[i][0]) - INSERTS[i][1]
OTCHET_T = ins_start(1) + .2
INHALE_T = ins_start(3) + .1
CORNER_T = ins_start(5) + .1
WARM_T = T(50.1)                  # улыбка: дрон уходит, тёплый пэд
NARR_END = T(69.56)
TITLE_T = NARR_END + 4.2
TOTAL = TITLE_T + 6.5
COPY_LINES = ("Сделаю", "Ты слишком громко дышишь")

# (кадр, старт, z0, z1, центр0, центр1, тряска)
SHOTS = [
    ("01_rassvet",       0.0,       1.0, 1.12, (540, 1100), (560, 1180), 0),
    ("02_tel",           T(1.7),    1.0, 1.08, (540, 900),  (540, 860), 0),
    ("03_ekran",         T(5.7),    1.0, 1.15, (540, 900),  (540, 860), 0),
    ("04_pravilo7",      T(11.9),   1.0, 1.25, (540, 900),  (560, 1000), 0),
    ("05_metro",         T(18.25),  1.1, 1.0,  (540, 1200), (540, 1000), 0),
    ("06_ofis",          T(26.05),  1.0, 1.6,  (540, 1000), (670, 1060), 0),
    ("07_kopiya",        ins_start(1), 1.15, 1.3, (560, 1050), (520, 1000), 0),
    ("08a_ofis_spinoy",  T(38.25),  1.0, 1.05, (540, 1000), (540, 980), 0),
    ("08b_ofis_golovy",  T(39.8),   1.05, 1.15, (540, 980), (540, 1050), .25),
    ("09_uho",           ins_start(2), 1.0, 1.15, (600, 900), (620, 860), 0),
    ("10a_vdoh",         T(46.2),   1.0, 1.15, (540, 980),  (540, 960), 0),
    ("10b_ulybka",       T(50.1),   1.15, 1.25, (540, 960), (540, 1000), 0),
    ("08b_ofis_golovy",  T(51.5),   1.15, 1.15, (540, 1050), (540, 1050), 0),
    ("11a_ugol",         T(52.55),  1.0, 1.2,  (420, 950),  (360, 920), 0),
    ("11b_ugol_ulybka",  CORNER_T + .35, 1.2, 1.28, (360, 920), (360, 910), 0),
    ("12a_ulybki",       T(54.8),   1.05, 1.0, (540, 1050), (540, 1000), 0),
    ("12b_ulybki_vse",   T(57.55),  1.0, 1.06, (540, 1000), (540, 980), 0),
    ("13_pyatyatsya",    T(59.75),  1.0, 1.12, (540, 1000), (560, 900), 0),
    ("14a_gorod",        ins_start(6), 1.9, 1.6, (534, 1166), (534, 1100), 0),
    ("14b_gorod",        T(65.2),   1.6, 1.25, (534, 1100), (540, 1000), 0),
    ("14c_gorod",        T(67.7),   1.25, 1.0, (540, 1000), (540, 960), 0),
    ("15_mama",          NARR_END + .3, 1.0, 1.15, (540, 1100), (560, 1180), 0),
    ("16_konec",         TITLE_T,   1.0, 1.06, (540, 1000), (540, 980), 0),
]
XFADE = {"02_tel": .4, "03_ekran": .2, "04_pravilo7": .4, "05_metro": .5, "06_ofis": .5, "08a_ofis_spinoy": .4, "09_uho": .3,
         "10a_vdoh": .4, "11a_ugol": .4, "12a_ulybki": .4, "12b_ulybki_vse": .6, "13_pyatyatsya": .4,
         "14a_gorod": .6, "14b_gorod": .8, "14c_gorod": .8, "15_mama": .8}

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
        k = 1 - (t - t0)/shake; cx += random.uniform(-12, 12)*k; cy += random.uniform(-12, 12)*k
    w, h = W/z, H/z
    x0 = min(max(cx - w/2, 0), W - w); y0 = min(max(cy - h/2, 0), H - h)
    return img(name).resize((W, H), Image.BICUBIC, box=(x0, y0, x0+w, y0+h))

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
    n = len(txt.split()); ws = words[wi:wi+n]; wi += n
    if txt.strip(" «».") in COPY_LINES:
        for w in ws: w[3] = "c"
    cur += ws
    if txt.rstrip()[-1] not in "—,:": blocks.append(cur); cur = []
if cur: blocks.append(cur)
def line_block(t0, s, e, txt, who):
    ws = txt.split(); ln = [len(w) + 2 for w in ws]; tt = t0 + s; out = []
    for w, l in zip(ws, ln):
        d = (e - s)*l/sum(ln); out.append([tt, tt + d, w, who]); tt += d
    return out
for i, (at, dur, pieces) in enumerate(INSERTS):
    for who, off, f, a, b, sents in pieces:
        for s, e, txt in sents: blocks.append(line_block(ins_start(i) + off, s, e, txt, who))
blocks.sort(key=lambda b: b[0][0])

RED, YEL, ZGR = (226, 66, 58), (242, 194, 48), (186, 200, 170)
COLOR = {"m": (202, 228, 190), "c": ZGR}
def clean(w): return w.upper().strip("«»,.:;!?…—")
def accent(prev, w, nxt, who):
    u, p, x = clean(w), clean(prev), clean(nxt)
    if u == "ДЫШИШЬ": return RED
    if who in COLOR: return COLOR[who]
    if u == "МЫ": return RED
    if u in ("ЖЁЛТОЙ", "КУРТКЕ"): return YEL
    if (u == "ТВОИМ" and x == "ГОЛОСОМ") or (u == "ГОЛОСОМ" and p == "ТВОИМ"): return RED
    if u in ("УЛЫБАЕШЬСЯ", "ВДЫХАЕТ"): return YEL
    if (u == "ЖИВЫХ" and x in ("СЛИШКОМ", "")) or (u in ("СЛИШКОМ", "МНОГО") and p in ("ЖИВЫХ", "СЛИШКОМ")): return YEL
    if u in ("ПОКАЗАТЬ", "ПЕРВЫМИ"): return YEL
    return None

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 66)
FONT_I = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf", 70)
FONT_Z = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 110)
SUB_Y = int(H*0.70)
SUB_Y_LOW = {"01_rassvet", "02_tel", "03_ekran", "04_pravilo7", "07_kopiya", "09_uho", "10a_vdoh", "10b_ulybka",
             "11a_ugol", "11b_ugol_ulybka", "15_mama"}

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
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    lh = 84; a_in = min(1, (t - blk[0][0] + .05)/.15)
    # блок может смешивать рассказчика и копию: шрифт выбираем по первому слову
    who0 = blk[0][3]; font = FONT if who0 == "n" else FONT_I
    toks, lines = layout(blk, font)
    y = (int(H*.84) if low else SUB_Y) - (len(lines)*lh)//2
    for ln in lines:
        x = (W - font.getlength(" ".join(toks[k] for k in ln)))/2
        for k in ln:
            wd = blk[k]
            col = accent(blk[k-1][2] if k else "", wd[2], blk[k+1][2] if k+1 < len(blk) else "", wd[3]) or (255, 255, 255)
            lit = t >= wd[0]; al = int(255*a_in*(1 if lit else .42))
            jx = random.uniform(-3, 3) if (lit and wd[3] == "c") else 0
            d.text((x + jx, y), toks[k], font=font, fill=(col if lit else (235, 235, 235)) + (al,),
                   stroke_width=6, stroke_fill=(15, 15, 18, int(al*.9)))
            x += font.getlength(toks[k] + " ")
        y += lh
    frame.paste(ov, (0, 0), ov); return frame

def draw_otchet(frame, t):
    u = t - OTCHET_T
    if not (0 <= u <= 2.0): return frame
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); txt = "ОТЧЁ-Ё-ЁТ…"
    a = int(255*min(1, u/.12)*min(1, (2.0 - u)/.3))
    x = (W - FONT_Z.getlength(txt))/2 + random.uniform(-5, 5); y = int(H*.22) + random.uniform(-5, 5)
    d.text((x, y), txt, font=FONT_Z, fill=ZGR + (a,), stroke_width=8, stroke_fill=(20, 22, 18, a))
    frame.paste(ov, (0, 0), ov); return frame

def frame_at(t):
    i = shot_index(t); name, t0 = SHOTS[i][0], SHOTS[i][1]
    f = render_shot(i, t)
    xf = XFADE.get(name, 0) if not (i and SHOTS[i-1][0] == name) else 0
    if i > 0 and xf and t - t0 < xf:
        f = Image.blend(render_shot(i-1, t), f, ease((t - t0)/xf))
    if name == "15_mama" and t > TITLE_T - 1.0:
        f = ImageEnhance.Brightness(f).enhance(max(0, (TITLE_T - t)/1.0))
    if name == "16_konec":
        u = t - t0
        if u < .8: f = Image.blend(Image.new("RGB", (W, H)), f, u/.8)
        if TOTAL - t < .8: f = Image.blend(Image.new("RGB", (W, H)), f, max(0, (TOTAL - t)/.8))
    else:
        f = draw_subs(f, t, name in SUB_Y_LOW); f = draw_otchet(f, t)
    return f

# ---------------------------------------------------------------- звук
def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()
def lowpass(x, k): return np.convolve(x, np.ones(k)/k, "same").astype(np.float32)

def build_audio(out):
    n = int(TOTAL*SR) + SR; rng = np.random.default_rng(7); tt = np.arange(n)/SR
    voice = load(P("audio", "voice.mp3"))
    files = {"mama": load(P("audio", "mama.mp3")), "zombie_otchet": load(P("audio", "zombie_otchet.mp3"))}
    music = load(os.path.join(ROOT, "..", "audio", "music.wav"))
    v = np.zeros(n, np.float32); lines = np.zeros(n, np.float32)
    cuts = [0.0] + [a for a, _, _ in INSERTS] + [len(voice)/SR]
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = voice[int(a*SR):int(b*SR)].copy()
        # шёпот копии: «Ты слишком громко дышишь» — тише, без низов, с дыханием
        w0, w1 = 44.45 - a, 45.95 - a
        if 0 <= w0 < (b - a):
            i0, i1 = int(w0*SR), min(int(w1*SR), len(seg))
            part = seg[i0:i1]; part = (part - lowpass(part, 40))*.9
            part += (rng.standard_normal(len(part))*.025*np.abs(np.convolve(part, np.ones(400)/400, "same"))*25).astype(np.float32)
            seg[i0:i1] = part
        o = int(T(a)*SR); v[o:o+len(seg)] += seg[:max(0, n-o)]
    for i, (at, dur, pieces) in enumerate(INSERTS):
        for who, off, f, a, b, _ in pieces:
            seg = files[f][int(a*SR):int(b*SR)].copy()
            if who == "b":
                seg = seg*1.1; d1 = int(.09*SR); seg = np.concatenate([seg, np.zeros(d1, np.float32)]); seg[d1:] += seg[:-d1]*.3
            o = int((ins_start(i) + off)*SR); lines[o:o+len(seg)] += seg*.95
    # музыка: тревожный дрон до улыбки, потом тишина и тёплый пэд
    m = np.resize(music, n).astype(np.float32); q = 10**(-27/20)
    env = np.full(n, q, np.float32); env[:SR] = np.linspace(0, q, SR)
    i0 = int(ins_start(2)*SR); env[i0:i0+SR//2] = np.linspace(q, 0, SR//2); env[i0+SR//2:] = 0
    m *= env
    # тёплый мажорный пэд (до мажор), растёт к финалу
    def pad_env():
        e = np.zeros(n, np.float32)
        def ramp(t0, t1, g0, g1): a, b = int(t0*SR), int(t1*SR); e[a:b] = np.linspace(g0, g1, b-a)
        ramp(WARM_T, T(54.8), 0, .25); ramp(T(54.8), ins_start(6), .25, .45); ramp(ins_start(6), NARR_END, .45, .8)
        ramp(NARR_END, TOTAL - 1.5, .8, .9); ramp(TOTAL - 1.5, TOTAL, .9, 0)
        return e
    chord1 = [130.81, 196.0, 261.63, 329.63, 392.0]          # C
    chord2 = [110.0, 164.81, 261.63, 329.63, 440.0]          # Am (на улыбках)
    chord3 = [87.31, 174.61, 261.63, 349.23, 440.0]          # F (город)
    def chord(fr):
        s = np.zeros(n, np.float32)
        for k, f in enumerate(fr):
            for det in (-.6, .6):
                s += np.sin(2*np.pi*(f + det)*tt + k).astype(np.float32)
        return s/(len(fr)*2)
    c1, c2, c3 = chord(chord1), chord(chord2), chord(chord3)
    sel = np.zeros((3, n), np.float32)
    def xf(t0, t1, a, b):
        i0, i1 = int(t0*SR), int(t1*SR); r = np.linspace(0, 1, i1-i0, dtype=np.float32)
        sel[a, i0:i1] = 1 - r; sel[b, i0:i1] = r; sel[b, i1:] = 1; sel[a, i1:] = 0
    sel[0, :] = 1
    xf(T(54.8), T(55.8), 0, 1); xf(ins_start(6), ins_start(6) + 1.0, 1, 2); xf(NARR_END, NARR_END + 2, 2, 0)
    pad = (c1*sel[0] + c2*sel[1] + c3*sel[2])*(1 + .08*np.sin(2*np.pi*.25*tt)).astype(np.float32)
    pad = lowpass(pad, 6)*pad_env()*.12
    sfx = np.zeros(n, np.float32)
    def add(t0, x): i = int(t0*SR); sfx[i:i+len(x)] += x[:max(0, n-i)]
    def noise(d, k=30): return lowpass(rng.standard_normal(int(d*SR)).astype(np.float32), k)
    def ping(f, d, amp, dec=6):
        L = int(d*SR); x = np.arange(L)/SR; return (np.sin(2*np.pi*f*x)*np.exp(-x*dec)*amp).astype(np.float32)
    # рассвет: редкие птицы
    for k, t0 in enumerate((.6, 1.4, 2.9, 4.2)):
        L = int(.18*SR); x = np.arange(L)/SR
        add(t0, (np.sin(2*np.pi*(2400 + 1800*x/.18)*x)*np.hanning(L)*.03).astype(np.float32))
    # вибрация и выключение телефона
    def buzz(t0, d=.35):
        L = int(d*SR); x = np.arange(L)/SR
        sq = np.sign(np.sin(2*np.pi*170*x)).astype(np.float32)*.05
        add(t0, lowpass(sq, 6)*np.minimum(1, np.minimum(x/.02, (d - x)/.03)).astype(np.float32))
    buzz(ins_start(0) + .05)
    L = int(.6*SR); x = np.arange(L)/SR
    add(T(5.75), (np.sin(2*np.pi*(660 - 400*x/.6)*x)*np.exp(-x*4)*.06).astype(np.float32))
    # метро: гул толпы
    i0, i1 = int(T(18.25)*SR), int(T(26.05)*SR)
    g = np.ones(i1-i0, np.float32); g[:SR//2] = np.linspace(0, 1, SR//2); g[-SR//2:] = np.linspace(1, 0, SR//2)
    sfx[i0:i1] += (lowpass(rng.standard_normal(i1-i0).astype(np.float32), 120)*.4 + np.sin(2*np.pi*55*tt[i0:i1])*.02)*g
    # офис: стоны до шёпота
    i0, i1 = int(T(26.05)*SR), int(ins_start(2)*SR); x = tt[i0:i1]
    moan = (np.sin(2*np.pi*(95 + 6*np.sin(2*np.pi*.7*x))*x)*.03 + np.sin(2*np.pi*(120 + 5*np.sin(2*np.pi*.5*x))*x)*.02).astype(np.float32)
    g = np.ones(i1-i0, np.float32); g[:SR] = np.linspace(0, 1, SR); g[-SR//3:] = np.linspace(1, 0, SR//3)
    sfx[i0:i1] += moan*g
    # повороты голов: шорох
    add(T(39.8), noise(.5, 6)*np.hanning(int(.5*SR)).astype(np.float32)*.25)
    # громкий вдох героя и тихий вдох в углу
    def inhale(t0, d, amp):
        L = int(d*SR); x = np.linspace(0, 1, L)
        s = rng.standard_normal(L).astype(np.float32); s = s - lowpass(s, 12)
        return (lowpass(s, 3)*(x**1.5)*np.minimum(1, (1 - x)*8)*amp).astype(np.float32)
    add(INHALE_T, inhale(INHALE_T, 1.1, .5)); add(CORNER_T, inhale(CORNER_T, .7, .25))
    # удар на поворот офиса
    def boom(t0, f=42, amp=.55, dec=2.5):
        L = int(dec*SR); x = np.arange(L)/SR
        add(t0, (np.sin(2*np.pi*f*x*(1-.25*x/dec))*np.exp(-x*2.2)*amp).astype(np.float32))
    boom(T(39.8), 44, .4)
    # сведение: фон тихо + приглушение под голосом (пэд — тоже фон)
    speech = v + lines
    act = (np.convolve(np.abs(speech), np.ones(SR//10)/(SR//10), "same") > 0.02).astype(np.float32)
    act = np.convolve(act, np.ones(SR//4)/(SR//4), "same")
    duck = 1 - 0.5*act
    mix = np.clip((speech + (m + sfx*.3 + pad)*duck)[:int(TOTAL*SR)], -1, 1)
    tmp = P("out", "_mix.f32"); mix.astype(np.float32).tofile(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", out], check=True)
    os.remove(tmp)

def main():
    os.makedirs(P("out"), exist_ok=True)
    wav = P("out", "_audio.wav"); build_audio(wav)
    out = P("out", "zhivoy_v_moskve_s07.mp4")
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
