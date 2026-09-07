import sys, re
from bs4 import BeautifulSoup
for code, name in [("N0060001","職業安全衛生法"),("N0060002","職業安全衛生法施行細則")]:
    html = open(f"法規原文/{code}.html", encoding="utf-8").read()
    s = BeautifulSoup(html, "lxml")
    date = ""
    for th in s.select("th"):
        if "修正日期" in th.get_text() or "公發布日" in th.get_text():
            td = th.find_next("td")
            if td: date = td.get_text(strip=True); break
    out = [f"# {name}（{code}）修正日期：{date}\n"]
    for row in s.select("div.row"):
        no = row.select_one(".col-no"); data = row.select_one(".col-data")
        if not no or not data: continue
        # preserve line/item structure
        lines = [ln.strip() for ln in data.get_text("\n").split("\n") if ln.strip()]
        out.append(f"{no.get_text(strip=True)}\n" + "\n".join(lines) + "\n")
    # chapter headings
    txt = "\n".join(out)
    open(f"法規原文/{name}.txt","w",encoding="utf-8").write(txt)
    print(name, date, "articles:", len(out)-1, "chars:", len(txt))
