"""Обложка: росток в сером горшке + «ПОСЛЕДНЕЕ РАСТЕНИЕ НА ЗЕМЛЕ» → out/cover.png"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import render as R
arr = R.camera(R.img("B__15_rostok"), 1.35, 700, 1000)
im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
g = R.glow_sprite().resize((700, 700)); gl = Image.new("RGBA", (700, 700), (110, 230, 100, 0)); gl.putalpha(g.point(lambda v: int(v * .55)))
im.alpha_composite(gl, (int((740 - 700) * 1.35 + 540 - 350), int((950 - 1000) * 1.35 + 960 - 350)))
d = ImageDraw.Draw(im); f = R.font(R.FONT_SERIF, 112)
for i, (line, col) in enumerate([("ПОСЛЕДНЕЕ", (255, 255, 255)), ("РАСТЕНИЕ", (120, 225, 105)), ("НА ЗЕМЛЕ", (255, 255, 255))]):
    d.text((540, 230 + i * 135), line, font=f, fill=col, anchor="ma", stroke_width=8, stroke_fill=(18, 18, 22))
d.text((540, 1650), "ЧТО ЕСЛИ… ИСЧЕЗНУТ РАСТЕНИЯ", font=R.font(R.FONT_SANS, 46), fill=(240, 238, 230), anchor="ma", stroke_width=5, stroke_fill=(18, 18, 22))
im.convert("RGB").save(os.path.join(R.OUT, "cover.png"))
