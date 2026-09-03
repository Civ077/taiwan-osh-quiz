import sys, subprocess, urllib.parse, re, json, time
from bs4 import BeautifulSoup
def find(name):
    url="https://law.moj.gov.tw/Law/LawSearchResult.aspx?ty=ONEBAR&kw="+urllib.parse.quote(name)
    html=subprocess.run(["curl","-sL","-A","Mozilla/5.0",url],capture_output=True).stdout.decode("utf-8","ignore")
    s=BeautifulSoup(html,"lxml")
    hits=[]
    for a in s.select("a[href*='pcode=']"):
        t=a.get_text(strip=True); m=re.search(r"pcode=([A-Z0-9]+)",a["href"])
        if m and t: hits.append((t,m.group(1)))
    exact=[h for h in hits if h[0]==name]
    return (exact[0] if exact else (hits[0] if hits else (None,None))), hits[:4]
res={}
for name in sys.argv[1:]:
    (t,p),hits=find(name); res[name]=p
    print(f"{name} -> {p} ({t})" + ("" if t==name else f"  hits={hits}"))
    time.sleep(0.3)
json.dump(res,open("_pcodes.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
