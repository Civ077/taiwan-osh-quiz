/* 台灣職安環保知識王 — 前端 v0.3
   單人闖關 / 每日挑戰 / 連線對戰（隨機配對、房間碼、電腦）＋ 全站排行榜（Firebase）
   題庫：GAS API（CFG.bankUrl）→ 失敗退回 data/questions.json
   計分：答對 500 + 500×(剩餘秒/15)，連對 3 題起每題 +50；答錯/逾時 0。 */
(() => {
'use strict';

const CFG = { questionsPerGame: 20, secondsPerQuestion: 15, baseScore: 500, speedBonusMax: 500,
              streakStart: 3, streakBonus: 50, dailyQuestions: 10, useDraft: true,
              pvpGapMs: 2500, pvpCountdownMs: 4000, lobbyWaitMs: 10000,
              // 題庫 API（GAS 網頁應用程式 /exec 網址；留空＝只用 repo 內的 data/questions.json）
              bankUrl: 'https://script.google.com/macros/s/AKfycbw8GLA29GyEC4hLyXCZoaRBrG3mgJl389Tye47b8XARo-2fKs3rY6Jbfcm6Uxe0ewDM/exec' };
const CFG_MAP = { questions_per_game: 'questionsPerGame', seconds_per_question: 'secondsPerQuestion', base_score: 'baseScore',
                  speed_bonus_max: 'speedBonusMax', streak_start: 'streakStart', streak_bonus: 'streakBonus', daily_questions: 'dailyQuestions',
                  lobby_wait_seconds: 'lobbyWaitSec' };

const I18N = {
  zh: { title:'台灣職安環保知識王', lead:'職業安全衛生 × 環保法規　限時搶答', solo:'單人闖關', soloDesc:'20 題・每題 15 秒・越快分越高',
        daily:'每日挑戰', dailyDesc:'每天 10 題，全站同題', pvp:'連線對戰', pvpDesc:'隨機配對或房間碼，同題同步搶答', nick:'暱稱',
        prev:'上一題', backCur:'回到目前題目', viewing:'回看第 {n} 題（你的作答已標示，倒數暫停中）', noAns:'未作答', resultTitle:'本局結果',
        pts:'分', again:'再來一局', home:'回首頁', review:'答題回顧', timeout:'時間到', ans:'正確答案', correctN:'答對', bestStreak:'最長連對', avgTime:'平均秒數',
        board:'排行榜', noBoard:'還沒有紀錄，先來一局！', diff:['','入門','進階','困難'], bank:'題庫', ver:'版本', draftNote:'（含待審 draft 題）',
        nickDefault:'玩家', dailyDone:'今天的每日挑戰已完成，明天再來！', bonus:'連對加成',
        match:'隨機配對', matchDesc:'10 秒內沒人就可改打電腦或開房間', host:'建立房間', hostDesc:'拿到四碼房號，傳給朋友', join:'輸入房號加入', joinBtn:'加入',
        bot:'跟電腦對戰', botDesc:'離線也能玩，電腦依難度隨機作答', roomCode:'房號', waitBot:'改打電腦', cancel:'取消',
        waitMatch:'配對中…', waitNoOne:'目前沒有其他玩家，可以改打電腦或建立房間邀請朋友', waitRoom:'等待朋友加入…把房號傳給對方', joining:'加入中…',
        found:'配對成功！對手：{n}', starting:'{s} 秒後開始', roomNotFound:'找不到這個房號或房間已開始', needOnline:'連線對戰需要網路與雲端登入，目前不可用；可改打電腦',
        bot1:'電腦', you:'你', opp:'對手', win:'你贏了！', lose:'你輸了', draw:'平手', gapMe:'你 +{a}', gapOpp:'對手 +{b}', oppLeft:'對手已離線，剩下題目由電腦代打',
        online:'雲端連線中', offline:'離線（排行榜僅本機）', globalNote:'全站前 10 名', localNote:'本機紀錄', vsBot:'（對電腦，不列入全站排行）',
        nickHint:'請先輸入暱稱（1–12 字）才能開始遊戲，暱稱會顯示在排行榜與對戰中', nickRequired:'⚠ 請先輸入暱稱再開始',
        groupOsh:'職業安全衛生', groupEnv:'環保', segNoteOsh:'目前出題範圍：職業安全衛生法規（單人、每日、對戰、排行榜各自獨立）', segNoteEnv:'目前出題範圍：環保法規（單人、每日、對戰、排行榜各自獨立）' },
  en: { title:'Taiwan OSH & Env Quiz', lead:'Occupational Safety × Environmental Law · Speed quiz', solo:'Solo Run', soloDesc:'20 questions · 15 s each · faster = more points',
        daily:'Daily Challenge', dailyDesc:'10 questions a day, same for everyone', pvp:'Online Battle', pvpDesc:'Random match or room code, same questions in sync', nick:'Nickname',
        prev:'Previous', backCur:'Back to current', viewing:'Viewing Q{n} (your answer marked; timer paused)', noAns:'No answer', resultTitle:'Results',
        pts:'pts', again:'Play again', home:'Home', review:'Review', timeout:'Time up', ans:'Answer', correctN:'Correct', bestStreak:'Best streak', avgTime:'Avg seconds',
        board:'Leaderboard', noBoard:'No records yet. Play a round!', diff:['','Easy','Medium','Hard'], bank:'Bank', ver:'version', draftNote:'(incl. draft items)',
        nickDefault:'Player', dailyDone:'Today\'s challenge is done. Come back tomorrow!', bonus:'Streak bonus',
        match:'Random match', matchDesc:'No one in 10 s? Play the bot or open a room', host:'Create room', hostDesc:'Get a 4-letter code to share', join:'Join with code', joinBtn:'Join',
        bot:'Play vs bot', botDesc:'Works offline; bot answers by difficulty', roomCode:'Room', waitBot:'Play bot instead', cancel:'Cancel',
        waitMatch:'Matching…', waitNoOne:'No other players right now. Play the bot or create a room for a friend', waitRoom:'Waiting for a friend… share the room code', joining:'Joining…',
        found:'Matched! Opponent: {n}', starting:'Starting in {s} s', roomNotFound:'Room not found or already started', needOnline:'Online battle needs network + cloud sign-in; try the bot instead',
        bot1:'Bot', you:'You', opp:'Opp', win:'You win!', lose:'You lose', draw:'Draw', gapMe:'You +{a}', gapOpp:'Opp +{b}', oppLeft:'Opponent left; the bot answers the rest',
        online:'Online', offline:'Offline (local leaderboard only)', globalNote:'Global top 10', localNote:'Local records', vsBot:'(vs bot, not ranked globally)',
        nickHint:'Enter a nickname (1–12 chars) to play; it appears on leaderboards and in battles', nickRequired:'⚠ Please enter a nickname first',
        groupOsh:'Occupational Safety', groupEnv:'Environment', segNoteOsh:'Current scope: occupational safety & health laws (solo, daily, battle and leaderboard are separate)', segNoteEnv:'Current scope: environmental laws (solo, daily, battle and leaderboard are separate)' }
};

let lang = localStorage.getItem('lang') || 'zh';
let GROUP = (localStorage.getItem('group') === 'ENV') ? 'ENV' : 'OSH';   // 出題範圍：OSH 職安 / ENV 環保，兩邊完全獨立
let BANK_ALL = [], BANK = [], BANK_BY_ID = {};
const scopeKey = mode => mode + '_' + GROUP;                               // 排行榜、每日挑戰都依範圍分開
let game = null;
let boardMode = 'solo';
const $ = id => document.getElementById(id);
const t = k => I18N[lang][k];
const L = (obj, key) => obj[key + '_' + lang] || obj[key + '_zh'];
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
async function loadBank() {
  let j = null, src = 'local';
  const url = new URLSearchParams(location.search).get('bank') || CFG.bankUrl;
  if (url) {
    try {
      const ctrl = new AbortController(); const tm = setTimeout(() => ctrl.abort(), 8000);
      const r = await fetch(url + (url.includes('?') ? '&' : '?') + 'status=' + (CFG.useDraft ? 'draft' : 'active'), { signal: ctrl.signal });
      clearTimeout(tm);
      if (r.ok) { j = await r.json(); src = 'cloud'; }
    } catch (e) { console.warn('雲端題庫讀取失敗，改用本機：', e); }
  }
  if (!j) { const r = await fetch('data/questions.json', { cache: 'no-cache' }); j = await r.json(); }
  if (j.config) Object.keys(CFG_MAP).forEach(k => { const v = Number(j.config[k]); if (k in j.config && !isNaN(v) && v > 0) CFG[CFG_MAP[k]] = v; });
  if (CFG.lobbyWaitSec) CFG.lobbyWaitMs = CFG.lobbyWaitSec * 1000;
  const secParam = Number(new URLSearchParams(location.search).get('sec'));   // 測試用：?sec=4 縮短每題秒數
  if (secParam > 0) CFG.secondsPerQuestion = secParam;
  BANK_ALL = j.questions.filter(q => CFG.useDraft ? q.status !== 'archived' : q.status === 'active');
  BANK_ALL.forEach(q => { if (!q.law_group) q.law_group = String(q.law_id || q.id || '').startsWith('ENV') ? 'ENV' : 'OSH'; });
  applyGroup();
  renderBankInfo(String(j.generated || '').slice(0, 10), src);
}
function applyGroup() {
  BANK = BANK_ALL.filter(q => q.law_group === GROUP);
  BANK_BY_ID = {}; BANK.forEach(q => BANK_BY_ID[q.id] = q);
}
function setGroup(g) {
  GROUP = g === 'ENV' ? 'ENV' : 'OSH'; localStorage.setItem('group', GROUP);
  applyGroup(); renderGroup(); renderBankInfo(); renderBoard();
}
function renderGroup() {
  document.querySelectorAll('.segbtn').forEach(b => { b.classList.toggle('active', b.dataset.group === GROUP); b.setAttribute('aria-selected', b.dataset.group === GROUP); });
  const n = $('segNote'); if (n) n.textContent = t(GROUP === 'ENV' ? 'segNoteEnv' : 'segNoteOsh');
}
function renderBankInfo(gen, src) {
  const el = $('bankInfo'); if (!el) return;
  el.dataset.gen = gen || el.dataset.gen || ''; el.dataset.src = src || el.dataset.src || '';
  const srcLabel = el.dataset.src === 'cloud' ? (lang === 'zh' ? '雲端' : 'cloud') : (lang === 'zh' ? '本機' : 'local');
  el.textContent = `${t(GROUP === 'ENV' ? 'groupEnv' : 'groupOsh')} ${t('bank')} ${BANK.length} ${lang === 'zh' ? '題' : 'questions'}（${lang === 'zh' ? '全部' : 'all'} ${BANK_ALL.length}） · ${srcLabel} · ${t('ver')} ${el.dataset.gen} ${CFG.useDraft ? t('draftNote') : ''}`;
}

/* ---------- 開局 ---------- */
function pickIds(mode) {
  if (mode === 'daily') { const rnd = mulberry32(hashStr('osh-daily-' + GROUP + '-' + today())); return shuffle(BANK, rnd).slice(0, CFG.dailyQuestions).map(q => q.id); }
  return shuffle(BANK).slice(0, CFG.questionsPerGame).map(q => q.id);
}
const Q_FIELDS = ['id','law','article','category','difficulty','q_zh','a_zh','b_zh','c_zh','d_zh','q_en','a_en','b_en','c_en','d_en','answer','explain_zh','explain_en'];
const slimQ = q => { const o = {}; Q_FIELDS.forEach(k => { if (q[k] != null) o[k] = q[k]; }); return o; };
function newGame(mode, ids, pvp) {
  // ids 可以是題目 id，也可以是題目物件（連線對戰由房主把整份題目存進房間，雙方保證同題）
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

/* ---------- 連線對戰 ---------- */
let pv = null; // 配對/房間狀態（進入 play 前）
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
}
function pvpCleanup() {
  if (!pv) return;
  try { pv.refs.forEach(r => r.off()); } catch (e) {}
  if (pv.lobbyRef) pv.lobbyRef.remove().catch(() => {});
  if (pv.roomRef && pv.role === 'host' && !pv.started) pv.roomRef.remove().catch(() => {});
  clearTimeout(pv.timer); clearInterval(pv.timer2);
  pv = null;
}
function roomCodeGen() { const A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; let s = ''; for (let i = 0; i < 4; i++) s += A[Math.floor(Math.random() * A.length)]; return s; }
function roomPayload(code, guestUid, guestNick) {
  const p = {}; p[FB.uid] = { nick: nickVal(), online: true }; if (guestUid) p[guestUid] = { nick: guestNick || '?', online: true };
  return { host: FB.uid, code, group: GROUP, state: guestUid ? 'ready' : 'waiting', players: p, createdAt: firebase.database.ServerValue.TIMESTAMP };
}

/* 隨機配對：進大廳；由「最早進入的等待者」負責配對最早的另一位 */
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
      pvpEnterRoom(code, 'host');
    }).catch(e => console.warn('create room failed', e));
  });
}
/* 建立房間（房間碼） */
function pvpHost() {
  pvpCleanup();
  pv = { role: 'host', refs: [], started: false };
  const code = roomCodeGen();
  pv.roomRef = FB.db.ref('rooms/' + code);
  pv.roomRef.set(roomPayload(code)).then(() => { pvpWaitUI(t('waitRoom'), { code }); pvpEnterRoom(code, 'host'); });
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
    if (!r || r.state !== 'waiting' || Object.keys(r.players || {}).length >= 2) { pvpWaitUI(t('roomNotFound')); setTimeout(pvpMenu, 1800); return; }
    if (r.group && r.group !== GROUP) setGroup(r.group);   // 用房號加入時，跟著房主的出題範圍
    return roomRef.child('players/' + FB.uid).set({ nick: nickVal(), online: true }).then(() => pvpEnterRoom(code, 'guest'));
  }).catch(e => { console.warn(e); pvpWaitUI(t('roomNotFound')); setTimeout(pvpMenu, 1800); });
}
/* 進房：監聽房間狀態；房主在兩人到齊時抽題並排定開始時間 */
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
    const oppUid = Object.keys(players).find(u => u !== FB.uid);
    if (role === 'host' && r.state !== 'playing' && oppUid && !pv.scheduling) {
      pv.scheduling = true;
      pv.roomRef.update({ state: 'playing', qs: pickIds('pvp').map(id => slimQ(BANK_BY_ID[id])), sec: CFG.secondsPerQuestion, startAt: now() + CFG.pvpCountdownMs });
      return;
    }
    if (oppUid && r.state !== 'playing') pvpWaitUI(fmt(t('found'), { n: players[oppUid].nick || '?' }), { code: role === 'host' ? code : null });
    if (r.state === 'playing' && r.qs && r.startAt && !pv.started) {
      pv.started = true;
      if (r.sec) CFG.secondsPerQuestion = r.sec;          // 以房主的每題秒數為準，雙方時程一致
      const oppNick = oppUid ? (players[oppUid].nick || '?') : '?';
      const opp = { uid: oppUid, nick: oppNick, bot: false, botAnswers: null };
      pvpStartCountdown(r, opp);
    }
  });
}
function pvpStartCountdown(r, opp) {
  const upd = () => {
    const s = Math.max(0, Math.ceil((r.startAt - now()) / 1000));
    pvpWaitUI(fmt(t('found'), { n: opp.nick }) + '　' + fmt(t('starting'), { s }));
    if (now() >= r.startAt - 200) { clearInterval(pv.timer2); beginPvp(r.qs, r.startAt, opp, pv.roomRef); }
  };
  upd(); pv.timer2 = setInterval(upd, 250);
}
/* 電腦對戰：本機模擬，不需雲端 */
function pvpBot() {
  pvpCleanup();
  const ids = pickIds('pvp');
  const rnd = mulberry32(hashStr('bot-' + Date.now()));
  const botAnswers = {};
  ids.forEach((id, k) => {
    const q = BANK_BY_ID[id]; if (!q) return;
    const pOk = [0, 0.8, 0.62, 0.45][q.difficulty] || 0.6;
    const ok = rnd() < pOk;
    const wrong = 'abcd'.replace(q.answer, '');
    botAnswers[k] = { c: ok ? q.answer : wrong[Math.floor(rnd() * 3)], ms: Math.round((0.15 + rnd() * 0.55) * CFG.secondsPerQuestion * 1000) };
  });
  beginPvp(ids, now() + 1500, { uid: 'bot', nick: t('bot1'), bot: true, botAnswers }, null);
}
function beginPvp(ids, startAt, opp, roomRef) {
  const p = { startAt, opp, roomRef, role: pv ? pv.role : null, k: -1, answers: {}, oppAnswers: opp.botAnswers || {}, oppScore: 0, oppStreak: 0, oppLog: [], gapShown: -1, oppLeft: false, refs: [] };
  if (roomRef) {
    const aRef = roomRef.child('answers/' + opp.uid); p.refs.push(aRef);
    aRef.on('value', s => { p.oppAnswers = s.val() || {}; recomputeOpp(); renderVs(); });
    const oRef = roomRef.child('players/' + opp.uid + '/online'); p.refs.push(oRef);
    oRef.on('value', s => { if (s.val() === false && !p.oppLeft) { p.oppLeft = true; botTakeover(); } });
  }
  newGame('pvp', ids, p);
}
function botTakeover() {
  const p = game.pvp; if (!p) return;
  const rnd = mulberry32(hashStr('takeover-' + p.startAt));
  game.qs.forEach((q, k) => { if (p.oppAnswers[k] == null && k >= p.k) { const ok = rnd() < 0.6; const wrong = 'abcd'.replace(q.answer, ''); p.oppAnswers[k] = { c: ok ? q.answer : wrong[Math.floor(rnd() * 3)], ms: Math.round((0.2 + rnd() * 0.55) * CFG.secondsPerQuestion * 1000), bot: true }; } });
  $('gap').textContent = t('oppLeft'); $('gap').classList.remove('hidden'); setTimeout(() => { if (game && game.pvp === p) $('gap').classList.add('hidden'); }, 2500);
  recomputeOpp(); renderVs();
}
function recomputeOpp() {
  const p = game && game.pvp; if (!p) return;
  let score = 0, streak = 0; p.oppLog = [];
  game.qs.forEach((q, k) => {
    const a = p.oppAnswers[k];
    const visible = k < p.k || (k === p.k && a && a.ms <= elapsedInQ());   // 只算「時間上已發生」的作答
    if (!a || !visible) { p.oppLog[k] = null; return; }
    const ok = a.c === q.answer;
    if (ok) streak++; else streak = 0;
    const s = scoreFor(ok, a.ms / 1000, streak);
    score += s.gained + s.bonus; p.oppLog[k] = { ok, gained: s.gained + s.bonus, chosen: a.c };
  });
  p.oppScore = score; p.oppStreak = streak;
}
const qSlot = () => CFG.secondsPerQuestion * 1000 + CFG.pvpGapMs;
function elapsedInQ() { const p = game.pvp; return now() - (p.startAt + p.k * qSlot()); }
function pvpTickStart() {
  clearInterval(game.timer);
  game.timer = setInterval(pvpTick, 100);
  pvpTick();
}
function pvpTick() {
  if (!game || !game.pvp) return;
  const p = game.pvp;
  const el = now() - p.startAt;
  if (el < 0) { updateTimer(CFG.secondsPerQuestion); if (p.k === -1 && !p.preRendered) { p.preRendered = true; game.i = 0; renderQuestion(true); document.querySelectorAll('.opt').forEach(b => b.disabled = true); } return; }
  const k = Math.floor(el / qSlot());
  if (k >= game.qs.length) { clearInterval(game.timer); return finish(); }
  if (k !== p.k) {                       // 進入新題
    p.k = k; game.i = k; game.view = null; game.locked = false;
    for (let j = 0; j < k; j++) if (!game.log[j]) { game.log[j] = { chosen: null, ok: false, used: CFG.secondsPerQuestion, gained: 0, bonus: 0 }; game.streak = 0; }
    $('gap').classList.add('hidden');
    renderQuestion(true);
  }
  const inQ = el - k * qSlot();
  const left = Math.max(0, CFG.secondsPerQuestion - inQ / 1000);
  if (game.view === null) updateTimer(left);
  if (inQ >= CFG.secondsPerQuestion * 1000) {   // 本題時間到：鎖定、顯示雙方得分（不揭曉答案）
    if (!game.log[k]) { game.locked = true; commit(null, false, CFG.secondsPerQuestion); document.querySelectorAll('.opt').forEach(b => b.disabled = true); }
    if (p.gapShown !== k) { p.gapShown = k; recomputeOpp(); renderVs(); showGap(k); }
  }
  // 電腦作答到時間點才算
  if (p.opp.bot || p.oppLeft) { recomputeOpp(); renderVs(); }
}
function showGap(k) {
  const me = game.log[k] ? game.log[k].gained + game.log[k].bonus : 0;
  const o = game.pvp.oppLog[k]; const ob = o ? o.gained : 0;
  $('gap').textContent = fmt(t('gapMe'), { a: me }) + '　·　' + fmt(t('gapOpp'), { b: ob });
  $('gap').classList.remove('hidden');
}
function pvpAnswer(chosen) {
  const p = game.pvp;
  const ms = Math.min(CFG.secondsPerQuestion * 1000, Math.max(0, elapsedInQ()));
  const q = game.qs[game.i];
  commit(chosen, chosen === q.answer, ms / 1000);
  document.querySelectorAll('.opt').forEach(b => { b.disabled = true; if (b.dataset.k === chosen) b.classList.add('picked'); });
  p.answers[game.i] = { c: chosen, ms };
  if (p.roomRef) p.roomRef.child('answers/' + FB.uid + '/' + game.i).set({ c: chosen || '', ms: Math.round(ms) }).catch(e => console.warn(e));
  renderVs();
}
function renderVs() {
  const p = game && game.pvp; if (!p) return;
  const oppDone = p.oppLog[game.i] != null;
  $('vsMe').innerHTML = `<b>${escapeHtml(game.nick)}</b> ${game.score}`;
  $('vsOpp').innerHTML = `${oppDone ? '✔ ' : ''}<b>${escapeHtml(p.opp.nick)}</b> ${p.oppScore}${p.oppLeft ? ' 🤖' : ''}`;
}

/* ---------- 結果與排行榜 ---------- */
function finish() {
  clearInterval(game.timer);
  const correct = game.log.filter(r => r && r.ok).length;
  const rec = { uid: FB.uid || 'local', nick: game.nick, score: game.score, correct, n: game.qs.length, date: today(), ts: Date.now() };
  let result = null;
  if (game.pvp) {
    const p = game.pvp; p.k = game.qs.length; recomputeOpp();
    result = game.score > p.oppScore ? 'win' : game.score < p.oppScore ? 'lose' : 'draw';
    rec.opp = p.opp.nick; rec.oppScore = p.oppScore; rec.result = result;
    if (p.refs) p.refs.forEach(r => r.off());
    if (p.roomRef && p.opp && !p.opp.bot) {
      p.roomRef.child('players/' + FB.uid + '/online').onDisconnect().cancel();
      if (p.role === 'host') { const ref = p.roomRef; setTimeout(() => ref.remove().catch(() => {}), 20000); }   // 對局結束 20 秒後清掉房間
    }
  }
  const board = JSON.parse(localStorage.getItem('board') || '[]');
  board.push({ ...rec, mode: game.mode, group: GROUP }); board.sort((a, b) => b.score - a.score); localStorage.setItem('board', JSON.stringify(board.slice(0, 60)));
  if (game.mode === 'daily') localStorage.setItem('daily-' + GROUP + '-' + today(), String(game.score));
  const isBot = game.pvp && game.pvp.opp.bot;
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
    const p = game.pvp;
    vr.className = 'vsresult ' + game.result;
    vr.innerHTML = `<div class="vr-title">${t(game.result)}</div><div class="vr-row"><span>${escapeHtml(game.nick)}<b>${game.score}</b></span><span class="vsx">vs</span><span>${escapeHtml(p.opp.nick)}<b>${p.oppScore}</b></span></div>`;
    vr.classList.remove('hidden');
    $('rNote').textContent = game.isBot ? t('vsBot') : '';
  } else { vr.classList.add('hidden'); $('rNote').textContent = ''; }
  const ol = $('reviewList'); ol.innerHTML = '';
  game.qs.forEach((q, i) => {
    const r = game.log[i] || { chosen: null, ok: false };
    const li = document.createElement('li'); li.className = r.ok ? 'ok' : 'ng';
    const oppTxt = game.pvp && game.pvp.oppLog[i] ? `　·　${escapeHtml(game.pvp.opp.nick)}：${game.pvp.oppLog[i].ok ? '✔' : '✘'}` : '';
    li.innerHTML = `<div class="rq">${escapeHtml(L(q, 'q'))}</div><div class="ra">${t('ans')}：${q.answer.toUpperCase()}. ${escapeHtml(L(q, q.answer))}${r.ok ? '' : r.chosen ? `　（${lang === 'zh' ? '你選' : 'you chose'} ${r.chosen.toUpperCase()}）` : `　（${t('timeout')}）`}${oppTxt}</div><div class="rx">${escapeHtml(L(q, 'explain'))}</div>`;
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
    }).catch(() => draw(local, t('localNote')));
  } else draw(local, t('localNote'));
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
syncNick();
$('btnMatch').addEventListener('click', pvpMatch);
$('btnHost').addEventListener('click', pvpHost);
$('btnJoin').addEventListener('click', () => pvpJoin($('joinCode').value));
$('joinCode').addEventListener('keydown', e => { if (e.key === 'Enter') pvpJoin($('joinCode').value); });
$('btnBot').addEventListener('click', pvpBot);
$('btnWaitBot').addEventListener('click', pvpBot);
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
initFirebase();
loadBank().catch(err => { $('bankInfo').textContent = '題庫載入失敗 / failed to load bank: ' + err; });
})();
