"""Персонажи и предметы для ролика «Вулкан в метро». Все спрайты: якорь — низ по центру (0,0)."""
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from core import *  # noqa

SKIN = (238, 200, 174)
HAIR = (44, 34, 40)
JACKET = (84, 108, 142)
JACKET_D = (62, 80, 108)
JEANS = (40, 50, 82)
SHOE = (30, 30, 38)
YEL = (246, 196, 46)
YEL_D = (214, 160, 30)
GHAIR = (124, 76, 42)
BOOT = (200, 60, 50)
TIGHTS = (62, 52, 74)
BLUSH = (240, 150, 140)


def pale(c, t=0.55):
    g = int(sum(c) / 3)
    return mix(c, (g + 30, g + 40, g + 55), t)


def _pal(ghost):
    names = dict(SKIN=SKIN, HAIR=HAIR, JACKET=JACKET, JACKET_D=JACKET_D, JEANS=JEANS, SHOE=SHOE,
                 YEL=YEL, YEL_D=YEL_D, GHAIR=GHAIR, BOOT=BOOT, TIGHTS=TIGHTS, BLUSH=BLUSH)
    if ghost:
        names = {k: pale(v) for k, v in names.items()}
    return names


# ------------------------------------------------------------------ adult
def adult(view="front", blink=False, ghost=False, worried=True, arm_out=False):
    p = _pal(ghost)
    c = Canvas(-210, -740, 420, 760)
    # ноги
    c.poly([(-64, -310), (-6, -310), (-12, -26), (-58, -26)], p["JEANS"])
    c.poly([(6, -310), (64, -310), (58, -26), (12, -26)], p["JEANS"])
    c.ellipse(-78, -40, -4, -2, p["SHOE"])
    c.ellipse(4, -40, 78, -2, p["SHOE"])
    # руки
    if arm_out:
        c.poly([(96, -556), (128, -536), (196, -420), (170, -400)], p["JACKET"])
        c.circle(186, -398, 21, p["SKIN"])
    else:
        c.poly([(96, -556), (136, -536), (150, -330), (116, -324)], p["JACKET"])
        c.circle(133, -312, 21, p["SKIN"])
    c.poly([(-96, -556), (-136, -536), (-150, -330), (-116, -324)], p["JACKET"])
    c.circle(-133, -312, 21, p["SKIN"])
    # куртка
    c.poly([(-102, -566), (102, -566), (114, -296), (-114, -296)], p["JACKET"])
    c.rect(-114, -330, 114, -296, p["JACKET_D"], w=6)
    if view == "front":
        c.line([(0, -560), (0, -300)], p["JACKET_D"], 5)
        c.poly([(-40, -570), (0, -520), (40, -570)], p["JACKET_D"], w=5)
    else:
        c.poly([(-70, -580), (70, -580), (60, -540), (-60, -540)], p["JACKET_D"], w=5)  # капюшон
    # шея и голова
    c.rect(-22, -590, 22, -556, p["SKIN"], w=5)
    if view == "front":
        c.ellipse(-80, -728, 80, -596, p["HAIR"])
        c.ellipse(-68, -704, 68, -570, p["SKIN"])
        c.poly([(-74, -672), (-50, -712), (0, -722), (50, -712), (74, -672), (66, -646), (40, -666), (12, -650), (-18, -668), (-46, -648), (-70, -638)], p["HAIR"], w=5)
        ey = -626
        if blink:
            c.line([(-34, ey), (-16, ey)], INK, 5)
            c.line([(16, ey), (34, ey)], INK, 5)
        else:
            c.circle(-25, ey, 8, INK, w=0)
            c.circle(25, ey, 8, INK, w=0)
        if worried:
            c.line([(-38, -650), (-14, -656)], INK, 4)
            c.line([(14, -656), (38, -650)], INK, 4)
            c.line([(-14, -592), (0, -596), (14, -592)], INK, 4)
        else:
            c.line([(-14, -594), (14, -594)], INK, 4)
    else:
        c.ellipse(-80, -730, 80, -584, p["HAIR"])
        c.ellipse(-90, -656, -70, -620, p["SKIN"], w=4)
        c.ellipse(70, -656, 90, -620, p["SKIN"], w=4)
    return c.done()


# ------------------------------------------------------------------ girl
def girl(view="front", blink=False, ghost=False, hand_up=False):
    p = _pal(ghost)
    c = Canvas(-150, -490, 300, 510)
    c.rect(-40, -120, -10, -24, p["TIGHTS"], w=5)
    c.rect(10, -120, 40, -24, p["TIGHTS"], w=5)
    c.ellipse(-56, -44, -4, -2, p["BOOT"])
    c.ellipse(4, -44, 56, -2, p["BOOT"])
    # рукава
    if hand_up:
        c.poly([(-50, -318), (-78, -300), (-128, -400), (-104, -414)], p["YEL"])
        c.circle(-120, -420, 15, p["SKIN"])
    else:
        c.poly([(-50, -318), (-80, -300), (-96, -170), (-70, -166)], p["YEL"])
        c.circle(-84, -156, 15, p["SKIN"])
    c.poly([(50, -318), (80, -300), (96, -170), (70, -166)], p["YEL"])
    c.circle(84, -156, 15, p["SKIN"])
    # плащ
    c.poly([(-58, -330), (58, -330), (100, -104), (-100, -104)], p["YEL"])
    if view == "front":
        c.line([(0, -326), (0, -108)], p["YEL_D"], 4)
        for yy in (-290, -240, -190, -140):
            c.circle(-14, yy, 6, p["YEL_D"], w=3)
        # голова в капюшоне
        c.circle(0, -380, 80, p["YEL"])
        c.ellipse(-56, -440, 56, -318, p["SKIN"])
        c.poly([(-58, -420), (58, -420), (54, -392), (20, -404), (-14, -390), (-56, -384)], p["GHAIR"], w=4)
        c.poly([(-56, -400), (-46, -340), (-60, -350)], p["GHAIR"], w=3)
        c.poly([(56, -400), (46, -340), (60, -350)], p["GHAIR"], w=3)
        ey = -372
        if blink:
            c.line([(-30, ey), (-12, ey)], INK, 4)
            c.line([(12, ey), (30, ey)], INK, 4)
        else:
            c.circle(-21, ey, 10, INK, w=0)
            c.circle(21, ey, 10, INK, w=0)
            c.circle(-18, ey - 4, 3, (255, 255, 255), w=0)
            c.circle(24, ey - 4, 3, (255, 255, 255), w=0)
        c.circle(-36, -350, 9, p["BLUSH"], w=0)
        c.circle(36, -350, 9, p["BLUSH"], w=0)
        c.line([(-8, -340), (0, -344), (8, -340)], INK, 3)
    else:
        c.circle(0, -380, 80, p["YEL"])
        c.line([(-50, -420), (0, -456), (50, -420)], p["YEL_D"], 4)
    return c.done()


# ------------------------------------------------------------------ rescuer
def rescuer(view="front", lamp_on=True):
    c = Canvas(-220, -780, 440, 800)
    suit = (150, 92, 46)
    suit_d = (112, 66, 32)
    c.poly([(-70, -320), (-8, -320), (-14, -28), (-62, -28)], suit_d)
    c.poly([(8, -320), (70, -320), (62, -28), (14, -28)], suit_d)
    c.ellipse(-84, -44, -2, -2, (26, 26, 30))
    c.ellipse(2, -44, 84, -2, (26, 26, 30))
    c.poly([(-108, -580), (108, -580), (120, -300), (-120, -300)], suit)
    c.rect(-120, -360, 120, -330, (210, 210, 90), w=5)  # светоотражающая полоса
    c.poly([(-104, -570), (-146, -548), (-160, -330), (-124, -322)], suit)
    c.poly([(104, -570), (146, -548), (160, -330), (124, -322)], suit)
    c.rect(-34, -612, 34, -576, (60, 60, 66), w=5)
    if view == "front":
        c.ellipse(-80, -740, 80, -592, (70, 72, 80))          # маска
        c.circle(-32, -676, 24, (150, 170, 180))
        c.circle(32, -676, 24, (150, 170, 180))
        c.circle(-38, -684, 8, (230, 240, 245), w=0)
        c.circle(26, -684, 8, (230, 240, 245), w=0)
        c.ellipse(-26, -630, 26, -580, (46, 46, 52))           # фильтр
        c.line([(-16, -606), (16, -606)], (90, 90, 96), 4)
    else:
        c.ellipse(-80, -740, 80, -592, (46, 46, 54))
        c.line([(60, -640), (110, -560), (100, -480)], (40, 40, 46), 12)
    c.poly([(-92, -716), (92, -716), (80, -770), (0, -790), (-80, -770)], (220, 196, 60))  # каска
    c.rect(-96, -726, 96, -706, (196, 170, 44), w=5)
    if view == "front":
        c.circle(0, -752, 16, (255, 250, 220) if lamp_on else (90, 90, 80), w=4)
    return c.done()


def leader():
    """Спокойный человек с фонарём (совет 3)."""
    c = Canvas(-230, -760, 460, 780)
    coat = (64, 98, 78)
    c.poly([(-64, -300), (-6, -300), (-12, -26), (-58, -26)], (46, 44, 52))
    c.poly([(6, -300), (64, -300), (58, -26), (12, -26)], (46, 44, 52))
    c.ellipse(-78, -40, -4, -2, SHOE)
    c.ellipse(4, -40, 78, -2, SHOE)
    c.poly([(-102, -566), (102, -566), (122, -250), (-122, -250)], coat)
    c.line([(0, -560), (0, -256)], (44, 72, 56), 5)
    c.poly([(-96, -556), (-136, -536), (-150, -330), (-116, -324)], coat)
    c.circle(-133, -312, 21, SKIN)
    # поднятая рука с фонарём
    c.poly([(96, -556), (134, -540), (200, -560), (190, -592)], coat)
    c.circle(204, -580, 21, SKIN)
    c.line([(204, -560), (204, -520)], INK, 5)
    c.rect(180, -520, 228, -450, (255, 214, 120), w=6, r=8)
    c.rect(176, -530, 232, -516, (60, 56, 50), w=5)
    c.rect(-22, -590, 22, -556, SKIN, w=5)
    c.ellipse(-78, -726, 78, -600, (150, 150, 156))  # седые волосы
    c.ellipse(-66, -704, 66, -572, SKIN)
    c.poly([(-70, -690), (70, -690), (64, -660), (-64, -660)], (150, 150, 156), w=5)
    c.line([(-34, -628), (-16, -628)], INK, 5)  # спокойные прикрытые глаза
    c.line([(16, -628), (34, -628)], INK, 5)
    c.line([(-12, -594), (0, -590), (12, -594)], INK, 4)
    c.poly([(-36, -606), (36, -606), (30, -570), (0, -556), (-30, -570)], (150, 150, 156), w=4)  # борода
    return c.done()


def silhouette(d, x, yf, h, col, panic=0.0, ph=0.0, arms_up=False):
    """Упрощённая фигура-прохожий, рисуется покадрово."""
    hr = h * 0.085
    sw = math.sin(ph) * 0.12 * h
    d.ellipse([x - hr, yf - h * 0.98, x + hr, yf - h * 0.98 + 2 * hr], fill=col)
    d.polygon([(x - h * 0.14, yf - h * 0.8), (x + h * 0.14, yf - h * 0.8),
               (x + h * 0.16, yf - h * 0.42), (x - h * 0.16, yf - h * 0.42)], fill=col)
    lw = max(3, int(h * 0.07))
    d.line([(x - h * 0.06, yf - h * 0.44), (x - h * 0.06 + sw, yf)], fill=col, width=lw)
    d.line([(x + h * 0.06, yf - h * 0.44), (x + h * 0.06 - sw, yf)], fill=col, width=lw)
    up = arms_up or panic > 0.5
    a = math.sin(ph * 1.7) * 0.08 * h
    if up:
        d.line([(x - h * 0.13, yf - h * 0.78), (x - h * 0.24, yf - h * 1.06 + a)], fill=col, width=lw)
        d.line([(x + h * 0.13, yf - h * 0.78), (x + h * 0.24, yf - h * 1.06 - a)], fill=col, width=lw)
    else:
        d.line([(x - h * 0.14, yf - h * 0.78), (x - h * 0.2 - sw * 0.4, yf - h * 0.45)], fill=col, width=lw)
        d.line([(x + h * 0.14, yf - h * 0.78), (x + h * 0.2 + sw * 0.4, yf - h * 0.45)], fill=col, width=lw)
