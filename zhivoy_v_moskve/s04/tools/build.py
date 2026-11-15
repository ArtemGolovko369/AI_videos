"""Сборка серии 4 «Мама».
python3 s04/tools/build.py            → s04/out/zhivoy_v_moskve_s04.mp4
python3 s04/tools/build.py --still 12 30 → отдельные кадры
Нужны: s04/frames (s04/tools/draw.py), s04/audio/voice.mp3 + mama.mp3, words/phrases.json
(python3 tools/align.py s04), audio/music.wav из серии 1.
"""
import json, os, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
P = lambda *a: os.path.join(ROOT, *a)
W, H, FPS, SR = 1080, 1920, 30, 48000

# ---------------------------------------------------------------- реплики мамы (куски mama.mp3)
# вставка: (момент в озвучке рассказчика, длительность паузы, [(сдвиг в паузе, начало куска, конец куска, [(s, e, текст)])])
LOVE = (0.00, 1.15, [(0.0, 1.06, "Я тебя люблю.")])
INSERTS = [
    (7.85, 3.7, [(0.35,) + LOVE, (2.05,) + LOVE]),     # одинаковая фраза дважды — как запись
    (49.75, 8.3, [(0.25, 1.60, 2.30, [(0.06, 0.62, "Ты поел?")]),
                  (1.55, 2.75, 8.83, [(0.10, 2.85, "Я пишу тебе одно и то же каждый вечер."),
                                      (3.15, 6.05, "Чтобы они думали, что я — одна из них.")])]),
]
def T(t): return t + sum(d for a, d, _ in INSERTS if t >= a)
def ins_start(i): return T(INSERTS[i][0]) - INSERTS[i][1]
NARR_END = T(57.3)
TITLE_T = NARR_END + 2.2
TOTAL = TITLE_T + 6.0

# (кадр, старт, z0, z1, центр0, центр1, тряска)
SHOTS = [
    ("01_zvonok",     0.0,      1.0,  1.1,  (540, 900),  (540, 860), 0),
    ("02_razgovor",   T(4.5),   1.1,  1.25, (540, 860),  (540, 800), 0),
    ("03_sbros",      T(8.2),   1.1,  1.15, (540, 1000), (560, 1100), .15),
    ("04_bloknot5",   T(10.0),  1.0,  1.3,  (540, 900),  (560, 1020), 0),
    ("05_vyhod",      T(17.7),  1.0,  1.12, (540, 1100), (540, 1000), 0),
    ("06_ulica",      T(19.6),  1.15, 1.0,  (420, 1150), (620, 1050), 0),
    ("07_dom",        T(27.2),  1.0,  2.1,  (540, 900),  (470, 640), 0),
    ("08_okno",       T(33.0),  1.0,  1.25, (540, 920),  (640, 1060), 0),
    ("08b_vibro",     T(35.95), 1.05, 1.12, (540, 900),  (540, 880), .4),
    ("09_dver",       T(38.5),  1.0,  1.25, (540, 960),  (720, 960), 0),
    ("10_spina",      T(39.9),  1.0,  1.15, (540, 1000), (540, 1050), 0),
    ("11_mama",       T(45.15), 1.0,  1.25, (540, 960),  (540, 900), 0),
    ("12_stranica",   T(50.0),  1.0,  1.35, (540, 960),  (540, 880), 0),
    ("12_stranica",   T(56.35), 1.35, 1.75, (540, 880),  (540, 1260), 0),
    ("13_zastavka",   TITLE_T,  1.0,  1.06, (540, 1000), (540, 980), 0),
]
XFADE = {"04_bloknot5": .4, "05_vyhod": .5, "06_ulica": .5, "07_dom": .5, "08_okno": .4, "09_dver": .4, "10_spina": .4, "12_stranica": .5}

imgs = {}
def img(name):
    if name not in imgs: imgs[name] = Image.open(P("frames", name + ".png")).convert("RGB")
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
        k = 1 - (t - t0)/shake; cx += random.uniform(-14, 14)*k; cy += random.uniform(-14, 14)*k
    w, h = W/z, H/z
    x0 = min(max(cx - w/2, 0), W - w); y0 = min(max(cy - h/2, 0), H - h)
    src = "11b_mama_rot" if (name == "11_mama" and talking(t)) else name
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
def mama_block(t0, s, e, txt):
    ws = txt.split(); ln = [len(w) + 2 for w in ws]; tt = t0 + s; out = []
    for w, l in zip(ws, ln):
        d = (e - s)*l/sum(ln); out.append([tt, tt + d, w, "m"]); tt += d
    return out
for i, (at, dur, pieces) in enumerate(INSERTS):
    for off, a, b, sents in pieces:
        for s, e, txt in sents: blocks.append(mama_block(ins_start(i) + off, s, e, txt))
blocks.sort(key=lambda b: b[0][0])

RED, YEL, MAMA_C = (226, 66, 58), (242, 194, 48), (202, 228, 190)
def accent(prev, w, nxt):
    u = w.upper().strip("«»,.:;!?…—"); p = prev.upper().strip("«»,.:;!?…—"); x = nxt.upper().strip("«»,.:;!?…—")
    if u in ("ВЫУЧИВАЮТ", "ПЕРВЫМИ"): return RED
    if (u == "КЕМ" and x == "БЫЛИ") or (u == "БЫЛИ" and p == "КЕМ"): return YEL
    if u in ("ТРИ", "ГОДА", "НАЗАД"): return RED
    if u == "МАМА" and w.strip().endswith("?»"): return YEL
    if u == "ВЕРА": return YEL
    return None
def accent_mama(prev, w, nxt):
    u = w.upper().strip("«»,.:;!?…—"); p = prev.upper().strip("«»,.:;!?…—"); x = nxt.upper().strip("«»,.:;!?…—")
    if (u == "ОДНА" and x == "ИЗ") or (u == "ИЗ" and p == "ОДНА") or (u == "НИХ" and p == "ИЗ"): return RED
    return MAMA_C

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 66)
FONT_M = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf", 70)
SUB_Y = int(H*0.70)
SUB_Y_LOW = {"01_zvonok", "02_razgovor", "03_sbros", "04_bloknot5", "08b_vibro", "11_mama", "12_stranica"}

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
    mom = blk[0][3] == "m"; font = FONT_M if mom else FONT; acc = accent_mama if mom else accent
    toks, lines = layout(blk, font)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    lh = 84; y = (int(H*.84) if low else SUB_Y) - (len(lines)*lh)//2; a_in = min(1, (t - blk[0][0] + .05)/.15)
    for ln in lines:
        x = (W - font.getlength(" ".join(toks[k] for k in ln)))/2
        for k in ln:
            wd = blk[k]
            col = acc(blk[k-1][2] if k else "", wd[2], blk[k+1][2] if k+1 < len(blk) else "") or (255, 255, 255)
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
    if i == len(SHOTS) - 2 and t > NARR_END + .6:      # уход в темноту перед заставкой
        f = ImageEnhance.Brightness(f).enhance(max(.0, 1 - (t - NARR_END - .6)/1.6))
    if name == "13_zastavka":
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
    n = int(TOTAL*SR) + SR; rng = np.random.default_rng(4); tt = np.arange(n)/SR
    voice = load(P("audio", "voice.mp3")); mama = load(P("audio", "mama.mp3"))
    music = load(os.path.join(ROOT, "..", "audio", "music.wav"))
    v = np.zeros(n, np.float32); mv = np.zeros(n, np.float32)
    cuts = [0.0] + [a for a, _, _ in INSERTS] + [len(voice)/SR]
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = voice[int(a*SR):int(b*SR)]; o = int(T(a)*SR); v[o:o+len(seg)] += seg[:max(0, n-o)]
    for i, (at, dur, pieces) in enumerate(INSERTS):
        for off, a, b, _ in pieces:
            seg = mama[int(a*SR):int(b*SR)].copy()
            if i == 0:   # голос «из трубки»: узкая полоса
                seg = np.convolve(seg, np.ones(6)/6, "same").astype(np.float32)
                seg = (seg - np.convolve(seg, np.ones(60)/60, "same")).astype(np.float32)*1.6
            o = int((ins_start(i) + off)*SR); mv[o:o+len(seg)] += seg
    hop = SR//FPS
    mama_env = np.array([np.sqrt(np.mean(mv[k*hop:(k+1)*hop]**2)) for k in range(n//hop)])
    def lowpass(x, k): return np.convolve(x, np.ones(k)/k, "same").astype(np.float32)
    # музыка (тихо, как в исправленной серии 3)
    m = np.resize(music, n).astype(np.float32); q = 10**(-27/20)
    env = np.full(n, q, np.float32); env[:SR] = np.linspace(0, q, SR)
    def ramp(t0, t1, g0, g1): i0, i1 = int(t0*SR), int(t1*SR); env[i0:i1] = np.linspace(g0, g1, i1-i0)
    ramp(T(56.3), T(56.3) + .3, q, 0); env[int((T(56.3)+.3)*SR):int(TITLE_T*SR)] = 0
    ramp(TITLE_T, TITLE_T + .4, 0, q*1.6); env[int((TITLE_T+.4)*SR):] = q*1.6
    ramp(TOTAL - 1.2, TOTAL, q*1.6, 0); env[int(TOTAL*SR):] = 0
    m *= env
    sfx = np.zeros(n, np.float32)
    def add(t0, x): i = int(t0*SR); sfx[i:i+len(x)] += x[:max(0, n-i)]
    def noise(d, k=30): return lowpass(rng.standard_normal(int(d*SR)).astype(np.float32), k)
    def tone(f, d, amp):
        L = int(d*SR); x = np.arange(L)/SR
        return (np.sin(2*np.pi*f*x)*amp*np.minimum(1, np.minimum(x/.01, (d - x)/.02))).astype(np.float32)
    # гудки
    for t0 in (1.15, 2.2, 3.2): add(T(t0), tone(425, .55, .12))
    # дыхание в трубке
    for t0 in (T(5.6), T(6.6), T(7.4)):
        L = int(.7*SR); add(t0, noise(.7, 8)*np.hanning(L).astype(np.float32)*.25)
    add(T(8.25), tone(425, .15, .1)); add(T(8.45), tone(425, .15, .1))       # короткие гудки после сброса
    # шорох страниц блокнота
    add(T(10.1), noise(.4, 4)*np.hanning(int(.4*SR)).astype(np.float32)*.25)
    # ночной город: ровный гул и ветер
    i0, i1 = int(T(17.7)*SR), int(T(38.5)*SR)
    city = lowpass(rng.standard_normal(i1-i0).astype(np.float32), 300)*.8 + (np.sin(2*np.pi*60*tt[i0:i1])*.01).astype(np.float32)
    g = np.ones(i1-i0, np.float32); g[:SR] = np.linspace(0, 1, SR); g[-SR:] = np.linspace(1, 0, SR)
    sfx[i0:i1] += city*g
    # вибрация в кармане
    def buzz(t0, d=.35):
        L = int(d*SR); x = np.arange(L)/SR
        sq = np.sign(np.sin(2*np.pi*170*x)).astype(np.float32)*.05
        add(t0, lowpass(sq, 6)*np.minimum(1, np.minimum(x/.02, (d - x)/.03)).astype(np.float32))
    buzz(T(35.95)); buzz(T(36.45))
    # скрип двери
    L = int(.9*SR); x = np.arange(L)/SR
    add(T(38.55), (np.sin(2*np.pi*(320 + 120*np.sin(2*np.pi*3*x))*x)*np.hanning(L)*.05).astype(np.float32))
    # кухня: холодильник гудит и обрывается на «Три года назад»
    i0, i1 = int(T(39.9)*SR), int(T(56.35)*SR)
    sfx[i0:i1] += (np.sin(2*np.pi*50*tt[i0:i1])*.03 + np.sin(2*np.pi*100*tt[i0:i1])*.015).astype(np.float32)
    add(T(56.35), noise(.06, 2)*.3)                                              # щелчок реле
    # стук клавиш телефона (мама печатает)
    for k in range(10): add(T(40.0) + k*.17 + rng.uniform(0, .05), noise(.02, 2)*.18)
    # удары
    def boom(t0, f=42, amp=.55, dec=2.5):
        L = int(dec*SR); x = np.arange(L)/SR
        add(t0, (np.sin(2*np.pi*f*x*(1-.25*x/dec))*np.exp(-x*2.2)*amp).astype(np.float32))
    boom(T(45.15), 46, .3); boom(T(56.4), 40, .55); boom(TITLE_T + .1, 38, .45, 3.0)
    # сведение: фон тихо + приглушение под голосом
    speech = v + mv*0.95
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
    out = P("out", "zhivoy_v_moskve_s04.mp4")
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
