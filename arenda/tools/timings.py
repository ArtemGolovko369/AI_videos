"""Word timings for subtitles + loudness envelope for lipsync.
Line starts come from vidIQ (scriptLines); inside a line, words are spread
by syllable weight, with extra weight for punctuation pauses, and snapped to
detected silences."""
import json, re, subprocess, os
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LINES = [
 (0.0, 3.5527, "Квартира в десяти минутах от работы за пятьдесят тысяч."),
 (3.5527, 4.9894, "Или такая же — за двадцать пять. Но до работы час. Что выберешь?"),
 (8.5420, 8.0457, "Тёма думал ноль секунд: «Конечно, рядом! Время — деньги!» Вика: «Двадцать пять тысяч на дороге не валяются»."),
 (16.5878, 5.7208, "Тёма встаёт в восемь сорок. Кофе, душ — и он уже в офисе. Красота."),
 (22.3086, 6.1910, "Вика встаёт в семь. Метро, пересадка, автобус. Час туда. Час обратно."),
 (28.4996, 9.4041, "Считаем. Два часа в день. Двадцать два рабочих дня. Это сорок четыре часа в месяц. Почти двое суток — в транспорте."),
 (37.9037, 11.0759, "Зато Вика экономит двадцать пять тысяч. Минус три тысячи на проезд — остаётся двадцать две. Делим на сорок четыре часа. Вика продаёт свой час за пятьсот рублей."),
 (48.9796, 5.4073, "А что Тёма делает со своими сорока четырьмя часами? Спит. И листает ленту."),
 (54.3869, 8.5943, "А Вика каждый день в метро проходила курс. Через полгода её позвали на новую работу. На тридцать тысяч больше. И удалённо."),
 (62.9812, 5.1461, "Теперь у неё дешёвая квартира, ноль часов дороги — и плюс тридцать тысяч."),
 (68.1273, 5.2506, "Так кто выиграл: время или деньги? А ты что выбрал? Пиши в комменты!"),
]
VOW = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
NUM = {"десяти","пятьдесят","тысяч","двадцать","пять","час","ноль","секунд","восемь","сорок","семь","два","часа",
       "двадцать","дня","четыре","двое","суток","три","тысячи","две","пятьсот","рублей","четырьмя","часами",
       "тридцать","полгода","часов"}

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
