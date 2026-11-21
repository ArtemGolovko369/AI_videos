"""Склеивает строки озвучки в одну дорожку и считает тайминги слов -> timeline.json."""
import json, re, subprocess, sys, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, 'audio')
SR = 44100

LINES = [
 "Я рассыпал детскую присыпку вокруг манекенов. Утром на ней были следы. Босые.",
 "Триста шестьдесят пять дней в торговом центре. Часть вторая.",
 "День шестой. Манекенов тринадцать. Вчера было двенадцать.",
 "Я осмотрел каждого. Ни грязи. Ни царапины. Все одинаковые.",
 "Значит, прятаться он умеет лучше меня.",
 "Тогда я взял в аптеке детскую присыпку. И рассыпал тонким слоем вокруг всего ряда.",
 "Если кто-то сдвинется — я увижу.",
 "День седьмой. Торговые автоматы на фудкорте погасли. Воды в бутылках — на неделю.",
 "В туалетах вода есть. Но мутная.",
 "Я сделал фильтр. Бутылка без дна. Аптечная марля. Уголь из аквариумного отдела. Песок из цветочного.",
 "Слой за слоем. А потом кипячу на туристической горелке.",
 "А утром я проверил присыпку. Следы босых ног выходили из ряда. Шли через весь этаж.",
 "До фудкорта. До того места, где сплю я. И возвращались обратно.",
 "День девятый. Я решил проверить, зачем обходчик считает. Вечером унёс одного манекена на склад.",
 "Два часа ночи. Ключи. Луч прошёл по ряду. И остановился. Ключи стихли.",
 "А потом шаги пошли не к складу. Ко мне.",
 "Я бегом вернул манекена на место. Шаги сразу затихли.",
 "Теперь я знаю правило. Счёт должен сходиться. Если кого-то не хватает — он берёт замену.",
 "День двенадцатый. Я долго считал. Двенадцать манекенов стояли здесь всегда.",
 "Тринадцатый пришёл, когда я встал среди них. Значит, лишний здесь не он. Лишний — я.",
 "Сегодня в два часа ночи ключи остановились у магазина одежды.",
 "И я услышал, как тринадцатый шагнул из ряда. Ко мне.",
 "Осталось триста пятьдесят три дня. Бежать — или замереть? Пиши один или два.",
]
GAP_BEFORE = {0: 0.25, 1: 0.7, 2: 0.9, 5: 0.4, 7: 1.0, 8: 0.4, 9: 0.4, 11: 0.9, 12: 0.3, 13: 1.0,
              14: 0.6, 15: 0.5, 16: 0.4, 17: 0.8, 18: 1.0, 19: 0.4, 20: 1.0, 21: 0.4, 22: 1.2}
DEFAULT_GAP = 0.3
TAIL = 4.5
INNER_PAUSE = {(14, 3): 0.4, (14, 4): 0.5, (15, 1): 0.6, (19, 2): 0.6, (21, 1): 0.5}

Y, R, G = 'y', 'r', 'g'
ACCENT = {
 0: {'босые': R, 'присыпку': Y},
 2: {'тринадцать': R, 'двенадцать': Y},
 3: {'одинаковые': Y},
 5: {'присыпку': Y},
 6: {'увижу': G},
 7: {'на': None, 'неделю': Y, 'погасли': R},
 8: {'мутная': R},
 9: {'фильтр': G},
 10: {'кипячу': G},
 11: {'босых': R},
 12: {'сплю': R, 'я': R, 'где': R},
 13: {'склад': Y},
 14: {'остановился': R, 'стихли': R},
 15: {'ко': R, 'мне': R},
 16: {'затихли': G},
 17: {'сходиться': Y, 'замену': R},
 18: {'всегда': Y, 'двенадцать': Y},
 19: {'лишний': R, 'я@2': R},
 20: {'одежды': Y},
 21: {'ко': R, 'мне': R, 'шагнул': R},
 22: {'бежать': Y, 'замереть': Y, 'один': Y, 'два': Y},
}

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def speech_segments(x, thr_db=-35, min_sil=0.12):
    win = int(0.01 * SR)
    n = len(x) // win
    rms = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(1) + 1e-12)
    loud = 20 * np.log10(rms) > thr_db
    segs, start, sil = [], None, 0
    for i, l in enumerate(loud):
        if l:
            if start is None: start = i
            sil = 0
        elif start is not None:
            sil += 1
            if sil * 0.01 >= min_sil:
                segs.append([start * 0.01, (i - sil + 1) * 0.01]); start = None; sil = 0
    if start is not None: segs.append([start * 0.01, n * 0.01])
    return segs

def phrases(text):
    # делим по . ? ! : — ,(только запятая перед паузой не нужна) ; сохраняем слова
    parts = re.split(r'(?<=[.?!:])\s+|\s+—\s+', text)
    return [p for p in parts if p.strip()]

def words_of(p):
    return p.split()

def clean(w):
    return re.sub(r'[^\wё-]', '', w.lower())

def main():
    out_lines, chunks, t = [], [], 0.0
    for i, text in enumerate(LINES):
        x = decode(os.path.join(AUD, f'l{i:02d}.mp3'))
        segs = speech_segments(x)
        ph = phrases(text)
        # сопоставление фраз с сегментами речи
        segs = [sg for sg in segs if sg[1] - sg[0] > 0.06]
        while len(segs) > len(ph):
            gaps = [segs[k + 1][0] - segs[k][1] for k in range(len(segs) - 1)]
            k = int(np.argmin(gaps)); segs[k:k + 2] = [[segs[k][0], segs[k + 1][1]]]
        if len(segs) == len(ph):
            ph_t = segs
        else:
            # объединяем: распределяем фразы по общему речевому времени пропорционально символам
            total = sum(e - s for s, e in segs)
            lens = np.array([len(p) for p in ph], float); lens /= lens.sum()
            # карта "речевое время" -> реальное время
            def real(st):
                acc = 0
                for s, e in segs:
                    if st <= acc + (e - s): return s + (st - acc)
                    acc += e - s
                return segs[-1][1]
            cum = np.concatenate([[0], np.cumsum(lens)]) * total
            ph_t = [[real(cum[k] + 1e-4), real(cum[k + 1] - 1e-4)] for k in range(len(ph))]
            print(f'line {i}: {len(ph)} phrases vs {len(segs)} segs -> proportional', file=sys.stderr)
        t += GAP_BEFORE.get(i, DEFAULT_GAP)
        # вставка внутренних пауз: режем аудио на куски по границам фраз
        cut_points = []  # (время в исходнике, доп. пауза)
        for (li, pk), d in INNER_PAUSE.items():
            if li == i:
                cut_points.append(((ph_t[pk - 1][1] + ph_t[pk][0]) / 2, d))
        cut_points.sort()
        def shift(tt):
            return sum(d for c, d in cut_points if tt > c)
        prev = 0
        for c, d in cut_points:
            chunks.append(x[int(prev * SR):int(c * SR)]); chunks.append(np.zeros(int(d * SR), np.float32)); prev = c
        chunks.append(x[int(prev * SR):])
        line_start = t
        acc = ACCENT.get(i, {})
        phr_out = []
        for pi, (p, (s, e)) in enumerate(zip(ph, ph_t)):
            ws = words_of(p)
            wl = np.array([len(clean(w)) + 1.5 for w in ws], float)
            edges = s + np.concatenate([[0], np.cumsum(wl) / wl.sum()]) * (e - s)
            wo = []
            for k, w in enumerate(ws):
                ws0 = edges[k] + shift(edges[k]); we = edges[k + 1] + shift(edges[k])
                wo.append({'w': w.upper(), 't0': round(line_start + ws0, 3), 't1': round(line_start + we, 3),
                           'c': acc.get(f'{clean(w)}@{pi}', acc.get(clean(w)))})
            phr_out.append({'t0': wo[0]['t0'], 't1': wo[-1]['t1'], 'words': wo})
        dur = len(x) / SR + sum(d for _, d in cut_points)
        out_lines.append({'i': i, 'text': text, 't0': round(line_start, 3), 't1': round(line_start + dur, 3),
                          'phrases': phr_out})
        # тишина перед строкой
        chunks.insert(len(chunks) - 1 - 2 * len(cut_points), np.zeros(int(GAP_BEFORE.get(i, DEFAULT_GAP) * SR), np.float32))
        t = line_start + dur
    total = t + TAIL
    audio = np.concatenate(chunks)
    audio = np.concatenate([audio, np.zeros(int(total * SR) - len(audio), np.float32)])
    import wave
    with wave.open(os.path.join(ROOT, 'build', 'narration.wav'), 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
    json.dump({'duration': round(total, 3), 'lines': out_lines}, open(os.path.join(ROOT, 'build', 'timeline.json'), 'w'),
              ensure_ascii=False, indent=1)
    for l in out_lines:
        print(f"{l['i']:2d} {l['t0']:7.2f}-{l['t1']:7.2f}  {l['text'][:50]}")
    print('total', round(total, 2), 'audio', len(audio) / SR)

main()
