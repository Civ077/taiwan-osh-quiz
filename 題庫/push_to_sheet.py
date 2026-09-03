# -*- coding: utf-8 -*-
"""把建好的 TSV 直接寫進 Google Sheet（透過 GAS v2 的 doPost），不再用剪貼簿。
用法（在 題庫/ 目錄）：
  python push_to_sheet.py ping                 # 應回 {"ok":true,"version":3,...}
  python push_to_sheet.py questions 4          # 把 tsv/Questions_batch4.tsv 接在 Questions 最後（id 重複會跳過）
  python push_to_sheet.py changelog 4          # 把 Changelog 中「建立批次4」那列接在最後
  python push_to_sheet.py laws                 # 用 tsv/Laws.tsv 的 law_version+source_url 覆寫 Laws!F2:G62（依 Sheet 順序）
  python push_to_sheet.py sync                 # 整批同步：用本地 tsv/Questions.tsv 覆寫 Questions!A2 起的 A–U 欄（題目內容），
                                               #   不動 V–Y 欄（status/batch/reviewer/review_note）；新題的 status/batch 只在空白時補上
  python push_to_sheet.py raw Config A2 "key<TAB>value"   # 任意分頁、任意起始格，range 模式
密鑰：環境變數 QUIZ_IMPORT_TOKEN，或 ../gas/.token 檔（已 gitignore），要和試算表選單「知識王 → 設定匯入密鑰」輸入的密碼相同。
"""
import sys, os, json, urllib.request

URL = "https://script.google.com/macros/s/AKfycbw8GLA29GyEC4hLyXCZoaRBrG3mgJl389Tye47b8XARo-2fKs3rY6Jbfcm6Uxe0ewDM/exec"
HERE = os.path.dirname(os.path.abspath(__file__))
TAB, NL = "\t", "\n"


def token():
    t = os.environ.get("QUIZ_IMPORT_TOKEN", "")
    f = os.path.join(HERE, "..", "gas", ".token")
    if not t and os.path.exists(f):
        t = open(f, encoding="utf-8").read().strip()
    if not t:
        sys.exit("缺少密鑰：設定環境變數 QUIZ_IMPORT_TOKEN 或建立 gas/.token")
    return t


def post(payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "text/plain;charset=utf-8"})
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read().decode("utf-8")
    try:
        return json.loads(body)
    except Exception:
        return {"ok": False, "error": body[:300]}


def read(name):
    p = os.path.join(HERE, name)
    return [l for l in open(p, encoding="utf-8").read().split(NL) if l.strip()]


def laws_in_sheet_order():
    laws = [r.split(TAB) for r in read("tsv/Laws.tsv")][1:]
    order = ([l for l in laws if l[0].startswith("OSH") and l[0] != "OSH-36"]
             + [l for l in laws if l[0].startswith("ENV")]
             + [l for l in laws if l[0] == "OSH-36"])
    assert len(order) == 61, len(order)
    return order


def main(a):
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "ping":
        with urllib.request.urlopen(URL + "?ping=1") as r:
            print(r.read().decode())
    elif cmd == "questions":
        rows = read("tsv/Questions_batch%s.tsv" % a[1])
        print(post({"token": token(), "sheet": "Questions", "mode": "append", "tsv": NL.join(rows)}))
    elif cmd == "changelog":
        rows = [r for r in read("tsv/Changelog.tsv") if ("建立批次%s" % a[1]) in r]
        print(post({"token": token(), "sheet": "Changelog", "mode": "append", "tsv": NL.join(rows)}))
    elif cmd == "laws":
        order = laws_in_sheet_order()
        tsv = NL.join(l[5] + TAB + l[6] for l in order)
        print(post({"token": token(), "sheet": "Laws", "mode": "range", "startCell": "F2", "tsv": tsv}))
    elif cmd == "sync":
        rows = [r.split(TAB) for r in read("tsv/Questions.tsv")]
        if rows and rows[0][0] == "id":
            rows = rows[1:]
        content = NL.join(TAB.join(r[:21]) for r in rows)           # A–U：id … explain_en
        print("內容欄 A–U：", post({"token": token(), "sheet": "Questions", "mode": "range", "startCell": "A2", "tsv": content}))
        fill = NL.join(r[0] + TAB + r[21] + TAB + r[22] for r in rows)   # id, status, batch
        print("補新題 status/batch：", post({"token": token(), "sheet": "Questions", "mode": "fill_status", "tsv": fill}))
    elif cmd == "raw":
        print(post({"token": token(), "sheet": a[1], "mode": "range", "startCell": a[2], "tsv": a[3].replace("<TAB>", TAB)}))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
