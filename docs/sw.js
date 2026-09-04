/* 台灣職安環保知識王 — service worker（離線 app shell）
   快取首頁／app.js／style.css／firebase-config.js／Firebase SDK；題庫本身存在 IndexedDB，不經此快取。
   策略：app shell 以「網路優先、失敗用快取」，確保有網路時永遠拿到最新版；離線時仍可開啟並跟電腦對戰。 */
const VERSION = 'osh-quiz-v0.9.6';
const SHELL = ['./', './index.html', './app.js?v=20260904t', './style.css?v=20260904t', './firebase-config.js',
  'https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js',
  'https://www.gstatic.com/firebasejs/10.14.1/firebase-app-check-compat.js',
  'https://www.gstatic.com/firebasejs/10.14.1/firebase-auth-compat.js',
  'https://www.gstatic.com/firebasejs/10.14.1/firebase-database-compat.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  if (url.hostname.includes('script.google.com') || url.hostname.includes('firebaseio.com') || url.hostname.includes('firebasedatabase.app') || url.hostname.includes('googleapis.com')) return;   // API／即時資料庫不快取
  e.respondWith(
    fetch(e.request).then(r => {
      if (r && r.ok && (url.origin === location.origin || url.hostname === 'www.gstatic.com')) {
        if (/\/data\//.test(e.request.url)) return r;   // 備援題庫 14 MB，只存 IndexedDB，不進 Cache Storage
        const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy));
      }
      return r;
    }).catch(() => caches.match(e.request).then(m => m || (url.pathname.endsWith('/') || url.pathname.endsWith('index.html') ? caches.match('./index.html') : undefined)))
  );
});
