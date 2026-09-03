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
 */
const GAS_VERSION = 1;
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

function buildBank_(status) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEET_QUESTIONS);
  const rows = sh.getDataRange().getValues();
  const head = rows.shift().map(h => String(h).trim());
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
    .addToUi();
}
function clearCache() {
  const c = CacheService.getScriptCache();
  ['active', 'all', 'draft', 'reviewed'].forEach(s => c.remove('bank:' + s + ':' + GAS_VERSION));
  SpreadsheetApp.getActiveSpreadsheet().toast('快取已清除', '知識王');
}
function checkBank() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEET_QUESTIONS);
  const rows = sh.getDataRange().getValues();
  const head = rows.shift().map(h => String(h).trim());
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
