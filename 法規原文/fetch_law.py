import sys, subprocess
from bs4 import BeautifulSoup
def fetch(code, name):
    subprocess.run(["curl","-sL","-A","Mozilla/5.0",f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={code}","-o",f"{code}.html"],check=True)
    s=BeautifulSoup(open(f"{code}.html",encoding="utf-8").read(),"lxml")
    title=(s.select_one("#hlLawName") or s.select_one("a.law-ch"))
    title=title.get_text(strip=True) if title else "?"
    date=""
    for th in s.select("th"):
        if "修正日期" in th.get_text() or "公發布日" in th.get_text():
            td=th.find_next("td"); date=td.get_text(strip=True) if td else ""; break
    out=[f"# {name}（{code}）修正日期：{date}\n"]
    for el in s.select("div.row, div.h3, div.char-1, div.char-2, div.char-3"):
        if 'row' in el.get('class',[]):
            no=el.select_one(".col-no"); data=el.select_one(".col-data")
            if not no or not data: continue
            lines=[ln.strip() for ln in data.get_text("\n").split("\n") if ln.strip()]
            out.append(f"{no.get_text(strip=True)}\n"+"\n".join(lines)+"\n")
        else: out.append("## "+el.get_text(strip=True)+"\n")
    txt="\n".join(out); open(f"{name}.txt","w",encoding="utf-8").write(txt)
    print(f"{code} title={title} | {name} | {date} | articles={sum(1 for o in out if o.startswith('第'))} chars={len(txt)} lines={txt.count(chr(10))}")
for code,name in [a.split("=") for a in sys.argv[1:]]:
    fetch(code,name)
