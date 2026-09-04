/* 台灣職安環保知識王 — 前端 v0.6
   單人闖關 / 每日挑戰 / 連線對戰（2–5 人房間、隨機配對、電腦）＋ 全站排行榜（Firebase）
   出題範圍：首頁「職業安全衛生／環保」切換，兩邊題庫、每日挑戰、對戰配對、排行榜完全獨立
   題庫：GAS API（CFG.bankUrl）→ 失敗退回 data/questions.json
   計分：答對 500 + 500×(剩餘秒/20)，連對 3 題起每題 +50；答錯/逾時 0。
   對戰：房主同步題目與每題起算時間；該題全員作答完畢（或時間到）即跳下一題，不必等倒數跑完。 */
(() => {
'use strict';

const CFG = { questionsPerGame: 20, secondsPerQuestion: 20, baseScore: 500, speedBonusMax: 500,
              streakStart: 3, streakBonus: 50, dailyQuestions: 10, useDraft: true,
              pvpGapMs: 2500, pvpCountdownMs: 4000, lobbyWaitMs: 10000, maxPlayers: 5,
              // 題庫 API（GAS 網頁應用程式 /exec 網址；留空＝只用 repo 內的 data/questions.json）
              bankUrl: 'https://script.google.com/macros/s/AKfycbw8GLA29GyEC4hLyXCZoaRBrG3mgJl389Tye47b8XARo-2fKs3rY6Jbfcm6Uxe0ewDM/exec' };
const CFG_MAP = { questions_per_game: 'questionsPerGame', seconds_per_question: 'secondsPerQuestion', base_score: 'baseScore',
                  speed_bonus_max: 'speedBonusMax', streak_start: 'streakStart', streak_bonus: 'streakBonus', daily_questions: 'dailyQuestions',
                  lobby_wait_seconds: 'lobbyWaitSec', max_players: 'maxPlayers' };

const I18N = {
  zh: { title:'台灣職安環保知識王', lead:'職業安全衛生 × 環保法規　限時搶答', solo:'單人闖關', soloDesc:'20 題・每題 20 秒・越快分越高',
        daily:'每日挑戰', dailyDesc:'每天 10 題，全站同題', pvp:'連線對戰', pvpDesc:'2–5 人房間或隨機配對，同題同步搶答', nick:'暱稱',
        prev:'上一題', backCur:'回到目前題目', viewing:'回看第 {n} 題（你的作答已標示，倒數暫停中）', noAns:'未作答', resultTitle:'本局結果',
        pts:'分', again:'再來一局', home:'回首頁', review:'答題回顧', timeout:'時間到', ans:'正確答案', correctN:'答對', bestStreak:'最長連對', avgTime:'平均秒數',
        board:'排行榜', noBoard:'還沒有紀錄，先來一局！', diff:['','入門','進階','困難'], bank:'題庫', ver:'版本', draftNote:'（含待審 draft 題）',
        nickDefault:'玩家', dailyDone:'今天的每日挑戰已完成，明天再來！', bonus:'連對加成',
        match:'隨機配對', matchDesc:'10 秒內沒人就可改打電腦或開房間', host:'建立房間', hostDesc:'拿到四碼房號，最多 5 人一起玩', join:'輸入房號加入', joinBtn:'加入',
        bot:'跟電腦對戰', botDesc:'離線也能玩，電腦依難度隨機作答', roomCode:'房號', waitBot:'改打電腦', cancel:'取消',
        waitMatch:'配對中…', waitNoOne:'目前沒有其他玩家，可以改打電腦或建立房間邀請朋友', waitRoom:'等待朋友加入…把房號傳給對方（最多 5 人），人數夠了按「開始對戰」', joining:'加入中…',
        found:'配對成功！對手：{n}', starting:'{s} 秒後開始', roomNotFound:'找不到這個房號、房間已開始或已滿', needOnline:'連線對戰需要網路與雲端登入，目前不可用；可改打電腦',
        waitHost:'已加入房間，等待房主開始…', startBtn:'開始對戰', players:'玩家', playersN:'{n} 人', hostTag:'房主', youTag:'你',
        bot1:'電腦', you:'你', opp:'對手', win:'你贏了！', lose:'你輸了', draw:'平手', gapMe:'你 +{a}', gapOpp:'{n} +{b}', oppLeft:'{n} 已離線，剩下題目由電腦代打',
        allAnswered:'全員作答完畢，準備下一題', rank:'第 {r} 名', hostLeft:'房主離線，改以計時方式繼續',
        nickHint:'請先輸入暱稱（1–12 字）才能開始遊戲，暱稱會顯示在排行榜與對戰中', nickRequired:'⚠ 請先輸入暱稱再開始',
        groupOsh:'職業安全衛生', groupEnv:'環保', segNoteOsh:'目前出題範圍：職業安全衛生法規（單人、每日、對戰、排行榜各自獨立）', segNoteEnv:'目前出題範圍：環保法規（單人、每日、對戰、排行榜各自獨立）',
        online:'雲端連線中', offline:'離線（排行榜僅本機）', globalNote:'全站前 10 名', localNote:'本機紀錄', vsBot:'（對電腦，不列入全站排行）',
        waitingFor:'尚未作答：{n}', allIn:'全員已作答', weekly:'每週冠軍', weekLead:'本週目前領先', weekN:'第 {w} 週（{a}～{b}）', noWeekly:'尚無週冠軍紀錄' },
  en: { title:'Taiwan OSH & Env Quiz', lead:'Occupational Safety × Environmental Law · Speed quiz', solo:'Solo Run', soloDesc:'20 questions · 20 s each · faster = more points',
        daily:'Daily Challenge', dailyDesc:'10 questions a day, same for everyone', pvp:'Online Battle', pvpDesc:'Rooms of 2–5 or random match, same questions in sync', nick:'Nickname',
        prev:'Previous', backCur:'Back to current', viewing:'Viewing Q{n} (your answer marked; timer paused)', noAns:'No answer', resultTitle:'Results',
        pts:'pts', again:'Play again', home:'Home', review:'Review', timeout:'Time up', ans:'Answer', correctN:'Correct', bestStreak:'Best streak', avgTime:'Avg seconds',
        board:'Leaderboard', noBoard:'No records yet. Play a round!', diff:['','Easy','Medium','Hard'], bank:'Bank', ver:'version', draftNote:'(incl. draft items)',
        nickDefault:'Player', dailyDone:'Today\'s challenge is done. Come back tomorrow!', bonus:'Streak bonus',
        match:'Random match', matchDesc:'No one in 10 s? Play the bot or open a room', host:'Create room', hostDesc:'Get a 4-letter code, up to 5 players', join:'Join with code', joinBtn:'Join',
        bot:'Play vs bot', botDesc:'Works offline; bot answers by difficulty', roomCode:'Room', waitBot:'Play bot instead', cancel:'Cancel',
        waitMatch:'Matching…', waitNoOne:'No other players right now. Play the bot or create a room for a friend', waitRoom:'Waiting for friends… share the room code (up to 5 players), then press Start', joining:'Joining…',
        found:'Matched! Opponent: {n}', starting:'Starting in {s} s', roomNotFound:'Room not found, already started or full', needOnline:'Online battle needs network + cloud sign-in; try the bot instead',
        waitHost:'Joined. Waiting for the host to start…', startBtn:'Start battle', players:'Players', playersN:'{n} players', hostTag:'host', youTag:'you',
        bot1:'Bot', you:'You', opp:'Opp', win:'You win!', lose:'You lose', draw:'Draw', gapMe:'You +{a}', gapOpp:'{n} +{b}', oppLeft:'{n} left; the bot answers for them',
        allAnswered:'Everyone answered — next question', rank:'Rank {r}', hostLeft:'Host offline; continuing on the timer',
        nickHint:'Enter a nickname (1–12 chars) to play; it appears on leaderboards and in battles', nickRequired:'⚠ Please enter a nickname first',
        groupOsh:'Occupational Safety', groupEnv:'Environment', segNoteOsh:'Current scope: occupational safety & health laws (solo, daily, battle and leaderboard are separate)', segNoteEnv:'Current scope: environmental laws (solo, daily, battle and leaderboard are separate)',
        online:'Online', offline:'Offline (local leaderboard only)', globalNote:'Global top 10', localNote:'Local records', vsBot:'(vs bot, not ranked globally)',
        waitingFor:'Waiting for: {n}', allIn:'Everyone answered', weekly:'Weekly champions', weekLead:'Leading this week', weekN:'Week {w} ({a}–{b})', noWeekly:'No weekly champions yet' }
};

let lang = localStorage.getItem('lang') || 'zh';
let GROUP = (localStorage.getItem('group') === 'ENV') ? 'ENV' : 'OSH';   // 出題範圍：OSH 職安 / ENV 環保，兩邊完全獨立
let BANK_ALL = [], BANK = [], BANK_BY_ID = {};
const BANKS = { OSH: null, ENV: null };        // 各範圍題庫（core 欄位）
const LAWS = { OSH: [], ENV: [] };             // 各範圍法規表（law_id, name, weight, family）
const EXPLAIN = {};                            // id → {explain_zh, explain_en}（背景載入）
let SITE_MODE = 'draft';                       // Config.site_mode：draft＝含待審題；active＝只出 active
const scopeKey = mode => mode + '_' + GROUP;                               // 排行榜、每日挑戰都依範圍分開
let game = null;
let boardMode = 'solo';
const $ = id => document.getElementById(id);
const t = k => I18N[lang][k];
const L = (obj, key) => { if (key === 'explain' && obj && EXPLAIN[obj.id]) obj = Object.assign({}, obj, EXPLAIN[obj.id]); return obj[key + '_' + lang] || obj[key + '_zh'] || ''; };
const fmt = (s, o) => s.replace(/\{(\w+)\}/g, (_, k) => o[k]);

/* ---------- Firebase（可選） ---------- */
const FB = { ok: false, uid: null, db: null, offset: 0, nick: '' };
function initFirebase() {
  try {
    if (!window.firebase || !window.FIREBASE_CONFIG) throw new Error('no firebase');
    firebase.initializeApp(window.FIREBASE_CONFIG);
    FB.db = firebase.database();
    firebase.auth().onAuthStateChanged(u => {
      if (u) { FB.uid = u.uid; FB.ok = true; syncNick(); renderNet(); renderBoard(); }
      else firebase.auth().signInAnonymously().catch(e => { console.warn('anon auth failed', e); FB.ok = false; renderNet(); });
    });
    FB.db.ref('.info/serverTimeOffset').on('value', s => { FB.offset = s.val() || 0; });
    FB.db.ref('.info/connected').on('value', s => { FB.conn = !!s.val(); renderNet(); });
  } catch (e) { console.warn('Firebase 未啟用：', e.message); FB.ok = false; renderNet(); }
}
const now = () => Date.now() + FB.offset;
function nickVal() { return $('nick').value.trim().slice(0, 12); }
function requireNick() {            // 暱稱必填：沒填就不能開始任何模式
  if (nickVal()) return true;
  const f = $('nick'); f.focus(); f.classList.add('shake'); setTimeout(() => f.classList.remove('shake'), 600);
  const h = $('nickHint'); if (h) { h.textContent = t('nickRequired'); h.classList.add('warn'); }
  return false;
}
function syncNick() {
  const n = nickVal(); localStorage.setItem('nick', n);
  const h = $('nickHint'); if (h) { h.textContent = n ? '' : t('nickHint'); h.classList.remove('warn'); }
  if (!n) return;
  if (FB.ok && FB.nick !== n) { FB.nick = n; FB.db.ref('users/' + FB.uid).set({ nick: n, updatedAt: firebase.database.ServerValue.TIMESTAMP }).catch(() => {}); }
}
function renderNet() {
  const el = $('netInfo'); if (!el) return;
  const on = FB.ok && FB.conn !== false;
  el.textContent = on ? '☁ ' + t('online') : '○ ' + t('offline');
  $('who').textContent = on ? nickVal() : '';
}

/* ---------- i18n ---------- */
function applyLang() {
  document.documentElement.lang = lang === 'zh' ? 'zh-Hant' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  $('langBtn').textContent = lang === 'zh' ? 'EN' : '中';
  $('nick').placeholder = t('nick');
  renderGroup(); renderBoard(); renderBankInfo(); renderNet();
  const h = $('nickHint'); if (h && !nickVal()) h.textContent = t('nickHint');
  if (game && $('play').classList.contains('active')) renderQuestion(true);
  if ($('result').classList.contains('active')) renderResult();
}

/* ---------- 工具 ---------- */
function mulberry32(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let x = Math.imul(a ^ a >>> 15, 1 | a); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; }; }
function hashStr(s) { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
function shuffle(arr, rnd = Math.random) { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const today = () => new Date().toLocaleDateString('sv-SE');
function show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); $(id).classList.add('active'); window.scrollTo(0, 0); }
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function scoreFor(ok, usedSec, streak) {
  if (!ok) return { gained: 0, bonus: 0 };
  const remain = Math.max(0, CFG.secondsPerQuestion - usedSec);
  return { gained: CFG.baseScore + Math.round(CFG.speedBonusMax * remain / CFG.secondsPerQuestion), bonus: streak >= CFG.streakStart ? CFG.streakBonus : 0 };
}

/* ---------- 題庫 ---------- */
/* 題庫載入（v0.5）：每個範圍各自載入 core 欄位（不含解析），先用 IndexedDB 快取立即開玩、背景更新；解析另外背景載入 */
function idbOpen() {
  return new Promise((res, rej) => {
    const r = indexedDB.open('osh-quiz', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('kv');
    r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
  });
}
async function idbGet(k) { try { const db = await idbOpen(); return await new Promise((res, rej) => { const t = db.transaction('kv').objectStore('kv').get(k); t.onsuccess = () => res(t.result); t.onerror = () => rej(t.error); }); } catch (e) { return null; } }
async function idbSet(k, v) { try { const db = await idbOpen(); await new Promise((res, rej) => { const t = db.transaction('kv', 'readwrite').objectStore('kv').put(v, k); t.onsuccess = res; t.onerror = () => rej(t.error); }); } catch (e) { console.warn('cache write failed', e); } }

const bankUrl = () => new URLSearchParams(location.search).get('bank') || CFG.bankUrl;
async function fetchJson(url, timeoutMs) {
  const ctrl = new AbortController(); const tm = setTimeout(() => ctrl.abort(), timeoutMs);
  try { const r = await fetch(url, { signal: ctrl.signal }); if (!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }
  finally { clearTimeout(tm); }
}
function applyConfig(j) {
  if (!j || !j.config) return;
  Object.keys(CFG_MAP).forEach(k => { const v = Number(j.config[k]); if (k in j.config && !isNaN(v) && v > 0) CFG[CFG_MAP[k]] = v; });
  if (CFG.lobbyWaitSec) CFG.lobbyWaitMs = CFG.lobbyWaitSec * 1000;
  CFG.maxPlayers = Math.min(5, Math.max(2, CFG.maxPlayers | 0));
  const secParam = Number(new URLSearchParams(location.search).get('sec'));   // 測試用：?sec=4 縮短每題秒數
  if (secParam > 0) CFG.secondsPerQuestion = secParam;
  const sm = String(j.config.site_mode || '').toLowerCase();
  SITE_MODE = sm === 'active' ? 'active' : 'draft';
  CFG.useDraft = SITE_MODE !== 'active';
}
function installBank(g, j, src) {
  applyConfig(j);
  const qs = (j.questions || []).filter(q => String(q.law_id || q.id || '').startsWith(g))   // GAS v6 以前不認 group 參數，會回全部：這裡再過濾一次
                                   .filter(q => SITE_MODE === 'active' ? q.status === 'active' : q.status !== 'archived');
  qs.forEach(q => { if (!q.law_group) q.law_group = String(q.law_id || q.id || '').startsWith('ENV') ? 'ENV' : 'OSH'; });
  BANKS[g] = qs; LAWS[g] = Array.isArray(j.laws) ? j.laws : [];
  if (g === GROUP) { BANK_ALL = qs; applyGroup(); renderBankInfo(String(j.generated || '').slice(0, 10), src); }
}
async function loadExplain(g) {                // 解析：背景載入到 EXPLAIN（結果頁答題回顧用），有快取先用快取
  const key = 'explain:' + g;
  const cached = await idbGet(key);
  if (cached && cached.questions) cached.questions.forEach(q => { EXPLAIN[q.id] = q; });
  const url = bankUrl(); if (!url) return;
  try {
    const j = await fetchJson(url + (url.includes('?') ? '&' : '?') + 'status=all&group=' + g + '&fields=explain', 180000);
    if (j && j.questions && j.questions.length) { j.questions.forEach(q => { EXPLAIN[q.id] = q; }); await idbSet(key, j); }
  } catch (e) { console.warn('解析載入失敗（不影響作答）：', e); }
}
async function loadBankGroup(g) {
  const url = bankUrl(); const key = 'bank:core:' + g;
  const el = $('bankInfo');
  const cached = url ? await idbGet(key) : null;
  if (cached && cached.questions && cached.questions.length) installBank(g, cached, 'cache');
  else if (g === GROUP && el) el.textContent = lang === 'zh' ? '題庫載入中（第一次約 10–30 秒）…' : 'Loading question bank (first time 10–30 s)…';
  if (url) {
    try {
      const j = await fetchJson(url + (url.includes('?') ? '&' : '?') + 'status=all&group=' + g + '&fields=core', 120000);
      if (!j || !Array.isArray(j.questions) || !j.questions.length) throw new Error('empty bank');
      const newer = !cached || String(j.generated || '') !== String(cached.generated || '') || j.questions.length !== cached.questions.length;
      if (newer) {
        await idbSet(key, j);
        const playing = document.getElementById('play').classList.contains('active');
        if (!cached || !playing) installBank(g, j, 'cloud');        // 作答中不換題庫，下次載入生效
      } else if (g === GROUP) { applyConfig(j); renderBankInfo(String(j.generated || '').slice(0, 10), 'cloud'); }
      loadExplain(g);
      return;
    } catch (e) { console.warn('雲端題庫讀取失敗：', e); if (cached) { loadExplain(g); return; } }
  }
  // 沒有快取且雲端失敗 → 站內 data/questions.json（含全部範圍與解析）
  const r = await fetch('data/questions.json', { cache: 'no-cache' }); const all = await r.json();
  const j = { generated: all.generated, config: all.config || {}, laws: [], questions: (all.questions || []).filter(q => String(q.law_id || q.id || '').startsWith(g)) };
  j.questions.forEach(q => { if (q.explain_zh || q.explain_en) EXPLAIN[q.id] = { id: q.id, explain_zh: q.explain_zh, explain_en: q.explain_en }; });
  installBank(g, j, 'local');
}
async function loadBank() {
  await loadBankGroup(GROUP);
  loadBankGroup(GROUP === 'OSH' ? 'ENV' : 'OSH');   // 另一範圍背景預載，切換時立刻可用
}
function applyGroup() {
  BANK_ALL = BANKS[GROUP] || [];
  BANK = BANK_ALL.slice();
  BANK_BY_ID = {}; BANK.forEach(q => BANK_BY_ID[q.id] = q);
}
function setGroup(g) {
  GROUP = g === 'ENV' ? 'ENV' : 'OSH'; localStorage.setItem('group', GROUP);
  applyGroup(); renderGroup(); renderBankInfo(); renderBoard();
  if (!BANKS[GROUP]) loadBankGroup(GROUP);
}
function renderGroup() {
  document.querySelectorAll('.segbtn').forEach(b => { b.classList.toggle('active', b.dataset.group === GROUP); b.setAttribute('aria-selected', b.dataset.group === GROUP); });
  const n = $('segNote'); if (n) n.textContent = t(GROUP === 'ENV' ? 'segNoteEnv' : 'segNoteOsh');
}
function renderBankInfo(gen, src) {
  const el = $('bankInfo'); if (!el) return;
  el.dataset.gen = gen || el.dataset.gen || ''; el.dataset.src = src || el.dataset.src || '';
  const srcLabel = el.dataset.src === 'cloud' ? (lang === 'zh' ? '雲端' : 'cloud') : el.dataset.src === 'cache' ? (lang === 'zh' ? '快取（背景更新中）' : 'cached (updating)') : (lang === 'zh' ? '本機' : 'local');
  const total = (BANKS.OSH ? BANKS.OSH.length : 0) + (BANKS.ENV ? BANKS.ENV.length : 0);
  el.textContent = `${t(GROUP === 'ENV' ? 'groupEnv' : 'groupOsh')} ${t('bank')} ${BANK.length} ${lang === 'zh' ? '題' : 'questions'}（${lang === 'zh' ? '全部' : 'all'} ${total}） · ${srcLabel} · ${t('ver')} ${el.dataset.gen}`;
}

/* ---------- 開局 ---------- */
/* 加權抽題：先依 Laws.weight 抽法規（同一局盡量不重複法規），再從該法規抽一題；小法規也有機會出現、大法規不會洗版 */
function pickWeighted(n, rnd) {
  const byLaw = {}; BANK.forEach(q => { (byLaw[q.law_id] = byLaw[q.law_id] || []).push(q); });
  const ids = Object.keys(byLaw); if (!ids.length) return [];
  const w = {}; (LAWS[GROUP] || []).forEach(l => { w[l.law_id] = Math.max(0.1, Number(l.weight) || 1); });
  const pool = {}; ids.forEach(id => { pool[id] = shuffle(byLaw[id], rnd); });
  const out = []; let avail = ids.slice(); let usedLaw = new Set();
  while (out.length < n && avail.length) {
    let cand = avail.filter(id => !usedLaw.has(id)); if (!cand.length) { usedLaw = new Set(); cand = avail; }
    const tot = cand.reduce((a, id) => a + (w[id] || 1), 0); let x = rnd() * tot, pick = cand[cand.length - 1];
    for (const id of cand) { x -= (w[id] || 1); if (x <= 0) { pick = id; break; } }
    out.push(pool[pick].pop().id); usedLaw.add(pick);
    if (!pool[pick].length) avail = avail.filter(id => id !== pick);
  }
  return out;
}
function pickIds(mode) {
  if (mode === 'daily') return pickWeighted(CFG.dailyQuestions, mulberry32(hashStr('osh-daily-' + GROUP + '-' + today())));
  return pickWeighted(CFG.questionsPerGame, Math.random);
}
const Q_FIELDS = ['id','law','article','category','difficulty','q_zh','a_zh','b_zh','c_zh','d_zh','q_en','a_en','b_en','c_en','d_en','answer','explain_zh','explain_en'];
const slimQ = q => { const o = {}; Q_FIELDS.forEach(k => { if (q[k] != null) o[k] = q[k]; }); return o; };
function newGame(mode, ids, pvp) {
  // ids 可以是題目 id，也可以是題目物件（連線對戰由房主把整份題目存進房間，所有人保證同題）
  const qs = ids.map(x => typeof x === 'string' ? BANK_BY_ID[x] : x).filter(Boolean);
  game = { mode, nick: nickVal(), qs, i: 0, view: null, score: 0, streak: 0, bestStreak: 0, log: [], timer: null, tLeft: 0, tStart: 0, paused: 0, locked: false, pvp: pvp || null };
  $('vs').classList.toggle('hidden', !pvp);
  $('gap').classList.add('hidden');
  show('play');
  if (pvp) pvpTickStart(); else renderQuestion();
}
function start(mode) {
  if (!BANK.length) return;
  if (!requireNick()) return;
  if (mode === 'daily' && localStorage.getItem('daily-' + GROUP + '-' + today())) { alert(t('dailyDone')); return; }
  syncNick();
  if (mode === 'pvp') { show('pvp'); pvpMenu(); return; }
  newGame(mode, pickIds(mode));
}

/* ---------- 作答（單人／回看共用） ---------- */
function renderQuestion(rerenderOnly) {
  const viewing = game.view !== null;
  const idx = viewing ? game.view : game.i;
  const q = game.qs[idx];
  $('qNo').textContent = `${idx + 1} / ${game.qs.length}`;
  $('score').textContent = game.score;
  $('streak').textContent = game.streak >= 2 ? `🔥 ${game.streak}` : '';
  $('qLaw').textContent = `${q.law}${q.article}`;
  $('qDiff').textContent = t('diff')[q.difficulty] || '';
  $('qText').textContent = L(q, 'q');
  $('prevBtn').disabled = idx === 0;
  $('backBtn').classList.toggle('hidden', !viewing);
  const opts = $('opts'); opts.innerHTML = '';
  const rec = game.log[idx];
  ['a', 'b', 'c', 'd'].forEach(k => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'opt'; b.dataset.k = k;
    b.innerHTML = `<span class="k">${k.toUpperCase()}</span><span>${escapeHtml(L(q, k))}</span>`;
    if (viewing || rec) { b.disabled = true; if (rec && k === rec.chosen) b.classList.add('picked'); }
    else b.onclick = () => answer(k);
    opts.appendChild(b);
  });
  const note = $('viewNote');
  note.classList.toggle('hidden', !viewing);
  if (viewing) note.textContent = fmt(t('viewing'), { n: idx + 1 }) + (rec && !rec.chosen ? `　(${t('noAns')})` : '');
  if (game.pvp) renderVs();
  if (!viewing && !rerenderOnly && !game.pvp) startTimer();
}
function startTimer() {
  clearInterval(game.timer);
  game.tLeft = CFG.secondsPerQuestion; game.tStart = performance.now(); game.paused = 0; game.locked = false;
  updateTimer(game.tLeft);
  game.timer = setInterval(tick, 100);
}
function tick() {
  if (game.view !== null) return;
  game.tLeft = Math.max(0, CFG.secondsPerQuestion - (performance.now() - game.tStart - game.paused) / 1000);
  updateTimer(game.tLeft);
  if (game.tLeft <= 0) answer(null);
}
function updateTimer(left) {
  const pct = left / CFG.secondsPerQuestion * 100;
  const bar = $('timerBar'); bar.style.width = pct + '%';
  bar.className = 'bar' + (pct < 25 ? ' danger' : pct < 50 ? ' warn' : '');
  $('timerNum').textContent = Math.ceil(left);
}
function viewPrev() {
  return;   // 作答中禁止回看上一題（防作弊）；答題回顧只在結果頁
  // eslint-disable-next-line no-unreachable
  const cur = game.view === null ? game.i : game.view;
  if (cur === 0 || (game.locked && !game.pvp)) return;
  if (game.view === null && !game.pvp) game.pauseAt = performance.now();
  game.view = cur - 1;
  renderQuestion(true);
}
function backToCurrent() {
  if (game.view === null) return;
  if (!game.pvp) game.paused += performance.now() - game.pauseAt;
  game.view = null;
  renderQuestion(true);
}
function answer(chosen) {
  if (game.locked || game.view !== null) return;
  game.locked = true;
  if (game.pvp) return pvpAnswer(chosen);
  clearInterval(game.timer);
  const q = game.qs[game.i];
  const used = Math.min(CFG.secondsPerQuestion, (performance.now() - game.tStart - game.paused) / 1000);
  commit(chosen, chosen === q.answer, used);
  document.querySelectorAll('.opt').forEach(b => { b.disabled = true; if (b.dataset.k === chosen) b.classList.add('picked'); });
  setTimeout(next, chosen ? 300 : 600);
}
function commit(chosen, ok, used) {
  if (ok) { game.streak++; game.bestStreak = Math.max(game.bestStreak, game.streak); } else game.streak = 0;
  const s = scoreFor(ok, used, game.streak);
  game.score += s.gained + s.bonus;
  const rec = { chosen, ok, used: Math.round(used * 10) / 10, gained: s.gained, bonus: s.bonus };
  game.log[game.i] = rec;
  $('score').textContent = game.score;
  $('streak').textContent = game.streak >= 2 ? `🔥 ${game.streak}` : '';
  return rec;
}
function next() {
  if (game.i + 1 < game.qs.length) { game.i++; renderQuestion(); }
  else finish();
}

/* ---------- 連線對戰（2–5 人） ----------
   房間資料：{ host, code, group, max, state:'waiting'|'playing', players:{uid:{nick,online}}, qs, sec, cur, curAt, answers:{uid:{k:{c,ms}}} }
   房主負責推進：第 k 題所有在線玩家都作答、或時間到 → 寫 cur=k+1、curAt=現在+間隔；其他人跟著 cur 走。
   電腦對戰在本機模擬同一套房間物件（LR），邏輯共用。 */
let pv = null;   // 配對/房間狀態（進入 play 前）
function pvpMenu() {
  pvpCleanup();
  $('pvpMenu').classList.remove('hidden'); $('pvpWait').classList.add('hidden');
  const on = FB.ok && FB.conn !== false;
  ['btnMatch', 'btnHost', 'btnJoin'].forEach(id => $(id).disabled = !on);
  if (!on) $('waitMsg').textContent = t('needOnline');
}
function pvpWaitUI(msg, opts = {}) {
  $('pvpMenu').classList.add('hidden'); $('pvpWait').classList.remove('hidden');
  $('waitMsg').textContent = msg;
  $('roomCodeBox').classList.toggle('hidden', !opts.code); if (opts.code) $('roomCode').textContent = opts.code;
  $('btnWaitBot').classList.toggle('hidden', !opts.bot);
  $('btnStart').classList.toggle('hidden', !opts.start); $('btnStart').disabled = !opts.startOk;
  const pl = $('roomPlayers'); pl.innerHTML = '';
  if (opts.players) {
    const list = Object.entries(opts.players);
    pl.innerHTML = `<div class="pl-head">${t('players')} ${fmt(t('playersN'), { n: list.length })} / ${opts.max || CFG.maxPlayers}</div>` +
      list.map(([u, p]) => `<span class="pl${u === FB.uid ? ' me' : ''}${p.online === false ? ' off' : ''}">${escapeHtml(p.nick || '?')}${u === opts.host ? ` <i>${t('hostTag')}</i>` : ''}${u === FB.uid ? ` <i>${t('youTag')}</i>` : ''}</span>`).join('');
  }
}
function pvpCleanup() {
  if (!pv) return;
  try { pv.refs.forEach(r => r.off()); } catch (e) {}
  if (pv.lobbyRef) pv.lobbyRef.remove().catch(() => {});
  if (pv.roomRef && pv.role === 'host' && !pv.started) pv.roomRef.remove().catch(() => {});
  if (pv.roomRef && pv.role === 'guest' && !pv.started && FB.uid) pv.roomRef.child('players/' + FB.uid).remove().catch(() => {});
  clearTimeout(pv.timer); clearInterval(pv.timer2);
  pv = null;
}
function roomCodeGen() { const A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; let s = ''; for (let i = 0; i < 4; i++) s += A[Math.floor(Math.random() * A.length)]; return s; }
function roomPayload(code, guestUid, guestNick) {
  const p = {}; p[FB.uid] = { nick: nickVal(), online: true }; if (guestUid) p[guestUid] = { nick: guestNick || '?', online: true };
  return { host: FB.uid, code, group: GROUP, max: CFG.maxPlayers, state: guestUid ? 'ready' : 'waiting', players: p, createdAt: firebase.database.ServerValue.TIMESTAMP };
}

/* 隨機配對：進大廳；由「最早進入的等待者」負責配對最早的另一位（同出題範圍），配到就直接開打 */
function pvpMatch() {
  pvpCleanup();
  pv = { role: null, refs: [], started: false };
  pv.lobbyRef = FB.db.ref('lobby/' + FB.uid);
  pv.lobbyRef.onDisconnect().remove();
  pv.lobbyRef.set({ nick: nickVal(), group: GROUP, ts: firebase.database.ServerValue.TIMESTAMP, room: null });
  pvpWaitUI(t('waitMatch'));
  pv.timer = setTimeout(() => { if (pv && !pv.roomRef) pvpWaitUI(t('waitNoOne'), { bot: true }); }, CFG.lobbyWaitMs);
  const lobby = FB.db.ref('lobby'); pv.refs.push(lobby);
  lobby.on('value', snap => {
    if (!pv || pv.roomRef) return;
    const all = snap.val() || {};
    const me = all[FB.uid]; if (!me) return;
    if (me.room) return pvpEnterRoom(me.room, 'guest');
    const waiting = Object.entries(all).filter(([u, v]) => v && !v.room && v.ts && now() - v.ts < 90000 && (v.group || 'OSH') === GROUP).sort((a, b) => a[1].ts - b[1].ts);   // 只配對同範圍（職安／環保）的玩家
    if (waiting.length < 2 || waiting[0][0] !== FB.uid) return;      // 只有最早者負責配對
    const [oppUid, opp] = waiting[1];
    const code = roomCodeGen();
    const roomRef = FB.db.ref('rooms/' + code);
    roomRef.set(roomPayload(code, oppUid, opp.nick)).then(() => {
      FB.db.ref('lobby/' + oppUid + '/room').set(code);
      pv.lobbyRef.remove();
      pv.autoStart = true;
      pvpEnterRoom(code, 'host');
    }).catch(e => console.warn('create room failed', e));
  });
}
/* 建立房間（房間碼）：等人進來，房主按「開始對戰」 */
function pvpHost() {
  pvpCleanup();
  pv = { role: 'host', refs: [], started: false };
  const code = roomCodeGen();
  pv.roomRef = FB.db.ref('rooms/' + code);
  pv.roomRef.set(roomPayload(code)).then(() => { pvpWaitUI(t('waitRoom'), { code, start: true }); pvpEnterRoom(code, 'host'); });
}
/* 以房號加入 */
function pvpJoin(code) {
  code = (code || '').trim().toUpperCase(); if (code.length !== 4) return;
  pvpCleanup();
  pv = { role: 'guest', refs: [], started: false };
  pvpWaitUI(t('joining'));
  const roomRef = FB.db.ref('rooms/' + code);
  roomRef.once('value').then(s => {
    const r = s.val();
    if (!r || r.state !== 'waiting' || Object.keys(r.players || {}).length >= (r.max || CFG.maxPlayers)) { pvpWaitUI(t('roomNotFound')); setTimeout(pvpMenu, 1800); return; }
    if (r.group && r.group !== GROUP) setGroup(r.group);   // 用房號加入時，跟著房主的出題範圍
    return roomRef.child('players/' + FB.uid).set({ nick: nickVal(), online: true }).then(() => pvpEnterRoom(code, 'guest'));
  }).catch(e => { console.warn(e); pvpWaitUI(t('roomNotFound')); setTimeout(pvpMenu, 1800); });
}
/* 進房：監聽房間；房主在按下開始（或配對成功）時抽題並排定第 1 題起算時間 */
function pvpEnterRoom(code, role) {
  if (!pv) pv = { refs: [], started: false };
  pv.role = role; pv.code = code;
  if (pv.lobbyRef) { pv.lobbyRef.remove().catch(() => {}); pv.lobbyRef = null; }
  pv.roomRef = FB.db.ref('rooms/' + code);
  pv.roomRef.child('players/' + FB.uid + '/online').onDisconnect().set(false);
  pv.refs.push(pv.roomRef);
  pv.roomRef.on('value', snap => {
    const r = snap.val(); if (!pv || !r) return;
    const players = r.players || {};
    const n = Object.keys(players).length;
    if (r.state !== 'playing') {
      if (role === 'host') {
        if (pv.autoStart && n >= 2 && !pv.scheduling) return pvpStartRoom();
        pvpWaitUI(n >= 2 ? fmt(t('found'), { n: Object.entries(players).filter(([u]) => u !== FB.uid).map(([, p]) => p.nick).join('、') }) : t('waitRoom'),
                  { code, start: true, startOk: n >= 2, players, host: r.host, max: r.max });
      } else pvpWaitUI(t('waitHost'), { players, host: r.host, max: r.max });
      return;
    }
    if (r.qs && r.curAt && !pv.started) {
      pv.started = true;
      if (r.sec) CFG.secondsPerQuestion = r.sec;          // 以房主的每題秒數為準，所有人時程一致
      pvpStartCountdown(r);
    }
  });
}
function pvpStartRoom() {
  if (!pv || pv.role !== 'host' || pv.scheduling) return;
  pv.scheduling = true;
  const at = now() + CFG.pvpCountdownMs;
  pv.roomRef.update({ state: 'playing', qs: pickIds('pvp').map(id => slimQ(BANK_BY_ID[id])), sec: CFG.secondsPerQuestion, gap: CFG.pvpGapMs, cur: 0, curAt: at, startAt: at })
    .catch(e => { console.warn(e); pv.scheduling = false; });
}
function pvpStartCountdown(r) {
  const upd = () => {
    const s = Math.max(0, Math.ceil((r.curAt - now()) / 1000));
    pvpWaitUI(fmt(t('found'), { n: Object.entries(r.players || {}).filter(([u]) => u !== FB.uid).map(([, p]) => p.nick).join('、') }) + '　' + fmt(t('starting'), { s }), { players: r.players, host: r.host, max: r.max });
    if (now() >= r.curAt - 200) { clearInterval(pv.timer2); beginPvp(r, pv.roomRef, pv.role); }
  };
  upd(); pv.timer2 = setInterval(upd, 250);
}
/* 電腦對戰：本機模擬一個房間，不需雲端 */
function pvpBot() {
  pvpCleanup();
  const ids = pickIds('pvp');
  const rnd = mulberry32(hashStr('bot-' + Date.now()));
  const bot = {};
  ids.forEach((id, k) => {
    const q = BANK_BY_ID[id]; if (!q) return;
    const pOk = [0, 0.8, 0.62, 0.45][q.difficulty] || 0.6;
    const ok = rnd() < pOk;
    const wrong = 'abcd'.replace(q.answer, '');
    bot[k] = { c: ok ? q.answer : wrong[Math.floor(rnd() * 3)], ms: Math.round((0.15 + rnd() * 0.55) * CFG.secondsPerQuestion * 1000) };
  });
  const me = FB.uid || 'me';
  const players = {}; players[me] = { nick: nickVal(), online: true }; players.bot = { nick: t('bot1'), online: true, bot: true };
  const LR = { host: me, code: 'BOT', group: GROUP, max: 2, state: 'playing', players, qs: ids.map(id => slimQ(BANK_BY_ID[id])), sec: CFG.secondsPerQuestion, gap: CFG.pvpGapMs, cur: 0, curAt: now() + 1500, answers: {}, botPlan: bot };
  beginPvp(LR, null, 'host');
}
/* 開打：p = 對戰狀態；roomRef 為 null 表示本機（電腦）房間 */
function beginPvp(r, roomRef, role) {
  const me = FB.uid || 'me';
  const p = { roomRef, role, me, room: r, local: !roomRef, k: -1, gapShown: -1, players: {}, order: [], refs: [], hostGone: false, lastAdvance: -1 };   // -1：第 0 題也要能推進（原本設 0 會卡在第一題）
  Object.entries(r.players || {}).forEach(([u, pl]) => { p.players[u] = { uid: u, nick: pl.nick || '?', online: pl.online !== false, bot: !!pl.bot, score: 0, streak: 0, log: [] }; });
  p.order = Object.keys(p.players);
  if (roomRef) {
    p.refs.push(roomRef);
    roomRef.on('value', s => { const v = s.val(); if (!v || !game || game.pvp !== p) return; p.room = v; onRoomUpdate(p); });
  }
  newGame('pvp', r.qs, p);
}
/* 房間資料變動：同步玩家在線狀態、答案、目前題號 */
function onRoomUpdate(p) {
  const r = p.room;
  Object.entries(r.players || {}).forEach(([u, pl]) => {
    if (!p.players[u]) { p.players[u] = { uid: u, nick: pl.nick || '?', online: true, bot: false, score: 0, streak: 0, log: [] }; p.order.push(u); }
    const was = p.players[u].online; p.players[u].online = pl.online !== false;
    if (was && !p.players[u].online && u !== p.me) { flash(fmt(t('oppLeft'), { n: p.players[u].nick })); if (u === r.host) p.hostGone = true; }
  });
  if (typeof r.cur === 'number' && r.cur !== game.i && r.cur >= 0) { if (r.cur >= game.qs.length) return finish(); pvpGoto(r.cur, r.curAt); }
  recomputeAll(); renderVs();
}
function flash(msg) { $('gap').textContent = msg; $('gap').classList.remove('hidden'); setTimeout(() => { if (game && $('gap').textContent === msg) $('gap').classList.add('hidden'); }, 2500); }
/* 進入第 k 題（時間以房間 curAt 為準） */
function pvpGoto(k, curAt) {
  const p = game.pvp;
  for (let j = 0; j < k; j++) if (!game.log[j]) { game.log[j] = { chosen: null, ok: false, used: CFG.secondsPerQuestion, gained: 0, bonus: 0 }; game.streak = 0; }
  p.k = k; p.curAt = curAt; game.i = k; game.view = null; game.locked = false; p.gapShown = -1;
  $('gap').classList.add('hidden');
  renderQuestion(true);
}
function pvpTickStart() {
  clearInterval(game.timer);
  const p = game.pvp; pvpGoto(p.room.cur || 0, p.room.curAt);
  game.timer = setInterval(pvpTick, 100);
  pvpTick();
}
function allAnswered(p, k) {
  return p.order.every(u => { const pl = p.players[u]; if (!pl.online && !pl.bot) return true; return getAnswer(p, u, k) != null; });
}
function getAnswer(p, u, k) {
  const r = p.room; if (p.players[u] && p.players[u].bot) { const a = r.botPlan && r.botPlan[k]; return a || null; }
  return r.answers && r.answers[u] && r.answers[u][k] ? r.answers[u][k] : null;
}
function pvpTick() {
  if (!game || !game.pvp) return;
  const p = game.pvp, r = p.room, k = p.k;
  const inQ = now() - p.curAt;
  if (inQ < 0) { updateTimer(CFG.secondsPerQuestion); if (!p.preRendered) { p.preRendered = true; renderQuestion(true); document.querySelectorAll('.opt').forEach(b => b.disabled = true); } return; }
  if (p.preRendered) { p.preRendered = false; renderQuestion(true); }
  const left = Math.max(0, CFG.secondsPerQuestion - inQ / 1000);
  if (game.view === null) updateTimer(left);
  const timeUp = inQ >= CFG.secondsPerQuestion * 1000;
  if (timeUp && !game.log[k]) { game.locked = true; commit(null, false, CFG.secondsPerQuestion); document.querySelectorAll('.opt').forEach(b => b.disabled = true); }
  // 本題結束（時間到，或全員作答完畢）→ 顯示各家得分；房主（或本機房間）排定下一題
  const done = timeUp || allAnswered(p, k);
  if (done && p.gapShown !== k) {
    p.gapShown = k; game.locked = true; document.querySelectorAll('.opt').forEach(b => b.disabled = true);
    recomputeAll(true); renderVs(); showGap(k, !timeUp);
    if (p.local || p.role === 'host') scheduleNext(p, k);
    else p.fallbackAt = now() + (r.gap || CFG.pvpGapMs) + 4000;   // 房主沒推進時的保險：時間到 4 秒後自己往下走
  }
  if (!p.local && p.role !== 'host' && p.fallbackAt && now() > p.fallbackAt && p.k === k) { p.fallbackAt = 0; if (!p.hostGone) flash(t('hostLeft')); const nk = k + 1; if (nk >= game.qs.length) return finish(); pvpGoto(nk, now() + 500); }
  if (p.local) { recomputeAll(); renderVs(); }
}
function scheduleNext(p, k) {
  if (p.lastAdvance === k) return; p.lastAdvance = k;
  const nk = k + 1, at = now() + (p.room.gap || CFG.pvpGapMs);
  if (p.local) { setTimeout(() => { if (!game || game.pvp !== p) return; p.room.cur = nk; p.room.curAt = at; if (nk >= game.qs.length) return finish(); pvpGoto(nk, at); }, at - now()); return; }
  p.roomRef.update({ cur: nk, curAt: at }).catch(e => console.warn('advance failed', e));
}
function showGap(k, early) {
  const p = game.pvp; recomputeAll(true);
  const parts = p.order.map(u => { const pl = p.players[u]; const g = pl.log[k] ? pl.log[k].gained : 0; return u === p.me ? fmt(t('gapMe'), { a: g }) : fmt(t('gapOpp'), { n: pl.nick, b: g }); });
  $('gap').textContent = (early ? t('allAnswered') + '　·　' : '') + parts.join('　·　');
  $('gap').classList.remove('hidden');
}
function pvpAnswer(chosen) {
  const p = game.pvp;
  const ms = Math.min(CFG.secondsPerQuestion * 1000, Math.max(0, now() - p.curAt));
  const q = game.qs[game.i];
  commit(chosen, chosen === q.answer, ms / 1000);
  document.querySelectorAll('.opt').forEach(b => { b.disabled = true; if (b.dataset.k === chosen) b.classList.add('picked'); });
  const a = { c: chosen || '', ms: Math.round(ms) };
  if (!p.room.answers) p.room.answers = {}; if (!p.room.answers[p.me]) p.room.answers[p.me] = {}; p.room.answers[p.me][game.i] = a;
  if (p.roomRef) p.roomRef.child('answers/' + p.me + '/' + game.i).set(a).catch(e => console.warn(e));
  renderVs();
}
/* 依房間答案重算每位玩家分數；final=true 時本題全部算入（不論時間點） */
function recomputeAll(final) {
  const p = game && game.pvp; if (!p) return;
  const r = p.room;
  p.order.forEach(u => {
    const pl = p.players[u]; if (u === p.me) { pl.score = game.score; pl.streak = game.streak; pl.log = game.log.map(x => x ? { ok: x.ok, gained: x.gained + x.bonus, chosen: x.chosen } : null); return; }
    let score = 0, streak = 0; pl.log = [];
    game.qs.forEach((q, k) => {
      const a = getAnswer(p, u, k);
      const elapsed = k < p.k ? Infinity : (k === p.k ? now() - p.curAt : -1);
      const visible = a && (k < p.k || (k === p.k && (final || a.ms <= elapsed)));   // 只算「時間上已發生」的作答
      if (!visible) { pl.log[k] = null; return; }
      const ok = a.c === q.answer;
      if (ok) streak++; else streak = 0;
      const s = scoreFor(ok, a.ms / 1000, streak);
      score += s.gained + s.bonus; pl.log[k] = { ok, gained: s.gained + s.bonus, chosen: a.c };
    });
    pl.score = score; pl.streak = streak;
  });
}
function rankOrder(p) { return p.order.slice().sort((a, b) => p.players[b].score - p.players[a].score || a.localeCompare(b)); }
function renderVs() {
  const p = game && game.pvp; if (!p) return;
  const k = game.i;
  $('vs').innerHTML = rankOrder(p).map((u, i) => { const pl = p.players[u]; const done = k < p.k || getAnswer(p, u, k) != null; return `<span class="vsp${u === p.me ? ' me' : ''}${pl.online ? '' : ' off'}${done ? ' done' : ' pending'}">${i + 1}. ${done ? '✔ ' : '⏳ '}<b>${escapeHtml(pl.nick)}</b> ${pl.score}${pl.online ? '' : ' 🤖'}</span>`; }).join('');
  // 本題尚未作答的人（在線且非電腦）；全員作答完畢會提前跳題
  const pending = p.order.filter(u => { const pl = p.players[u]; return pl.online && !pl.bot && getAnswer(p, u, k) == null; }).map(u => p.players[u].nick);
  let w = $('vsWait'); if (!w) { w = document.createElement('div'); w.id = 'vsWait'; w.className = 'vswait'; $('vs').after(w); }
  w.textContent = pending.length ? fmt(t('waitingFor'), { n: pending.map(n => escapeHtml(n)).join('、') }) : t('allIn');
  w.classList.toggle('all', !pending.length);
}

/* ---------- 結果與排行榜 ---------- */
function finish() {
  clearInterval(game.timer);
  if (game.finished) return; game.finished = true;
  const correct = game.log.filter(r => r && r.ok).length;
  const rec = { uid: FB.uid || 'local', nick: game.nick, score: game.score, correct, n: game.qs.length, date: today(), ts: Date.now() };
  let result = null;
  if (game.pvp) {
    const p = game.pvp; p.k = game.qs.length; recomputeAll(true);
    const order = rankOrder(p); const top = p.players[order[0]].score; const myRank = order.indexOf(p.me) + 1;
    const tiedTop = order.filter(u => p.players[u].score === top).length;
    result = game.score === top ? (tiedTop > 1 ? 'draw' : 'win') : 'lose';
    const best = order.find(u => u !== p.me);
    rec.opp = best ? p.players[best].nick.slice(0, 12) : '?'; rec.oppScore = best ? p.players[best].score : 0; rec.result = result;
    game.rank = myRank;
    if (p.refs) p.refs.forEach(r => r.off());
    if (p.roomRef) {
      p.roomRef.child('players/' + p.me + '/online').onDisconnect().cancel();
      if (p.role === 'host') { const ref = p.roomRef; setTimeout(() => ref.remove().catch(() => {}), 30000); }   // 對局結束 30 秒後清掉房間
    }
  }
  const board = JSON.parse(localStorage.getItem('board') || '[]');
  board.push({ ...rec, mode: game.mode, group: GROUP }); board.sort((a, b) => b.score - a.score); localStorage.setItem('board', JSON.stringify(board.slice(0, 60)));
  if (game.mode === 'daily') localStorage.setItem('daily-' + GROUP + '-' + today(), String(game.score));
  const isBot = game.pvp && game.pvp.local;
  if (FB.ok && !isBot) FB.db.ref('scores/' + scopeKey(game.mode)).push(rec).catch(e => console.warn('score push failed', e));
  game.result = result; game.isBot = !!isBot;
  pvpCleanup();
  show('result'); renderResult();
}
function renderResult() {
  if (!game) return;
  $('rScore').textContent = game.score;
  const correct = game.log.filter(r => r && r.ok).length;
  const avg = (game.log.reduce((s, r) => s + (r ? r.used : CFG.secondsPerQuestion), 0) / game.log.length).toFixed(1);
  $('rStats').innerHTML = `<div><b>${correct}/${game.qs.length}</b><span>${t('correctN')}</span></div><div><b>${game.bestStreak}</b><span>${t('bestStreak')}</span></div><div><b>${avg}s</b><span>${t('avgTime')}</span></div>`;
  const vr = $('vsResult');
  if (game.pvp) {
    const p = game.pvp; const order = rankOrder(p);
    vr.className = 'vsresult ' + game.result;
    vr.innerHTML = `<div class="vr-title">${t(game.result)}　<small>${fmt(t('rank'), { r: game.rank })}</small></div><div class="vr-list">${order.map((u, i) => `<div class="vr-row${u === p.me ? ' me' : ''}"><span>${i + 1}. ${escapeHtml(p.players[u].nick)}</span><b>${p.players[u].score}</b></div>`).join('')}</div>`;
    vr.classList.remove('hidden');
    $('rNote').textContent = game.isBot ? t('vsBot') : '';
  } else { vr.classList.add('hidden'); $('rNote').textContent = ''; }
  const ol = $('reviewList'); ol.innerHTML = '';
  game.qs.forEach((q, i) => {
    const r = game.log[i] || { chosen: null, ok: false };
    const li = document.createElement('li'); li.className = r.ok ? 'ok' : 'ng';
    const oppTxt = game.pvp ? game.pvp.order.filter(u => u !== game.pvp.me).map(u => { const l = game.pvp.players[u].log[i]; return `${escapeHtml(game.pvp.players[u].nick)}：${l ? (l.ok ? '✔' : '✘') : '—'}`; }).join('　') : '';
    li.innerHTML = `<div class="rq">${escapeHtml(L(q, 'q'))}</div><div class="ra">${t('ans')}：${q.answer.toUpperCase()}. ${escapeHtml(L(q, q.answer))}${r.ok ? '' : r.chosen ? `　（${lang === 'zh' ? '你選' : 'you chose'} ${r.chosen.toUpperCase()}）` : `　（${t('timeout')}）`}${oppTxt ? '　·　' + oppTxt : ''}</div><div class="rx">${escapeHtml(L(q, 'explain'))}</div>`;
    ol.appendChild(li);
  });
  renderBoard();
}
function renderBoard() {
  const el = $('boardBody'); if (!el) return;
  document.querySelectorAll('.tab').forEach(b => b.classList.toggle('active', b.dataset.board === boardMode));
  const local = JSON.parse(localStorage.getItem('board') || '[]').filter(r => r.mode === boardMode && (r.group || 'OSH') === GROUP);
  const draw = (rows, note) => {
    if (!rows.length) { el.innerHTML = `<p class="empty">${t('noBoard')}</p>`; return; }
    el.innerHTML = `<table>${rows.slice(0, 10).map((r, i) => `<tr><td>${i + 1}. ${escapeHtml(r.nick)}${r.uid && r.uid === FB.uid ? ' ★' : ''}</td><td>${r.result ? ({ win: '🏆', lose: '·', draw: '=' })[r.result] + ' ' : ''}${r.correct}/${r.n} · ${r.date}</td><td>${r.score}</td></tr>`).join('')}</table><p class="note">${note}</p>`;
  };
  if (FB.ok) {
    FB.db.ref('scores/' + scopeKey(boardMode)).orderByChild('score').limitToLast(10).once('value').then(s => {
      const rows = []; s.forEach(c => { rows.push(c.val()); }); rows.sort((a, b) => b.score - a.score || a.ts - b.ts);
      draw(rows, t('globalNote'));
      renderWeekly();
    }).catch(() => draw(local, t('localNote')));
  } else draw(local, t('localNote'));
}
/* 每週冠軍：以週一為一週起點（台灣時間），從該範圍／模式的全部紀錄算出每週最高分；本週顯示「目前領先」 */
function weekKey(ts) {
  const d = new Date(ts + 8 * 3600e3);                      // 以 UTC+8 計算週次
  const day = (d.getUTCDay() + 6) % 7;                       // 週一=0
  const mon = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - day));
  return mon.getTime();
}
const fmtMD = ms => { const d = new Date(ms); return (d.getUTCMonth() + 1) + '/' + d.getUTCDate(); };
function renderWeekly() {
  const el = $('weeklyBody'); if (!el || !FB.ok) return;
  FB.db.ref('scores/' + scopeKey(boardMode)).orderByChild('ts').limitToLast(2000).once('value').then(s => {
    const best = {};
    s.forEach(c => { const r = c.val(); if (!r || !r.ts) return; const wk = weekKey(r.ts); if (!best[wk] || r.score > best[wk].score || (r.score === best[wk].score && r.ts < best[wk].ts)) best[wk] = r; });
    const weeks = Object.keys(best).map(Number).sort((a, b) => b - a);
    const cur = weekKey(now());
    if (!weeks.length) { el.innerHTML = `<p class="empty">${t('noWeekly')}</p>`; return; }
    el.innerHTML = `<table>${weeks.slice(0, 12).map(wk => { const r = best[wk]; const d = new Date(wk); const isoWeek = (() => { const t0 = new Date(Date.UTC(d.getUTCFullYear(), 0, 4)); const w = Math.round(((wk - t0.getTime()) / 86400e3 - 3 + ((t0.getUTCDay() + 6) % 7)) / 7) + 1; return w; })();
      return `<tr><td>${wk === cur ? '⏳ ' : '🏆 '}${fmt(t('weekN'), { w: isoWeek, a: fmtMD(wk), b: fmtMD(wk + 6 * 86400e3) })}</td><td>${escapeHtml(r.nick)}${r.uid && r.uid === FB.uid ? ' ★' : ''}${wk === cur ? ' <small>' + t('weekLead') + '</small>' : ''}</td><td>${r.score}</td></tr>`; }).join('')}</table>`;
  }).catch(() => { el.innerHTML = ''; });
}

/* ---------- 綁定 ---------- */
document.querySelectorAll('.mode').forEach(b => b.addEventListener('click', () => start(b.dataset.mode)));
document.querySelectorAll('.segbtn').forEach(b => b.addEventListener('click', () => setGroup(b.dataset.group)));
document.querySelectorAll('.tab').forEach(b => b.addEventListener('click', () => { boardMode = b.dataset.board; renderBoard(); }));
$('prevBtn').addEventListener('click', viewPrev);
$('backBtn').addEventListener('click', backToCurrent);
$('againBtn').addEventListener('click', () => { const m = game.mode; if (m === 'pvp') { show('pvp'); pvpMenu(); } else start(m); });
$('homeBtn').addEventListener('click', () => { clearInterval(game && game.timer); game = null; pvpCleanup(); show('home'); renderBoard(); });
$('langBtn').addEventListener('click', () => { lang = lang === 'zh' ? 'en' : 'zh'; localStorage.setItem('lang', lang); applyLang(); });
$('nick').value = localStorage.getItem('nick') || '';
$('nick').addEventListener('change', syncNick);
$('nick').addEventListener('input', () => { const h = $('nickHint'); if (h && nickVal()) { h.textContent = ''; h.classList.remove('warn'); } });
$('btnMatch').addEventListener('click', pvpMatch);
$('btnHost').addEventListener('click', pvpHost);
$('btnJoin').addEventListener('click', () => pvpJoin($('joinCode').value));
$('joinCode').addEventListener('keydown', e => { if (e.key === 'Enter') pvpJoin($('joinCode').value); });
$('btnBot').addEventListener('click', pvpBot);
$('btnWaitBot').addEventListener('click', pvpBot);
$('btnStart').addEventListener('click', pvpStartRoom);
$('btnCancelWait').addEventListener('click', pvpMenu);
$('pvpBack').addEventListener('click', () => { pvpCleanup(); show('home'); renderBoard(); });
document.addEventListener('keydown', e => {
  if (!game || !$('play').classList.contains('active')) return;
  const k = e.key.toLowerCase();
  if ('abcd'.includes(k) && k.length === 1) answer(k);
  else if (e.key === 'ArrowLeft') viewPrev();
  else if (e.key === 'ArrowRight' || e.key === 'Escape') backToCurrent();
});
window.addEventListener('beforeunload', () => pvpCleanup());
window.__dbg = () => ({ game, pv, FB: { ok: FB.ok, uid: FB.uid, offset: FB.offset }, CFG });
applyLang();
syncNick();
initFirebase();
loadBank().catch(err => { $('bankInfo').textContent = '題庫載入失敗 / failed to load bank: ' + err; });
if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(e => console.warn('sw', e));
})();
