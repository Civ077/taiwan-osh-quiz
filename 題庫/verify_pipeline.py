# -*- coding: utf-8 -*-
"""管線一致性查核：確認「原始題目檔 → 建表洗牌 → 匯出 JSON → 雲端 API」四個環節，
正確答案都還指向同一段文字。任何一個環節錯位，玩家看到的答案就是錯的。

檢查項目
  P1 建表後的 answer 欄位所指的選項文字，等於原始檔中 answer 欄位所指的選項文字（中英各一）
  P2 四個選項是原始四個選項的重排（沒有遺漏、重複或被竄改）
  P3 每題 id 唯一；同一題在 tsv / json / xlsx 之間內容一致
  P4 docs/data/questions.json（離線備援）與建表結果一致
  P5 雲端 API 回傳的題目與本地一致（可加 --api，會抓兩個範圍各一次）

用法（在 題庫/）：python verify_pipeline.py [--api]
"""
import sys, os, json, glob, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_sheet as bs


def source_questions():
    """原始題目檔中的題目：key = (law_id, q_zh)，value = (正確中文選項, 正確英文選項, 四個中文選項集合)"""
    out = {}
    dup = []
    for bno, mods in sorted(bs.BATCHES.items()):
        for m in mods:
            for t in importlib.import_module(m).Q:
                lid, art, diff, cat, qz, oz, ans, ez, qe, oe, ee = t
                if not bs.in_scope(lid):
                    continue
                ai = 'abcd'.find(str(ans).strip().lower())
                if ai < 0 or ai >= len(oz):
                    dup.append(('答案字母異常', m, qz[:30]))
                    continue
                key = (lid, qz.strip())
                if key in out:
                    dup.append(('原始檔重複題', m, qz[:30]))
                out[key] = (oz[ai], oe[ai] if ai < len(oe) else '', tuple(sorted(oz)), tuple(sorted(oe)))
    return out, dup


def built_rows():
    rows = [r.split("\t") for r in open(os.path.join(HERE, 'tsv', 'Questions.tsv'), encoding='utf-8').read().split("\n") if r.strip()]
    head = rows[0]
    ix = {h: i for i, h in enumerate(head)}
    return head, ix, rows[1:]


def main(use_api=False):
    src, dup = source_questions()
    head, ix, rows = built_rows()
    errs = []
    ids = set()
    for r in rows:
        qid, lid, qz, ans = r[ix['id']], r[ix['law_id']], r[ix['q_zh']].strip(), r[ix['answer']].strip().lower()
        if qid in ids:
            errs.append(('P3 id 重複', qid, ''))
        ids.add(qid)
        key = (lid, qz)
        if key not in src:
            errs.append(('P3 建表有但原始檔找不到', qid, qz[:30]))
            continue
        want_zh, want_en, set_zh, set_en = src[key]
        got_zh = r[ix[ans + '_zh']]
        got_en = r[ix[ans + '_en']]
        if got_zh != want_zh:
            errs.append(('P1 中文答案錯位', qid, '建表=%s / 原始=%s' % (got_zh[:24], want_zh[:24])))
        if want_en and got_en != want_en:
            errs.append(('P1 英文答案錯位', qid, '建表=%s / 原始=%s' % (got_en[:24], want_en[:24])))
        if tuple(sorted(r[ix[k + '_zh']] for k in 'abcd')) != set_zh:
            errs.append(('P2 中文選項內容變動', qid, qz[:30]))
        if want_en and tuple(sorted(r[ix[k + '_en']] for k in 'abcd')) != set_en:
            errs.append(('P2 英文選項內容變動', qid, qz[:30]))

    # P4：網站離線備援檔
    p = os.path.join(os.path.dirname(HERE), 'docs', 'data', 'questions.json')
    if os.path.exists(p):
        j = json.load(open(p, encoding='utf-8'))
        byid = {q['id']: q for q in j.get('questions', [])}
        if len(byid) != len(rows):
            errs.append(('P4 備援檔題數不同', '%d vs %d' % (len(byid), len(rows)), ''))
        for r in rows[:99999]:
            q = byid.get(r[ix['id']])
            if not q:
                errs.append(('P4 備援檔缺題', r[ix['id']], ''))
                continue
            a = q.get('answer', '')
            if a != r[ix['answer']] or q.get(a + '_zh') != r[ix[a + '_zh']]:
                errs.append(('P4 備援檔答案不同', r[ix['id']], ''))

    # P5：雲端 API
    if use_api:
        import urllib.request
        URL = [l for l in open(os.path.join(HERE, 'push_to_sheet.py'), encoding='utf-8') if l.startswith('URL')][0].split('"')[1]
        for g in ('OSH', 'ENV'):
            d = urllib.request.urlopen(URL + '?status=active&group=%s&fields=core' % g, timeout=300).read()
            api = {q['id']: q for q in json.loads(d.decode('utf-8'))['questions']}
            local = {r[ix['id']]: r for r in rows if r[ix['id']].startswith(g)}
            if len(api) != len(local):
                errs.append(('P5 雲端題數不同 ' + g, '%d vs %d' % (len(api), len(local)), ''))
            for qid, r in local.items():
                q = api.get(qid)
                if not q:
                    errs.append(('P5 雲端缺題', qid, ''))
                    continue
                a = q.get('answer', '')
                if a != r[ix['answer']] or q.get(a + '_zh') != r[ix[a + '_zh']]:
                    errs.append(('P5 雲端答案不同', qid, ''))

    print('原始題目 %d、建表題目 %d' % (len(src), len(rows)))
    if dup:
        print('原始檔問題 %d：' % len(dup), dup[:5])
    from collections import Counter
    print('不一致 %d' % len(errs), Counter(e[0] for e in errs))
    for e in errs[:25]:
        print('  ', e[0], e[1], e[2])
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main('--api' in sys.argv))
