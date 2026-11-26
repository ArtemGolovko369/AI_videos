"""Word timings for subtitles + loudness envelope for lipsync.
Line starts come from vidIQ (scriptLines); inside a line, words are spread
by syllable weight, with extra weight for punctuation pauses, and snapped to
detected silences."""
import json, re, subprocess, os
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LINES = [
 (0, 3.239184, 'Каждый вечер ужин из доставки за семьсот рублей.'),
 (3.239184, 5.564082, 'Или готовишь сам: продукты двести пятьдесят, но час у плиты. Что выберешь?'),
 (8.803265, 7.967347, 'Тёма уже жмёт «заказать»: «Час жизни на котлеты? Нет уж!» Вика достаёт сковородку: «Посмотрим, кто кого».'),
 (16.770612, 4.519184, 'Месяц доставки — двадцать одна тысяча. Если верить приложению.'),
 (21.289796, 12.277551, 'А теперь правда. Сервисный сбор. Чаевые курьеру. И десерт — добить до бесплатной доставки. Реальный чек — девятьсот пятьдесят. За месяц — двадцать восемь с половиной тысяч.'),
 (33.567347, 11.650612, 'Вика тратит на продукты семь с половиной тысяч. И тридцать часов у плиты. Считаем. Экономия двадцать одна тысяча. Делим на тридцать часов. Семьсот рублей в час.'),
 (45.217959, 9.247347, 'И тут Вика хитрит. Готовит по воскресеньям. Три часа — и еда на всю неделю. Теперь у неё двенадцать часов в месяц, а не тридцать.'),
 (54.465306, 6.765714, 'Делим на двенадцать. Тысяча семьсот пятьдесят рублей в час! Больше, чем платят Тёме на работе.'),
 (61.23102, 5.955918, 'А Тёма? Тёма теперь ужинает у Вики по пятницам. И приносит десерт. Из доставки.'),
 (67.186939, 5.146122, 'Так что выгоднее: время или деньги? А ты что выбрал? Пиши в комменты!'),
]
VOW = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
NUM = {"семьсот","рублей","двести","пятьдесят","час","двадцать","одна","тысяча","тысяч","девятьсот","восемь","половиной","семь","тридцать","часов",
       "три","часа","неделю","двенадцать","пятьдесят","воскресеньям","пятницам"}

def syl(w): return max(1, sum(c in VOW for c in w))

def main():
    words = []
    for li, (st, du, text) in enumerate(LINES):
        toks = text.replace("—", " — ").split()
        toks = [t for t in toks if t != "—"]
        weights, pauses = [], []
        for t in toks:
            weights.append(syl(t) + 0.6)
            p = 0.0
            if re.search(r"[.!?]»?\.?$", t): p = 2.2
            elif re.search(r"[,:;»]$", t): p = 1.0
            pauses.append(p)
        # small lead-in/out silence of ~0.12s inside each line
        lead, tail = 0.10, 0.25
        span = du - lead - tail
        total = sum(weights) + sum(pauses[:-1])
        k = span / total
        t = st + lead
        for i, tok in enumerate(toks):
            w = weights[i] * k
            clean = re.sub(r"[«»:;,.!?]", "", tok)
            words.append(dict(w=tok, s=round(t, 3), e=round(t + w, 3), line=li,
                              num=clean.lower() in NUM, end=pauses[i] > 0))
            t += w + (pauses[i] * k if i < len(toks) - 1 else 0)
    # group into subtitle chunks: 1–4 words, break after punctuation
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if w["end"] or len(cur) >= 3 or (len(cur) >= 2 and len(w["w"]) > 9):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    subs = [dict(s=c[0]["s"], e=c[-1]["e"], words=[dict(w=x["w"], s=x["s"], num=x["num"]) for x in c]) for c in chunks]
    # extend each chunk's end until next chunk starts (max +0.6s)
    for a, b in zip(subs, subs[1:]):
        a["e"] = min(b["s"], a["e"] + 0.6)
    subs[-1]["e"] += 1.5
    # loudness envelope at 30 fps
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{ROOT}/audio/voice.mp3", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 16000 // 30
    env = [float(np.sqrt(np.mean(a[i:i + hop] ** 2))) for i in range(0, len(a), hop)]
    m = max(env)
    env = [round(e / m, 3) for e in env]
    json.dump(dict(lines=[dict(s=s, d=d, t=t) for s, d, t in LINES], words=words, subs=subs, env=env),
              open(f"{ROOT}/build/timing.json", "w"), ensure_ascii=False)
    print(len(words), "words", len(subs), "subs", len(env), "env frames")

if __name__ == "__main__":
    os.makedirs(f"{ROOT}/build", exist_ok=True)
    main()
