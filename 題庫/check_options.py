# -*- coding: utf-8 -*-
"""檢查選項長度是否洩題（正確選項明顯比其他選項長）。
用法：python check_options.py batch6_a [batch6_b ...]   或   python check_options.py all
規則（zh 與 en 分開看）：正確選項長度 > 最長錯誤選項 ×1.25，或比它長 12 字以上 → 列出。
另列出「任一錯誤選項短於正確選項 45%」的題（太短也很可疑）。
"""
import sys, importlib, glob, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

def check(mod):
    m = importlib.import_module(mod); bad = 0
    for i, tpl in enumerate(m.Q):
        lid, art, diff, cat, qz, oz, ans, ez, qe, oe, ee = tpl
        k = 'abcd'.index(ans)
        for tag, opts in (('zh', oz), ('en', oe)):
            c = len(opts[k]); others = [len(o) for j, o in enumerate(opts) if j != k]
            mx = max(others); mn = min(others)
            reasons = []
            if c > mx * 1.25 or c - mx >= 12: reasons.append('正確最長 %d vs %d' % (c, mx))
            if mn < c * 0.45: reasons.append('有錯誤選項太短 %d vs %d' % (mn, c))
            if reasons:
                bad += 1
                print('%s #%d [%s] %s | %s | %s' % (mod, i + 1, tag, art, qz[:22], '；'.join(reasons)))
    print('%s：%d 個問題（共 %d 題）' % (mod, bad, len(m.Q)))
    return bad

if __name__ == '__main__':
    mods = sys.argv[1:] or ['all']
    if mods == ['all']:
        mods = sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(HERE, 'batch*_*.py')))
    total = sum(check(x) for x in mods)
    print('合計問題數：', total)
