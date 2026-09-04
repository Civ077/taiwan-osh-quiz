# -*- coding: utf-8 -*-
"""把建好的 TSV 直接寫進 Google Sheet（透過 GAS v2 的 doPost），不再用剪貼簿。
用法（在 題庫/ 目錄）：
  python push_to_sheet.py ping                 # 應回 {"ok":true,"version":3,...}
  python push_to_sheet.py questions 4          # 把 tsv/Questions_batch4.tsv 接在 Questions 最後（id 重複會跳過）
  python push_to_sheet.py changelog 4          # 把 Changelog 中「建立批次4」那列接在最後
  python push_to_sheet.py laws-all             # 用 tsv/Laws.tsv 覆寫 Laws!A2:I62 全部欄位（依 Sheet 順序）
  python push_to_sheet.py laws                 # 用 tsv/Laws.tsv 的 law_version+source_url 覆寫 Laws!F2:G62（依 Sheet 順序）
  python push_to_sheet.py approve ENV-01 active   # 審題：整部法規（可用 OSH-* / all）的 status 一次改成 active（或 draft/reviewed）
  python push_to_sheet.py sync-split / laws-split / articles-split   # 職安／環保分開的分頁（Questions_OSH…）；drop-combined 清舊合併分頁
  python push_to_sheet.py sync                 # 整批同步：用本地 tsv/Questions.tsv 覆寫 Questions!A2 起的 A–U 欄（題目內容），
                                               #   不動 V–Y 欄（status/batch/reviewer/review_note）；新題的 status/batch 只在空白時補上
  python push_to_sheet.py raw Config A2 "key<TAB>value"   # 任意分頁、任意起始格，range 模式
  python push_to_sheet.py articles             # 用 tsv/Articles.tsv 整張重灌 Articles 分頁（完整法條，需 GAS v5）
  python push_to_sheet.py clear Laws 200       # 刪除 Laws 第 200 列以後（需 GAS v5）
  python push_to_sheet.py reset-all            # 雲端 Questions/Laws/Changelog 全部清掉、用本地 tsv 重灌（需 GAS v5；審題狀態會被本地覆蓋）
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


def post(payload, _retry=3):
    """送到 GAS；遇到 HTTP 錯誤／連線中斷自動重試"""
    import time
    for attempt in range(_retry):
        try:
            return _post_once(payload)
        except Exception as e:                       # HTTPError 404/5xx、URLError、timeout
            if attempt == _retry - 1: raise
            print("  post 重試（%s）" % e); time.sleep(5)

def _post_once(payload):
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



import re as _re
_COERCE = _re.compile(r"""^(
    [=+\-@].*                                   # 會被當成公式
  | \d{1,3}(,\d{3})+(\.\d+)?                   # 1,000
  | \d+(\.\d+)?%?                              # 33.0 / 20%
  | \d{1,4}[-/.]\d{1,2}([-/.]\d{1,2})?          # 2026-09-04 / 7/1
  | \d{1,4}\s*年\s*\d{1,2}\s*月(\s*\d{1,2}\s*日)?   # 115年7月1日
  | \d{1,2}\s*[:：]\s*\d{1,2}(\s*[:：]\s*\d{1,2})?   # 07:00
)$""", _re.X)


def guard(v):
    """Google Sheets 會把「115年7月1日」「20%」「1,000」自動轉成日期或數字，存進去就走樣。
    在前面加一個半形單引號，Sheets 會存成純文字，讀回來時單引號不會出現。"""
    v = "" if v is None else str(v)
    return "'" + v if _COERCE.match(v.strip()) else v


def guard_row(cells):
    return [guard(c) for c in cells]

def laws_in_sheet_order():
    # Laws 分頁順序 = 本地 tsv/Laws.tsv 順序（依法規體系排序，由 build_sheet.FAMILIES 決定）
    return [r.split(TAB) for r in read("tsv/Laws.tsv")][1:]


def blank_tail(sheet, first_row, last_row, ncols):
    """把 first_row..last_row 以空字串覆寫（雲端 GAS 仍是 v3、沒有 clear_from 時用來清掉多餘舊列）"""
    if last_row < first_row:
        return {"ok": True, "skipped": "nothing to blank"}
    lines = [TAB.join([""] * ncols) for _ in range(last_row - first_row + 1)]
    lines[-1] = TAB.join([""] * (ncols - 1) + ["（以上為空白列，可整段刪除）"])   # range 模式會丟掉尾端全空列，最後一列放標記
    tsv = NL.join(lines)
    return post({"token": token(), "sheet": sheet, "mode": "range", "startCell": "A%d" % first_row, "tsv": tsv})


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
    elif cmd == "laws-all":
        # 含標題列，從 A1 覆寫；之後把多出來的舊列以空白覆寫（不需 GAS v5）
        order = laws_in_sheet_order()
        head = read("tsv/Laws.tsv")[0]
        rows = [head] + [TAB.join(r) for r in order]
        print("Laws A1 起：", post({"token": token(), "sheet": "Laws", "mode": "range", "startCell": "A1", "tsv": NL.join(rows)}))
        print("清空多餘列：", blank_tail("Laws", len(rows) + 1, 300, len(head.split(TAB))))
    elif cmd == "reset-all":
        # 雲端全部重灌（需 GAS v5）：Questions/Laws/Changelog 清掉舊列後用本地 tsv 重寫；Articles 另用 articles 指令
        print("Questions 清空：", post({"token": token(), "sheet": "Questions", "mode": "clear_from", "from": 2}))
        rows = read("tsv/Questions.tsv")
        step = 200
        for i in range(1, len(rows), step):
            r = post({"token": token(), "sheet": "Questions", "mode": "append", "tsv": NL.join(rows[i:i + step])})
            print("Questions %d-%d" % (i, i + step - 1), r if not r.get("ok") else r.get("lastRow"))
            if not r.get("ok"): sys.exit("中斷")
        main(["laws-all"])
        cl = read("tsv/Changelog.tsv")
        print("Changelog 清空：", post({"token": token(), "sheet": "Changelog", "mode": "clear_from", "from": 2}))
        print("Changelog：", post({"token": token(), "sheet": "Changelog", "mode": "append", "tsv": NL.join(cl[1:])}))
    elif cmd == "clear":
        print(post({"token": token(), "sheet": a[1], "mode": "clear_from", "from": int(a[2])}))
    elif cmd == "articles":
        # 用 tsv/Articles.tsv 整張重灌 Articles（需 GAS v5）；`articles 251` 表示不清空、從第 251 筆續灌；每塊失敗自動重試 3 次
        import time
        rows = read("tsv/Articles.tsv")
        start = int(a[1]) - 1 if len(a) > 1 else 0
        if start == 0:
            print("清空：", post({"token": token(), "sheet": "Articles", "mode": "clear_from", "from": 1, "create": True}))
        step = 250
        for i in range(start, len(rows), step):
            chunk = rows[i:i + step]
            for attempt in range(3):
                # 用 range 模式寫到固定列（重試不會重複寫入）；第 1 列為標題
                r = post({"token": token(), "sheet": "Articles", "mode": "range", "startCell": "A%d" % (i + 1), "tsv": NL.join(chunk)})
                if r.get("ok"):
                    break
                time.sleep(5)
            print("%d-%d" % (i + 1, i + len(chunk)), "ok" if r.get("ok") else r)
            if not r.get("ok"): sys.exit("中斷於 %d，可用 `articles %d` 續灌" % (i + 1, i + 1))
    elif cmd == "approve":
        # 審題：把某部法規（或 all）的題目 status 一次改成指定值。用法：approve ENV-01 active ／ approve OSH-* active ／ approve all draft
        # 依本地 tsv/Questions_<G>.tsv 的列順序定位（Sheet 分頁與本地同序），只寫 V 欄。
        import fnmatch
        target, st = a[1], (a[2] if len(a) > 2 else "active")
        for g in ("OSH", "ENV"):
            rows = [r.split(TAB) for r in read("tsv/Questions_%s.tsv" % g)][1:]
            hit = [i for i, r in enumerate(rows) if target == "all" or fnmatch.fnmatch(r[2], target)]
            if not hit: continue
            # 連續區段一次寫
            segs = []; s0 = hit[0]; prev = hit[0]
            for i in hit[1:]:
                if i != prev + 1: segs.append((s0, prev)); s0 = i
                prev = i
            segs.append((s0, prev))
            for s0, s1 in segs:
                r = post({"token": token(), "sheet": "Questions_" + g, "mode": "range", "startCell": "V%d" % (s0 + 2), "tsv": NL.join([st] * (s1 - s0 + 1))})
                print("Questions_%s 第 %d–%d 列 → %s：" % (g, s0 + 2, s1 + 2, st), "ok" if r.get("ok") else r)
    elif cmd == "sync-split":
        # 職安／環保分開：tsv/Questions_OSH.tsv → Questions_OSH、tsv/Questions_ENV.tsv → Questions_ENV（含標題，從 A1 覆寫；不存在則建立；
        # 500 列一塊、range 定位寫入可重試；之後補 status/batch（只補空白列）並刪掉多餘舊列。需 GAS v5+。
        import time
        for g in ("OSH", "ENV"):
            sheet = "Questions_" + g
            rows = read("tsv/Questions_%s.tsv" % g)
            head, body = rows[0], rows[1:]
            content = [head.split(TAB)[:21]] + [guard_row(r.split(TAB)[:21]) for r in body]      # A–U（加防轉型保護）
            print(sheet, "建立/確認：", post({"token": token(), "sheet": sheet, "mode": "range", "startCell": "A1", "tsv": TAB.join(content[0]), "create": True}))
            step = 500
            for i in range(1, len(content), step):
                chunk = content[i:i + step]
                for attempt in range(3):
                    r = post({"token": token(), "sheet": sheet, "mode": "range", "startCell": "A%d" % (i + 1), "tsv": NL.join(TAB.join(c) for c in chunk)})
                    if r.get("ok"): break
                    time.sleep(5)
                print(" %d-%d" % (i, i + len(chunk) - 1), "ok" if r.get("ok") else r)
                if not r.get("ok"): sys.exit("中斷")
            # V–Y 標題 + 補 status/batch
            hv = head.split(TAB)
            print(" 標題 V–Y：", post({"token": token(), "sheet": sheet, "mode": "range", "startCell": "V1", "tsv": TAB.join(hv[21:25])}))
            fill = NL.join(r.split(TAB)[0] + TAB + r.split(TAB)[21] + TAB + r.split(TAB)[22] for r in body)
            print(" 補 status/batch：", post({"token": token(), "sheet": sheet, "mode": "fill_status", "tsv": fill}))
            print(" 清多餘列：", post({"token": token(), "sheet": sheet, "mode": "clear_from", "from": len(content) + 1}))
    elif cmd == "laws-split":
        for g in ("OSH", "ENV"):
            sheet = "Laws_" + g
            rows = read("tsv/Laws_%s.tsv" % g)
            print(sheet, post({"token": token(), "sheet": sheet, "mode": "range", "startCell": "A1", "tsv": NL.join(rows), "create": True}))
            print(" 清多餘列：", post({"token": token(), "sheet": sheet, "mode": "clear_from", "from": len(rows) + 1}))
    elif cmd == "articles-split":
        import time
        for g in ("OSH", "ENV"):
            sheet = "Articles_" + g
            rows = read("tsv/Articles_%s.tsv" % g)
            print(sheet, "建立/確認：", post({"token": token(), "sheet": sheet, "mode": "range", "startCell": "A1", "tsv": rows[0], "create": True}))
            step = 250
            for i in range(1, len(rows), step):
                chunk = rows[i:i + step]
                for attempt in range(3):
                    r = post({"token": token(), "sheet": sheet, "mode": "range", "startCell": "A%d" % (i + 1), "tsv": NL.join(chunk)})
                    if r.get("ok"): break
                    time.sleep(5)
                if not r.get("ok"): sys.exit("中斷於 %d" % i)
            print(" 寫入 %d 條；清多餘列：" % (len(rows) - 1), post({"token": token(), "sheet": sheet, "mode": "clear_from", "from": len(rows) + 1}))
    elif cmd == "drop-combined":
        # GAS v6 上線後，把舊的合併分頁 Questions／Laws／Articles 清空（保留分頁，避免 GAS 舊版找不到）
        for sheet in ("Questions", "Laws", "Articles"):
            print(sheet, post({"token": token(), "sheet": sheet, "mode": "clear_from", "from": 1}))
    elif cmd == "sync":
        rows = [r.split(TAB) for r in read("tsv/Questions.tsv")]
        if rows and rows[0][0] == "id":
            rows = rows[1:]
        content = NL.join(TAB.join(r[:21]) for r in rows)           # A–U：id … explain_en
        print("內容欄 A–U：", post({"token": token(), "sheet": "Questions", "mode": "range", "startCell": "A2", "tsv": content}))
        fill = NL.join(r[0] + TAB + r[21] + TAB + r[22] for r in rows)   # id, status, batch
        print("補新題 status/batch：", post({"token": token(), "sheet": "Questions", "mode": "fill_status", "tsv": fill}))
        tail_to = int(os.environ.get("SYNC_TAIL", "0") or 0)          # 例：SYNC_TAIL=4856 會把 (題數+2)..4856 列清空
        if tail_to:
            print("清空多餘列：", blank_tail("Questions", len(rows) + 2, tail_to, 25))
    elif cmd == "status":
        # 用本地 status 欄覆寫 Questions!V2 起（會蓋掉 Sheet 上的審題狀態，僅在全部尚未審題時使用）
        rows = [r.split(TAB) for r in read("tsv/Questions.tsv")]
        if rows and rows[0][0] == "id":
            rows = rows[1:]
        print(post({"token": token(), "sheet": "Questions", "mode": "range", "startCell": "V2", "tsv": NL.join(r[21] + TAB + r[22] + TAB + r[23] + TAB + r[24] for r in rows)}))
    elif cmd == "raw":
        print(post({"token": token(), "sheet": a[1], "mode": "range", "startCell": a[2], "tsv": a[3].replace("<TAB>", TAB)}))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
