/* Firebase 專案設定（Web SDK 公開設定，非機密：任何前端網頁的設定都必須送到瀏覽器才能運作）
   專案：taiwan-osh-quiz（Spark 免費方案）  建立日期：2026-09-03

   安全性不靠隱藏這份設定，而靠三層：
     1. Realtime Database 規則（firebase/database.rules.json，已部署）
     2. API 金鑰的 HTTP 參照網址限制（已設定：只允許 https://civ077.github.io/*）
        注意：此限制擋得住把設定複製到別的網頁的人，擋不住偽造 Referer 標頭的程式
     3. App Check（把這份設定綁在本站網域，別的地方拿去用會被拒絕）
   刻意不寫 storageBucket：本專案沒有用到 Cloud Storage，不留設定，
   將來就算有人在主控台誤按啟用，網站也不會連上去。 */
window.FIREBASE_CONFIG = {
  apiKey: "AIzaSyC7f2383ETIAYw1FeNzo9O8dJ5R9LyDTlY",
  authDomain: "taiwan-osh-quiz.firebaseapp.com",
  databaseURL: "https://taiwan-osh-quiz-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "taiwan-osh-quiz",
  messagingSenderId: "217326299212",
  appId: "1:217326299212:web:01274a53c87db6d5792ce9"
};

/* App Check（尚未啟用；填上金鑰後自動生效，程式不必再改）
   目的：讓上面這份設定「只有從本站網域送出的請求才有效」，別人複製走也用不了。
   啟用步驟（Firebase 主控台）：
     1. 建構 → App Check → Apps → 註冊網頁應用程式 → 選 reCAPTCHA v3
     2. 依指示到 Google reCAPTCHA 建立網站金鑰，網域填 civ077.github.io
     3. 把網站金鑰填到下面這行並取消註解，推上 GitHub
     4. 回主控台 App Check → APIs → Realtime Database → 先看幾天「未驗證請求」
        的比例，確認正常玩家都通過後，再按「強制執行」
   注意：第 4 步一按下去，沒有權杖的請求會全部被拒，所以務必先觀察再強制執行。 */
// window.FIREBASE_APPCHECK_KEY = "在這裡填 reCAPTCHA v3 網站金鑰";
