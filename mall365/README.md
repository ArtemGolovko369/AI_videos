# 365 дней в торговом центре — Часть 1

Стиль 6 («N дней в …»), 9:16, 1080×1920, 30 к/с, 2:18. Голос River (vidIQ).

- `mall365_part1.mp4` — готовый ролик, `cover.jpg` — обложка.
- `audio/l00–l22.mp3` — строки озвучки vidIQ.

Пересборка:
```
python3 build/timeline.py        # склейка озвучки, тайминги слов -> build/timeline.json, narration.wav
node build/render.js full 4      # кадры (HTML+SVG в scene/) -> build/frames, события звука -> build/sfx.json
python3 build/sfx.py             # дрон + шумы + голос -> build/mix.wav
ffmpeg -framerate 30 -i build/frames/f%05d.jpg -i build/mix.wav -c:v libx264 -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -af loudnorm=I=-14:TP=-1.5 -shortest mall365_part1.mp4
node build/cover.js              # обложка
```
