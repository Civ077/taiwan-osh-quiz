# -*- coding: utf-8 -*-
"""Firebase 對外暴露檢查（唯讀，不會改動任何東西）

本專案只該開啟 Realtime Database + 匿名登入。這支腳本確認沒有別的服務被誤開、
API 金鑰仍限制在本站網域，以及資料庫規則沒有被改成對外開放。任何一項不符就回傳非 0，方便排進例行檢查。

用法：python firebase/check_exposure.py
"""
import json, os, re, subprocess, sys, urllib.error, urllib.request

PROJECT = 'taiwan-osh-quiz'
HERE = os.path.dirname(os.path.abspath(__file__))
BUCKETS = [PROJECT + '.firebasestorage.app', PROJECT + '.appspot.com']
bad = []


def http(url):
    try:
        return urllib.request.urlopen(url, timeout=30).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)


def check_control():
    """先確認檢查方法本身有效：一個確定存在的公開 bucket 必須回 200。"""
    if http('https://storage.googleapis.com/storage/v1/b/gcp-public-data-landsat') != 200:
        print('!! 對照組失敗，可能沒有網路，本次檢查結果不可信')
        sys.exit(2)


def check_storage():
    for b in BUCKETS:
        code = http('https://storage.googleapis.com/storage/v1/b/' + b)
        if code == 404:
            print('OK   Cloud Storage %s 不存在' % b)
        else:
            bad.append('Cloud Storage %s 回應 %s（可能已被啟用）→ 立刻執行 '
                       'npx firebase-tools deploy --only storage' % (b, code))


def check_firestore():
    try:
        r = subprocess.run(['npx', '--yes', 'firebase-tools', 'firestore:databases:list',
                            '--project', PROJECT], capture_output=True, text=True, timeout=300, shell=True)
        out = (r.stdout or '') + (r.stderr or '')
    except Exception as e:
        print('??   Firestore 檢查跳過（%s）' % e)
        return
    if 'has not been used' in out or 'it is disabled' in out:
        print('OK   Firestore 未啟用')
    elif '(default)' in out or 'projects/' in out:
        bad.append('Firestore 似乎已被啟用 → 立刻執行 npx firebase-tools deploy --only firestore')
    else:
        print('??   Firestore 狀態判讀不出來，請自行確認：\n     ' + out.strip()[:200])


def check_key_referrer():
    """確認 API 金鑰仍限制在本站網域：從別的來源網址請求匿名登入必須被拒。
    這一項若失守，任何人都能把公開設定複製走使用。"""
    import json as _json
    key = None
    cfg = os.path.join(os.path.dirname(HERE), 'docs', 'firebase-config.js')
    m = re.search(r'apiKey:\s*"([^"]+)"', open(cfg, encoding='utf-8').read())
    if not m:
        bad.append('firebase-config.js 找不到 apiKey，無法檢查金鑰限制'); return
    key = m.group(1)
    req = urllib.request.Request(
        'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=' + key,
        data=_json.dumps({'returnSecureToken': True}).encode(), method='POST',
        headers={'Content-Type': 'application/json', 'Referer': 'https://not-our-site.example/'})
    try:
        urllib.request.urlopen(req, timeout=30)
        bad.append('API 金鑰沒有網域限制：從 not-our-site.example 也能登入 → 到 Google Cloud 主控台'
                   '「憑證」把應用程式限制設為「網站」並只允許 https://civ077.github.io/*')
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print('OK   API 金鑰限制在本站網域（外部來源被拒）')
        else:
            print('??   API 金鑰檢查回應 %s，請自行確認' % e.code)
    except Exception as e:
        print('??   API 金鑰檢查跳過（%s）' % e)


def check_rules():
    p = os.path.join(HERE, 'database.rules.json')
    txt = open(p, encoding='utf-8').read()
    d = json.loads(txt)['rules']
    if d.get('.read') is not False or d.get('.write') is not False:
        bad.append('database.rules.json 的根節點沒有 .read/.write = false')
    else:
        print('OK   資料庫規則根節點預設拒絕')
    for m in re.finditer(r'"\.(read|write)"\s*:\s*true', txt):
        bad.append('database.rules.json 出現無條件開放的 ".%s": true' % m.group(1))
    if '"champions"' not in txt or '"scores"' not in txt:
        bad.append('database.rules.json 缺少 scores 或 champions 區塊')


def check_config():
    p = os.path.join(os.path.dirname(HERE), 'docs', 'firebase-config.js')
    s = open(p, encoding='utf-8').read()
    if re.search(r'^\s*storageBucket\s*:', s, re.M):
        bad.append('firebase-config.js 又出現 storageBucket，網站會連上不該用的 Storage')
    else:
        print('OK   網站設定沒有指向 Cloud Storage')
    print('%s App Check %s' % ('OK  ' if re.search(r'^\s*window\.FIREBASE_APPCHECK_KEY\s*=', s, re.M) else '注意',
                               '已設定金鑰' if re.search(r'^\s*window\.FIREBASE_APPCHECK_KEY\s*=', s, re.M)
                               else '尚未設定金鑰（設定後這份公開設定在別的網域就會失效）'))


check_control(); check_storage(); check_firestore(); check_key_referrer(); check_rules(); check_config()
print()
if bad:
    print('發現 %d 個問題：' % len(bad))
    for b in bad:
        print('  !! ' + b)
    sys.exit(1)
print('全部通過：只有 Realtime Database 對外，規則預設拒絕。')
