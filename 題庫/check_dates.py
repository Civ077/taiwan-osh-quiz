# -*- coding: utf-8 -*-
"""施行日期題查核：抓出「干擾選項寫的日期剛好等於該法規真正的發布／修正日期」的題目。
這種題目會出現兩個正確答案（例如正解是「自發布日施行」，干擾選項卻寫出真正的發布日）。
用法（在 題庫/）：python check_dates.py  → 輸出 _spec/日期查核.tsv
"""
import sys, os, re, glob, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_sheet as bs
from verify_answers import cn2num
SRC = os.path.join(os.path.dirname(HERE), "法規原文")

DATE = re.compile(r'(?:中華民國)?\s*([0-9零○〇一二三四五六七八九十百]+)\s*年\s*([0-9零○〇一二三四五六七八九十]+)\s*月\s*([0-9零○〇一二三四五六七八九十]+)\s*日')


def num(tok):
    tok = tok.strip()
    if tok.isdigit():
        return int(tok)
    v = cn2num(tok)
    return int(v) if v is not None else None


def dates(text):
    out = set()
    for y, m, d in DATE.findall(text or ''):
        yy, mm, dd = num(y), num(m), num(d)
        if yy and mm and dd:
            out.add((yy, mm, dd))
    return out


def law_date(zh):
    p = os.path.join(SRC, zh + ".txt")
    if not os.path.exists(p):
        return None
    head = open(p, encoding="utf-8").read(400)
    ds = dates(head)
    return next(iter(ds)) if len(ds) == 1 else (sorted(ds)[-1] if ds else None)


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, 'batch*_*.py'))):
        mod = importlib.import_module(os.path.basename(f)[:-3])
        for i, t in enumerate(mod.Q):
            lid, art, diff, cat, qz, oz, ans, ez, qe, oe, ee = t
            if not bs.in_scope(lid) or lid not in bs.LAWS:
                continue
            ld = law_date(bs.LAWS[lid][0])
            if not ld:
                continue
            ai = 'abcd'.find(str(ans).strip().lower())
            if ai < 0:
                continue
            for j, opt in enumerate(oz):
                if j == ai:
                    continue
                if ld in dates(opt):                       # 干擾選項寫的日期就是法規真正的發布／修正日
                    rows.append((os.path.basename(f)[:-3], i, lid, bs.LAWS[lid][0], art,
                                 "%d.%02d.%02d" % ld, 'abcd'[j], opt[:50], oz[ai][:40]))
    out = os.path.join(HERE, '_spec', '日期查核.tsv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write("file\tindex\tlaw_id\tlaw\tarticle\tlaw_date\tbad_option\toption_text\tcorrect_option\n")
        fh.write("\n".join("\t".join(str(c) for c in r) for r in rows) + "\n")
    print("干擾選項日期＝法規真實日期：%d 題 → %s" % (len(rows), out))
    for r in rows[:20]:
        print(" ", r[0], '#' + str(r[1]), r[3][:18], r[4], r[5], '選項' + r[6].upper(), '|', r[7][:34])


if __name__ == '__main__':
    main()
