"""Строит таймлайн ролика: где стоит каждая фраза озвучки, когда звучит каждое слово,
где начинается и кончается каждая сцена. Результат: tools/timeline.json (его читает
render.html) и audio/voice_placed.wav (озвучка, разложенная по таймлайну с паузами)."""
import json, os, re, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SR = 44100

# начало и длительность каждой строки в общем MP3 vidIQ
LINES = [(0, 1.567347), (1.567347, 11.31102), (12.878367, 5.720816), (18.599184, 9.560816),
         (28.16, 13.949388), (42.109388, 8.829388), (50.938776, 10.840816), (61.779592, 7.235918),
         (69.01551, 10.44898), (79.46449, 8.75102), (88.21551, 14.680816), (102.896327, 13.792653),
         (116.68898, 19.069388), (135.758367, 9.247347), (145.005714, 3.709388), (148.715102, 4.127347)]
TEXT = [l.strip() for l in open(os.path.join(HERE, "voice_lines.txt"), encoding="utf-8") if l.strip()]
assert len(TEXT) == len(LINES)

wav = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "audio/voice_full.wav"),
                      "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
voice = np.frombuffer(wav, dtype=np.float32)

def silences(x, thr_db=-38, min_len=0.12):
    win = int(0.01 * SR)
    n = len(x) // win
    rms = np.sqrt(np.mean(x[:n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
    quiet = 20 * np.log10(rms) < thr_db
    out, s = [], None
    for i, q in enumerate(quiet):
        if q and s is None: s = i
        if not q and s is not None:
            if (i - s) * 0.01 >= min_len: out.append((s * 0.01, i * 0.01))
            s = None
    return out, quiet

def speech_bounds(quiet):
    idx = np.where(~quiet)[0]
    return idx[0] * 0.01, (idx[-1] + 1) * 0.01

def split_parts(text):
    # делим строку на смысловые куски по паузам в тексте
    parts = re.split(r'(?<=[.?!:…])\s+|\s+—\s+', text)
    return [p for p in parts if p.strip()]

def words_of(part):
    return part.split()

lines_out = []
for li, ((st, du), text) in enumerate(zip(LINES, TEXT)):
    seg = voice[int(st * SR): int((st + du) * SR)]
    sil, quiet = silences(seg)
    a, b = speech_bounds(quiet)
    parts = split_parts(text)
    w = [len(p) + 3 for p in parts]
    tot = sum(w)
    # ожидаемые границы кусков пропорционально длине, потом притягиваем к реальным паузам
    est, acc = [], 0
    for x in w[:-1]:
        acc += x; est.append(a + (b - a) * acc / tot)
    used, bounds, last = set(), [], a
    for e in est:
        cands = [(abs((s0 + s1) / 2 - e), k) for k, (s0, s1) in enumerate(sil) if k not in used and last < s0 < b]
        cands = [c for c in cands if c[0] < 1.3]
        if cands:
            _, k = min(cands); used.add(k); bounds.append(sil[k])
        else:
            e = max(e, last + 0.2); bounds.append((e, e))
        last = bounds[-1][1]
    starts = [a] + [s1 for s0, s1 in bounds]
    ends = [s0 for s0, s1 in bounds] + [b]
    words = []
    for p, s, e in zip(parts, starts, ends):
        ws = words_of(p)
        ww = [len(x) + 1.5 for x in ws]
        t = s
        for x, wl in zip(ws, ww):
            d = (e - s) * wl / sum(ww)
            words.append({"w": x, "s": round(t, 3), "e": round(t + d, 3)})
            t += d
    lines_out.append({"text": text, "src": st, "dur": du, "parts": parts,
                      "words": words, "speech": [a, b]})

# ---- раскладка по сценам
# сцена 1..14 = строка 0..13, сцена 15 = строки 14 и 15
PRE = {1: 2.8}                      # сцена 1: сначала щелчок фонарика и луч
LEAD = 0.45                         # голос вступает чуть позже начала сцены
TAIL = 0.55
EXTRA = {6: 2.0, 8: 0.7, 10: 2.0, 12: 2.0, 13: 2.0}   # паузы из сценария
scenes, placed = [], []
t = 0.0
for sc in range(1, 16):
    start = t
    li_list = [sc - 1] if sc < 15 else [14, 15]
    vt = start + PRE.get(sc, LEAD)
    for k, li in enumerate(li_list):
        L = lines_out[li]
        placed.append({"line": li, "at": round(vt, 3)})
        vt += L["dur"]
        if sc == 15 and k == 0:
            vt += 2.6               # фонарик гаснет, свет между силуэтами остаётся
    end = vt + TAIL + EXTRA.get(sc, 0)
    if sc == 1: end = vt + 0.5
    if sc == 15: end = vt + 5.0     # титр и затемнение
    scenes.append({"id": sc, "start": round(start, 3), "end": round(end, 3)})
    t = end

total = scenes[-1]["end"]
for p in placed:
    L = lines_out[p["line"]]
    p["words"] = [{"w": w["w"], "s": round(p["at"] + w["s"], 3), "e": round(p["at"] + w["e"], 3)} for w in L["words"]]
    p["parts"] = L["parts"]
    p["end"] = round(p["at"] + L["speech"][1], 3)
    p["start"] = round(p["at"] + L["speech"][0], 3)

json.dump({"total": round(total, 3), "scenes": scenes, "voice": placed},
          open(os.path.join(HERE, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- озвучка по таймлайну
out = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
for p in placed:
    st, du = LINES[p["line"]]
    seg = voice[int(st * SR): int((st + du) * SR)]
    i = int(p["at"] * SR)
    out[i:i + len(seg)] += seg[:len(out) - i]
np.save(os.path.join(ROOT, "audio/voice_placed.npy"), out)
print("total", round(total, 2))
for s in scenes: print(s)
