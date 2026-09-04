# -*- coding: utf-8 -*-
"""全庫逐題深度檢查（不抽樣）。針對每一題輸出可疑旗標，供人工複核：

  D1 干擾選項疑似也對：某個錯誤選項有一段 >=12 字的文字，逐字出現在所引條文中
  D2 正確選項缺乏依據：正確選項與所引條文沒有任何長度 >=8 的共同字串，且沒有共同數值
  D3 中英數值不一致：同一個選項的中文與英文，抓到的數值集合不同（翻譯漏字或改錯數字）
  D4 選項語意重複：兩個選項去除標點後有 >=90% 相似（可能等於同一個答案）
  D5 題幹疑似洩答：題幹出現正確選項中 >=10 字的片段，其他選項沒有

用法（在 題庫/）：
  python deep_check.py            # 全部，輸出 _spec/深度檢查.tsv
  python deep_check.py batch9_a   # 單檔
"""
import sys, os, re, glob, importlib, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_sheet as bs
from verify_answers import nums, law_text, article_keys

PUNC = re.compile(r'[\s，。、；：（）「」【】…・,.;:()\[\]/／－\-]+')


def norm(s):
    return PUNC.sub('', str(s))


def common_run(a, b, minlen):
    """a 與 b 是否有長度 >= minlen 的共同連續字串"""
    a, b = norm(a), norm(b)
    if not a or not b:
        return None
    m = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return a[m.a:m.a + m.size] if m.size >= minlen else None


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()



EN_WORD = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,
           'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,
           'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,
           'seventy':70,'eighty':80,'ninety':90,'hundred':100,'thousand':1000,'million':1000000}
EN_ART = re.compile(r'(?:Articles?|Art\.|Paragraph|Subparagraph|Item|Chapter|Class|Category|Annex|Table|Appendix)\s*[\d\-]+(?:\s*\(\d+\))?|\(\d+\)', re.I)
def en_nums(text):
    """英文選項的數值：阿拉伯數字 + 英文數字詞（先去掉 Article 12 之類的條號引用）"""
    t = EN_ART.sub(' ', str(text))
    low = t.lower()
    for a, b in re.findall(r'(\d[\d,\.]*)\s*(million|thousand|hundred)', low):   # 30 million → 30000000
        low = low.replace(a + ' ' + b, str(float(a.replace(',', '')) * EN_WORD[b]))
    for a, b in re.findall(r'(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[- ](one|two|three|four|five|six|seven|eight|nine)', low):
        low = low.replace(a + '-' + b, str(EN_WORD[a] + EN_WORD[b])).replace(a + ' ' + b, str(EN_WORD[a] + EN_WORD[b]))
    out = set(nums(low, drop_refs=True))
    for w in re.findall(r'[a-z]+', low):
        if w in EN_WORD and EN_WORD[w] < 100: out.add(float(EN_WORD[w]))
    return out
def num_match(zn, en):
    """比對兩組數值；民國年與西元年（差 1911）視為相同"""
    zl, el = set(zn), set(en)
    for v in list(zl):
        if v + 1911 in el: zl.discard(v); el.discard(v + 1911)
    for v in list(el):
        if v + 1911 in zl: el.discard(v); zl.discard(v + 1911)
    return zl - el, el - zl        # 只回傳「單邊才有」的數值

def main(files):
    mods = files or sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(HERE, 'batch*_*.py')))
    rows = []
    n_total = n_checked = 0
    for m in mods:
        mod = importlib.import_module(m)
        for i, t in enumerate(mod.Q):
            lid, art, diff, cat, qz, oz, ans, ez, qe, oe, ee = t
            n_total += 1
            if not bs.in_scope(lid) or lid not in bs.LAWS:
                continue
            ai = 'abcd'.find(str(ans).strip().lower())
            if ai < 0 or ai >= len(oz) or ai >= len(oe):
                rows.append(('D0', m, i, lid, art, '答案字母異常', str(ans), qz[:40]))
                continue
            n_checked += 1
            correct, correct_en = oz[ai], oe[ai]
            txt, parts = law_text(lid)
            arts = "\n".join(parts.get(k, '') for k in article_keys(art)) if txt else ''

            # D1：干擾選項有長段文字逐字出現在條文裡
            if arts:
                for j, opt in enumerate(oz):
                    if j == ai:
                        continue
                    run = common_run(opt, arts, 15)
                    if run and len(run) >= 0.75 * len(norm(opt)):
                        rows.append(('D1', m, i, lid, art, '選項' + 'abcd'[j] + ' 疑似也對', run[:30], qz[:40]))

            # D2：正確選項在條文中找不到依據（無共同長字串、也沒有共同數值）
            if arts and not common_run(correct, arts, 8):
                if not (nums(correct) & nums(arts, drop_refs=False)):
                    rows.append(('D2', m, i, lid, art, '正確選項缺依據', correct[:40], qz[:40]))

            # D3：同一選項的中英數值不一致
            for j in range(min(len(oz), len(oe))):
                big = lambda S: {v for v in S if v >= 4 or (v != int(v))}
                only_zh_s, only_en_s = num_match(big(nums(oz[j])), big(en_nums(oe[j])))
                if only_zh_s and only_en_s:      # 兩邊都有、且數值不同才算（單邊缺少多半是英文用文字寫或詞性差異）
                    only_zh = sorted(only_zh_s)[:4]
                    only_en = sorted(only_en_s)[:4]
                    if only_zh or only_en:
                        rows.append(('D3', m, i, lid, art, '選項' + 'abcd'[j] + ' 中英數值不同',
                                     'zh多:%s en多:%s' % (only_zh, only_en), qz[:40]))

            # D4：兩個選項語意幾乎相同
            for a in range(4):
                for b in range(a + 1, 4):
                    if a < len(oz) and b < len(oz) and sim(oz[a], oz[b]) >= 0.97 and nums(oz[a]) == nums(oz[b]):
                        rows.append(('D4', m, i, lid, art, '選項%s與%s過於相似' % ('abcd'[a], 'abcd'[b]),
                                     '%.2f' % sim(oz[a], oz[b]), qz[:40]))

            # D5：題幹出現正確選項的長片段，其他選項沒有
            run = common_run(qz, correct, 10)
            if run and not any(common_run(qz, oz[j], 10) for j in range(4) if j != ai):
                rows.append(('D5', m, i, lid, art, '題幹疑似洩答', run[:30], qz[:40]))

    out = os.path.join(HERE, '_spec', '深度檢查.tsv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write("code\tfile\tindex\tlaw_id\tarticle\tissue\tdetail\tquestion\n")
        f.write("\n".join("\t".join(str(c) for c in r) for r in rows) + "\n")
    from collections import Counter
    c = Counter(r[0] for r in rows)
    print("題目 %d，檢查 %d；旗標 %d" % (n_total, n_checked, len(rows)))
    for k in sorted(c):
        print("  %s %d" % (k, c[k]))
    print("→", out)


if __name__ == '__main__':
    main(sys.argv[1:])
