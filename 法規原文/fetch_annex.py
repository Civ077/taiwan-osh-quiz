# 下載各法規之附表／附件（PDF/ODT/DOCX）並轉成文字：python fetch_annex.py [N0060027 ...]（不給參數＝全部 N*.html）
import sys, os, re, glob, subprocess, json, zipfile
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

pc = json.load(open('pcodes.json', encoding='utf-8')); inv = {v: k for k, v in pc.items() if v}
codes = sys.argv[1:] or [h[:-5] for h in sorted(glob.glob('N*.html'))]


def office_text(fn, ext):
    try:
        z = zipfile.ZipFile(fn)
        xml = z.read('content.xml' if ext == 'ODT' else 'word/document.xml').decode('utf-8')
        xml = re.sub(r'</(?:text:p|text:h|w:p|table:table-row|w:tr)>', '\n', xml)
        xml = re.sub(r'</(?:table:table-cell|w:tc)>', '\t', xml)
        txt = re.sub(r'<[^>]+>', '', xml)
        return re.sub(r'\n{3,}', '\n\n', txt)
    except Exception as e:
        return f'[{ext} 解析失敗: {e}]'


def pdf_text(fn):
    try:
        doc = fitz.open(fn); txt = '\n'.join(p.get_text() for p in doc); doc.close(); return txt
    except Exception as e:
        return f'[PDF 解析失敗: {e}]'


for code in codes:
    s = BeautifulSoup(open(code + '.html', encoding='utf-8').read(), 'lxml')
    name = inv.get(code, code)
    links = {}
    for a in s.select('a[href*="LawGetFile"]'):
        t = a.get_text(strip=True); href = a['href']
        base = re.sub(r'\.(PDF|DOC|DOCX|ODT|XLS|XLSX)$', '', t, flags=re.I)
        ext = t.rsplit('.', 1)[-1].upper() if '.' in t else ''
        links.setdefault(base, {})[ext] = href
    if not links:
        print(f'{code} {name}: 無附件'); continue
    d = f'附件/{code}_{name}'; os.makedirs(d, exist_ok=True)
    combined = [f'# {name}（{code}）附表／附件全文\n']
    for base, exts in links.items():
        ext = 'PDF' if 'PDF' in exts else ('ODT' if 'ODT' in exts else ('DOCX' if 'DOCX' in exts else sorted(exts)[0]))
        url = 'https://law.moj.gov.tw/LawClass/' + exts[ext]
        safe = re.sub(r'[\\/:*?"<>|\s]+', '_', base)[:80]
        fn = f'{d}/{safe}.{ext.lower()}'
        if not os.path.exists(fn):
            subprocess.run(['curl', '-sL', '-A', 'Mozilla/5.0', url, '-o', fn], check=True)
        if ext == 'PDF':
            txt = pdf_text(fn)
        elif ext in ('ODT', 'DOCX'):
            txt = office_text(fn, ext)
        else:
            txt = f'[非 PDF 檔（{ext}），未解析]'
        open(fn.rsplit('.', 1)[0] + '.txt', 'w', encoding='utf-8').write(txt)
        combined.append(f'\n## {base}\n{txt.strip()}\n')
        print(f'  {base[:40]:<40} {ext} {len(txt):>6} chars')
    # 人工抄錄檔（圖片型附表）一併併入
    for m in sorted(glob.glob(f'{d}/*人工抄錄*.txt')):
        combined.append(f'\n## {os.path.basename(m)[:-4]}\n' + open(m, encoding='utf-8').read())
    open(f'{name}_附件.txt', 'w', encoding='utf-8').write('\n'.join(combined))
    print(f'{code} {name}: {len(links)} 個附件 → {name}_附件.txt')
