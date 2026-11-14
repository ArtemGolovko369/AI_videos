"""Выравнивание текста озвучки по паузам (без ASR): ffmpeg silencedetect + DP.
Результат: audio/words.json — [[start, end, word], ...]"""
import re, subprocess, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
AUD = os.path.join(ROOT, "audio/voice.mp3")
TEXT = open(os.path.join(ROOT, "audio/voice.txt")).read()

dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",AUD]))
log = subprocess.run(["ffmpeg","-hide_banner","-i",AUD,"-af","silencedetect=noise=-38dB:d=0.12","-f","null","-"],capture_output=True,text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
segs=[]; cur=0.0
for a,b in zip(st,en):
    if a-cur>0.05: segs.append((cur,a))
    cur=b
if dur-cur>0.05: segs.append((cur,dur))
# фразы: режем по . ! ? … , — :
toks = re.findall(r"[^.!?…,—:]+[.!?…,—:»]*", TEXT.replace("\n"," "))
phr = [t.strip(" .") .strip() for t in toks if re.search(r"\w", t)]
phr = [re.sub(r"^[.…\s]+","",p) for p in phr]
def ch(p): return len(re.sub(r"[^\wё]","",p.lower()))+2
C=[ch(p) for p in phr]; D=[b-a for a,b in segs]
rate=sum(D)/sum(C)
INF=1e18; n,m=len(phr),len(segs)
dp=[[INF]*(m+1) for _ in range(n+1)]; bk={}
dp[0][0]=0
for i in range(n):
    for j in range(m):
        if dp[i][j]>=INF: continue
        for i2 in range(i+1,min(n,i+4)+1):
            for j2 in range(j+1,min(m,j+5)+1):
                d=segs[j2-1][1]-segs[j][0]; c=sum(C[i:i2])*rate
                cost=dp[i][j]+(d-c)**2/max(c,.3)+0.15*(i2-i-1)
                if cost<dp[i2][j2]: dp[i2][j2]=cost; bk[(i2,j2)]=(i,j)
i,j=n,m; groups=[]
while (i,j)!=(0,0):
    pi,pj=bk[(i,j)]; groups.append((pi,i,pj,j)); i,j=pi,pj
groups.reverse()
words=[]; phrases=[]
for (a,b,sa,sb) in groups:
    t0,t1=segs[sa][0],segs[sb-1][1]
    ps=phr[a:b]; tot=sum(C[a:b]); t=t0
    for p in ps:
        pd=(t1-t0)*ch(p)/tot; phrases.append([round(t,2),round(t+pd,2),p])
        ws=p.split(); wc=[ch(w) for w in ws]; tw=t
        for w,c in zip(ws,wc):
            wd=pd*c/sum(wc); words.append([round(tw,2),round(tw+wd,2),w]); tw+=wd
        t+=pd
json.dump(words,open(os.path.join(ROOT,"audio/words.json"),"w"),ensure_ascii=False,indent=0)
json.dump(phrases,open(os.path.join(ROOT,"audio/phrases.json"),"w"),ensure_ascii=False,indent=0)
for p in phrases: print(f"{p[0]:6.2f}-{p[1]:6.2f}  {p[2]}")
