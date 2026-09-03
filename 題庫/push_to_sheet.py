# -*- coding: utf-8 -*-
"""把建好的 TSV 直接寫進 Google Sheet（透過 GAS v2 的 doPost），不再用剪貼簿。
用法（在 題庫/ 目錄）：
  python push_to_sheet.py questions 4          # 把 tsv/Questions_batch4.tsv 接在 Questions 最後（id 重複會跳過）
  python push_to_sheet.py changelog 4          # 把 Changelog 中「建立批次4」那列接在最後
  python push_to_sheet.py laws                 # 用 tsv/Laws.tsv 的 law_version+source_url 覆寫 Laws!F2:G62（依 Sheet 順序）
  python push_to_sheet.py raw Config A2 "key\tvalue"   # 任意分頁、任意起始格，range 模式
密鑰：環境變數 QUIZ_IMPORT_TOKEN，或 ../gas/.token 檔（已 gitignore），要和 Sheet Config 分頁 import_token 相同。
"""
import sys, os, json, urllib.request
URL = "https://script.google.com/macros/s/AKfycbw8GLA29GyEC4hLyXCZoaRBrG3mgJl389Tye47b8XARo-2fKs3rY6Jbfcm6Uxe0ewDM/exec"

def token():
    t = os.environ.get("QUIZ_IMPORT_TOKEN") or (open(os.path.join(os.path.dirname(__file__), "..", "gas", ".token"), encoding="utf-8").read().strip() if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "gas", ".token")) else "")
    if not t: sys.exit("缺少密鑰：設定環境變數 QUIZ_IMPORT_TOKEN 或建立 gas/.token")
    return t

def post(payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "text/plain;charset=utf-8"})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read().decode("utf-8")
    try: return json.loads(body)
    except Exception: return {"ok": False, "error": body[:300]}

def read(p): return [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()]

def main(a):
    if not a: sys.exit(__doc__)
    cmd = a[0]
    if cmd == "questions":
        rows = read(f"tsv/Questions_batch{a[1]}.tsv")
        print(post({"token": token(), "sheet": "Questions", "mode": "append", "tsv": "\n".join(rows)}))
    elif cmd == "changelog":
        rows = [r for r in read("tsv/Changelog.tsv") if f"建立批次{a[1]}" in r]
        print(post({"token": token(), "sheet": "Changelog", "mode": "append", "tsv": "\n".join(rows)}))
    elif cmd == "laws":
        laws = [r.split("\t") for r in read("tsv/Laws.tsv")][1:]
        order = [l for l in laws if l[0].startswith("OSH") and l[0] != "OSH-36"] + [l for l in laws if l[0].startswith("ENV")] + [l for l in laws if l[0] == "OSH-36"]
        assert len(order) == 61, len(order)
        print(post({"token": token(), "sheet": "Laws", "mode": "range", "startCell": "F2", "tsv": "\n".join(l[5] + "\t" + l[6] for l in order)}))
    elif cmd == "raw":
        print(post({"token": token(), "sheet": a[1], "mode": "range", "startCell": a[2], "tsv": a[3]}))
    elif cmd == "ping":
        with urllib.request.urlopen(URL + "?ping=1") as r: print(r.read().decode())
    else: sys.exit(__doc__)

if __name__ == "__main__": main(sys.argv[1:])
