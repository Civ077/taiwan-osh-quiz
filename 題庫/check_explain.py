# -*- coding: utf-8 -*-
"""解析一致性檢查：答題回顧會顯示解析，若解析講的數值和正確選項不同，玩家會被誤導。
  E1 正確選項的關鍵數值，解析裡完全沒有出現，卻出現了某個「錯誤選項」獨有的數值
  E2 解析明確指向另一個選項的文字（解析與某個錯誤選項有 >=20 字逐字重疊，與正解卻沒有）
用法（在 題庫/）：python check_explain.py → 輸出 _spec/解析查核.tsv
"""
import sys, os, glob, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_sheet as bs
from verify_answers import nums
from deep_check import common_run, norm

def main():
    rows = []; n = 0
    for f in sorted(glob.glob(os.path.join(HERE, 'batch*_*.py'))):
        m = os.path.basename(f)[:-3]; mod = importlib.import_module(m)
        for i, t in enumerate(mod.Q):
            lid, art, diff, cat, qz, oz, ans, ez, qe, oe, ee = t
            if not bs.in_scope(lid): continue
            ai = 'abcd'.find(str(ans).strip().lower())
            if ai < 0 or ai >= len(oz): continue
            n += 1
            en = nums(ez); cn = nums(oz[ai])
            big = lambda S: {v for v in S if v >= 4 or v != int(v)}
            # E1：正解的數值解析完全沒提，卻提到了某個錯誤選項才有的數值
            miss = big(cn) - en
            if miss:
                for j, o in enumerate(oz):
                    if j == ai: continue
                    only = big(nums(o)) - big(cn)
                    if only and only & en:
                        rows.append(('E1', m, i, lid, art, '解析數值偏向選項' + 'abcd'[j],
                                     '正解缺:%s 解析有:%s' % (sorted(miss)[:3], sorted(only & en)[:3]), qz[:40]))
                        break
            # E2：解析與某個錯誤選項大段逐字重疊，與正解卻沒有
            if not common_run(ez, oz[ai], 14):
                for j, o in enumerate(oz):
                    if j == ai: continue
                    r = common_run(ez, o, 20)
                    if r:
                        rows.append(('E2', m, i, lid, art, '解析文字偏向選項' + 'abcd'[j], r[:34], qz[:40]))
                        break
    out = os.path.join(HERE, '_spec', '解析查核.tsv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write("code\tfile\tindex\tlaw_id\tarticle\tissue\tdetail\tquestion\n")
        fh.write("\n".join("\t".join(str(c) for c in r) for r in rows) + "\n")
    from collections import Counter
    c = Counter(r[0] for r in rows)
    print("檢查 %d 題；旗標 %d %s → %s" % (n, len(rows), dict(c), out))
    for r in rows[:15]: print(' ', r[0], r[1], '#' + str(r[2]), r[3], r[4], r[5], '|', r[6][:44])

if __name__ == '__main__':
    main()
