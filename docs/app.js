/* 台灣職安環保知識王 — 單機版前端（v0.1）
   讀 data/questions.json；單人闖關 20 題、每日挑戰 10 題；15 秒倒數；
   計分：答對 500 + 500×(剩餘秒/15)，連對 3 題起每題 +50；答錯/逾時 0。 */
(() => {
'use strict';

const CFG = { questionsPerGame: 20, secondsPerQuestion: 15, baseScore: 500, speedBonusMax: 500,
              streakStart: 3, streakBonus: 50, dailyQuestions: 10, useDraft: true };

const I18N = {
  zh: { title:'台灣職安環保知識王', lead:'職業安全衛生 × 環保法規　限時搶答', solo:'單人闖關', soloDesc:'20 題・每題 15 秒・越快分越高',
        daily:'每日挑戰', dailyDesc:'每天 10 題，全站同題', pvp:'連線對戰', pvpDesc:'即將推出（Firebase 建置中）', nick:'暱稱',
        next:'下一題', finish:'看結果', resultTitle:'本局結果', pts:'分', again:'再來一局', home:'回首頁', review:'答題回顧',
        correct:'答對！', wrong:'答錯', timeout:'時間到', ans:'正確答案', correctN:'答對', bestStreak:'最長連對', avgTime:'平均秒數',
        board:'本機排行榜', noBoard:'還沒有紀錄，先來一局！', diff:['','入門','進階','困難'], bank:'題庫', ver:'版本', draftNote:'（含待審 draft 題）',
        nickDefault:'玩家', dailyDone:'今天的每日挑戰已完成，明天再來！', bonus:'連對加成', timeLeft:'剩餘' },
  en: { title:'Taiwan OSH & Env Quiz', lead:'Occupational Safety × Environmental Law · Speed quiz', solo:'Solo Run', soloDesc:'20 questions · 15 s each · faster = more points',
        daily:'Daily Challenge', dailyDesc:'10 questions a day, same for everyone', pvp:'Online Battle', pvpDesc:'Coming soon (Firebase in progress)', nick:'Nickname',
        next:'Next', finish:'Results', resultTitle:'Results', pts:'pts', again:'Play again', home:'Home', review:'Review',
        correct:'Correct!', wrong:'Wrong', timeout:'Time up', ans:'Answer', correctN:'Correct', bestStreak:'Best streak', avgTime:'Avg seconds',
        board:'Local leaderboard', noBoard:'No records yet. Play a round!', diff:['','Easy','Medium','Hard'], bank:'Bank', ver:'version', draftNote:'(incl. draft items)',
        nickDefault:'Player', dailyDone:'Today\'s challenge is done. Come back tomorrow!', bonus:'Streak bonus', timeLeft:'left' }
};

let lang = localStorage.getItem('lang') || 'zh';
let BANK = [];
let game = null;
const $ = id => document.getElementById(id);
const t = k => I18N[lang][k];
const L = (obj, key) => obj[key + '_' + lang] || obj[key + '_zh'];

/* ---------- i18n ---------- */
function applyLang() {
  document.documentElement.lang = lang === 'zh' ? 'zh-Hant' : 'en';
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  $('langBtn').textContent = lang === 'zh' ? 'EN' : '中';
  $('nick').placeholder = t('nick');
  renderBoard();
  renderBankInfo();
  if (game && $('play').classList.contains('active')) renderQuestion(true);
  if ($('result').classList.contains('active')) renderResult();
}

/* ---------- 工具 ---------- */
function mulberry32(a) { return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let x = Math.imul(a ^ a >>> 15, 1 | a); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; }; }
function hashStr(s) { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
function shuffle(arr, rnd = Math.random) { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const today = () => new Date().toLocaleDateString('sv-SE'); // YYYY-MM-DD 本地日期
function show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); $(id).classList.add('active'); window.scrollTo(0, 0); }

/* ---------- 題庫 ---------- */
async function loadBank() {
  const r = await fetch('data/questions.json', { cache: 'no-cache' });
  const j = await r.json();
  BANK = j.questions.filter(q => CFG.useDraft ? true : q.status === 'active');
  renderBankInfo(j.generated);
}
function renderBankInfo(gen) {
  const el = $('bankInfo'); if (!el) return;
  el.dataset.gen = gen || el.dataset.gen || '';
  el.textContent = `${t('bank')} ${BANK.length} ${lang === 'zh' ? '題' : 'questions'} · ${t('ver')} ${el.dataset.gen} ${CFG.useDraft ? t('draftNote') : ''}`;
}

/* ---------- 開局 ---------- */
function pick(mode) {
  if (mode === 'daily') {
    const rnd = mulberry32(hashStr('osh-daily-' + today()));
    return shuffle(BANK, rnd).slice(0, CFG.dailyQuestions);
  }
  return shuffle(BANK).slice(0, CFG.questionsPerGame);
}
function start(mode) {
  if (!BANK.length) return;
  if (mode === 'daily' && localStorage.getItem('daily-' + today())) { alert(t('dailyDone')); return; }
  const nick = ($('nick').value.trim() || t('nickDefault')).slice(0, 12);
  localStorage.setItem('nick', nick);
  game = { mode, nick, qs: pick(mode), i: 0, score: 0, streak: 0, bestStreak: 0, log: [], timer: null, tLeft: 0, tStart: 0 };
  show('play');
  renderQuestion();
}

/* ---------- 作答 ---------- */
function renderQuestion(rerenderOnly) {
  const q = game.qs[game.i];
  $('qNo').textContent = `${game.i + 1} / ${game.qs.length}`;
  $('score').textContent = game.score;
  $('streak').textContent = game.streak >= 2 ? `🔥 ${game.streak}` : '';
  $('qLaw').textContent = `${q.law}${q.article}`;
  $('qDiff').textContent = t('diff')[q.difficulty] || '';
  $('qText').textContent = L(q, 'q');
  const opts = $('opts'); opts.innerHTML = '';
  const answered = game.log[game.i];
  ['a', 'b', 'c', 'd'].forEach(k => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'opt'; b.dataset.k = k;
    b.innerHTML = `<span class="k">${k.toUpperCase()}</span><span>${escapeHtml(L(q, k))}</span>`;
    if (answered) { b.disabled = true; if (k === q.answer) b.classList.add('correct'); else if (k === answered.chosen) b.classList.add('wrong'); }
    else b.onclick = () => answer(k);
    opts.appendChild(b);
  });
  if (answered) { showFeedback(answered); return; }
  $('feedback').classList.add('hidden');
  if (!rerenderOnly) startTimer();
}
function startTimer() {
  clearInterval(game.timer);
  game.tLeft = CFG.secondsPerQuestion; game.tStart = performance.now();
  updateTimer();
  game.timer = setInterval(() => {
    game.tLeft = Math.max(0, CFG.secondsPerQuestion - (performance.now() - game.tStart) / 1000);
    updateTimer();
    if (game.tLeft <= 0) answer(null);
  }, 100);
}
function updateTimer() {
  const pct = game.tLeft / CFG.secondsPerQuestion * 100;
  const bar = $('timerBar'); bar.style.width = pct + '%';
  bar.className = 'bar' + (pct < 25 ? ' danger' : pct < 50 ? ' warn' : '');
  $('timerNum').textContent = Math.ceil(game.tLeft);
}
function answer(chosen) {
  clearInterval(game.timer);
  const q = game.qs[game.i];
  const used = Math.min(CFG.secondsPerQuestion, (performance.now() - game.tStart) / 1000);
  const remain = Math.max(0, CFG.secondsPerQuestion - used);
  const ok = chosen === q.answer;
  let gained = 0, bonus = 0;
  if (ok) {
    game.streak++; game.bestStreak = Math.max(game.bestStreak, game.streak);
    gained = CFG.baseScore + Math.round(CFG.speedBonusMax * remain / CFG.secondsPerQuestion);
    if (game.streak >= CFG.streakStart) bonus = CFG.streakBonus;
  } else game.streak = 0;
  game.score += gained + bonus;
  const rec = { chosen, ok, used: Math.round(used * 10) / 10, gained, bonus };
  game.log[game.i] = rec;
  document.querySelectorAll('.opt').forEach(b => { b.disabled = true; if (b.dataset.k === q.answer) b.classList.add('correct'); else if (b.dataset.k === chosen) b.classList.add('wrong'); });
  $('score').textContent = game.score;
  $('streak').textContent = game.streak >= 2 ? `🔥 ${game.streak}` : '';
  showFeedback(rec);
}
function showFeedback(rec) {
  const q = game.qs[game.i];
  const head = $('fbHead');
  head.className = 'fb-head ' + (rec.ok ? 'ok' : 'ng');
  head.textContent = rec.ok ? `${t('correct')} +${rec.gained}${rec.bonus ? ` (${t('bonus')} +${rec.bonus})` : ''}`
                            : `${rec.chosen ? t('wrong') : t('timeout')}　${t('ans')}：${q.answer.toUpperCase()}`;
  $('fbExplain').textContent = L(q, 'explain');
  $('nextBtn').textContent = game.i + 1 < game.qs.length ? t('next') : t('finish');
  $('feedback').classList.remove('hidden');
}
function next() {
  if (game.i + 1 < game.qs.length) { game.i++; renderQuestion(); }
  else finish();
}

/* ---------- 結果與排行榜 ---------- */
function finish() {
  clearInterval(game.timer);
  const rec = { nick: game.nick, mode: game.mode, score: game.score, correct: game.log.filter(r => r.ok).length, n: game.qs.length, date: today() };
  const board = JSON.parse(localStorage.getItem('board') || '[]');
  board.push(rec); board.sort((a, b) => b.score - a.score); localStorage.setItem('board', JSON.stringify(board.slice(0, 20)));
  if (game.mode === 'daily') localStorage.setItem('daily-' + today(), String(game.score));
  show('result'); renderResult();
}
function renderResult() {
  if (!game) return;
  $('rScore').textContent = game.score;
  const correct = game.log.filter(r => r.ok).length;
  const avg = (game.log.reduce((s, r) => s + r.used, 0) / game.log.length).toFixed(1);
  $('rStats').innerHTML = `<div><b>${correct}/${game.qs.length}</b><span>${t('correctN')}</span></div><div><b>${game.bestStreak}</b><span>${t('bestStreak')}</span></div><div><b>${avg}s</b><span>${t('avgTime')}</span></div>`;
  const ol = $('reviewList'); ol.innerHTML = '';
  game.qs.forEach((q, i) => {
    const r = game.log[i];
    const li = document.createElement('li'); li.className = r.ok ? 'ok' : 'ng';
    li.innerHTML = `<div class="rq">${escapeHtml(L(q, 'q'))}</div><div class="ra">${t('ans')}：${q.answer.toUpperCase()}. ${escapeHtml(L(q, q.answer))}${r.ok ? '' : r.chosen ? `　（${lang === 'zh' ? '你選' : 'you chose'} ${r.chosen.toUpperCase()}）` : `　（${t('timeout')}）`}</div><div class="rx">${escapeHtml(L(q, 'explain'))}</div>`;
    ol.appendChild(li);
  });
  renderBoard();
}
function renderBoard() {
  const el = $('board'); if (!el) return;
  const board = JSON.parse(localStorage.getItem('board') || '[]');
  if (!board.length) { el.innerHTML = `<h4>${t('board')}</h4><p class="empty">${t('noBoard')}</p>`; return; }
  el.innerHTML = `<h4>${t('board')}</h4><table>${board.slice(0, 10).map((r, i) => `<tr><td>${i + 1}. ${escapeHtml(r.nick)}</td><td>${r.mode === 'daily' ? '📅' : '🎯'} ${r.correct}/${r.n} · ${r.date}</td><td>${r.score}</td></tr>`).join('')}</table>`;
}
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

/* ---------- 綁定 ---------- */
document.querySelectorAll('.mode').forEach(b => b.addEventListener('click', () => start(b.dataset.mode)));
$('nextBtn').addEventListener('click', next);
$('againBtn').addEventListener('click', () => start(game.mode));
$('homeBtn').addEventListener('click', () => { game = null; show('home'); renderBoard(); });
$('langBtn').addEventListener('click', () => { lang = lang === 'zh' ? 'en' : 'zh'; localStorage.setItem('lang', lang); applyLang(); });
$('nick').value = localStorage.getItem('nick') || '';
document.addEventListener('keydown', e => {
  if (!$('play').classList.contains('active')) return;
  const k = e.key.toLowerCase();
  if ('abcd'.includes(k) && !game.log[game.i]) answer(k);
  else if ((e.key === 'Enter' || e.key === ' ') && game.log[game.i]) { e.preventDefault(); next(); }
});
applyLang();
loadBank().catch(err => { $('bankInfo').textContent = '題庫載入失敗 / failed to load bank: ' + err; });
})();
