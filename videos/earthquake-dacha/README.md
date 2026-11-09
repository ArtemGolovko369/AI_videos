# Если землетрясение застало вас на даче — видео v2

Собрано по `files/style-01-time-loop-drama.md` + `files/common-tiktok-format.md`
(ветка `claude/video-characters-visual-desc-w0jqih`).

- **Итог:** `earthquake-dacha.mp4` — 1080×1920, 30 fps, 93,6 сек.
- Плоская 2D-иллюстрация с толстым контуром, ночная палитра, бумажное зерно, виньетка.
- Герой «вы» — холодная серо-голубая кофта; незнакомка — горчично-жёлтая куртка; второстепенные — красная куртка / серая кепка.
- HUD сверху: часы, день недели и дата, бейдж «ДЕНЬ N». Каждый толчок — ровно в **03:17**, счётчик дней растёт (петля).
- Субтитры по 1–4 слова, синхронно с голосом (паузы найдены `silencedetect`), жёлтый — советы, красный — опасность.
- Концовка-интерактив: «ОСТАТЬСЯ НА ДАЧЕ С НЕЗНАКОМЦАМИ?» ДА / НЕТ · «РЕШАТЬ ВАМ.», затем заставка «ЧТО ЕСЛИ…».
- Звук: озвучка vidIQ (голос Brian) + сгенерированный гул, рокот толчков, тиканье часов.

## Пересборка
```bash
cd videos/earthquake-dacha
python3 -c "import os,scenes;os.makedirs('build/svg',exist_ok=True);[open(f'build/svg/{k}.svg','w').write(f()) for k,f in scenes.SCENES.items()]"
node render_scenes.js build      # SVG → PNG (Playwright)
python3 build.py                 # кадры + HUD + субтитры + звук → earthquake-dacha.mp4
```
Тайминги сцен — `SHOTS`, фразы озвучки — `CHUNKS` в `build.py`; рисунки — `scenes.py`.
