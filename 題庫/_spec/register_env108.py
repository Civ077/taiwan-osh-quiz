# -*- coding: utf-8 -*-
"""把 env_add_108_en.tsv 的法規登記進 build_sheet.py（ENV_LAWS 追加 + FAMILIES 追加）。可重複執行（已登記者略過）。"""
import re, io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); Q = os.path.dirname(HERE)
bs_path = os.path.join(Q, 'build_sheet.py')
s = open(bs_path, encoding='utf-8').read()
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, os.environ.get('ENV_ADD_FILE', 'env_add_108_en.tsv')), encoding='utf-8') if l.strip()]
assert all(len(r) == 4 for r in rows), [r for r in rows if len(r) != 4]
def family(name, cat):
    if re.search(r'噪音|航空噪音', name): return "環保-噪音"
    if cat == '空氣噪音目' or re.search(r'室內空氣', name): return "環保-空氣品質（含室內空品）"
    if cat == '水質保護目' or re.search(r'飲用水|水體|放流水|水污染', name): return "環保-水污染與飲用水"
    if cat == '廢棄物資源循環目' or re.search(r'廢棄物|回收|再生|資源', name): return "環保-廢棄物與資源循環"
    if cat == '化學物質環境用藥目' or re.search(r'毒性|化學物質|環境用藥|病媒', name): return "環保-毒性化學物質與環境用藥"
    if cat == '土壤地下水及環管目' or re.search(r'土壤|地下水|底泥', name): return "環保-土壤及地下水"
    if cat == '氣候變遷目' or re.search(r'溫室氣體|碳|氣候', name): return "環保-氣候變遷"
    if cat == '環境教育目' or cat == '環境檢驗訓練目' or re.search(r'環境教育|檢驗測定|訓練', name): return "環保-環境教育與環檢機構"
    if re.search(r'公害', name): return "環保-公害糾紛"
    if re.search(r'環境影響評估|環境保護', name): return "環保-環境基本與環評"
    return "環保-環境基本與環評"
# 目前 ENV_LAWS 數
m = re.search(r'^ENV_LAWS = \[\n(.*?)^\]', s, re.M | re.S)
body = m.group(1)
sys.path.insert(0, Q); import build_sheet as _bs
existing = [t[0] for t in _bs.ENV_LAWS]
n0 = len(existing)
new = [(c, zh, cat, en) for c, zh, cat, en in rows if zh not in existing]
lines = []
fam_add = {}
for k, (c, zh, cat, en) in enumerate(new, start=n0 + 1):
    en = en.replace('"', "'")
    lines.append(f' ("{zh}","{en}","{c}",1,2),')
    fam_add.setdefault(family(zh, cat), []).append(k)
s = s[:m.end(1)] + '\n'.join(lines) + ('\n' if lines else '') + s[m.end(1):]
# FAMILIES：把新 id 接在對應體系後面
for fam, ids in fam_add.items():
    pat = re.compile(r'(\("' + re.escape(fam) + r'", \[[^\]]*)\]')
    assert pat.search(s), fam
    s = pat.sub(lambda mm: mm.group(1) + ',' + ','.join(str(i) for i in ids) + ']', s, count=1)
open(bs_path, 'w', encoding='utf-8').write(s)
print('已登記', len(new), '部；ENV 總數', n0 + len(new))
for fam, ids in fam_add.items(): print(' ', fam, len(ids))
