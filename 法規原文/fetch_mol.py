# 從勞動部勞動法令查詢系統抓行政規則（要點）：python fetch_mol.py FL024857=違反職業安全衛生法及勞動檢查法案件處理要點 ...
# 輸出 <名稱>.txt，格式與 fetch_law.py 相同（# 名稱（FL編號）修正日期：…）
import sys, subprocess, re
from bs4 import BeautifulSoup

def fetch(fid, name):
    url = f"https://laws.mol.gov.tw/FLAW/FLAWDAT0202.aspx?id={fid}"
    subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", url, "-o", f"{fid}.html"], check=True)
    s = BeautifulSoup(open(f"{fid}.html", encoding="utf-8").read(), "lxml")
    text = s.get_text("\n")
    m = re.search(r"\(民國\s*([\d\s年月日]+?)(?:修正|訂定|發布)\)", text)
    date = ("民國 " + re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""
    out = [f"# {name}（{fid}）修正日期：{date}\n"]
    nos = s.select(".col-no"); datas = s.select(".col-data")
    for no, data in zip(nos, datas):
        lines = [ln.strip() for ln in data.get_text("\n").split("\n") if ln.strip()]
        body = "\n".join(lines)
        # 行政規則以「一、二、…」為點次；標成「第 N 點」方便引用
        out.append(f"第 {no.get_text(strip=True)} 點\n{body}\n")
    txt = "\n".join(out)
    open(f"{name}.txt", "w", encoding="utf-8").write(txt)
    # 附件連結（PDF/ODT）
    links = [(a.get_text(strip=True), a.get("href")) for a in s.select("a[href]") if re.search(r"\.(pdf|odt|doc|docx)$", a.get("href", ""), re.I) or "GetFile" in a.get("href", "")]
    print(f"{fid} | {name} | {date} | points={len(nos)} chars={len(txt)} annex_links={len(links)}")
    return links

for arg in sys.argv[1:]:
    fid, name = arg.split("=", 1)
    fetch(fid, name)
