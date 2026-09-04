# -*- coding: utf-8 -*-
"""檢查全國法規資料庫是否有比本地原文更新的版本（快速版：先抓各「目」的清單頁，一頁就有幾十部法規的修正日期）
  python check_updates.py            # 全部範圍內法規
  python check_updates.py ENV-01 OSH-07
輸出：_spec/法規更新檢查.tsv（law_id, 名稱, 本地日期, 線上日期, 狀態）
狀態 UPDATED 者：python ../法規原文/fetch_law.py <pcode>=<名稱> 重抓 → python coverage.py 看新條文是否缺題 → 補題後 build/sync。
"""
import sys, os, re, json, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_sheet as bs
SRC = os.path.join(os.path.dirname(HERE), "法規原文")
PC = json.load(open(os.path.join(SRC, "pcodes.json"), encoding="utf-8"))
CATS = ["04010005", "04010006", "04010007", "04013001", "04013002", "04013003", "04013004", "04013005",
        "04013006", "04013007", "04013008", "04013009", "04013010"]
DATE = re.compile(r"民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日")

def curl(url, max_time=120):
    for attempt in range(3):
        r = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", str(max_time), url], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 2000:
            return r.stdout.decode("utf-8", "ignore")
        time.sleep(3)
    return ""

def fmt(m):
    return "%03d-%02d-%02d" % tuple(int(x) for x in m.groups())

def local_date(zh):
    p = os.path.join(SRC, zh + ".txt")
    if not os.path.exists(p): return ""
    m = DATE.search(open(p, encoding="utf-8").read(400))
    return fmt(m) if m else ""

def category_dates():
    """各目清單頁：<a ... href="...PCode=N0060002">名稱</a> (民國 115 年 06 月 26 日 ) → {pcode: date}"""
    out = {}
    for ty in CATS:
        html = curl("https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=" + ty)
        n = 0
        for m in re.finditer(r'PCode=([A-Z]\d{7})"[^>]*>[^<]*</a>\s*\(\s*民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日', html, re.I):
            out[m.group(1)] = "%03d-%02d-%02d" % (int(m.group(2)), int(m.group(3)), int(m.group(4))); n += 1
        print("目", ty, "→", n, "部", flush=True)
    return out

def law_page_date(pcode):
    html = curl("https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=" + pcode)
    if not html: return "ERR:curl"
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, "lxml")
    for th in s.select("th"):
        tt = th.get_text()
        if any(k in tt for k in ("修正日期", "公發布日", "公布日期", "發布日期", "廢止日期", "廢/停止適用日期")):
            td = th.find_next("td"); m = DATE.search(td.get_text(" ", strip=True) if td else "")
            if m: return ("廢止 " if "廢" in tt else "") + fmt(m)
    return "ERR:no-date"

def main(ids):
    laws = [("OSH-%02d" % i, zh) for i, (zh, *_) in enumerate(bs.OSH_LAWS, 1)] + \
           [("ENV-%02d" % i, zh) for i, (zh, *_) in enumerate(bs.ENV_LAWS, 1)]
    laws = [(lid, zh) for lid, zh in laws if bs.in_scope(lid) and (not ids or lid in ids)]
    cat = category_dates() if not ids else {}
    rows, upd = [], []
    for lid, zh in laws:
        code = PC.get(zh, "").split(":")[-1]
        if not code or zh == "營建剩餘土石方處理方案":
            rows.append((lid, zh, local_date(zh), "", "SKIP")); continue
        loc = local_date(zh)
        onl = cat.get(code) or law_page_date(code)
        st = "ERR" if onl.startswith("ERR") else ("REPEALED" if onl.startswith("廢止") else ("UPDATED" if onl > loc else "OK"))
        rows.append((lid, zh, loc, onl, st))
        if st != "OK": upd.append((lid, zh, loc, onl, st)); print(lid, zh, loc, onl, st, flush=True)
    os.makedirs(os.path.join(HERE, "_spec"), exist_ok=True)
    with open(os.path.join(HERE, "_spec", "法規更新檢查.tsv"), "w", encoding="utf-8") as f:
        f.write("law_id\tname\tlocal\tonline\tstatus\n" + "\n".join("\t".join(r) for r in rows) + "\n")
    print("\n檢查 %d 部：OK %d、需更新／異常 %d" % (len(rows), sum(1 for r in rows if r[4] == "OK"), len(upd)))
    for r in upd: print(" ", *r)

if __name__ == "__main__":
    main(sys.argv[1:])
