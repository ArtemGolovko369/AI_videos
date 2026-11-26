"""Склеивает строки озвучки в одну дорожку и считает тайминги слов -> timeline.json."""
import json, re, subprocess, sys, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, 'audio')
SR = 44100

LINES = [
 "Вы выбрали — выключить камеры.",
 "Я опустил рубильник. Экраны погасли. А вместе с ними — весь торговый центр.",
 "Триста шестьдесят пять дней в торговом центре. Часть четвёртая.",
 "Погасли даже зелёные таблички Выход. Я замер.",
 "Два часа ночи. Ключи. Впервые — не внизу. Здесь. В моём коридоре.",
 "Шаги прошли мимо склада, где я прятался. И ушли.",
 "Я понял второе правило. Он ходит там, где темно.",
 "День девятнадцатый. Рубильник не поднимается. Сгорели предохранители.",
 "Значит, свет я сделаю сам. Налобные фонари из спорттоваров. Пауэрбанки из первой недели. Зелёные пакеты поверх стекла.",
 "Шесть фонарей — по всему коридору.",
 "В два часа ключи дошли до двери. Постояли. И свернули.",
 "День двадцать второй. Я посчитал заряд. Шесть фонарей съедают один пауэрбанк за ночь.",
 "Осталось двадцать девять. Это меньше месяца. Нужны предохранители.",
 "Я снова открыл журнал. На полях — заметка дежурного. Предохранители — склад, третья полка. И подпись.",
 "Я достал свой блокнот. Сравнил. Те же буквы. Тот же наклон.",
 "Это мой почерк.",
 "День двадцать пятый. Третья полка. Коробка предохранителей. Я поднял рубильник.",
 "Свет вернулся. Экраны тоже. Шестнадцатая камера — пусто. За моей спиной никого.",
 "Я посмотрел на магазин одежды. Тринадцать. На плечах у тринадцатого — оранжевый рюкзак.",
 "Я оглянулся. Моего рюкзака нет.",
 "Осталось триста сорок дней. Забрать рюкзак — или оставить ему? Пиши один или два.",
]
GAP_BEFORE = {0: 0.7, 1: 0.5, 2: 0.8, 3: 0.9, 4: 0.5, 5: 0.5, 6: 0.6, 7: 1.0, 8: 0.4, 9: 0.3, 10: 0.6, 11: 1.0,
              12: 0.3, 13: 0.5, 14: 0.4, 15: 0.9, 16: 1.0, 17: 0.4, 18: 0.6, 19: 0.6, 20: 1.3}
DEFAULT_GAP = 0.3
TAIL = 4.5
INNER_PAUSE = {(4, 1): 0.4, (10, 1): 0.4, (10, 2): 0.4, (19, 1): 0.7, (18, 1): 0.3}

Y, R, G = 'y', 'r', 'g'
ACCENT = {
 0: {'выключить': Y},
 1: {'весь': R, 'торговый': R, 'центр': R},
 3: {'выход': Y},
 4: {'здесь': R, 'ключи': R},
 6: {'темно': Y, 'где': Y},
 7: {'предохранители': R},
 9: {'шесть': Y, 'фонарей': Y},
 10: {'свернули': G},
 11: {'один': Y},
 12: {'меньше': R, 'месяца': R},
 13: {'третья': Y, 'полка': Y},
 15: {'мой': R, 'почерк': R},
 17: {'свет': G, 'вернулся': G, 'никого': Y},
 18: {'оранжевый': Y, 'рюкзак': Y},
 19: {'нет': R},
 20: {'забрать': Y, 'оставить': Y, 'один': Y, 'два': Y},
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
