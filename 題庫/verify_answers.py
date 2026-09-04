# -*- coding: utf-8 -*-
"""答案數值查核：把每題「正確選項」裡的數字，拿去跟法規原文比對。
  A 級（高風險）：該數字在整部法規原文都找不到 → 可能是杜撰的數值
  B 級：整部法規找得到，但不在所引條文 → 可能引錯條號
用法（在 題庫/）：
  python verify_answers.py            # 全部，輸出 _spec/答案查核.tsv
  python verify_answers.py batch9_a   # 單一檔
中文數字（一二三…十百千萬、點、分之）會換算成阿拉伯數字後雙向比對。
"""
import sys, os, re, glob, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_sheet as bs
SRC = os.path.join(os.path.dirname(HERE), "法規原文")

DOTS = '[點．‧・·˙・]'      # 法規原文的小數點寫法很多：．(FF0E)、‧(2027)、˙(02D9)、・(30FB)
PCT = re.compile(r'(百|千|萬)分之')   # 百分之二十五 → 二十五，避免把「百」誤算成 100
CN = {'零': 0, '○': 0, '〇': 0, '一': 1, '二': 2, '兩': 2, '三': 3, '四': 4, '五': 5,
      '六': 6, '七': 7, '八': 8, '九': 9}
UNIT = {'十': 10, '百': 100, '千': 1000, '萬': 10000}


def cn2num(s):
    """中文數字轉數值；支援 一點五 / 二十五 / 一百八十 / 二千 / 三萬。無法解析回 None。"""
    if not s:
        return None
    if re.search(DOTS, s):
        parts = re.split(DOTS, s, maxsplit=1)
        a, b = parts[0], (parts[1] if len(parts) > 1 else '')
        ia = cn2num(a) if a else 0
        frac = ''
        for ch in b:
            if ch in CN:
                frac += str(CN[ch])
            else:
                break
        if ia is None or not frac:
            return None
        return float(f"{int(ia)}.{frac}")
    if len(s) >= 2 and all(ch in CN for ch in s):        # 位數並列寫法：一七五＝175、二二○＝220、三○○＝300
        return float(''.join(str(CN[ch]) for ch in s))
    total, cur, seen = 0, 0, False
    for ch in s:
        if ch in CN:
            cur = CN[ch]; seen = True
        elif ch in UNIT:
            u = UNIT[ch]
            if u == 10000:
                total = (total + (cur if cur else 0)) * u; cur = 0
            else:
                total += (cur if cur else 1) * u; cur = 0
            seen = True
        else:
            return None
    if not seen:
        return None
    return float(total + cur)


TOKEN_CN = re.compile('[零○〇一二三四五六七八九十百千萬兩點．‧・·˙]{1,10}')
TOKEN_AR = re.compile(r'\d[\d,]*(?:\.\d+)?')
ART_REF = re.compile(r'第\s*[\d零○〇一二三四五六七八九十百千兩]+\s*(?:條|項|款|目|章|節|類|級|期|附表|附件)')


# 法規原文混用異體字：全形數字０-９、希臘 Ο 與西里爾 О 代替○。不正規化的話
# 「０‧０五mg/m3」會被讀成 5 而不是 0.05，真的錯答案就可能混過檢查。
_CN10 = '○一二三四五六七八九'   # ○一二三四五六七八九
_FW = {ord(c): _CN10[i] for i, c in enumerate('０１２３４５６７８９')}   # 全形數字轉中文數字，才能與中文數字混寫的小數一起解析
_DOT_BETWEEN_DIGITS = re.compile('(?<=[0-9])' + DOTS + '(?=[0-9])')
def normalize(t):
    t = str(t).translate(_FW).replace('Ο', '○').replace('О', '○')
    return _DOT_BETWEEN_DIGITS.sub('.', t)   # 半形數字之間的．‧˙ 一律當小數點


def nums(text, drop_refs=True):
    """取出文字中的數值集合（阿拉伯 + 中文數字），預設先移除「第X條/項/款…」等條號引用。"""
    t = PCT.sub('', normalize(text))
    if drop_refs:
        t = ART_REF.sub(' ', t)
    out = set()
    for m in TOKEN_AR.findall(t):
        try:
            out.add(float(m.replace(',', '')))
        except ValueError:
            pass
    for m in TOKEN_CN.findall(t):
        v = cn2num(m)
        if v is not None:
            out.add(v)
    return out


_ART_SPLIT = re.compile(r'^第 ([\d\-]+) 條', re.M)
_law_cache = {}


def law_text(lid):
    if lid in _law_cache:
        return _law_cache[lid]
    zh = bs.LAWS[lid][0]
    p = os.path.join(SRC, zh + ".txt")
    txt = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    parts, cur, buf = {}, None, []
    for line in txt.split("\n"):
        m = _ART_SPLIT.match(line)
        if m:
            if cur:
                parts[cur] = "\n".join(buf)
            cur, buf = m.group(1), [line]
        elif cur:
            buf.append(line)
    if cur:
        parts[cur] = "\n".join(buf)
    _law_cache[lid] = (txt, parts)
    return _law_cache[lid]


def article_keys(art):
    return [n + ('-' + (s1 or s2) if (s1 or s2) else '')
            for n, s1, s2 in re.findall(r'第\s*(\d+)(?:-(\d+))?\s*條(?:之\s*(\d+))?', str(art))]


def main(files):
    mods = files or sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(HERE, 'batch*_*.py')))
    rows, stats = [], {'total': 0, 'checked': 0, 'A': 0, 'B': 0}
    for m in mods:
        mod = importlib.import_module(m)
        for i, t in enumerate(mod.Q):
            lid, art, diff, cat, qz, oz, ans, ez, qe, oe, ee = t
            stats['total'] += 1
            if not bs.in_scope(lid) or lid not in bs.LAWS:
                continue
            txt, parts = law_text(lid)
            if not txt:
                continue
            keys = article_keys(art)
            arts = "\n".join(parts.get(k, '') for k in keys)
            if not arts.strip():
                continue
            stats['checked'] += 1
            ai = 'abcd'.find(str(ans).strip().lower())
            if ai < 0 or ai >= len(oz):
                continue
            correct = oz[ai]                     # 依 answer 欄位取正確選項（批次 1–3 的答案不一定是第一個）
            want = nums(correct)
            if not want:
                continue
            have_art, have_law = nums(arts, drop_refs=False), nums(txt, drop_refs=False)
            missA = sorted(v for v in want if v not in have_law)
            missB = sorted(v for v in want if v in have_law and v not in have_art)
            if missA:
                stats['A'] += 1
                rows.append(('A', m, i, lid, bs.LAWS[lid][0], art, ';'.join(fmtv(v) for v in missA), qz[:40], correct[:60]))
            elif missB:
                stats['B'] += 1
                rows.append(('B', m, i, lid, bs.LAWS[lid][0], art, ';'.join(fmtv(v) for v in missB), qz[:40], correct[:60]))
    out = os.path.join(HERE, '_spec', '答案查核.tsv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write("level\tfile\tindex\tlaw_id\tlaw\tarticle\tmissing_numbers\tquestion\tcorrect_option\n")
        f.write("\n".join("\t".join(str(c) for c in r) for r in rows) + "\n")
    print("題目 %d，可比對 %d；A 級（法規找不到此數值）%d、B 級（不在所引條文）%d" % (stats['total'], stats['checked'], stats['A'], stats['B']))
    print("→", out)


def fmtv(v):
    return str(int(v)) if float(v).is_integer() else str(v)


if __name__ == '__main__':
    main(sys.argv[1:])
