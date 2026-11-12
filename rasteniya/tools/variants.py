import runpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(HERE, "draw.py"), run_name="lib")
src = open(os.path.join(HERE, "draw.py")).read()
save = L['save']
def patched(fn_name, out_name, repl):
    # re-exec function source with string replacements
    start = src.index(f"def {fn_name}():"); end = src.index("\n# ----------", start)
    code = src[start:end]
    for a,b in repl: 
        assert a in code, (fn_name, a[:40]); code = code.replace(a,b)
    code = code.replace(f'save("', f'save("{out_name}__', 1)
    ns = dict(L); exec(code, ns); ns[fn_name]()
# originals
for n in ["s01","s02","s03","s04","s05","s06","s07","s08","s09","s10","s11","s12","s13","s14","s15","s16"]:
    L[n]()
# 01a: full cactus, no sparkles
patched("s01","A",[("<g opacity=\".28\">","<g opacity=\"1\">"),("for i in range(26)","for i in range(0)")])
# 13b: blade gone
patched("s13","B",[("filter=\"url(#glow)\"/>\n","/>\n")] if False else [("stroke=\"#5DA858\" stroke-width=\"14\"","stroke=\"#5DA858\" stroke-width=\"0\""),("stroke=\"#6dbb66\" stroke-width=\"10\"","stroke=\"#6dbb66\" stroke-width=\"0\"")])
# 15a: empty pot, no curtain ; 15b: sprout, no curtain
nocurtain=[("b+='<path d=\"M60,200 h560","b+='<!--'+'<path d=\"M60,200 h560"),("<rect x=\"40\" y=\"190\" width=\"1000\" height=\"24\" rx=\"12\" fill=\"#5c5753\"/>'","<rect x=\"40\" y=\"190\" width=\"1000\" height=\"24\" rx=\"12\" fill=\"#5c5753\"/>-->'"),("for x in range(110,600,90): b+=","for x in range(0): b+=")]
patched("s15","B",nocurtain)
patched("s15","A",nocurtain+[("b+='<circle cx=\"740\" cy=\"960\" r=\"150\"","b+='<!--'+'<circle cx=\"740\" cy=\"960\" r=\"150\""),("for i in range(14):","b+='-->'\n    for i in range(0):")])
# 11a: pharmacy — empty shelves, sign АПТЕКА with faded cross, no queue
patched("s06","C",[('font-size="54" fill="#8a7f6e">ХЛЕБ</text>','font-size="54" fill="#8a7f6e">АПТЕКА</text><rect x="330" y="160" width="64" height="20" fill="#7d8f80"/><rect x="352" y="138" width="20" height="64" fill="#7d8f80"/>'),
    ('fill="#d9b27a" opacity=".6"','fill="#e9e6df" opacity=".9"'),("for i in range(9):","for i in range(0):")])
