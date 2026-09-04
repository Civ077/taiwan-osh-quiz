# -*- coding: utf-8 -*-
"""列出某法規尚未出題的條文：python coverage.py OSH-07 [OSH-41 ...]；不帶參數則列全部法規摘要。"""
import sys, os, re, glob, importlib
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_sheet as bs
ART = re.compile(r'^第 ([\d\-]+) 條', re.M)

def covered():
    cov = defaultdict(set)
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'batch*_*.py'))):
        try:
            m = importlib.import_module(os.path.basename(f)[:-3])
        except Exception as e:
            print('!! import failed', f, e); continue
        for t in m.Q:
            for n, s1, s2 in re.findall(r'第\s*(\d+)(?:-(\d+))?\s*條(?:之\s*(\d+))?', t[1]):
                cov[t[0]].add(n + ('-' + (s1 or s2) if (s1 or s2) else ''))
    return cov

def laws():
    out = [("OSH-%02d" % i, zh) for i, (zh, *_) in enumerate(bs.OSH_LAWS, 1)]
    out += [("ENV-%02d" % i, zh) for i, (zh, *_) in enumerate(bs.ENV_LAWS, 1)]
    out = [(lid, zh) for lid, zh in out if bs.in_scope(lid)]   # 只看指定範圍內法規
    return dict(out)

def articles(zh):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '法規原文', zh + '.txt')
    if not os.path.exists(p): return []
    txt = open(p, encoding='utf-8').read()
    dele = set(re.findall(r'^第 ([\d\-]+) 條[^\n]*\n\s*（刪除）', txt, re.M))
    return [a for a in ART.findall(txt) if a not in dele]        # 「（刪除）」條不計入應出題條文

if __name__ == '__main__':
    cov = covered(); L = laws()
    ids = sys.argv[1:] or sorted(L)
    for lid in ids:
        zh = L.get(lid)
        if not zh: print(f'{lid}：不在範圍或不存在'); continue
        arts = articles(zh)
        miss = [a for a in arts if a not in cov[lid]]
        if sys.argv[1:]:
            print(f"{lid} {zh}：共 {len(arts)} 條，未出題 {len(miss)} 條")
            print(' '.join('第' + a.replace('-', '條之') + ('' if '-' in a else '條') for a in miss))
        else:
            print(f"{lid}\t{zh}\t{len(arts)}\t{len(miss)}")
