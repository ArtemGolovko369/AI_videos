"""Артём (32), Соня (6), одуванчик и прочие спрайты. Якорь спрайтов — низ по центру (0,0)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from core import *  # noqa

SKIN = (238, 200, 174)
SKIN_D = (214, 170, 146)
HAIR = (52, 38, 34)
STUBBLE = (222, 184, 160)
HOODIE = (86, 104, 132)
HOODIE_D = (64, 78, 102)
JEANS = (44, 52, 78)
SHOE = (34, 32, 40)
SON_TOP = (238, 112, 72)
SON_TOP_D = (206, 84, 54)
SON_HAIR = (130, 80, 44)
TIGHTS = (240, 236, 228)
SON_SHOE = (190, 48, 52)
BLUSH = (244, 150, 140)
STEM = (70, 150, 60)
STEM_D = (50, 116, 46)
PETAL = (255, 210, 40)
PETAL_D = (240, 170, 20)


def dandelion(c, x, y, s=1.0, petal_shift=0.0, stem=True, skip=None):
    """Одуванчик: (x,y) — центр цветка, стебель вниз на 120*s."""
    if stem:
        c.line([(x, y + 6 * s), (x - 6 * s, y + 70 * s), (x, y + 130 * s)], STEM, max(4, 7 * s))
        c.poly([(x - 2 * s, y + 100 * s), (x - 40 * s, y + 80 * s), (x - 24 * s, y + 96 * s), (x - 46 * s, y + 104 * s),
                (x - 4 * s, y + 116 * s)], STEM, w=3 * s)
    for k in range(14):
        if k == skip:
            continue
        a = k / 14 * 2 * math.pi + petal_shift
        px, py = x + 26 * s * math.cos(a), y + 26 * s * math.sin(a)
        c.ellipse(px - 13 * s, py - 13 * s, px + 13 * s, py + 13 * s, PETAL, w=3 * s)
    c.circle(x, y, 18 * s, PETAL_D, w=3 * s)
    c.circle(x, y, 9 * s, PETAL, w=0)


def _face_artyom(c, cx, cy, expr, look, blink):
    # cy — центр лица
    c.ellipse(cx - 82, cy - 96, cx + 82, cy + 46, HAIR)                 # волосы сзади
    c.ellipse(cx - 70, cy - 74, cx + 70, cy + 66, SKIN)
    c.poly([(cx - 60, cy + 24), (cx - 24, cy + 30), (cx + 24, cy + 30), (cx + 60, cy + 24), (cx + 46, cy + 54), (cx, cy + 66), (cx - 46, cy + 54)],
           STUBBLE, w=0)                                               # щетина
    c.poly([(cx - 78, cy - 40), (cx - 60, cy - 94), (cx - 10, cy - 108), (cx + 50, cy - 100), (cx + 80, cy - 52),
            (cx + 70, cy - 30), (cx + 40, cy - 56), (cx, cy - 46), (cx - 40, cy - 58), (cx - 70, cy - 22)], HAIR, w=5)
    lx = 6 * look
    ey = cy - 4
    if blink:
        c.line([(cx - 34, ey), (cx - 14, ey)], INK, 5)
        c.line([(cx + 14, ey), (cx + 34, ey)], INK, 5)
    elif expr == "shock":
        for ex in (-25, 25):
            c.circle(cx + ex, ey, 14, (255, 255, 255), w=4)
            c.circle(cx + ex + lx * 0.5, ey, 5, INK, w=0)
    else:
        c.circle(cx - 25 + lx, ey, 8, INK, w=0)
        c.circle(cx + 25 + lx, ey, 8, INK, w=0)
    if expr in ("worried", "shock"):
        c.line([(cx - 40, cy - 28), (cx - 14, cy - 36)], INK, 4)
        c.line([(cx + 14, cy - 36), (cx + 40, cy - 28)], INK, 4)
    else:
        c.line([(cx - 40, cy - 30), (cx - 14, cy - 30)], INK, 4)
        c.line([(cx + 14, cy - 30), (cx + 40, cy - 30)], INK, 4)
    my = cy + 34
    if expr == "smile":
        c.line([(cx - 20, my - 4), (cx, my + 6), (cx + 20, my - 4)], INK, 5)
    elif expr == "shock":
        c.ellipse(cx - 12, my - 8, cx + 12, my + 16, (90, 40, 40), w=4)
    elif expr == "worried":
        c.line([(cx - 16, my + 4), (cx, my - 2), (cx + 16, my + 4)], INK, 4)
    else:
        c.line([(cx - 14, my), (cx + 14, my)], INK, 4)


def artyom(pose="stand", expr="neutral", look=0, blink=False, arm="down", res=1):
    c = Canvas(-240, -800, 480, 820, ss=2 * res)
    if pose == "sit":
        c.poly([(-150, -40), (150, -40), (130, 0), (-130, 0)], JEANS)
        c.ellipse(-170, -50, -110, -6, SHOE)
        c.ellipse(110, -50, 170, -6, SHOE)
        top = 256
    else:
        c.poly([(-64, -310), (-6, -310), (-12, -26), (-58, -26)], JEANS)
        c.poly([(6, -310), (64, -310), (58, -26), (12, -26)], JEANS)
        c.ellipse(-80, -40, -4, -2, SHOE)
        c.ellipse(4, -40, 80, -2, SHOE)
        top = 0
    oy = top  # смещение верхней части
    if arm == "out":
        c.poly([(96, oy - 556), (130, oy - 536), (210, oy - 450), (186, oy - 424)], HOODIE)
        c.circle(204, oy - 430, 22, SKIN)
    elif arm == "hug":
        c.poly([(96, oy - 556), (136, oy - 536), (200, oy - 380), (170, oy - 360)], HOODIE)
        c.circle(196, oy - 360, 22, SKIN)
    else:
        c.poly([(96, oy - 556), (136, oy - 536), (150, oy - 330), (116, oy - 324)], HOODIE)
        c.circle(133, oy - 312, 22, SKIN)
    c.poly([(-96, oy - 556), (-136, oy - 536), (-150, oy - 330), (-116, oy - 324)], HOODIE)
    c.circle(-133, oy - 312, 22, SKIN)
    c.poly([(-104, oy - 566), (104, oy - 566), (116, oy - 296), (-116, oy - 296)], HOODIE)
    c.rect(-116, oy - 334, 116, oy - 296, HOODIE_D, w=6)
    if pose != "back":
        c.poly([(-50, oy - 470), (50, oy - 470), (56, oy - 380), (-56, oy - 380)], HOODIE_D, w=4)  # карман
        c.line([(-22, oy - 566), (-26, oy - 500)], (220, 220, 220), 4)
        c.line([(22, oy - 566), (26, oy - 500)], (220, 220, 220), 4)
    c.poly([(-80, oy - 590), (80, oy - 590), (70, oy - 548), (-70, oy - 548)], HOODIE_D, w=5)
    c.rect(-22, oy - 600, 22, oy - 560, SKIN, w=5)
    if pose == "back":
        c.ellipse(-82, oy - 740, 82, oy - 594, HAIR)
        c.ellipse(-92, oy - 670, -72, oy - 634, SKIN, w=4)
        c.ellipse(72, oy - 670, 92, oy - 634, SKIN, w=4)
    else:
        _face_artyom(c, 0, oy - 660, expr, look, blink)
    return c.done(scale=res)


def sonya(pose="stand", arms="down", blink=False, look=0, expr="smile", flower=True, petal=0.0, res=1):
    c = Canvas(-200, -520, 400, 540, ss=2 * res)
    c.rect(-38, -130, -10, -26, TIGHTS, w=5)
    c.rect(10, -130, 38, -26, TIGHTS, w=5)
    c.ellipse(-56, -44, -4, -4, SON_SHOE)
    c.ellipse(4, -44, 56, -4, SON_SHOE)
    # руки
    if arms == "out":       # протягивает цветок влево
        c.poly([(-48, -300), (-70, -280), (-170, -270), (-168, -300)], SON_TOP)
        c.circle(-176, -286, 15, SKIN)
        if flower:
            dandelion(c, -186, -420, 1.05)
    if arms == "up":        # рисует на стене (вид со спины)
        c.poly([(48, -300), (74, -292), (130, -440), (104, -452)], SON_TOP)
        c.circle(120, -456, 15, SKIN)
        c.rect(112, -490, 126, -462, (250, 250, 250), w=3)
    if arms in ("down", "up"):
        c.poly([(-48, -310), (-74, -294), (-88, -180), (-62, -176)], SON_TOP)
        c.circle(-76, -166, 15, SKIN)
    if arms in ("down", "out"):
        c.poly([(48, -310), (74, -294), (88, -180), (62, -176)], SON_TOP)
        c.circle(76, -166, 15, SKIN)
    # кофта + юбка
    c.poly([(-56, -320), (56, -320), (70, -200), (-70, -200)], SON_TOP)
    c.poly([(-70, -210), (70, -210), (94, -126), (-94, -126)], SON_TOP_D)
    if arms == "hold":
        c.poly([(-48, -310), (-74, -290), (-30, -232), (-12, -250)], SON_TOP)
        c.poly([(48, -310), (74, -290), (30, -232), (12, -250)], SON_TOP)
        if flower:
            dandelion(c, 0, -296, 0.95)
        c.circle(-14, -240, 15, SKIN)
        c.circle(14, -240, 15, SKIN)
    # голова
    hy = -390
    if pose == "back":
        c.circle(-74, hy - 10, 26, SON_HAIR)
        c.circle(74, hy - 10, 26, SON_HAIR)
        c.ellipse(-62, hy - 70, 62, hy + 60, SON_HAIR)
        c.circle(-60, hy - 10, 8, SON_TOP_D, w=3)
        c.circle(60, hy - 10, 8, SON_TOP_D, w=3)
        return c.done(scale=res)
    c.circle(-78, hy + 6, 28, SON_HAIR)
    c.circle(78, hy + 6, 28, SON_HAIR)
    c.circle(-58, hy - 6, 9, SON_TOP_D, w=3)
    c.circle(58, hy - 6, 9, SON_TOP_D, w=3)
    c.ellipse(-62, hy - 70, 62, hy + 58, SKIN)
    c.poly([(-64, hy - 6), (-56, hy - 56), (-10, hy - 78), (40, hy - 72), (64, hy - 30), (62, hy - 4), (40, hy - 34),
            (10, hy - 26), (-20, hy - 40), (-50, hy - 16)], SON_HAIR, w=4)
    ey = hy + 4
    lx = 5 * look
    if blink:
        c.line([(-32, ey), (-12, ey)], INK, 4)
        c.line([(12, ey), (32, ey)], INK, 4)
    else:
        c.circle(-22 + lx, ey, 10, INK, w=0)
        c.circle(22 + lx, ey, 10, INK, w=0)
        c.circle(-19 + lx, ey - 4, 3, (255, 255, 255), w=0)
        c.circle(25 + lx, ey - 4, 3, (255, 255, 255), w=0)
    c.circle(-38, hy + 26, 9, BLUSH, w=0)
    c.circle(38, hy + 26, 9, BLUSH, w=0)
    if expr == "smile":
        c.line([(-12, hy + 30), (0, hy + 38), (12, hy + 30)], INK, 4)
    else:
        c.line([(-8, hy + 36), (0, hy + 32), (8, hy + 36)], INK, 3)
    return c.done(scale=res)


def cow():
    c = Canvas(-300, -420, 600, 440)
    for x in (-150, -90, 100, 160):
        c.rect(x - 16, -160, x + 16, -20, (240, 236, 228), w=5)
        c.rect(x - 18, -30, x + 18, -4, (60, 50, 50), w=4)
    c.ellipse(-200, -330, 220, -130, (240, 236, 228))
    c.ellipse(-120, -320, -20, -230, (50, 44, 48), w=0)
    c.ellipse(40, -260, 150, -170, (50, 44, 48), w=0)
    c.ellipse(-200, -330, 220, -130, None)
    c.line([(214, -260), (250, -170)], INK, 6)
    c.ellipse(-300, -380, -170, -230, (240, 236, 228))
    c.ellipse(-300, -300, -210, -236, (240, 170, 170))
    c.circle(-280, -268, 6, INK, w=0)
    c.circle(-240, -268, 6, INK, w=0)
    c.circle(-262, -336, 8, INK, w=0)
    c.circle(-212, -336, 8, INK, w=0)
    c.line([(-276, -352), (-250, -348)], INK, 4)
    c.poly([(-290, -372), (-320, -400), (-280, -386)], (230, 220, 190), w=4)
    c.poly([(-190, -372), (-160, -400), (-196, -386)], (230, 220, 190), w=4)
    return c.done()
