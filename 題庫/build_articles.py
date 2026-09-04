# -*- coding: utf-8 -*-
"""把 法規原文/*.txt 拆成逐條資料 → tsv/Articles.tsv（完整法條，給 Google Sheet 的 Articles 分頁）
欄位：law_id, group, law, article, has_annex, text
   text 內的換行以「 ／ 」連接（TSV 一列一條）。
用法（在 題庫/ 目錄）：python build_articles.py
"""
import os, re, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
bs = importlib.import_module("build_sheet")
SRC = os.path.join(os.path.dirname(HERE), "法規原文")

ART_RE = re.compile(r'^第 ([\d\-]+) 條(?:\s*【有附表／附件】)?\s*$')

def split_articles(txt):
    out = []; cur = None; buf = []
    for line in txt.split("\n"):
        line = line.rstrip()
        m = ART_RE.match(line)
        if m:
            if cur: out.append((cur[0], cur[1], buf))
            cur = (m.group(1), "【有附表／附件】" in line); buf = []
            continue
        if line.startswith("## "):          # 章節標題／頁尾雜訊
            if cur: out.append((cur[0], cur[1], buf)); cur = None; buf = []
            continue
        if cur is not None and line.strip():
            buf.append(line.strip())
    if cur: out.append((cur[0], cur[1], buf))
    return out

def main():
    laws = [("OSH-%02d" % i, "OSH", zh) for i, (zh, *_r) in enumerate(bs.OSH_LAWS, start=1)] + \
           [("ENV-%02d" % i, "ENV", zh) for i, (zh, *_r) in enumerate(bs.ENV_LAWS, start=1)]
    laws = [l for l in laws if bs.in_scope(l[0])]   # 只灌指定範圍內的法規
    rows = [["law_id", "group", "law", "article", "has_annex", "text"]]
    missing = []; per_law = {}
    for lid, grp, zh in laws:
        p = os.path.join(SRC, zh + ".txt")
        if not os.path.exists(p):
            missing.append(zh); continue
        arts = split_articles(open(p, encoding="utf-8").read())
        per_law[lid] = len(arts)
        for no, annex, lines in arts:
            text = " ／ ".join(lines).replace("\t", " ")
            rows.append([lid, grp, zh, ("第%s條之%s" % tuple(no.split("-"))) if "-" in no else "第%s條" % no, "Y" if annex else "", text])
    os.makedirs(os.path.join(HERE, "tsv"), exist_ok=True)
    with open(os.path.join(HERE, "tsv", "Articles.tsv"), "w", encoding="utf-8", newline="") as f:
        f.write("\n".join("\t".join(str(c) for c in r) for r in rows))
    for g in ("OSH", "ENV"):   # 職安／環保分開的分頁
        with open(os.path.join(HERE, "tsv", "Articles_%s.tsv" % g), "w", encoding="utf-8", newline="") as f:
            f.write(chr(10).join(chr(9).join(str(c) for c in r) for r in [rows[0]] + [r for r in rows[1:] if r[1] == g]))
    print("Articles.tsv：%d 部法規、%d 條" % (len(per_law), len(rows) - 1))
    if missing: print("找不到原文：", missing)
    return per_law

if __name__ == "__main__":
    main()
