import os
d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scene') + '/'
src = open(d + '../../scene/scenes.js').read()
i = src.index('function blueprint(t, title)'); j = src.index('// 7. Схема: четыре болта')
bp = src[i:j].replace("mono(80, 640, title, 30, '#a9cbf5') + `<line x1=\"80\" y1=\"655\" x2=\"1000\" y2=\"655\"", "mono(80, 740, title, 30, '#a9cbf5') + `<line x1=\"80\" y1=\"755\" x2=\"1000\" y2=\"755\"")
pre = "const scenes = [];\nconst add = (t0, t1, draw, fade = .35) => scenes.push({ t0, t1, draw, fade });\n" + bp + "\n"
open(d + 'scenes.js', 'w').write(open(d + '_head.js').read() + pre + open(d + '_p3.js').read() + open(d + '_subs.js').read() + open(d + '_frame.js').read())
