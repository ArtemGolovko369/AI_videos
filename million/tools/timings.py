"""Word timings for subtitles + loudness envelope for lipsync.
Line starts come from vidIQ (scriptLines); inside a line, words are spread
by syllable weight, with extra weight for punctuation pauses, and snapped to
detected silences."""
import json, re, subprocess, os
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LINES = [
 (0, 2.429388, 'Миллион рублей прямо сейчас.'),
 (2.429388, 7.967347, 'Или три тысячи каждый день целый год. Но забирать лично. В семь утра. Не пришёл — день сгорел. Что выберешь?'),
 (10.396735, 4.989388, 'Тёма: «Миллион! Сразу! Вставать в семь? Я что, петух?»'),
 (15.386122, 9.404082, 'Вика молча считает: три тысячи умножить на триста шестьдесят пять. Миллион девяносто пять тысяч. Больше миллиона!'),
 (24.790204, 8.594286, 'Но у Тёмы есть козырь. Он кладёт деньги на вклад. Под десять процентов это сто тысяч сверху. И никаких будильников.'),
 (33.38449, 7.079184, 'А Вика бегает за деньгами. В дождь. В мороз. В воскресенье. Тридцать первого декабря — тоже.'),
 (40.463673, 7.627755, 'За год она проспала четыре раза и болела неделю. Сгорело четырнадцать дней. Минус сорок две тысячи.'),
 (48.091429, 8.907755, 'Но в первую же неделю он понял, что ему нужен мотоцикл. Триста тысяч. На вкладе осталось семьсот. Проценты — семьдесят.'),
 (56.999184, 11.72898, 'Итог года. У Тёмы семьсот семьдесят тысяч и мотоцикл, который стоит в гараже. Ноябрь же. У Вики — миллион пятьдесят три тысячи. Она не успевала их тратить.'),
 (68.728163, 4.832653, 'Получается, главный минус миллиона — не проценты. А ты сам.'),
 (73.560816, 3.474286, 'А ты бы вставал в семь каждый день? Пиши в комменты!'),
]
VOW = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
NUM = {"миллион","миллиона","три","тысячи","тысяч","год","семь","триста","шестьдесят","пять","девяносто","десять","процентов","сто",
       "тридцать","первого","декабря","четыре","раза","неделю","четырнадцать","дней","сорок","две","триста","семьсот","семьдесят","пятьдесят"}

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
