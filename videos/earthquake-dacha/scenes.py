"""Flat 2D illustrations for «Если землетрясение застало вас на даче».

Style: files/style-01-time-loop-drama.md — thick dark outline, flat fills,
paper grain, vignette, night palette (navy / graphite / dirty violet) with a
single warm light source. Hero («ты») wears cold blue-grey, the stranger
woman wears mustard yellow, a background stranger wears a red jacket.

Every scene is drawn on a 1080x1920 canvas and returned as an SVG string.
"""
import math
import random

W, H = 1080, 1920
OUT = "#17162a"   # outline
SW = 7            # outline width

# palette
NIGHT_SKY = "#1b2140"
NIGHT_SKY2 = "#2b2a52"
VIOLET = "#3a3159"
GROUND = "#202838"
GRASS = "#1d3236"
WOOD = "#5b4434"
WOOD_D = "#3f2f27"
ROOF = "#3b2d43"
WARM = "#ffcf6b"
WARM2 = "#ffb347"
SKIN = "#f1c7a5"
HERO_TOP = "#5f7d9c"
HERO_JEANS = "#2a3a5c"
HAIR_D = "#1e1b22"
MUSTARD = "#d9a52b"
HAIR_B = "#6b3f26"
RED = "#c43b33"
GREY = "#6c6f80"
DAWN_SKY = "#8fa7bd"
DAWN_SKY2 = "#b9c6cf"
PANEL = "#7d8794"


def wrap(body, bg=NIGHT_SKY, vignette=0.75, grain=0.10):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <radialGradient id="vig" cx="50%" cy="48%" r="75%">
    <stop offset="55%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#05040c" stop-opacity="{vignette}"/>
  </radialGradient>
  <radialGradient id="glow">
    <stop offset="0%" stop-color="{WARM}" stop-opacity="0.75"/>
    <stop offset="45%" stop-color="{WARM2}" stop-opacity="0.25"/>
    <stop offset="100%" stop-color="{WARM2}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="coldglow">
    <stop offset="0%" stop-color="#cfe3ff" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="#cfe3ff" stop-opacity="0"/>
  </radialGradient>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
</defs>
<rect width="{W}" height="{H}" fill="{bg}"/>
{body}
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{grain}" style="mix-blend-mode:overlay"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</svg>'''


def o(extra=""):
    return f'stroke="{OUT}" stroke-width="{SW}" stroke-linejoin="round" stroke-linecap="round" {extra}'


def glow(x, y, r, cold=False, op=1.0):
    g = "coldglow" if cold else "glow"
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{g})" opacity="{op}"/>'


def stars(n=40, seed=1, ymax=900):
    rnd = random.Random(seed)
    s = []
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, ymax)
        r = rnd.choice([1.5, 2, 2.5, 3])
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#e8e4ff" opacity="{rnd.uniform(.3,.9):.2f}"/>')
    return "".join(s)


def moon(x, y, r=55):
    return (glow(x, y, r * 3, cold=True, op=0.6)
            + f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e9e4cf" {o()}/>'
            + f'<circle cx="{x-15}" cy="{y-10}" r="{r*0.18}" fill="#d3ccb2"/>'
            + f'<circle cx="{x+18}" cy="{y+16}" r="{r*0.12}" fill="#d3ccb2"/>')


def hills(y, color=VIOLET, seed=3):
    rnd = random.Random(seed)
    pts = [f"0,{y}"]
    for i in range(0, W + 120, 120):
        pts.append(f"{i},{y - rnd.uniform(20, 90):.0f}")
    pts += [f"{W},{H}", f"0,{H}"]
    return f'<polygon points="{" ".join(pts)}" fill="{color}"/>'


def trees(y, n=7, seed=5, color="#141c2a"):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x = rnd.uniform(-40, W + 40)
        h = rnd.uniform(160, 300)
        w = h * 0.38
        out.append(f'<polygon points="{x},{y-h} {x-w},{y} {x+w},{y}" fill="{color}"/>')
    return "".join(out)


def crack(points, width=6, color=OUT):
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>'


def zigzag(x, y, length, angle, seed=1, segs=6, spread=22):
    rnd = random.Random(seed)
    pts = [(x, y)]
    for i in range(1, segs + 1):
        t = length * i / segs
        dx = math.cos(angle) * t + rnd.uniform(-spread, spread)
        dy = math.sin(angle) * t + rnd.uniform(-spread, spread)
        pts.append((round(x + dx), round(y + dy)))
    return pts


# ---------------------------------------------------------------- props

def house(x, y, s=1.0, lit=True, cracked=False, tilt=0, broken=False):
    """Wooden dacha house; (x,y) = bottom centre."""
    w, h = 420 * s, 300 * s
    l, t = x - w / 2, y - h
    win = WARM if lit else "#2c3150"
    parts = [f'<g transform="rotate({tilt} {x} {y})">']
    # chimney
    parts.append(f'<rect x="{x+w*0.18}" y="{t-h*0.62}" width="{w*0.09}" height="{h*0.4}" fill="#4b3a3a" {o()}/>')
    # roof
    parts.append(f'<polygon points="{l-30*s},{t} {x},{t-h*0.6} {l+w+30*s},{t}" fill="{ROOF}" {o()}/>')
    # body
    parts.append(f'<rect x="{l}" y="{t}" width="{w}" height="{h}" fill="{WOOD}" {o()}/>')
    for i in range(1, 6):
        yy = t + h * i / 6
        parts.append(f'<line x1="{l+6}" y1="{yy}" x2="{l+w-6}" y2="{yy}" stroke="{WOOD_D}" stroke-width="4"/>')
    # windows
    for wx in (l + w * 0.12, l + w * 0.62):
        parts.append(f'<rect x="{wx}" y="{t+h*0.22}" width="{w*0.26}" height="{h*0.3}" fill="{win}" {o()}/>')
        parts.append(f'<line x1="{wx+w*0.13}" y1="{t+h*0.22}" x2="{wx+w*0.13}" y2="{t+h*0.52}" stroke="{OUT}" stroke-width="5"/>')
        if lit:
            parts.append(glow(wx + w * 0.13, t + h * 0.37, 110 * s, op=0.55))
    # door
    parts.append(f'<rect x="{x-w*0.07}" y="{t+h*0.55}" width="{w*0.16}" height="{h*0.45}" fill="{WOOD_D}" {o()}/>')
    # porch step
    parts.append(f'<rect x="{x-w*0.12}" y="{y-8*s}" width="{w*0.26}" height="{16*s}" fill="#4a3b33" {o()}/>')
    if cracked or broken:
        parts.append(crack(zigzag(l + w * 0.45, t + 4, h * 0.95, math.pi / 2.2, seed=11), 7))
        parts.append(crack(zigzag(l + w * 0.85, t + 10, h * 0.6, math.pi / 1.7, seed=12), 6))
        parts.append(crack(zigzag(l + w * 0.1, t + h * 0.15, h * 0.5, math.pi / 2.5, seed=13), 5))
    if broken:
        # caved-in roof corner + rubble
        parts.append(f'<polygon points="{x+20*s},{t-h*0.45} {l+w+40*s},{t+h*0.25} {l+w*0.55},{t+h*0.1}" fill="{NIGHT_SKY}"/>')
        rnd = random.Random(9)
        for _ in range(9):
            rx = rnd.uniform(l + w * 0.5, l + w + 60 * s)
            ry = y - rnd.uniform(0, 30) * s
            rs = rnd.uniform(18, 40) * s
            parts.append(f'<rect x="{rx}" y="{ry-rs}" width="{rs*1.4}" height="{rs}" fill="{WOOD_D}" transform="rotate({rnd.uniform(-30,30):.0f} {rx} {ry})" {o()}/>')
    parts.append("</g>")
    return "".join(parts)


def fence(y, x0=-20, x1=W + 20, h=150, color="#4e4038", gap=None):
    out = [f'<rect x="{x0}" y="{y-h*0.75}" width="{x1-x0}" height="16" fill="{WOOD_D}" {o()}/>',
           f'<rect x="{x0}" y="{y-h*0.3}" width="{x1-x0}" height="16" fill="{WOOD_D}" {o()}/>']
    x = x0
    while x < x1:
        if not (gap and gap[0] < x < gap[1]):
            out.append(f'<polygon points="{x},{y} {x},{y-h} {x+20},{y-h-22} {x+40},{y-h} {x+40},{y}" fill="{color}" {o()}/>')
        x += 58
    return "".join(out)


def bucket(x, y, s=1, color="#7f8fa3"):
    return (f'<polygon points="{x-40*s},{y-80*s} {x+40*s},{y-80*s} {x+30*s},{y} {x-30*s},{y}" fill="{color}" {o()}/>'
            f'<path d="M{x-38*s},{y-80*s} Q{x},{y-150*s} {x+38*s},{y-80*s}" fill="none" {o()}/>')


def jar(x, y, s=1, fill="#c85a3c", tilt=0):
    return (f'<g transform="rotate({tilt} {x} {y})">'
            f'<rect x="{x-32*s}" y="{y-90*s}" width="{64*s}" height="{90*s}" rx="{14*s}" fill="#bcd3dc" {o()}/>'
            f'<rect x="{x-26*s}" y="{y-60*s}" width="{52*s}" height="{55*s}" rx="{8*s}" fill="{fill}"/>'
            f'<rect x="{x-36*s}" y="{y-104*s}" width="{72*s}" height="{18*s}" fill="#d9b25a" {o()}/></g>')


def bottle(x, y, s=1, tilt=0):
    return (f'<g transform="rotate({tilt} {x} {y})">'
            f'<rect x="{x-26*s}" y="{y-120*s}" width="{52*s}" height="{120*s}" rx="{14*s}" fill="#8fc3e0" {o()}/>'
            f'<rect x="{x-12*s}" y="{y-146*s}" width="{24*s}" height="{28*s}" fill="#3d6fb4" {o()}/>'
            f'<rect x="{x-22*s}" y="{y-80*s}" width="{44*s}" height="{30*s}" fill="#e6f2fa"/></g>')


def canister(x, y, s=1, color=RED, level=None):
    out = [f'<path d="M{x-70*s},{y} L{x-70*s},{y-150*s} L{x-30*s},{y-190*s} L{x+70*s},{y-190*s} L{x+70*s},{y} Z" fill="{color}" {o()}/>',
           f'<rect x="{x+10*s}" y="{y-225*s}" width="{34*s}" height="{36*s}" fill="#2b2b2b" {o()}/>',
           f'<path d="M{x-40*s},{y-30*s} L{x+40*s},{y-150*s} M{x-40*s},{y-150*s} L{x+40*s},{y-30*s}" stroke="#00000044" stroke-width="{10*s}"/>']
    if level is not None:
        out.append(f'<rect x="{x+90*s}" y="{y-190*s}" width="{34*s}" height="{190*s}" fill="#1f2433" {o()}/>')
        out.append(f'<rect x="{x+96*s}" y="{y-190*s*level}" width="{22*s}" height="{190*s*level-6*s}" fill="{RED}"/>')
    return "".join(out)


def firstaid(x, y, s=1):
    return (f'<rect x="{x-90*s}" y="{y-120*s}" width="{180*s}" height="{120*s}" rx="{14*s}" fill="#e8e3d6" {o()}/>'
            f'<rect x="{x-14*s}" y="{y-100*s}" width="{28*s}" height="{80*s}" fill="{RED}"/>'
            f'<rect x="{x-40*s}" y="{y-74*s}" width="{80*s}" height="{28*s}" fill="{RED}"/>')


def backpack(x, y, s=1, color=HERO_TOP):
    return (f'<rect x="{x-80*s}" y="{y-200*s}" width="{160*s}" height="{200*s}" rx="{40*s}" fill="{color}" {o()}/>'
            f'<rect x="{x-55*s}" y="{y-95*s}" width="{110*s}" height="{70*s}" rx="{16*s}" fill="#4b6683" {o()}/>'
            f'<path d="M{x-40*s},{y-200*s} Q{x},{y-260*s} {x+40*s},{y-200*s}" fill="none" {o()}/>')


def axe(x, y, s=1, rot=0):
    return (f'<g transform="rotate({rot} {x} {y})">'
            f'<rect x="{x-10*s}" y="{y-260*s}" width="{20*s}" height="{260*s}" rx="6" fill="#a8743f" {o()}/>'
            f'<path d="M{x-10*s},{y-250*s} L{x-80*s},{y-275*s} L{x-70*s},{y-185*s} L{x-10*s},{y-205*s} Z" fill="#9aa5b1" {o()}/></g>')


def crowbar(x, y, s=1, rot=0):
    return (f'<g transform="rotate({rot} {x} {y})">'
            f'<path d="M{x},{y} L{x},{y-300*s} Q{x},{y-340*s} {x+40*s},{y-335*s}" fill="none" stroke="{OUT}" stroke-width="{30*s}" stroke-linecap="round"/>'
            f'<path d="M{x},{y} L{x},{y-300*s} Q{x},{y-340*s} {x+40*s},{y-335*s}" fill="none" stroke="#b33a32" stroke-width="{16*s}" stroke-linecap="round"/></g>')


def flashlight(x, y, s=1, rot=0, beam=True):
    out = [f'<g transform="rotate({rot} {x} {y})">']
    if beam:
        out.append(f'<polygon points="{x+60*s},{y-30*s} {x+520*s},{y-180*s} {x+520*s},{y+180*s} {x+60*s},{y+30*s}" fill="{WARM}" opacity="0.22"/>')
    out.append(f'<rect x="{x-90*s}" y="{y-22*s}" width="{120*s}" height="{44*s}" rx="10" fill="#33415c" {o()}/>')
    out.append(f'<polygon points="{x+30*s},{y-22*s} {x+64*s},{y-38*s} {x+64*s},{y+38*s} {x+30*s},{y+22*s}" fill="#4d5f80" {o()}/>')
    out.append(f'<rect x="{x+60*s}" y="{y-36*s}" width="{10*s}" height="{72*s}" fill="{WARM}"/></g>')
    return "".join(out)


def stove(x, y, s=1, fire=True):
    out = []
    if fire:
        out.append(glow(x, y - 150 * s, 420 * s, op=0.9))
    out.append(f'<rect x="{x-20*s}" y="{y-620*s}" width="{40*s}" height="{340*s}" fill="#3a3a44" {o()}/>')
    out.append(f'<rect x="{x-130*s}" y="{y-290*s}" width="{260*s}" height="{290*s}" rx="{18*s}" fill="#2e2f3a" {o()}/>')
    out.append(f'<rect x="{x-80*s}" y="{y-210*s}" width="{160*s}" height="{120*s}" rx="{10*s}" fill="{"#ff9a3c" if fire else "#1a1a22"}" {o()}/>')
    if fire:
        out.append(f'<path d="M{x-50*s},{y-95*s} Q{x-40*s},{y-170*s} {x-10*s},{y-150*s} Q{x},{y-205*s} {x+25*s},{y-150*s} Q{x+50*s},{y-175*s} {x+50*s},{y-95*s} Z" fill="{WARM}"/>')
    out.append(f'<rect x="{x-110*s}" y="{y-20*s}" width="{40*s}" height="{20*s}" fill="{OUT}"/><rect x="{x+70*s}" y="{y-20*s}" width="{40*s}" height="{20*s}" fill="{OUT}"/>')
    return "".join(out)


def wallclock(x, y, r=120, hh=3, mm=17, cracked=False, tilt=0):
    out = [f'<g transform="rotate({tilt} {x} {y})">',
           f'<circle cx="{x}" cy="{y}" r="{r}" fill="#c9a24a" {o()}/>',
           f'<circle cx="{x}" cy="{y}" r="{r*0.84}" fill="#f2e8cf" {o("stroke-width=\'4\'")}/>']
    for i in range(12):
        a = math.radians(i * 30)
        x1, y1 = x + math.sin(a) * r * 0.72, y - math.cos(a) * r * 0.72
        x2, y2 = x + math.sin(a) * r * 0.62, y - math.cos(a) * r * 0.62
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{OUT}" stroke-width="5"/>')
    ah = math.radians((hh % 12 + mm / 60) * 30)
    am = math.radians(mm * 6)
    out.append(f'<line x1="{x}" y1="{y}" x2="{x+math.sin(ah)*r*0.4:.1f}" y2="{y-math.cos(ah)*r*0.4:.1f}" stroke="{OUT}" stroke-width="{r*0.08:.1f}" stroke-linecap="round"/>')
    out.append(f'<line x1="{x}" y1="{y}" x2="{x+math.sin(am)*r*0.62:.1f}" y2="{y-math.cos(am)*r*0.62:.1f}" stroke="{OUT}" stroke-width="{r*0.05:.1f}" stroke-linecap="round"/>')
    out.append(f'<line x1="{x}" y1="{y}" x2="{x+math.sin(am+2.4)*r*0.66:.1f}" y2="{y-math.cos(am+2.4)*r*0.66:.1f}" stroke="{RED}" stroke-width="{r*0.025:.1f}"/>')
    out.append(f'<circle cx="{x}" cy="{y}" r="{r*0.06}" fill="{OUT}"/>')
    if cracked:
        out.append(crack(zigzag(x - r * 0.7, y - r * 0.3, r * 1.3, 0.35, seed=4, segs=5, spread=12), 4))
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- people

PEOPLE = {
    "hero": dict(top=HERO_TOP, legs=HERO_JEANS, hair=HAIR_D, style="short"),
    "woman": dict(top=MUSTARD, legs="#3b3446", hair=HAIR_B, style="bob"),
    "red": dict(top=RED, legs="#2d2d38", hair="#3a2a20", style="short"),
    "grey": dict(top=GREY, legs="#2d2d38", hair="#4a4a55", style="cap"),
}


def person(x, y, s=1.0, who="hero", back=False, arm="down", face="calm", simple=False):
    """Standing figure, (x,y) = feet centre. ~520px tall at s=1."""
    p = PEOPLE[who]
    out = [f'<g transform="translate({x},{y}) scale({s})">']
    # legs
    out.append(f'<rect x="-48" y="-230" width="42" height="230" rx="10" fill="{p["legs"]}" {o()}/>')
    out.append(f'<rect x="6" y="-230" width="42" height="230" rx="10" fill="{p["legs"]}" {o()}/>')
    out.append(f'<rect x="-56" y="-14" width="54" height="22" rx="8" fill="{OUT}"/><rect x="2" y="-14" width="54" height="22" rx="8" fill="{OUT}"/>')
    # arms
    if arm == "down":
        out.append(f'<rect x="-98" y="-410" width="36" height="200" rx="16" fill="{p["top"]}" {o()}/>')
        out.append(f'<rect x="62" y="-410" width="36" height="200" rx="16" fill="{p["top"]}" {o()}/>')
        out.append(f'<circle cx="-80" cy="-205" r="20" fill="{SKIN}" {o()}/><circle cx="80" cy="-205" r="20" fill="{SKIN}" {o()}/>')
    elif arm == "point":
        out.append(f'<rect x="-98" y="-410" width="36" height="200" rx="16" fill="{p["top"]}" {o()}/>')
        out.append(f'<circle cx="-80" cy="-205" r="20" fill="{SKIN}" {o()}/>')
        out.append(f'<rect x="60" y="-405" width="220" height="36" rx="16" fill="{p["top"]}" {o()}/>')
        out.append(f'<circle cx="290" cy="-387" r="20" fill="{SKIN}" {o()}/>')
    elif arm == "watch":
        out.append(f'<rect x="-98" y="-410" width="36" height="200" rx="16" fill="{p["top"]}" {o()}/>')
        out.append(f'<circle cx="-80" cy="-205" r="20" fill="{SKIN}" {o()}/>')
        out.append(f'<path d="M80,-400 L80,-300 L-10,-330" fill="none" stroke="{OUT}" stroke-width="50" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<path d="M80,-400 L80,-300 L-10,-330" fill="none" stroke="{p["top"]}" stroke-width="36" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<circle cx="-25" cy="-332" r="20" fill="{SKIN}" {o()}/><rect x="-6" y="-350" width="24" height="30" rx="4" fill="{WARM}" {o("stroke-width=\'4\'")}/>')
    # torso
    out.append(f'<path d="M-70,-420 Q0,-450 70,-420 L64,-215 L-64,-215 Z" fill="{p["top"]}" {o()}/>')
    if who == "hero" and not back:
        out.append(f'<path d="M-30,-420 Q0,-380 30,-420" fill="none" stroke="{OUT}" stroke-width="5"/>')
        out.append(f'<rect x="-40" y="-300" width="80" height="40" rx="10" fill="#557190" stroke="{OUT}" stroke-width="4"/>')
    if who == "woman":
        out.append(f'<line x1="0" y1="-430" x2="0" y2="-215" stroke="{OUT}" stroke-width="5"/>')
    # head
    out.append(f'<rect x="-18" y="-455" width="36" height="40" fill="{SKIN}" {o()}/>')
    out.append(f'<circle cx="0" cy="-515" r="72" fill="{SKIN}" {o()}/>')
    hair = p["hair"]
    if p["style"] == "short":
        if back:
            out.append(f'<path d="M-72,-505 Q-75,-600 0,-592 Q75,-600 72,-505 Q70,-470 0,-462 Q-70,-470 -72,-505 Z" fill="{hair}" {o()}/>')
        else:
            out.append(f'<path d="M-74,-510 Q-80,-600 0,-594 Q80,-600 74,-510 Q40,-560 -10,-545 Q-40,-560 -74,-510 Z" fill="{hair}" {o()}/>')
    elif p["style"] == "bob":
        if back:
            out.append(f'<path d="M-82,-450 Q-95,-600 0,-596 Q95,-600 82,-450 Z" fill="{hair}" {o()}/>')
        else:
            out.append(f'<path d="M-84,-450 Q-98,-602 0,-598 Q98,-602 84,-450 L60,-450 Q62,-540 0,-548 Q-62,-540 -60,-450 Z" fill="{hair}" {o()}/>')
    else:  # cap
        out.append(f'<path d="M-74,-530 Q-70,-600 0,-600 Q70,-600 74,-530 Z" fill="#3c4250" {o()}/>')
        out.append(f'<rect x="{-10 if back else 10}" y="-540" width="100" height="18" rx="8" fill="#3c4250" {o()}/>')
    if not back and not simple:
        out.append(face_marks(0, -512, 1.0, face))
    out.append("</g>")
    return "".join(out)


def face_marks(cx, cy, k, face):
    e = []
    if face == "scared":
        e.append(f'<circle cx="{cx-26*k}" cy="{cy-4*k}" r="{11*k}" fill="#fff" stroke="{OUT}" stroke-width="{4*k}"/><circle cx="{cx-26*k}" cy="{cy-4*k}" r="{5*k}" fill="{OUT}"/>')
        e.append(f'<circle cx="{cx+26*k}" cy="{cy-4*k}" r="{11*k}" fill="#fff" stroke="{OUT}" stroke-width="{4*k}"/><circle cx="{cx+26*k}" cy="{cy-4*k}" r="{5*k}" fill="{OUT}"/>')
        e.append(f'<ellipse cx="{cx}" cy="{cy+34*k}" rx="{9*k}" ry="{12*k}" fill="{OUT}"/>')
    else:
        e.append(f'<circle cx="{cx-26*k}" cy="{cy}" r="{7*k}" fill="{OUT}"/><circle cx="{cx+26*k}" cy="{cy}" r="{7*k}" fill="{OUT}"/>')
        if face == "tense":
            e.append(f'<line x1="{cx-14*k}" y1="{cy+34*k}" x2="{cx+14*k}" y2="{cy+34*k}" stroke="{OUT}" stroke-width="{5*k}" stroke-linecap="round"/>')
            e.append(f'<line x1="{cx-40*k}" y1="{cy-24*k}" x2="{cx-14*k}" y2="{cy-18*k}" stroke="{OUT}" stroke-width="{5*k}" stroke-linecap="round"/>')
            e.append(f'<line x1="{cx+40*k}" y1="{cy-24*k}" x2="{cx+14*k}" y2="{cy-18*k}" stroke="{OUT}" stroke-width="{5*k}" stroke-linecap="round"/>')
        else:
            e.append(f'<path d="M{cx-14*k},{cy+32*k} Q{cx},{cy+38*k} {cx+14*k},{cy+32*k}" fill="none" stroke="{OUT}" stroke-width="{5*k}" stroke-linecap="round"/>')
    return "".join(e)


def bighead(x, y, k=3.0, who="hero", face="scared", light=None):
    """Close-up head + shoulders; (x,y) = centre of face."""
    p = PEOPLE[who]
    out = [f'<g transform="translate({x},{y}) scale({k})">']
    out.append(f'<path d="M-170,260 Q-160,120 0,110 Q160,120 170,260 L170,400 L-170,400 Z" fill="{p["top"]}" {o()}/>')
    out.append(f'<rect x="-30" y="40" width="60" height="80" fill="{SKIN}" {o()}/>')
    out.append(f'<circle cx="0" cy="0" r="100" fill="{SKIN}" {o()}/>')
    if p["style"] == "short":
        out.append(f'<path d="M-104,-10 Q-112,-135 0,-128 Q112,-135 104,-10 Q60,-80 -10,-62 Q-60,-82 -104,-10 Z" fill="{p["hair"]}" {o()}/>')
    elif p["style"] == "bob":
        out.append(f'<path d="M-116,80 Q-136,-140 0,-134 Q136,-140 116,80 L84,80 Q88,-50 0,-60 Q-88,-50 -84,80 Z" fill="{p["hair"]}" {o()}/>')
    else:
        out.append(f'<path d="M-104,-30 Q-100,-130 0,-130 Q100,-130 104,-30 Z" fill="#3c4250" {o()}/>')
        out.append(f'<rect x="10" y="-44" width="140" height="24" rx="10" fill="#3c4250" {o()}/>')
    out.append(face_marks(0, 8, 1.4, face))
    if light == "warm":
        out.append(f'<path d="M0,-100 A100,100 0 0 1 0,100 Z" fill="{WARM}" opacity="0.18"/>')
    out.append("</g>")
    return "".join(out)


def hand(x, y, s=1.0, rot=0, sleeve=HERO_TOP):
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s})">'
            f'<rect x="-300" y="-55" width="260" height="110" rx="30" fill="{sleeve}" {o()}/>'
            f'<rect x="-60" y="-60" width="40" height="120" rx="14" fill="#557190" {o()}/>'
            f'<path d="M-20,-50 L80,-55 Q110,-50 108,-25 L60,-20 L120,-10 Q140,10 120,25 L60,30 L105,45 Q115,65 90,70 L-20,55 Z" fill="{SKIN}" {o()}/></g>')


# ---------------------------------------------------------------- scenes

def bg_night(seed=1, moonpos=(820, 330)):
    return (f'<rect width="{W}" height="{H*0.55}" fill="{NIGHT_SKY}"/>'
            + stars(45, seed) + (moon(*moonpos) if moonpos else "")
            + hills(1060, VIOLET, seed) + trees(1120, 8, seed + 2))


def ground(y, color=GROUND):
    return f'<rect x="0" y="{y}" width="{W}" height="{H-y}" fill="{color}"/>'


def scene(name):
    return SCENES[name]()


def s_hook_house():
    b = bg_night(1)
    b += ground(1180, GRASS)
    b += house(540, 1380, 1.45, lit=True, cracked=True)
    b += fence(1560, h=130)
    b += crack(zigzag(-10, 1640, 1100, 0.04, seed=21, segs=10, spread=30), 10)
    b += person(250, 1880, 0.55, "hero", back=True)
    return wrap(b)


def s_jars_fall():
    b = f'<rect width="{W}" height="{H}" fill="#2a2440"/>'
    b += glow(540, 600, 700, op=0.7)
    b += f'<line x1="540" y1="0" x2="540" y2="380" stroke="{OUT}" stroke-width="6"/>'
    b += f'<path d="M470,380 L610,380 L580,330 L500,330 Z" fill="#d9a52b" {o()}/>'
    b += glow(540, 420, 260, op=0.9)
    for yy in (900, 1300):
        b += f'<rect x="80" y="{yy}" width="920" height="34" fill="{WOOD}" {o()}/>'
    b += jar(200, 900, 1.2, tilt=-8) + jar(360, 900, 1.2, "#7a3d6b") + jar(820, 900, 1.2, "#5f8a3a", tilt=10)
    b += jar(540, 700, 1.2, tilt=35) + jar(680, 640, 1.2, "#e09a3a", tilt=-40)
    b += jar(250, 1300, 1.2, "#5f8a3a") + jar(900, 1300, 1.2, tilt=6)
    b += jar(560, 1180, 1.2, "#7a3d6b", tilt=70)
    for (cx, cy) in [(520, 1720), (600, 1760), (470, 1780), (660, 1700)]:
        b += f'<polygon points="{cx},{cy} {cx+40},{cy-20} {cx+60},{cy+20}" fill="#bcd3dc" {o("stroke-width=\'4\'")}/>'
    b += f'<rect x="0" y="1800" width="{W}" height="120" fill="#3a3046"/>'
    b += wallclock(860, 1620, 110, 3, 17, cracked=True, tilt=-20)
    return wrap(b)


def s_hero_face():
    b = f'<rect width="{W}" height="{H}" fill="#1f1d36"/>'
    b += glow(330, 650, 600, op=0.8)
    b += bighead(560, 980, 2.6, "hero", "scared", light="warm")
    return wrap(b)


def s_phone():
    b = f'<rect width="{W}" height="{H}" fill="#1a1a30"/>'
    b += glow(540, 900, 600, cold=True, op=0.5)
    b += f'<rect x="300" y="520" width="480" height="900" rx="60" fill="#22232e" {o()}/>'
    b += f'<rect x="330" y="580" width="420" height="780" rx="30" fill="#c8d8e8"/>'
    for i, h in enumerate([30, 50, 70, 90]):
        b += f'<rect x="{430+i*60}" y="{860-h}" width="40" height="{h}" fill="#8e9bb0"/>'
    b += f'<line x1="410" y1="720" x2="680" y2="900" stroke="{RED}" stroke-width="22" stroke-linecap="round"/>'
    b += f'<text x="540" y="1040" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="56" fill="#2a2f40">НЕТ СЕТИ</text>'
    b += f'<text x="540" y="1110" text-anchor="middle" font-family="DejaVu Sans" font-size="36" fill="#55607a">только экстренные</text>'
    b += hand(380, 1500, 1.3, rot=-70)
    return wrap(b)


def s_road_blocked():
    b = (f'<rect width="{W}" height="{H}" fill="{NIGHT_SKY}"/>' + stars(40, 4) + moon(220, 300, 45)
         + hills(980, VIOLET, 4) + trees(1050, 9, 8))
    b += ground(1050, "#262a3c")
    b += f'<polygon points="440,1050 640,1050 1000,1920 80,1920" fill="#3a3a4c"/>'
    b += crack(zigzag(300, 1500, 600, 0.15, seed=31, segs=8, spread=40), 14)
    # fallen tree across the road
    b += f'<g transform="rotate(-8 540 1350)"><rect x="40" y="1310" width="1000" height="80" rx="30" fill="#4a362b" {o()}/></g>'
    for (x, y) in [(860, 1270), (920, 1330), (780, 1300)]:
        b += f'<circle cx="{x}" cy="{y}" r="70" fill="#1f3a30" {o()}/>'
    for (x, y, r) in [(250, 1620, 70), (340, 1660, 50), (700, 1600, 85), (820, 1690, 55)]:
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.7}" fill="#5d5a66" {o()}/>'
    return wrap(b)


def s_strangers_wide():
    b = bg_night(5, moonpos=(160, 280)) + ground(1150, GRASS)
    b += house(220, 1150, 0.6, lit=False) + house(860, 1130, 0.55, lit=True)
    b += person(260, 1560, 0.62, "grey", face="tense")
    b += person(560, 1590, 0.7, "woman", face="tense")
    b += person(830, 1570, 0.66, "red", face="tense")
    b += fence(1640, h=170)
    b += person(540, 2130, 0.75, "hero", back=True)
    return wrap(b)


def s_woman_close():
    b = f'<rect width="{W}" height="{H}" fill="#1b1d38"/>' + stars(30, 9, 700)
    b += glow(760, 600, 550, op=0.55)
    b += bighead(540, 960, 2.5, "woman", "tense", light="warm")
    b += fence(1920, h=520)
    return wrap(b)


def s_gate_wide(open_=False, strangers=False):
    b = bg_night(6) + ground(1250, GRASS)
    b += fence(1400, -20, 330, h=200) + fence(1400, 750, W + 20, h=200)
    b += f'<rect x="320" y="1110" width="40" height="300" fill="{WOOD_D}" {o()}/><rect x="720" y="1110" width="40" height="300" fill="{WOOD_D}" {o()}/>'
    if open_:
        b += f'<polygon points="360,1150 470,1110 470,1440 360,1400" fill="#6a5240" {o()}/>'
        if strangers:
            b += glow(540, 1150, 300, cold=True, op=0.4)
            b += person(560, 1380, 0.5, "red", simple=True)
            b += person(650, 1360, 0.42, "grey", simple=True)
    else:
        b += f'<rect x="360" y="1150" width="360" height="250" fill="#6a5240" {o()}/>'
        for gx in range(380, 720, 50):
            b += f'<line x1="{gx}" y1="1150" x2="{gx}" y2="1400" stroke="{WOOD_D}" stroke-width="5"/>'
        b += f'<rect x="640" y="1250" width="90" height="26" fill="#9aa5b1" {o()}/>'
    b += person(540, 1950, 0.8, "hero", back=True)
    return wrap(b)


def s_gate_latch():
    b = f'<rect width="{W}" height="{H}" fill="#5a4535"/>'
    for gx in range(0, W, 180):
        b += f'<rect x="{gx}" y="0" width="170" height="{H}" fill="#6a5240" {o()}/>'
    b += glow(540, 900, 500, cold=True, op=0.35)
    b += f'<rect x="150" y="880" width="620" height="80" rx="12" fill="#9aa5b1" {o()}/>'
    b += f'<rect x="760" y="830" width="120" height="180" rx="10" fill="#7c8794" {o()}/>'
    b += f'<rect x="420" y="800" width="60" height="100" rx="12" fill="#9aa5b1" {o()}/>'
    b += hand(520, 760, 1.4, rot=20)
    return wrap(b, vignette=0.85)


def s_yard_stuff():
    b = bg_night(7) + ground(1100, GRASS)
    b += house(780, 1150, 0.7, lit=True)
    # garden chair
    b += f'<g transform="rotate(-12 260 1420)"><rect x="160" y="1280" width="200" height="30" fill="#e6e6e6" {o()}/><rect x="160" y="1150" width="30" height="270" fill="#e6e6e6" {o()}/><rect x="330" y="1300" width="30" height="120" fill="#e6e6e6" {o()}/></g>'
    b += bucket(540, 1460, 1.2) + bucket(880, 1560, 1.0, "#3d6fb4")
    b += jar(400, 1680, 1.1) + jar(620, 1700, 1.0, "#5f8a3a", tilt=15)
    b += f'<g transform="rotate(25 300 1800)"><rect x="300" y="1500" width="16" height="320" fill="#a8743f" {o()}/><rect x="250" y="1490" width="120" height="24" fill="#9aa5b1" {o()}/></g>'
    for (x, y) in [(540, 1460), (400, 1680), (880, 1560)]:
        b += f'<circle cx="{x}" cy="{y-70}" r="115" fill="none" stroke="{RED}" stroke-width="8" stroke-dasharray="20 14"/>'
    return wrap(b)


def s_well_water():
    b = bg_night(8, moonpos=(860, 260)) + ground(1150, GRASS)
    b += f'<rect x="120" y="1080" width="300" height="240" fill="#6f6a72" {o()}/>'
    b += f'<rect x="130" y="880" width="24" height="200" fill="{WOOD_D}" {o()}/><rect x="386" y="880" width="24" height="200" fill="{WOOD_D}" {o()}/>'
    b += f'<polygon points="100,890 270,790 440,890" fill="{ROOF}" {o()}/>'
    b += person(620, 1640, 0.8, "hero", face="tense")
    b += bottle(330, 1700, 1.3) + bottle(440, 1720, 1.3, tilt=8) + bottle(860, 1760, 1.3)
    b += f'<rect x="900" y="1500" width="140" height="210" rx="20" fill="#8fc3e0" {o()}/><rect x="940" y="1470" width="60" height="40" fill="#3d6fb4" {o()}/>'
    return wrap(b)


def s_meds_pack():
    b = f'<rect width="{W}" height="{H}" fill="#2a2a44"/>' + glow(540, 1000, 650, op=0.55)
    b += f'<rect x="0" y="1250" width="{W}" height="670" fill="{WOOD}" {o()}/>'
    b += backpack(330, 1500, 1.6)
    b += firstaid(760, 1420, 1.4)
    b += bottle(560, 1560, 1.1, tilt=-10)
    for i in range(3):
        b += f'<rect x="{620+i*110}" y="1640" width="90" height="130" rx="10" fill="#e5e5ea" {o("stroke-width=\'4\'")}/>'
        for j in range(3):
            b += f'<circle cx="{665+i*110}" cy="{1670+j*36}" r="11" fill="#c86ab0"/>'
    return wrap(b)


def s_pipe_burst():
    b = f'<rect width="{W}" height="{H}" fill="#202638"/>'
    b += f'<rect x="-20" y="880" width="1120" height="110" rx="20" fill="#7f8fa3" {o()}/>'
    b += f'<rect x="480" y="860" width="120" height="150" fill="#6c7b8e" {o()}/>'
    b += crack([(510, 900), (540, 950), (530, 990), (560, 1010)], 8)
    for i in range(14):
        a = -math.pi / 2 + (i - 7) * 0.16
        L = 420 + (i % 3) * 90
        b += f'<line x1="540" y1="900" x2="{540+math.cos(a)*L:.0f}" y2="{900+math.sin(a)*L:.0f}" stroke="#a8d8f0" stroke-width="{14 - abs(i-7)}" stroke-linecap="round" opacity="0.85"/>'
    for i in range(20):
        rnd = random.Random(i)
        b += f'<circle cx="{rnd.uniform(200,880):.0f}" cy="{rnd.uniform(1050,1800):.0f}" r="{rnd.uniform(8,20):.0f}" fill="#a8d8f0" opacity="0.8"/>'
    b += f'<ellipse cx="540" cy="1780" rx="420" ry="60" fill="#3c5a78" opacity="0.8"/>'
    return wrap(b)


def s_pharmacy_sign():
    b = (f'<rect width="{W}" height="{H}" fill="{NIGHT_SKY}"/>' + stars(50, 12) + hills(1050, VIOLET, 12)
         + ground(1100, "#262a3c"))
    b += f'<polygon points="500,1100 580,1100 900,1920 180,1920" fill="#3a3a4c"/>'
    b += f'<rect x="700" y="800" width="24" height="600" fill="#9aa5b1" {o()}/>'
    b += f'<rect x="520" y="700" width="420" height="230" rx="10" fill="#2f6aa8" {o()}/>'
    b += f'<rect x="545" y="725" width="370" height="180" rx="6" fill="none" stroke="#e8eef5" stroke-width="5"/>'
    b += f'<text x="730" y="800" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="56" fill="#fff">АПТЕКА</text>'
    b += f'<text x="730" y="878" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="64" fill="{WARM}">34 км</text>'
    b += person(300, 1800, 0.6, "hero", back=True)
    return wrap(b)


def s_shed():
    b = bg_night(13, moonpos=(200, 300)) + ground(1150, GRASS)
    b += f'<g transform="rotate(9 540 1500)">'
    b += f'<polygon points="230,1000 540,820 850,1000" fill="{ROOF}" {o()}/>'
    b += f'<rect x="260" y="1000" width="560" height="500" fill="{WOOD}" {o()}/>'
    for i in range(1, 8):
        b += f'<line x1="{260+i*70}" y1="1005" x2="{260+i*70}" y2="1495" stroke="{WOOD_D}" stroke-width="5"/>'
    b += f'<rect x="440" y="1180" width="200" height="320" fill="#120f18" {o()}/>'
    b += crack(zigzag(300, 1020, 420, 1.2, seed=41), 7)
    b += '</g>'
    b += f'<rect x="830" y="1050" width="30" height="520" fill="{WOOD_D}" transform="rotate(-25 845 1560)" {o()}/>'
    b += person(560, 1880, 0.7, "hero", back=True)
    return wrap(b)


def s_tools():
    b = f'<rect width="{W}" height="{H}" fill="#1d2234"/>' + glow(700, 900, 600, op=0.4)
    b += f'<rect x="0" y="1150" width="{W}" height="770" fill="#2c3343"/>'
    b += crowbar(220, 1650, 1.5, rot=-20)
    b += axe(470, 1640, 1.3, rot=12)
    b += canister(820, 1680, 1.25)
    b += flashlight(380, 1080, 1.4, rot=-8)
    return wrap(b)


def s_tools_vs_money():
    b = f'<rect width="{W}" height="{H}" fill="#1b2036"/>'
    b += glow(330, 1000, 420, op=0.7)
    b += crowbar(250, 1500, 1.4, rot=-5) + flashlight(260, 1640, 1.0, rot=-90, beam=False)
    rnd = random.Random(3)
    for i in range(7):
        x, y = rnd.uniform(620, 1000), rnd.uniform(500, 1500)
        r = rnd.uniform(-40, 40)
        b += f'<g transform="rotate({r:.0f} {x:.0f} {y:.0f})" opacity="{rnd.uniform(.45,.8):.2f}"><rect x="{x-90:.0f}" y="{y-45:.0f}" width="180" height="90" rx="8" fill="#9bbf8a" {o("stroke-width=\'5\'")}/><circle cx="{x:.0f}" cy="{y:.0f}" r="24" fill="#6f9a5c"/></g>'
    b += f'<line x1="540" y1="600" x2="540" y2="1500" stroke="#ffffff22" stroke-width="6" stroke-dasharray="30 20"/>'
    return wrap(b)


def s_stove_close():
    b = f'<rect width="{W}" height="{H}" fill="#241d2c"/>'
    b += f'<rect x="0" y="1500" width="{W}" height="420" fill="#3a2c2a"/>'
    for i in range(0, W, 110):
        b += f'<line x1="{i}" y1="0" x2="{i}" y2="1500" stroke="#2f2533" stroke-width="6"/>'
    b += stove(540, 1560, 1.6)
    return wrap(b, vignette=0.85)


def s_shelter_wide():
    b = bg_night(14, moonpos=(860, 260)) + ground(1150, GRASS)
    b += house(250, 1180, 0.55, lit=False, cracked=True)
    # banya with open door + smoke
    b += f'<polygon points="440,1050 700,920 960,1050" fill="{ROOF}" {o()}/>'
    b += f'<rect x="470" y="1050" width="460" height="330" fill="{WOOD}" {o()}/>'
    b += f'<rect x="800" y="840" width="40" height="150" fill="#4b3a3a" {o()}/>'
    for i, (dx, dy, r) in enumerate([(0, -40, 40), (30, -110, 55), (-10, -200, 70)]):
        b += f'<circle cx="{820+dx}" cy="{840+dy}" r="{r}" fill="#8a8aa0" opacity="{0.5-i*0.12:.2f}"/>'
    b += f'<rect x="560" y="1150" width="140" height="230" fill="{WARM}" {o()}/>'
    b += f'<polygon points="560,1150 500,1170 500,1400 560,1380" fill="#6a5240" {o()}/>'
    b += glow(630, 1260, 380, op=0.8)
    b += f'<rect x="770" y="1130" width="110" height="90" fill="{WARM}" {o()}/>'
    b += person(400, 1700, 0.55, "woman", back=True) + person(860, 1720, 0.55, "red", back=True)
    b += person(620, 1830, 0.6, "hero", back=True)
    return wrap(b)


def s_vent():
    b = f'<rect width="{W}" height="{H}" fill="#241d2c"/>' + glow(380, 1200, 600, op=0.8)
    b += f'<rect x="560" y="500" width="400" height="1150" fill="#14172a" {o()}/>'
    b += stars(18, 22, 1500).replace('<circle cx="', '<circle cx="1') if False else ""
    b += f'<rect x="580" y="520" width="360" height="1110" fill="#1f2a4a"/>'
    b += f'<polygon points="560,500 420,560 420,1700 560,1650" fill="#6a5240" {o()}/>'
    for i in range(3):
        y = 800 + i * 220
        b += f'<path d="M640,{y} Q760,{y-50} 880,{y}" fill="none" stroke="#cfe3ff" stroke-width="10" stroke-linecap="round" opacity="0.8"/>'
        b += f'<polygon points="880,{y} 850,{y-30} 845,{y+18}" fill="#cfe3ff" opacity="0.8"/>'
    b += stove(250, 1750, 1.0)
    return wrap(b, vignette=0.85)


def s_canister_gauge():
    b = f'<rect width="{W}" height="{H}" fill="#221d2c"/>' + glow(540, 1000, 600, op=0.45)
    b += f'<rect x="0" y="1450" width="{W}" height="470" fill="#33282a"/>'
    b += canister(470, 1600, 2.2, level=0.18)
    return wrap(b)


def s_empty_road():
    b = (f'<rect width="{W}" height="{H}" fill="{NIGHT_SKY}"/>' + stars(70, 16) + hills(1080, VIOLET, 16)
         + trees(1120, 10, 17) + ground(1120, "#232838"))
    b += f'<polygon points="520,1120 560,1120 960,1920 120,1920" fill="#353648"/>'
    for i in range(6):
        y = 1180 + i * 130
        w = 6 + i * 6
        b += f'<rect x="{540-w/2}" y="{y}" width="{w}" height="{50+i*10}" fill="#d9d9e0" opacity="0.6"/>'
    b += f'<rect x="200" y="760" width="16" height="420" fill="#555a6a" {o()}/><path d="M208,770 Q260,740 300,780" fill="none" {o()}/>'
    b += glow(300, 800, 160, op=0.35)
    b += person(540, 1880, 0.6, "hero", back=True)
    return wrap(b)


def s_water_glass():
    b = f'<rect width="{W}" height="{H}" fill="#22213a"/>' + glow(700, 700, 600, op=0.5)
    b += f'<rect x="0" y="1300" width="{W}" height="620" fill="{WOOD}" {o()}/>'
    b += f'<path d="M370,700 L710,700 L670,1300 L410,1300 Z" fill="#bcd8ea" opacity="0.55" {o()}/>'
    b += f'<path d="M386,860 L694,860 L670,1300 L410,1300 Z" fill="#8fc3e0" opacity="0.75"/>'
    for i, r in enumerate([40, 80, 120]):
        b += f'<ellipse cx="540" cy="862" rx="{r}" ry="{r*0.18}" fill="none" stroke="#ffffff" stroke-width="4" opacity="{0.9-i*0.25:.2f}"/>'
    b += f'<text x="790" y="1020" font-family="DejaVu Sans" font-weight="bold" font-size="70" fill="#cfe3ff" opacity="0.8">~</text>'
    return wrap(b)


def s_relaxed_group():
    b = f'<rect width="{W}" height="{H}" fill="#241d2c"/>' + stove(860, 1500, 1.0)
    b += f'<rect x="0" y="1500" width="{W}" height="420" fill="#3a2c2a"/>'
    b += person(160, 1700, 0.55, "grey", face="calm") + person(400, 1720, 0.58, "woman", face="calm")
    b += person(640, 1740, 0.6, "hero", face="tense")
    return wrap(b)


def s_boots():
    b = f'<rect width="{W}" height="{H}" fill="#24253a"/>' + glow(540, 1200, 500, op=0.35)
    b += f'<rect x="0" y="1400" width="{W}" height="520" fill="#3a2c2a"/>'
    for x in (330, 650):
        b += f'<rect x="{x}" y="900" width="140" height="520" fill="{HERO_JEANS}" {o()}/>'
        b += f'<path d="M{x-10},1260 L{x+150},1260 L{x+150},1440 L{x+300},1460 Q{x+330},1530 {x+280},1540 L{x-10},1540 Z" fill="#4a3428" {o()}/>'
        for k in range(3):
            b += f'<line x1="{x+20}" y1="{1300+k*40}" x2="{x+130}" y2="{1300+k*40}" stroke="{WARM}" stroke-width="5"/>'
    return wrap(b)


def s_pack_exit():
    b = f'<rect width="{W}" height="{H}" fill="#241d2c"/>'
    b += f'<rect x="520" y="420" width="430" height="1200" fill="#1f2a4a" {o()}/>' + stars(14, 30, 0)
    b += moon(760, 700, 45)
    b += f'<polygon points="520,420 400,500 400,1700 520,1620" fill="#6a5240" {o()}/>'
    b += f'<rect x="0" y="1620" width="{W}" height="300" fill="#3a2c2a"/>'
    b += backpack(240, 1700, 1.4)
    b += f'<path d="M560,1650 L900,1650" stroke="{WARM}" stroke-width="10" stroke-dasharray="40 25"/>'
    return wrap(b)


def s_watch_sleep(assign=False):
    b = f'<rect width="{W}" height="{H}" fill="#1e1a2a"/>' + stove(140, 1350, 0.9)
    b += f'<rect x="0" y="1350" width="{W}" height="570" fill="#33282a"/>'
    for i, (x, c) in enumerate([(360, MUSTARD), (640, RED), (880, GREY)]):
        b += f'<ellipse cx="{x}" cy="1700" rx="140" ry="70" fill="{c}" {o()}/>'
        b += f'<circle cx="{x-130}" cy="1670" r="46" fill="{SKIN}" {o()}/>'
        if not assign:
            b += f'<text x="{x+40}" y="1560" font-family="DejaVu Sans" font-weight="bold" font-size="54" fill="#cfd3ff" opacity="0.8">z</text>'
    if assign:
        icons = [bottle(360, 1540, 0.8), axe(660, 1580, 0.6, rot=20), firstaid(880, 1550, 0.6)]
        for ic in icons:
            b += ic
        b += person(560, 1350, 0.62, "hero", arm="point", face="tense")
    else:
        b += person(560, 1360, 0.62, "hero", arm="watch", face="tense")
    return wrap(b)


def s_faces_fire():
    b = f'<rect width="{W}" height="{H}" fill="#18141f"/>' + glow(540, 1650, 800, op=1.0)
    b += bighead(230, 900, 1.15, "grey", "tense", light="warm")
    b += bighead(820, 880, 1.15, "red", "tense", light="warm")
    b += bighead(530, 1250, 1.3, "woman", "tense", light="warm")
    b += f'<path d="M420,1920 Q460,1700 540,1760 Q560,1640 640,1730 Q700,1680 690,1920 Z" fill="{WARM}" {o()}/>'
    return wrap(b)


def s_house_cracked_woman():
    b = bg_night(19, moonpos=(860, 280)) + ground(1250, GRASS)
    b += house(540, 1480, 1.35, lit=False, cracked=True, tilt=-3)
    b += person(560, 1800, 0.55, "woman", back=True)
    return wrap(b)


def s_grab_shoulder():
    b = f'<rect width="{W}" height="{H}" fill="#1c1d36"/>'
    b += bighead(640, 900, 2.0, "woman", "scared")
    b += hand(260, 1220, 1.6, rot=-25)
    for i in range(14):
        rnd = random.Random(40 + i)
        b += f'<rect x="{rnd.uniform(0,W):.0f}" y="{rnd.uniform(0,700):.0f}" width="{rnd.uniform(10,30):.0f}" height="{rnd.uniform(10,30):.0f}" fill="#bdb6a8" opacity="0.8"/>'
    return wrap(b)


def s_docs_inside():
    b = f'<rect width="{W}" height="{H}" fill="#2a2638"/>'
    b += crack(zigzag(100, 200, 900, 0.9, seed=51, segs=9), 8)
    b += f'<rect x="0" y="1200" width="{W}" height="720" fill="{WOOD}" {o()}/>'
    b += f'<rect x="180" y="1120" width="360" height="250" fill="#d8cfb8" transform="rotate(-8 360 1245)" {o()}/>'
    b += f'<text x="360" y="1260" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="44" fill="#6b3a2a" transform="rotate(-8 360 1245)">ПАСПОРТ</text>'
    b += f'<rect x="620" y="1150" width="220" height="380" rx="30" fill="#22232e" transform="rotate(12 730 1340)" {o()}/>'
    rnd = random.Random(8)
    for i in range(40):
        b += f'<circle cx="{rnd.uniform(0,W):.0f}" cy="{rnd.uniform(100,1100):.0f}" r="{rnd.uniform(3,10):.0f}" fill="#d9d2c0" opacity="0.7"/>'
    for i in range(5):
        x = rnd.uniform(100, 980)
        b += f'<polygon points="{x},{300+i*120} {x+50},{330+i*120} {x+20},{380+i*120}" fill="#bdb6a8" {o("stroke-width=\'4\'")}/>'
    return wrap(b)


def s_collapse(broken=False):
    b = bg_night(23, moonpos=(200, 300)) + ground(1250, GRASS)
    b += house(540, 1520, 1.5, lit=False, cracked=True, broken=broken, tilt=-4 if broken else -2)
    if broken:
        rnd = random.Random(5)
        for i in range(30):
            b += f'<circle cx="{rnd.uniform(500,1080):.0f}" cy="{rnd.uniform(700,1500):.0f}" r="{rnd.uniform(20,70):.0f}" fill="#8d8a9a" opacity="{rnd.uniform(.15,.4):.2f}"/>'
    return wrap(b)


def s_loop_watch():
    b = f'<rect width="{W}" height="{H}" fill="#151425"/>' + glow(540, 960, 650, op=0.6)
    b += f'<rect x="80" y="760" width="920" height="400" rx="200" fill="{HERO_TOP}" {o()}/>'
    b += f'<rect x="380" y="620" width="320" height="680" rx="60" fill="#2a2a36" {o()}/>'
    b += f'<rect x="420" y="760" width="240" height="400" rx="40" fill="#0f1a12" {o()}/>'
    b += f'<text x="540" y="1000" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="104" fill="#ff5b4f">03</text>'
    b += f'<text x="540" y="1120" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="104" fill="#ff5b4f">17</text>'
    return wrap(b)


def s_loop_yard():
    b = bg_night(31, moonpos=(820, 300)) + ground(1180, GRASS)
    b += house(300, 1250, 0.7, lit=False, broken=True)
    b += f'<polygon points="560,1140 760,1040 960,1140" fill="{ROOF}" {o()}/><rect x="590" y="1140" width="340" height="230" fill="{WOOD}" {o()}/><rect x="660" y="1210" width="100" height="160" fill="{WARM}" {o()}/>'
    b += glow(710, 1290, 300, op=0.8)
    b += wallclock(540, 1650, 150, 3, 17, cracked=True, tilt=-8)
    return wrap(b)


def s_village_aerial():
    b = f'<rect width="{W}" height="{H}" fill="#121528"/>' + stars(80, 40, 600)
    b += f'<rect x="0" y="600" width="{W}" height="1320" fill="#18202a"/>'
    rnd = random.Random(12)
    for row in range(6):
        for col in range(5):
            x = 60 + col * 210 + rnd.uniform(-20, 20)
            y = 700 + row * 200 + rnd.uniform(-20, 20)
            b += f'<rect x="{x}" y="{y}" width="180" height="160" fill="none" stroke="#2a3540" stroke-width="5"/>'
            b += f'<rect x="{x+50}" y="{y+40}" width="70" height="60" fill="#2b2633" transform="rotate({rnd.uniform(-15,15):.0f} {x+85} {y+70})"/>'
    b += glow(530, 1280, 160, op=1.0) + f'<circle cx="530" cy="1280" r="10" fill="{WARM}"/>'
    b += crack(zigzag(-20, 900, 1150, 0.5, seed=77, segs=12, spread=40), 9, "#05060c")
    return wrap(b)


def s_question():
    b = f'<rect width="{W}" height="{H}" fill="#0f0f1c"/>' + glow(540, 760, 520, op=0.7)
    b += wallclock(540, 760, 200, 3, 17, cracked=True)
    return wrap(b, vignette=0.9)


def s_endcard():
    b = f'<rect width="{W}" height="{H}" fill="#0f0f1c"/>' + glow(540, 960, 500, op=0.35)
    return wrap(b, vignette=0.9)


SCENES = {
    "hook_house": s_hook_house, "jars_fall": s_jars_fall, "hero_face": s_hero_face,
    "phone": s_phone, "road_blocked": s_road_blocked, "strangers_wide": s_strangers_wide,
    "woman_close": s_woman_close, "gate_wide": lambda: s_gate_wide(False), "gate_latch": s_gate_latch,
    "yard_stuff": s_yard_stuff, "gate_open": lambda: s_gate_wide(True, True), "well_water": s_well_water,
    "meds_pack": s_meds_pack, "pipe_burst": s_pipe_burst, "pharmacy_sign": s_pharmacy_sign,
    "shed": s_shed, "tools": s_tools, "tools_vs_money": s_tools_vs_money, "stove_close": s_stove_close,
    "shelter_wide": s_shelter_wide, "vent": s_vent, "canister_gauge": s_canister_gauge,
    "empty_road": s_empty_road, "water_glass": s_water_glass, "relaxed_group": s_relaxed_group,
    "boots": s_boots, "pack_exit": s_pack_exit, "watch_sleep": lambda: s_watch_sleep(False),
    "assign": lambda: s_watch_sleep(True), "faces_fire": s_faces_fire,
    "house_cracked_woman": s_house_cracked_woman, "grab_shoulder": s_grab_shoulder,
    "docs_inside": s_docs_inside, "walls_crack": lambda: s_collapse(False),
    "collapse": lambda: s_collapse(True), "loop_watch": s_loop_watch, "loop_yard": s_loop_yard,
    "village_aerial": s_village_aerial, "question": s_question, "endcard": s_endcard,
}
