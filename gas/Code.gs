/**
 * 台灣職安環保知識王 — 題庫 API（Google Apps Script，綁定在 OSH_ENV_QuizBank 試算表）
 *
 * 部署為網頁應用程式後，前端以 GET 取得 JSON：
 *   GET  <webapp>/exec                → status=active 的題目 + Config 參數
 *   GET  <webapp>/exec?status=all     → 全部題目（含 draft，審題期間用）
 *   GET  <webapp>/exec?status=draft   → 只要 draft
 *   GET  <webapp>/exec?ping=1         → {ok:true, version:GAS_VERSION}
 *
 * 快取：同一參數 5 分鐘內回同一份（CacheService），改完 Sheet 最多 5 分鐘生效；
 *       要立即生效可在試算表選單「知識王 → 清除快取」。
 *
 * 匯入（v2）：POST <webapp>/exec，body 為 JSON：
 *   { token, sheet:'Questions'|'Laws'|'Changelog'|'Config', mode:'append'|'range', tsv:'...', startCell:'F2' }
 *   token 要和試算表選單「知識王 → 設定匯入密鑰」存入指令碼屬性 IMPORT_TOKEN 的值相同（不放 Config，避免隨 JSON 外洩）；
 *   append 會先檢查 Questions 的 id 不重複。
 *   用 題庫/push_to_sheet.py 呼叫，之後新批次不必再用剪貼簿貼。
 * v5：body 加 create:true 時分頁不存在會自動建立（例如 Articles 完整法條）；
 *     mode:'clear_from', from:N → 刪除第 N 列以後所有列（from=1 整張清空），用來縮短 Laws 或重灌 Articles。
 */
const GAS_VERSION = 6;   // v5：append/range 可自動建立分頁（create:true）；新增 clear_from 模式（刪除第 N 列以後）
const SHEET_QUESTIONS = 'Questions';
const SHEET_CONFIG = 'Config';
const CACHE_SEC = 300;

function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.ping) return json_({ ok: true, version: GAS_VERSION, time: new Date().toISOString() });
  const status = String(p.status || 'active').toLowerCase();
  const key = 'bank:' + status + ':' + GAS_VERSION;
  const cache = CacheService.getScriptCache();
  let body = cache.get(key);
  if (!body) {
    body = JSON.stringify(buildBank_(status));
    if (body.length < 95000) cache.put(key, body, CACHE_SEC);   // CacheService 單筆上限 100KB
  }
  return ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  let req;
  try { req = JSON.parse((e && e.postData && e.postData.contents) || '{}'); }
  catch (err) { return json_({ ok: false, error: 'bad json' }); }
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return json_({ ok: false, error: 'busy' });
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const token = String(PropertiesService.getScriptProperties().getProperty('IMPORT_TOKEN') || '').trim();
    if (!token || String(req.token || '') !== token) return json_({ ok: false, error: 'bad token' });
    let sh = ss.getSheetByName(String(req.sheet || ''));
    if (!sh && req.create) sh = ss.insertSheet(String(req.sheet));
    if (!sh) return json_({ ok: false, error: 'no sheet ' + req.sheet });
    if (req.mode === 'clear_from') {                 // clear_from：刪掉第 from 列（含）以後的所有列；from=1 表示整張清空
      const from = Math.max(1, Number(req.from || 2)); const last = sh.getLastRow(); let deleted = 0;
      if (from === 1) { sh.clearContents(); deleted = last; }
      else if (last >= from) { deleted = last - from + 1; sh.deleteRows(from, deleted); }
      clearCacheSilent_();
      return json_({ ok: true, mode: 'clear_from', sheet: sh.getName(), from, deleted, lastRow: sh.getLastRow() });
    }
    let rows = String(req.tsv || '').split(/\r?\n/).map(r => r.split('\t'));
    if (req.mode === 'range') {                     // range：保留中間的空白列（位置要對齊），只去掉尾端空白列
      while (rows.length && rows[rows.length - 1].join('').trim() === '') rows.pop();
    } else {
      rows = rows.filter(r => r.join('').trim() !== '');
    }
    if (!rows.length) return json_({ ok: false, error: 'empty' });
    const width = Math.max.apply(null, rows.map(r => r.length));
    rows.forEach(r => { while (r.length < width) r.push(''); });
    if (req.mode === 'range') {
      const a1 = String(req.startCell || 'A2');
      sh.getRange(a1).offset(0, 0, rows.length, width).setValues(rows);
      clearCacheSilent_();
      return json_({ ok: true, mode: 'range', sheet: sh.getName(), startCell: a1, rows: rows.length, cols: width });
    }
    if (req.mode === 'fill_status' && isQuestionSheet_(sh)) {
      // rows: id 	 status 	 batch —— 只補 status 空白的列（新題），不動已審題目
      const last0 = sh.getLastRow(); if (last0 < 2) return json_({ ok: true, filled: 0 });
      const rng = sh.getRange(2, 1, last0 - 1, 23); const vals = rng.getValues();
      const want = {}; rows.forEach(r => { want[String(r[0]).trim()] = [r[1] || 'draft', r[2] || '']; });
      let filled = 0;
      vals.forEach(v => { const id = String(v[0]).trim(); if (id && want[id] && String(v[21]).trim() === '') { v[21] = want[id][0]; v[22] = want[id][1]; filled++; } });
      sh.getRange(2, 22, last0 - 1, 2).setValues(vals.map(v => [v[21], v[22]]));
      clearCacheSilent_();
      return json_({ ok: true, mode: 'fill_status', filled });
    }
    // append：Questions 依 id 去重；其他分頁直接接在最後一列之後
    const last = sh.getLastRow();
    let skipped = 0, toWrite = rows;
    if (isQuestionSheet_(sh) && last >= 2) {
      const ids = {}; sh.getRange(2, 1, last - 1, 1).getValues().forEach(r => { const v = String(r[0]).trim(); if (v) ids[v] = 1; });
      toWrite = rows.filter(r => { const dup = ids[String(r[0]).trim()]; if (dup) skipped++; return !dup; });
    }
    if (toWrite.length) sh.getRange(last + 1, 1, toWrite.length, width).setValues(toWrite);
    clearCacheSilent_();
    return json_({ ok: true, mode: 'append', sheet: sh.getName(), firstRow: last + 1, written: toWrite.length, skipped, lastRow: sh.getLastRow() });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally { lock.releaseLock(); }
}

function clearCacheSilent_() {
  const c = CacheService.getScriptCache();
  ['active', 'all', 'draft', 'reviewed'].forEach(s => c.remove('bank:' + s + ':' + GAS_VERSION));
}

// v6：題目分「Questions_OSH」「Questions_ENV」兩張分頁（職安／環保分開）；都不存在時回退到舊的「Questions」
const SHEET_QUESTIONS_SPLIT = ['Questions_OSH', 'Questions_ENV'];
function questionSheets_(ss) {
  const list = SHEET_QUESTIONS_SPLIT.map(n => ss.getSheetByName(n)).filter(Boolean);
  if (list.length) return list;
  const old = ss.getSheetByName(SHEET_QUESTIONS);
  return old ? [old] : [];
}
function isQuestionSheet_(sh) { return sh.getName() === SHEET_QUESTIONS || SHEET_QUESTIONS_SPLIT.indexOf(sh.getName()) >= 0; }
function readQuestionRows_(ss) {   // 合併各題目分頁：回傳 {head, rows}，欄位以第一張分頁為準
  let head = null; const rows = [];
  questionSheets_(ss).forEach(sh => {
    const v = sh.getDataRange().getValues(); if (!v.length) return;
    const h = v.shift().map(x => String(x).trim());
    if (!head) head = h;
    const map = h.map(x => head.indexOf(x));
    v.forEach(r => { const o = new Array(head.length).fill(''); h.forEach((x, i) => { if (map[i] >= 0) o[map[i]] = r[i]; }); rows.push(o); });
  });
  return { head: head || [], rows };
}

function buildBank_(status) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const { head, rows } = readQuestionRows_(ss);
  const idx = {}; head.forEach((h, i) => idx[h] = i);
  const need = ['id','law_id','law','article','law_version','category','difficulty',
                'q_zh','a_zh','b_zh','c_zh','d_zh','q_en','a_en','b_en','c_en','d_en','answer','explain_zh','explain_en','status'];
  const missing = need.filter(k => !(k in idx));
  if (missing.length) throw new Error('Questions 缺欄位：' + missing.join(', '));
  const questions = [];
  rows.forEach(r => {
    const id = String(r[idx.id] || '').trim();
    if (!id) return;
    const st = String(r[idx.status] || '').trim().toLowerCase();
    if (status !== 'all' && st !== status) return;
    const ans = String(r[idx.answer] || '').trim().toLowerCase();
    if (!'abcd'.includes(ans) || ans.length !== 1) return;          // 答案不合法就不出
    const q = {};
    need.forEach(k => { q[k] = r[idx[k]]; });
    q.difficulty = Number(q.difficulty) || 2;
    q.answer = ans; q.status = st;
    need.forEach(k => { if (typeof q[k] === 'string') q[k] = q[k].trim(); });
    questions.push(q);
  });
  return { generated: new Date().toISOString(), source: 'gas', gasVersion: GAS_VERSION,
           status, count: questions.length, config: readConfig_(ss), questions };
}

function readConfig_(ss) {
  const sh = ss.getSheetByName(SHEET_CONFIG);
  if (!sh) return {};
  const cfg = {};
  sh.getDataRange().getValues().slice(1).forEach(r => {
    const k = String(r[0] || '').trim(); if (!k) return;
    const v = r[1];
    cfg[k] = (typeof v === 'number') ? v : (isNaN(Number(v)) || String(v).trim() === '' ? String(v) : Number(v));
  });
  delete cfg.import_token;   // 密鑰不對外回傳（改用指令碼屬性，此行為保險）
  return cfg;
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/* ---------- 試算表選單 ---------- */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('知識王')
    .addItem('清除快取（改題後立即生效）', 'clearCache')
    .addItem('檢查題庫（答案/欄位）', 'checkBank')
    .addItem('設定匯入密鑰（給 push_to_sheet.py 用）', 'setImportToken')
    .addToUi();
}
function setImportToken() {
  const ui = SpreadsheetApp.getUi();
  const r = ui.prompt('設定匯入密鑰', '輸入一串自訂密碼（建議 20 個以上英數字），同一串要存成 gas/.token。留空＝停用匯入。', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  const t = r.getResponseText().trim();
  const props = PropertiesService.getScriptProperties();
  if (t) props.setProperty('IMPORT_TOKEN', t); else props.deleteProperty('IMPORT_TOKEN');
  SpreadsheetApp.getActiveSpreadsheet().toast(t ? '密鑰已儲存（' + t.length + ' 字）' : '匯入已停用', '知識王');
}
function clearCache() {
  const c = CacheService.getScriptCache();
  ['active', 'all', 'draft', 'reviewed'].forEach(s => c.remove('bank:' + s + ':' + GAS_VERSION));
  SpreadsheetApp.getActiveSpreadsheet().toast('快取已清除', '知識王');
}
function checkBank() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const { head, rows } = readQuestionRows_(ss);
  const iId = head.indexOf('id'), iAns = head.indexOf('answer'), iSt = head.indexOf('status');
  const bad = [], seen = {}, cnt = { active: 0, draft: 0, reviewed: 0, other: 0 };
  rows.forEach((r, n) => {
    const id = String(r[iId] || '').trim(); if (!id) return;
    if (seen[id]) bad.push(`第 ${n + 2} 列：id 重複 ${id}`); seen[id] = 1;
    const a = String(r[iAns] || '').trim().toLowerCase();
    if (!'abcd'.includes(a) || a.length !== 1) bad.push(`第 ${n + 2} 列 ${id}：answer 不是 a–d（${a}）`);
    const st = String(r[iSt] || '').trim().toLowerCase();
    cnt[st in cnt ? st : 'other']++;
  });
  const msg = `題數：active ${cnt.active}、reviewed ${cnt.reviewed}、draft ${cnt.draft}、其他 ${cnt.other}\n` +
              (bad.length ? '問題：\n' + bad.slice(0, 20).join('\n') : '沒有發現問題');
  SpreadsheetApp.getUi().alert('題庫檢查', msg, SpreadsheetApp.getUi().ButtonSet.OK);
}
