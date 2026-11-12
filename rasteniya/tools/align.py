"""Привязка слов текста к озвучке без ASR: паузы (silencedetect) ↔ знаки препинания, DP."""
import re, json, subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
md = open(os.path.join(ROOT, "script.md")).read()
text = md.split("### Текст озвучки")[1].split("## Раскадровка")[0].strip()
paras = [p.strip() for p in text.split("\n\n") if p.strip()]
words = []  # dict(w, para, strength)
for pi, p in enumerate(paras):
    toks = p.split()
    for i, t in enumerate(toks):
        if t in ("—",):  # dash glued as punctuation to previous word
            words[-1]["w"] += " —"; words[-1]["s"] = max(words[-1]["s"], 1); continue
        s = 0
        if re.search(r"(\.\.\.|…|[.?!:])[»\"]?$", t): s = 2
        elif re.search(r"[,;]$", t): s = 1
        if i == len(toks) - 1: s = 3
        words.append(dict(w=t, para=pi, s=s))
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",os.path.join(ROOT,"audio/voice.mp3")]))
out = subprocess.run(["ffmpeg","-hide_banner","-i",os.path.join(ROOT,"audio/voice.mp3"),"-af","silencedetect=noise=-38dB:d=0.15","-f","null","-"],capture_output=True,text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
sil = list(zip(st, en))
lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
sil = [s for s in sil if s[0] > 0.05 and s[1] < dur - 0.05]
tail_end = dur
if out.count("silence_start") > out.count("silence_end"):  # trailing silence
    tail_end = st[-1]
def L(w): return len(re.sub(r"[^\wё]", "", w["w"].lower())) + 1.5
cum = [0.0]
for w in words: cum.append(cum[-1] + L(w))
speech = (tail_end - lead) - sum(e - s for s, e in sil)
rate = speech / cum[-1]
B = [i + 1 for i, w in enumerate(words[:-1]) if w["s"] > 0]  # boundary after word i
S = len(sil); INF = 1e18
def segcost(a, b, t0, t1):
    exp = (cum[b] - cum[a]) * rate; d = t1 - t0
    return (d - exp) ** 2 / max(exp, 0.3)
def skip_pen(a, b):  # strong boundaries inside a segment without a pause
    return sum({1: 0.15, 2: 1.2, 3: 3.0}[words[k - 1]["s"]] for k in B if a < k < b)
# dp[i][j]: silence i assigned to boundary B[j]
dp = [[INF] * len(B) for _ in range(S)]; bk = [[-1] * len(B) for _ in range(S)]
for j, b in enumerate(B):
    dp[0][j] = segcost(0, b, lead, sil[0][0]) + skip_pen(0, b)
for i in range(1, S):
    for j, b in enumerate(B):
        best, arg = INF, -1
        for k in range(j):
            if dp[i - 1][k] >= INF: continue
            c = dp[i - 1][k] + segcost(B[k], b, sil[i - 1][1], sil[i][0]) + skip_pen(B[k], b)
            if c < best: best, arg = c, k
        dp[i][j], bk[i][j] = best, arg
N = len(words)
fin = [dp[S - 1][j] + segcost(B[j], N, sil[-1][1], tail_end) + skip_pen(B[j], N) for j in range(len(B))]
j = min(range(len(B)), key=lambda x: fin[x]); assign = [0] * S
for i in range(S - 1, -1, -1): assign[i] = j; j = bk[i][j]
cuts = [(0, lead)] + [(B[assign[i]], None) for i in range(S)] + [(N, None)]
starts = [lead] + [sil[i][1] for i in range(S)]; ends = [sil[i][0] for i in range(S)] + [tail_end]
bounds = [0] + [B[assign[i]] for i in range(S)] + [N]
for s in range(len(bounds) - 1):
    a, b = bounds[s], bounds[s + 1]; t0, t1 = starts[s], ends[s]; tot = cum[b] - cum[a]
    for k in range(a, b):
        words[k]["t0"] = round(t0 + (t1 - t0) * (cum[k] - cum[a]) / tot, 3)
        words[k]["t1"] = round(t0 + (t1 - t0) * (cum[k + 1] - cum[a]) / tot, 3)
json.dump(dict(duration=dur, paras=paras, words=words), open(os.path.join(ROOT, "audio/words.json"), "w"), ensure_ascii=False, indent=0)
if "-v" in sys.argv:
    for s in range(len(bounds) - 1):
        a, b = bounds[s], bounds[s + 1]
        d = ends[s] - starts[s]; e = (cum[b] - cum[a]) * rate
        print(f"{starts[s]:7.2f}-{ends[s]:7.2f} ({d:4.1f}/{e:4.1f}) " + " ".join(w["w"] for w in words[a:b]))
