import math, random, os, subprocess
W, H = 1080, 1920
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frames")

def hx(c): c=c.lstrip('#'); return [int(c[i:i+2],16) for i in (0,2,4)]
def mix(a,b,t):
    A,B=hx(a),hx(b); return '#%02x%02x%02x'%tuple(round(A[i]+(B[i]-A[i])*t) for i in range(3))
def gr(c,g,grey=None):
    """fade colour c toward its own grey/rust version as g goes 1->0"""
    r,gg,b=hx(c); l=int(0.3*r+0.59*gg+0.11*b)
    base = grey or '#%02x%02x%02x'%(min(255,l+12),l,max(0,l-12))
    return mix(c,base,1-g)

DEFS = '''<defs>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix type="saturate" values="0"/></filter>
<filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="blur30"><feGaussianBlur stdDeviation="30"/></filter>
<filter id="glow"><feGaussianBlur stdDeviation="18" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".45"/></radialGradient>
</defs>'''

def svg(body, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            + DEFS + extra_defs + body +
            f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".07"/>'
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')

def sky(id_, top, bot):
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>'

def save(name, s):
    p=f"{OUT}/{name}.svg"; open(p,"w").write(s)
    import shutil
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert","-w",str(W),"-h",str(H),p,"-o",f"{OUT}/{name}.png"],check=True)
    else:  # pip install cairosvg
        import cairosvg; cairosvg.svg2png(url=p, write_to=f"{OUT}/{name}.png", output_width=W, output_height=H)
    os.remove(p)

def person(x,y,s=1,col="#4a4f5c",head="#e8c4a6",flip=False,arm_up=False):
    a = f'<path d="M{x-28*s},{y-150*s} q{28*s},-20 {56*s},0 l{6*s},{95*s} h{-68*s} z" fill="{col}"/>'
    a+= f'<rect x="{x-24*s}" y="{y-58*s}" width="{20*s}" height="{58*s}" rx="{8*s}" fill="#33363f"/><rect x="{x+4*s}" y="{y-58*s}" width="{20*s}" height="{58*s}" rx="{8*s}" fill="#33363f"/>'
    a+= f'<circle cx="{x}" cy="{y-178*s}" r="{26*s}" fill="{head}"/>'
    a+= f'<path d="M{x-26*s},{y-182*s} q{4*s},-30 {28*s},-28 q{24*s},0 {24*s},{24*s} q-{20*s},-10 -{52*s},{4*s}z" fill="#2b2b33"/>'
    if arm_up:
        a+= f'<path d="M{x-20*s},{y-140*s} q-10,-40 {6*s},-{62*s}" stroke="{col}" stroke-width="{16*s}" stroke-linecap="round" fill="none"/>'
    return a

def buildings(y0, g, n=7, seed=1, col="#9fb0c4", win="#f3e6b8", lit=0.3):
    random.seed(seed); s=""; x=-40
    while x<W+40:
        w=random.randint(150,240); h=random.randint(320,620); c=gr(mix(col,'#ffffff',random.random()*.25),0.3+0.7*g)
        s+=f'<rect x="{x}" y="{y0-h}" width="{w}" height="{h+400}" fill="{c}"/>'
        for wy in range(y0-h+30, y0-20, 60):
            for wx in range(x+20, x+w-30, 46):
                f = win if random.random()<lit else mix(c,'#000000',.12)
                s+=f'<rect x="{wx}" y="{wy}" width="26" height="34" rx="3" fill="{f}"/>'
        x+=w+random.randint(-10,20)
    return s

# ---------- 1. cactus on windowsill
def s01():
    g=1
    d=sky("sk","#a9d3ec","#f6e2c4")
    b=f'<rect width="{W}" height="{H}" fill="#e9dccb"/>'
    b+=f'<rect x="140" y="260" width="800" height="1000" rx="14" fill="url(#sk)"/>'
    b+=f'<g opacity=".85">{buildings(1260,g,seed=4)}</g>'.replace('height="','height="',1)
    b+=f'<rect x="140" y="260" width="800" height="1000" rx="14" fill="none" stroke="#f7f1e8" stroke-width="36"/>'
    b+=f'<rect x="522" y="260" width="36" height="1000" fill="#f7f1e8"/><rect x="140" y="740" width="800" height="30" fill="#f7f1e8"/>'
    b+=f'<rect x="60" y="1260" width="960" height="70" rx="10" fill="#fbf6ef"/><rect x="60" y="1330" width="960" height="30" fill="#d9cbb7"/>'
    b+=f'<rect x="0" y="1360" width="{W}" height="560" fill="#d8c8b2"/>'
    # sunlight patch
    b+=f'<polygon points="140,1260 940,1260 1040,1900 40,1900" fill="#fff4d6" opacity=".25"/>'
    # pot
    b+='<path d="M420,1060 h240 l-30,200 h-180 z" fill="#c8693f"/><rect x="405" y="1040" width="270" height="44" rx="10" fill="#d97b4f"/>'
    b+='<ellipse cx="540" cy="1046" rx="118" ry="14" fill="#5b3a26"/>'
    # fading cactus ghost
    b+='<g opacity=".28"><rect x="500" y="760" width="80" height="290" rx="40" fill="#5DA858"/><rect x="430" y="860" width="56" height="120" rx="28" fill="#5DA858"/><rect x="455" y="955" width="60" height="30" fill="#5DA858"/><rect x="600" y="820" width="56" height="130" rx="28" fill="#5DA858"/><rect x="570" y="925" width="60" height="30" fill="#5DA858"/></g>'
    random.seed(7)
    for i in range(26):
        x=random.randint(420,680); y=random.randint(720,1040); r=random.randint(3,9)
        b+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9fe39a" opacity="{random.uniform(.4,.9):.2f}"/>'
    save("01_kaktus", svg(b,"<defs>"+d+"</defs>"))

# ---------- 2. phone news
def s02():
    b=f'<rect width="{W}" height="{H}" fill="#cfd8de"/>'
    b+=f'<g opacity=".5" filter="url(#blur8)">{buildings(1000,1,seed=9)}</g>'
    b+=f'<rect x="0" y="1000" width="{W}" height="920" fill="#b7c3c9"/>'
    # hand + phone
    b+='<path d="M300,1920 q-40,-420 60,-560 l120,-40 q60,10 40,80 l-40,140 q120,-30 160,10 l60,370z" fill="#e8c4a6"/>'
    b+='<rect x="290" y="480" width="500" height="980" rx="60" fill="#1c1f26"/><rect x="314" y="510" width="452" height="920" rx="44" fill="#f5f6f8"/>'
    b+='<rect x="480" y="524" width="120" height="22" rx="11" fill="#1c1f26"/>'
    b+='<rect x="340" y="580" width="400" height="230" rx="18" fill="#d8dde3"/>'
    b+='<path d="M490,780 h100 l-14,-70 h-72z" fill="#c8693f"/><ellipse cx="540" cy="712" rx="52" ry="8" fill="#5b3a26"/>'
    b+='<text x="352" y="618" font-family="DejaVu Sans" font-weight="bold" font-size="22" fill="#d6453d">● СРОЧНО</text>'
    txt=["Комнатные растения","исчезают по всему","миру"]
    for i,t in enumerate(txt):
        b+=f'<text x="345" y="{870+i*42}" font-family="DejaVu Sans" font-weight="bold" font-size="34" fill="#1c1f26">{t}</text>'
    b+='<text x="345" y="1010" font-family="DejaVu Sans" font-size="22" fill="#6b7280">Учёные просят не паниковать</text>'
    b+='<rect x="340" y="1050" width="400" height="2" fill="#e2e5ea"/>'
    for i,(t,e) in enumerate([("мой фикус ушёл за хлебом","😂 12К"),("горшки без цветов — тренд","🔥 8К"),("фиалка, вернись","💔 5К")]):
        y=1100+i*100
        b+=f'<circle cx="372" cy="{y}" r="24" fill="{["#f2b880","#9fc6e8","#c7a6e0"][i]}"/><text x="410" y="{y-4}" font-family="DejaVu Sans" font-size="23" fill="#1c1f26">{t}</text><text x="410" y="{y+26}" font-family="DejaVu Sans" font-size="19" fill="#9aa0a8">{e}</text>'
    b+='<path d="M560,1460 q120,-40 200,40 q20,60 -20,90 l-120,-60z" fill="#e8c4a6"/>'
    save("02_novosti", svg(b))

def dust(seed, n, y0, y1, col, op=.35):
    random.seed(seed); s=""
    for i in range(n):
        x=random.randint(-100,W+100); y=random.randint(y0,y1); rx=random.randint(120,320)
        s+=f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*0.35:.0f}" fill="{col}" opacity="{random.uniform(op*.5,op):.2f}" filter="url(#blur30)"/>'
    return s

# ---------- 3. yard, grass gone
def s03():
    g=.85
    d=sky("sk",mix("#a9cfe6","#d9b48a",.45),"#e7c79e")
    b=f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b+='<circle cx="760" cy="360" r="90" fill="#fff1cf" opacity=".55"/>'
    b+=buildings(1150,g,seed=2,col="#c9c2b8",lit=.15)
    b+=f'<path d="M0,1150 H{W} V{H} H0z" fill="#c98f5e"/>'
    random.seed(5)
    for i in range(40):
        x=random.randint(0,W); y=random.randint(1170,1900); b+=f'<ellipse cx="{x}" cy="{y}" rx="{random.randint(8,30)}" ry="5" fill="#a9724a" opacity=".6"/>'
    # sidewalk tiles with empty cracks
    b+='<path d="M380,1920 L520,1150 H600 L760,1920z" fill="#b7aea4"/>'
    for y in range(1200,1920,90): 
        t=(y-1150)/770; b+=f'<line x1="{520-140*t}" y1="{y}" x2="{600+160*t}" y2="{y}" stroke="#8f877e" stroke-width="4"/>'
    # bench, swing
    b+='<rect x="120" y="1330" width="200" height="20" fill="#7b5a43"/><rect x="130" y="1350" width="12" height="60" fill="#5a4031"/><rect x="298" y="1350" width="12" height="60" fill="#5a4031"/>'
    b+='<path d="M820,1180 v220 M1000,1180 v220 M810,1180 h200" stroke="#6a6f7a" stroke-width="12" fill="none"/><path d="M880,1180 v160 M940,1180 v160" stroke="#6a6f7a" stroke-width="4"/><rect x="870" y="1340" width="80" height="14" fill="#d6453d"/>'
    b+=person(640,1560,1.2,"#6b7da3")
    b+=dust(11,16,900,1500,"#d8a978",.5)
    save("03_trava", svg(b,"<defs>"+d+"</defs>"))

# ---------- 4. flowerbed
def s04():
    g=.7
    d=sky("sk",mix("#b7d6ea","#d9c2a2",.4),"#e3d2bb")
    b=f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b+=f'<g opacity=".7">{buildings(900,g,seed=6,col="#b9bcc4",lit=.1)}</g>'
    b+=f'<rect y="900" width="{W}" height="1020" fill="#a9a39a"/>'
    b+='<ellipse cx="540" cy="1380" rx="430" ry="190" fill="#d9d4cc"/><ellipse cx="540" cy="1360" rx="390" ry="160" fill="#8d6a4e"/>'
    random.seed(8)
    for i in range(30):
        x=random.randint(200,880); y=random.randint(1260,1460)
        if ((x-540)/390)**2+((y-1360)/160)**2<0.85:
            b+=f'<path d="M{x},{y} v-14" stroke="{gr("#6aa85e",g)}" stroke-width="5" stroke-linecap="round" opacity=".55"/>'
    # bee
    bx,by=560,980
    b+=f'<path d="M300,1150 q120,-200 230,-120 q90,60 0,-120" stroke="#5a5040" stroke-width="3" stroke-dasharray="10 14" fill="none" opacity=".55"/>'
    b+=f'<ellipse cx="{bx-30}" cy="{by-48}" rx="44" ry="26" fill="#fff" opacity=".75" transform="rotate(-25 {bx-30} {by-48})"/><ellipse cx="{bx+18}" cy="{by-52}" rx="40" ry="24" fill="#fff" opacity=".75" transform="rotate(20 {bx+18} {by-52})"/>'
    b+=f'<ellipse cx="{bx}" cy="{by}" rx="70" ry="48" fill="#f2c23a"/><path d="M{bx-28},{by-44} v88 M{bx+6},{by-46} v92 M{bx+38},{by-38} v76" stroke="#2b2620" stroke-width="16"/>'
    b+=f'<circle cx="{bx-70}" cy="{by-6}" r="34" fill="#2b2620"/><circle cx="{bx-82}" cy="{by-14}" r="9" fill="#fff"/>'
    b+=f'<path d="M{bx-78},{by-36} q-10,-40 -36,-44 M{bx-66},{by-38} q4,-44 -14,-56" stroke="#2b2620" stroke-width="5" fill="none"/>'
    save("04_cvety", svg(b,"<defs>"+d+"</defs>"))

# ---------- 5. street without trees
def s05():
    g=.55
    d=sky("sk","#e8c890","#f3e3c4")
    b=f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b+='<circle cx="540" cy="300" r="140" fill="#fff6dc" filter="url(#glow)"/>'
    b+=buildings(1020,g,seed=3,col="#d2b79a",lit=.05)
    b+=f'<polygon points="0,1020 {W},1020 {W},{H} 0,{H}" fill="#7b7a7d"/>'
    b+=f'<polygon points="0,1020 260,1020 0,1400" fill="#c2b8aa"/><polygon points="{W},1020 {W-260},1020 {W},1400" fill="#c2b8aa"/>'
    b+='<polygon points="520,1020 560,1020 640,1920 440,1920" fill="#e9e1cf"/>'
    # empty tree pits
    for i,(x,y,s) in enumerate([(120,1080,.5),(60,1200,.8),(-10,1400,1.3),(960,1080,.5),(1020,1200,.8),(1090,1400,1.3)]):
        b+=f'<rect x="{x-60*s}" y="{y-20*s}" width="{120*s}" height="{40*s}" rx="{6*s}" fill="#6a4d39" stroke="#9a9184" stroke-width="{8*s}"/>'
    # heat haze
    for y in range(1100,1700,70):
        b+=f'<path d="M100,{y} q60,-14 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0" stroke="#fff" stroke-width="3" fill="none" opacity=".25"/>'
    b+=person(330,1700,1.4,"#a35d4f",arm_up=True)+person(780,1560,1.05,"#4f6a8f",arm_up=True)
    save("05_derevya", svg(b,"<defs>"+d+"</defs>"))

# ---------- 6. empty supermarket
def s06():
    b=f'<rect width="{W}" height="{H}" fill="#d9d6cf"/>'
    b+='<rect x="0" y="0" width="1080" height="260" fill="#efeee9"/>'
    for x in range(80,1080,200): b+=f'<rect x="{x}" y="60" width="140" height="18" rx="9" fill="#fffbe8"/>'
    b+='<text x="540" y="200" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="54" fill="#8a7f6e">ХЛЕБ</text>'
    for sx in (60,580):
        b+=f'<rect x="{sx}" y="300" width="440" height="1060" fill="#b9b2a6"/>'
        for sy in range(420,1360,190):
            b+=f'<rect x="{sx}" y="{sy}" width="440" height="22" fill="#8c857b"/>'
        b+=f'<rect x="{sx+30}" y="{sy-50}" width="70" height="50" rx="10" fill="#d9b27a" opacity=".6"/>'
        b+=f'<rect x="{sx+20}" y="440" width="120" height="44" fill="#fff" stroke="#c8c1b5"/><text x="{sx+80}" y="472" text-anchor="middle" font-family="DejaVu Sans" font-size="22" fill="#d6453d">НЕТ</text>'
    b+=f'<rect y="1360" width="{W}" height="560" fill="#bcb6ab"/>'
    random.seed(4); cols=["#6b7da3","#a35d4f","#5d7a62","#8a6fa3","#c08a4a","#55606e"]
    for i in range(9):
        x=80+i*115+random.randint(-20,20); b+=person(x,1820+random.randint(-40,40),1.25,cols[i%6])
    save("06_zerno", svg(b))

# ---------- 7. cow in bare field
def s07():
    d=sky("sk","#cbbfa8","#e4d3b4")
    b=f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b+=f'<path d="M0,1000 q300,-40 540,0 t540,-20 V{H} H0z" fill="#b9875c"/>'
    b+='<path d="M0,1060 L1080,1040" stroke="#7a5a40" stroke-width="3"/>'
    for x in range(40,1080,140): b+=f'<rect x="{x}" y="980" width="12" height="100" fill="#6d5240"/>'
    b+='<path d="M0,1000 L1080,990 M0,1030 L1080,1020" stroke="#6d5240" stroke-width="5"/>'
    random.seed(3)
    for i in range(60):
        x=random.randint(0,W); y=random.randint(1100,1900)
        b+=f'<path d="M{x},{y} l40,-6" stroke="#9d6e48" stroke-width="5" stroke-linecap="round" opacity=".6"/>'
    # cow
    cx,cy=540,1420
    b+=f'<ellipse cx="{cx}" cy="{cy+250}" rx="300" ry="34" fill="#8f6646" opacity=".6"/>'
    b+=f'<rect x="{cx-240}" y="{cy-90}" width="420" height="230" rx="100" fill="#f4efe6"/>'
    b+=f'<path d="M{cx-120},{cy-80} q60,40 30,120 q-70,-10 -80,-90z" fill="#3a3533"/><path d="M{cx+70},{cy-60} q60,20 60,90 q-60,30 -90,-30z" fill="#3a3533"/>'
    for lx in (cx-210,cx-140,cx+80,cx+150):
        b+=f'<rect x="{lx}" y="{cy+100}" width="44" height="150" rx="16" fill="#f4efe6"/><rect x="{lx}" y="{cy+225}" width="44" height="26" rx="8" fill="#3a3533"/>'
    hx_,hy=cx+230,cy-140
    b+=f'<path d="M{cx+150},{cy-60} q60,-40 80,-80" stroke="#f4efe6" stroke-width="80" stroke-linecap="round" fill="none"/>'
    b+=f'<rect x="{hx_-80}" y="{hy-90}" width="160" height="200" rx="70" fill="#f4efe6"/><rect x="{hx_-74}" y="{hy+40}" width="148" height="78" rx="38" fill="#e9b5a6"/>'
    b+=f'<circle cx="{hx_-32}" cy="{hy+76}" r="8" fill="#7a4a42"/><circle cx="{hx_+32}" cy="{hy+76}" r="8" fill="#7a4a42"/>'
    b+=f'<circle cx="{hx_-38}" cy="{hy-10}" r="16" fill="#2b2b33"/><circle cx="{hx_+38}" cy="{hy-10}" r="16" fill="#2b2b33"/><circle cx="{hx_-34}" cy="{hy-16}" r="5" fill="#fff"/><circle cx="{hx_+42}" cy="{hy-16}" r="5" fill="#fff"/>'
    b+=f'<path d="M{hx_-60},{hy-40} q12,-14 28,-8 M{hx_+60},{hy-40} q-12,-14 -28,-8" stroke="#2b2b33" stroke-width="5" fill="none"/>'
    b+=f'<ellipse cx="{hx_-100}" cy="{hy-30}" rx="40" ry="18" fill="#e9dccb"/><ellipse cx="{hx_+100}" cy="{hy-30}" rx="40" ry="18" fill="#e9dccb"/>'
    b+=f'<path d="M{hx_-60},{hy-86} q-20,-40 0,-60 M{hx_+60},{hy-86} q20,-40 0,-60" stroke="#e6d9b8" stroke-width="16" stroke-linecap="round" fill="none"/>'
    b+=f'<path d="M{cx-240},{cy-40} q-50,40 -30,140" stroke="#f4efe6" stroke-width="12" fill="none"/>'
    save("07_korova", svg(b,"<defs>"+d+"</defs>"))

# ---------- 8. globe
def s08():
    g=.25
    b=f'<rect width="{W}" height="{H}" fill="#14161f"/>'
    random.seed(2)
    for i in range(140): b+=f'<circle cx="{random.randint(0,W)}" cy="{random.randint(0,H)}" r="{random.uniform(.8,2.6):.1f}" fill="#fff" opacity="{random.uniform(.3,.9):.2f}"/>'
    cx,cy,r=540,960,400
    defs='<defs><clipPath id="gc"><circle cx="540" cy="960" r="400"/></clipPath><radialGradient id="sh" cx="35%" cy="35%" r="75%"><stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset=".7" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient></defs>'
    b+=f'<circle cx="{cx}" cy="{cy}" r="{r+30}" fill="#6fa8d8" opacity=".18" filter="url(#blur30)"/>'
    b+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#3f6f9e"/>'
    land=gr("#4f9a4c",g,"#b0835a")
    alive="#4f9a4c"
    b+='<g clip-path="url(#gc)">'
    # americas
    b+=f'<path d="M260,620 q80,-40 160,10 q30,60 -10,110 q-60,30 -40,90 q50,40 60,110 q40,60 10,150 q-30,120 -70,180 q-40,-60 -40,-170 q-10,-90 -60,-150 q-60,-80 -50,-180 q10,-80 40,-150z" fill="{land}"/>'
    # amazon still partly green fading
    b+=f'<ellipse cx="380" cy="1080" rx="70" ry="60" fill="{alive}" opacity=".55"/><ellipse cx="380" cy="1080" rx="40" ry="34" fill="{alive}" opacity=".7"/>'
    # africa/europe
    b+=f'<path d="M610,640 q90,-40 170,0 q40,50 0,90 q50,40 70,120 q20,100 -40,180 q-40,80 -70,140 q-40,-30 -50,-110 q-20,-80 -70,-120 q-60,-60 -40,-150 q10,-90 30,-150z" fill="{land}"/>'
    b+=f'<ellipse cx="700" cy="1000" rx="46" ry="40" fill="{alive}" opacity=".45"/>'
    b+=f'<path d="M780,600 q120,-20 220,40 v120 q-80,30 -150,0 q-60,-60 -70,-160z" fill="{land}"/>'
    b+='<rect x="0" y="0" width="1080" height="1920" fill="url(#sh)"/>'
    # clouds thinning
    for (x,y,w) in [(300,800,120),(760,1180,90),(500,700,70)]:
        b+=f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{w*.25}" fill="#fff" opacity=".35"/>'
    b+='</g>'
    save("08_lesa", svg(b,defs))

# ---------- 9. heat
def s09():
    d=sky("sk","#d99a6c","#efcfa0")
    b=f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b+='<circle cx="820" cy="320" r="160" fill="#ffe1a8" filter="url(#glow)" opacity=".9"/>'
    b+=f'<g opacity=".8">{buildings(1100,.1,seed=12,col="#b8a493",lit=0)}</g>'
    # factory
    b+='<rect x="80" y="620" width="90" height="480" fill="#7d6f66"/><rect x="200" y="720" width="70" height="380" fill="#7d6f66"/>'
    b+=dust(21,10,250,700,"#8f8178",.55)
    b+=f'<rect y="1100" width="{W}" height="820" fill="#a8917c"/>'
    b+=dust(22,8,900,1150,"#e8c6a0",.5)
    # wall thermometer
    b+='<rect x="600" y="820" width="260" height="900" rx="40" fill="#f3eee6" stroke="#cbbfb0" stroke-width="6"/>'
    b+='<rect x="700" y="880" width="60" height="660" rx="30" fill="#fff" stroke="#9a8f82" stroke-width="5"/>'
    b+='<rect x="712" y="940" width="36" height="620" rx="18" fill="#d6453d"/><circle cx="730" cy="1610" r="62" fill="#d6453d" stroke="#9a8f82" stroke-width="5"/>'
    for i,t in enumerate(range(50,-10,-10)):
        y=930+i*120; b+=f'<line x1="770" y1="{y}" x2="800" y2="{y}" stroke="#6b6157" stroke-width="5"/><text x="808" y="{y+10}" font-family="DejaVu Sans" font-weight="bold" font-size="28" fill="#6b6157">{t}</text>'
    b+='<path d="M620,980 l24,-26 l24,26" stroke="#d6453d" stroke-width="8" fill="none" stroke-linecap="round"/>'
    save("09_zhara", svg(b,"<defs>"+d+"</defs>"))

# ---------- 10. empty fridge
def s10():
    b=f'<rect width="{W}" height="{H}" fill="#1b1d26"/>'
    b+='<polygon points="300,560 760,560 1080,1920 0,1920" fill="#dfe9f2" opacity=".22"/>'
    b+='<rect x="300" y="360" width="460" height="1120" rx="24" fill="#c9cfd6"/><rect x="330" y="400" width="400" height="1040" fill="#f2f7fb"/>'
    for y in (640,880,1120): b+=f'<rect x="330" y="{y}" width="400" height="12" fill="#cfdae3"/>'
    b+='<rect x="580" y="1340" width="120" height="90" rx="8" fill="#e3e9ee"/><circle cx="420" cy="1395" r="16" fill="#e9e1cf"/>'
    b+='<path d="M760,370 l170,-60 v1260 l-170,-90z" fill="#aeb5bd"/>'
    for y in (520,800,1100): b+=f'<rect x="785" y="{y}" width="120" height="16" rx="4" fill="#8f979f"/>'
    b+='<rect x="900" y="840" width="12" height="240" rx="6" fill="#6f777f"/>'
    b+=person(250,1840,1.55,"#3c4659",head="#c9a98e")
    save("10_holodilnik", svg(b))

# ---------- 11. gas station at night
def s11():
    b=f'<rect width="{W}" height="{H}" fill="#2a2c33"/>'
    b+=f'<g opacity=".55">{buildings(1100,0,seed=14,col="#4d4f57",win="#6b6a62",lit=.08)}</g>'
    b+=f'<rect y="1100" width="{W}" height="820" fill="#3a3c43"/>'
    b+='<polygon points="140,760 940,760 1080,1920 0,1920" fill="#fff4cf" opacity=".12"/>'
    b+='<rect x="120" y="680" width="840" height="90" fill="#e9ecef"/><rect x="120" y="760" width="840" height="20" fill="#d6453d"/>'
    b+='<rect x="160" y="780" width="760" height="12" fill="#fff6d8" filter="url(#glow)"/>'
    for x in (300,760): b+=f'<rect x="{x-22}" y="780" width="44" height="560" fill="#cfd4da"/>'
    for x in (430,640):
        b+=f'<rect x="{x-60}" y="1040" width="120" height="300" rx="12" fill="#f0f2f4"/><rect x="{x-44}" y="1070" width="88" height="70" rx="6" fill="#2c7a8c"/><rect x="{x-60}" y="1260" width="120" height="30" fill="#d6453d"/>'
    b+='<rect x="860" y="400" width="140" height="300" rx="10" fill="#e9ecef"/><text x="930" y="490" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="32" fill="#1c1f26">95</text><text x="930" y="560" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="32" fill="#e8a33a">59.9</text><text x="930" y="630" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="32" fill="#1c1f26">92</text>'
    # car
    b+='<rect x="200" y="1480" width="520" height="150" rx="50" fill="#4f6a8f"/><path d="M290,1480 q40,-110 140,-110 h120 q80,0 120,110z" fill="#4f6a8f"/><path d="M330,1475 q30,-80 100,-80 h110 q60,0 90,80z" fill="#a9c3d6"/>'
    b+='<circle cx="320" cy="1640" r="56" fill="#1c1f26"/><circle cx="620" cy="1640" r="56" fill="#1c1f26"/><rect x="690" y="1520" width="40" height="30" rx="8" fill="#fff4cf"/>'
    save("11_zapravka", svg(b))

# ---------- 12. rot
def s12():
    b=f'<rect width="{W}" height="{H}" fill="#6f665c"/>'
    b+=f'<rect y="1100" width="{W}" height="820" fill="#5b5249"/>'
    random.seed(9)
    b+='<path d="M120,1500 q140,-380 420,-420 q300,40 420,420 z" fill="#5a4a36"/>'
    for i in range(70):
        x=random.randint(200,880); y=random.randint(1180,1490)
        c=random.choice(["#7d6a45","#8a7550","#6b5a3d","#9a7a52"])
        b+=f'<ellipse cx="{x}" cy="{y}" rx="{random.randint(20,46)}" ry="{random.randint(10,20)}" fill="{c}" transform="rotate({random.randint(-40,40)} {x} {y})"/>'
    for i in range(45):
        x=random.randint(220,860); y=random.randint(1200,1480); r=random.randint(8,30)
        b+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="{random.choice(["#e8e4d2","#cfd9b8","#b9c9c4"])}" opacity="{random.uniform(.5,.9):.2f}"/>'
    for (x,y) in [(380,1200),(620,1170),(760,1290)]:
        b+=f'<rect x="{x-8}" y="{y-60}" width="16" height="60" fill="#efe6d4"/><ellipse cx="{x}" cy="{y-64}" rx="40" ry="22" fill="#c9a77a"/>'
    b+=dust(31,6,1000,1300,"#9c9184",.35)
    save("12_gnienie", svg(b))

# ---------- 13. last blade at dawn
def s13():
    d=sky("sk","#8f8d96","#d7b59a")
    b=f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b+='<circle cx="540" cy="1020" r="130" fill="#f2d2a8" opacity=".7"/>'
    b+=f'<g opacity=".85">{buildings(1060,0,seed=17,col="#8c8a8f",win="#b8ab98",lit=.05)}</g>'
    b+=f'<rect y="1060" width="{W}" height="860" fill="#7d7a78"/>'
    b+='<path d="M540,1920 L560,1700 L520,1560 L548,1430 L530,1300" stroke="#4f4c4a" stroke-width="12" fill="none" stroke-linejoin="round"/>'
    b+='<path d="M560,1700 L700,1640 L780,1680 M520,1560 L380,1520" stroke="#4f4c4a" stroke-width="7" fill="none"/>'
    b+='<path d="M548,1440 q-6,-120 -40,-230" stroke="#5DA858" stroke-width="14" stroke-linecap="round" fill="none" filter="url(#glow)"/>'
    b+='<path d="M552,1440 q10,-80 46,-140" stroke="#6dbb66" stroke-width="10" stroke-linecap="round" fill="none"/>'
    b+='<rect x="380" y="260" width="320" height="140" rx="22" fill="#1c1f26" opacity=".85"/><text x="540" y="360" text-anchor="middle" font-family="DejaVu Sans Mono" font-weight="bold" font-size="96" fill="#f3f1ea">06:00</text>'
    save("13_poslednyaya_travinka", svg(b,"<defs>"+d+"</defs>"))

# ---------- 14. grey city
def s14():
    d=sky("sk","#9a9894","#c4b8a8")
    b=f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
    b+=buildings(1250,0,seed=21,col="#8f8c88",win="#a39d94",lit=.05)
    b+=f'<g opacity=".9">{buildings(1500,0,seed=22,col="#77736f",win="#8c867f",lit=.03)}</g>'
    b+=f'<rect y="1500" width="{W}" height="420" fill="#8e7f70"/>'
    b+=dust(41,14,1100,1700,"#b5a796",.45)
    save("14_seryy_gorod", svg(b,"<defs>"+d+"</defs>"))

# ---------- 15. sprout
def s15():
    b=f'<rect width="{W}" height="{H}" fill="#a29d97"/>'
    b+='<rect x="140" y="260" width="800" height="1000" rx="14" fill="#b9b3ab"/>'
    b+=f'<g opacity=".7">{buildings(1260,0,seed=4,col="#8f8b86",win="#a09a91",lit=.05)}</g>'
    # curtain being drawn from left
    b+='<path d="M60,200 h560 q-30,300 0,560 q-30,300 0,560 h-560z" fill="#6f6a66"/>'
    for x in range(110,600,90): b+=f'<path d="M{x},210 q-20,560 0,1110" stroke="#5c5753" stroke-width="10" fill="none"/>'
    b+='<rect x="40" y="190" width="1000" height="24" rx="12" fill="#5c5753"/>'
    b+='<rect x="60" y="1260" width="960" height="70" rx="10" fill="#c3bdb5"/><rect x="0" y="1330" width="1080" height="590" fill="#8f8a84"/>'
    b+='<path d="M620,1060 h240 l-30,200 h-180 z" fill="#8a7e75"/><rect x="605" y="1040" width="270" height="44" rx="10" fill="#958a80"/><ellipse cx="740" cy="1046" rx="118" ry="14" fill="#4a3f38"/>'
    b+='<circle cx="740" cy="960" r="150" fill="#7be27a" opacity=".22" filter="url(#blur30)"/>'
    b+='<path d="M740,1046 q-6,-70 4,-120" stroke="#5DA858" stroke-width="12" stroke-linecap="round" fill="none" filter="url(#glow)"/>'
    b+='<path d="M744,940 q-80,-60 -110,10 q60,30 110,-10z" fill="#6cc463" filter="url(#glow)"/><path d="M746,930 q70,-80 120,-20 q-60,50 -120,20z" fill="#7bd472" filter="url(#glow)"/>'
    random.seed(5)
    for i in range(14): b+=f'<circle cx="{random.randint(640,840)}" cy="{random.randint(820,1030)}" r="{random.randint(3,7)}" fill="#c8ffc0" opacity="{random.uniform(.4,.9):.2f}"/>'
    save("15_rostok", svg(b))

# ---------- 16. title card
def s16():
    b=f'<rect width="{W}" height="{H}" fill="#121318"/>'
    random.seed(1)
    for i in range(60): b+=f'<circle cx="{random.randint(0,W)}" cy="{random.randint(0,H)}" r="{random.uniform(1,3.5):.1f}" fill="#d8cbb8" opacity="{random.uniform(.15,.5):.2f}"/>'
    b+='<text x="540" y="820" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="92" fill="#e9e4da">ЧТО ЕСЛИ…</text>'
    b+='<text x="540" y="960" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="84" fill="#e9e4da">ИСЧЕЗНУТ</text>'
    b+='<text x="540" y="1090" text-anchor="middle" font-family="DejaVu Serif" font-weight="bold" font-size="84" fill="#e9e4da">РАСТЕНИ<tspan fill="#6cc463" filter="url(#glow)">Я</tspan></text>'
    b+='<line x1="380" y1="1160" x2="700" y2="1160" stroke="#6b665e" stroke-width="3"/>'
    b+='<text x="540" y="1260" text-anchor="middle" font-family="DejaVu Sans" font-size="38" fill="#b9b2a6">Что бы ты сделал</text>'
    b+='<text x="540" y="1312" text-anchor="middle" font-family="DejaVu Sans" font-size="38" fill="#b9b2a6">с последним растением на Земле?</text>'
    save("16_zastavka", svg(b))

if __name__=='__main__':
  for f in [s01,s02,s03,s04,s05,s06,s07,s08,s09,s10,s11,s12,s13,s14,s15,s16]: f(); print(f.__name__)
