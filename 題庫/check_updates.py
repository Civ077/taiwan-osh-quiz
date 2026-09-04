# -*- coding: utf-8 -*-
"""檢查全國法規資料庫是否有比本地原文更新的版本：
  python check_updates.py            # 全部範圍內法規（約 258 部，需數分鐘）
  python check_updates.py ENV-01 OSH-07
輸出：_spec/法規更新檢查.tsv（law_id, 名稱, 本地日期, 線上日期, 狀態）；狀態 UPDATED 者用
  python ../法規原文/fetch_law.py <pcode>=<名稱> 重抓，再用 python coverage.py 看新條文是否缺題。
"""
import sys, os, re, json, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_sheet as bs
SRC = os.path.join(os.path.dirname(HERE), "法規原文")
PC = json.load(open(os.path.join(SRC, "pcodes.json"), encoding="utf-8"))

def local_date(zh):
    p = os.path.join(SRC, zh + ".txt")
    if not os.path.exists(p): return ""
    head = open(p, encoding="utf-8").read(400)
    m = re.search(r"民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日", head)
    return "%03d-%02d-%02d" % tuple(int(x) for x in m.groups()) if m else ""

def online_date(pcode):
    url = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=" + pcode
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(3):
        try:
            html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
            break
        except Exception as e:
            if attempt == 2: return "ERR:" + str(e)[:40]
            time.sleep(3)
    # 修正日期／發布日期／廢止日期（頁面「法規內容」表格）
    m = re.search(r"(修正|發布|訂定|廢止|制定)日期[^民]*民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日", html)
    if not m: return "ERR:no-date"
    d = "%03d-%02d-%02d" % (int(m.group(2)), int(m.group(3)), int(m.group(4)))
    if m.group(1) == "廢止": d = "廢止 " + d
    return d

def main(ids):
    laws = [("OSH-%02d" % i, zh) for i, (zh, *_) in enumerate(bs.OSH_LAWS, 1)] + \
           [("ENV-%02d" % i, zh) for i, (zh, *_) in enumerate(bs.ENV_LAWS, 1)]
    laws = [(lid, zh) for lid, zh in laws if bs.in_scope(lid) and (not ids or lid in ids)]
    rows = []; upd = []
    for lid, zh in laws:
        code = PC.get(zh, "").split(":")[-1]
        if not code or zh == "營建剩餘土石方處理方案":
            rows.append((lid, zh, local_date(zh), "", "SKIP")); continue
        loc, onl = local_date(zh), online_date(code)
        st = "ERR" if onl.startswith("ERR") else ("REPEALED" if onl.startswith("廢止") else ("UPDATED" if onl > loc else "OK"))
        rows.append((lid, zh, loc, onl, st))
        if st != "OK": upd.append((lid, zh, loc, onl, st))
        print(lid, zh, loc, onl, st, flush=True)
        time.sleep(0.5)
    os.makedirs(os.path.join(HERE, "_spec"), exist_ok=True)
    with open(os.path.join(HERE, "_spec", "法規更新檢查.tsv"), "w", encoding="utf-8") as f:
        f.write("law_id\tname\tlocal\tonline\tstatus\n" + "\n".join("\t".join(r) for r in rows) + "\n")
    print("\n檢查 %d 部：需更新／異常 %d 部" % (len(rows), len(upd)))
    for r in upd: print(" ", *r)

if __name__ == "__main__":
    main(sys.argv[1:])
