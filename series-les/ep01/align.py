"""Тайминги слов без распознавания речи.

Текст озвучки известен точно, поэтому:
1) ffmpeg находит паузы -> куски речи;
2) динамическое программирование раскладывает слова по кускам так, чтобы длительность куска
   совпадала с числом слогов, а границы кусков приходились на знаки препинания;
3) внутри куска слова получают время пропорционально слогам.
Результат: words.json [{w, start, end, sent}]
"""
import json, re, subprocess, sys

AUDIO = sys.argv[1] if len(sys.argv) > 1 else 'audio/voice_full_sarah.mp3'
TEXT = sys.argv[2] if len(sys.argv) > 2 else 'voice_clean_short.txt'
VOW = set('аеёиоуыэюяАЕЁИОУЫЭЮЯ')


def duration(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))


def speech_segments(p, total):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'silencedetect=n=-38dB:d=0.18', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', out)]
    en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', out)]
    segs, cur = [], 0.0
    for s, e in zip(st, en):
        if s - cur > 0.02:
            segs.append([cur, s])
        cur = e
    if total - cur > 0.05:
        segs.append([cur, total])
    # склеить слишком короткие (вдохи, щелчки) с соседом
    merged = []
    for a, b in segs:
        if b - a < 0.18 and merged:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return merged


def words_from_text(t):
    out, sent = [], 0
    for line in t.splitlines():
        for tok in line.split():
            if not re.search(r'\w', tok):
                continue
            syl = max(1, sum(c in VOW for c in tok))
            strong = bool(re.search(r'[.!?…»]$', tok))
            weak = bool(re.search(r'[,—:;]$', tok))
            out.append({'w': tok, 'syl': syl, 'strong': strong, 'weak': weak, 'sent': sent})
            if strong:
                sent += 1
        # конец строки — тоже конец фразы
    # «—» отдельным токеном даёт паузу после предыдущего слова
    toks = t.split()
    i = 0
    for k, tok in enumerate(toks):
        if tok == '—' and k > 0:
            # найти предыдущее слово
            pass
    return out


def align(words, segs):
    n, m = len(words), len(segs)
    syl_cum = [0]
    for w in words:
        syl_cum.append(syl_cum[-1] + w['syl'] + 0.6)  # +0.6 «вес» слова
    speech = sum(b - a for a, b in segs)
    k = speech / syl_cum[-1]
    INF = 1e18
    dp = [[INF] * (n + 1) for _ in range(m + 1)]
    bk = [[0] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = 0
    for j in range(1, m + 1):
        d = segs[j - 1][1] - segs[j - 1][0]
        for i in range(1, n + 1):
            # граница после слова i-1 (последнее слово куска)
            w = words[i - 1]
            bpen = 0 if (w['strong'] or i == n) else (0.6 if w['weak'] else 3.0)
            best, arg = INF, 0
            for p in range(max(0, i - 25), i):
                if dp[j - 1][p] >= INF:
                    continue
                exp = k * (syl_cum[i] - syl_cum[p])
                c = dp[j - 1][p] + ((d - exp) / (0.25 + 0.25 * exp)) ** 2 + bpen
                if c < best:
                    best, arg = c, p
            dp[j][i], bk[j][i] = best, arg
    # восстановление
    groups, i = [], n
    for j in range(m, 0, -1):
        p = bk[j][i]
        groups.append((p, i, segs[j - 1]))
        i = p
    groups.reverse()
    res = []
    for p, i, (a, b) in groups:
        tot = sum(words[q]['syl'] + 0.6 for q in range(p, i))
        t = a
        for q in range(p, i):
            dt = (b - a) * (words[q]['syl'] + 0.6) / tot
            res.append({'w': words[q]['w'], 'start': round(t, 3), 'end': round(t + dt, 3), 'sent': words[q]['sent'],
                        'seg': [round(a, 2), round(b, 2)]})
            t += dt
    return res


if __name__ == '__main__':
    total = duration(AUDIO)
    segs = speech_segments(AUDIO, total)
    words = words_from_text(open(TEXT, encoding='utf-8').read())
    res = align(words, segs)
    json.dump({'duration': total, 'words': res}, open('words.json', 'w'), ensure_ascii=False, indent=1)
    cur = None
    for r in res:
        if r['seg'] != cur:
            cur = r['seg']
            print(f"\n[{cur[0]:6.2f}-{cur[1]:6.2f}]", end=' ')
        print(r['w'], end=' ')
    print(f"\n\nсегментов: {len(segs)}, слов: {len(res)}")
