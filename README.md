# 台灣職安環保知識王（法規對戰）

知識王式問答對戰 App，題目涵蓋台灣職業安全衛生法規與環保法規。
規劃決策見 claude.ai 專案「台灣職安知識」對話「台灣職安環保知識王應用」（2026-09-03）。

## 已定案

| 項目 | 決定 |
|---|---|
| 對象 / 用途 | 所有人、娛樂競賽、中英雙語、記名計分 |
| 模式 | 單人闖關、雙人/多人連線對戰（隨機配對＋房間碼）、每日挑戰（以日期當 seed 抽 10 題） |
| 每局 | 20 題、每題 15 秒 |
| 計分 | 答對 500 ＋ 500 ×（剩餘秒 ÷ 15）；答錯/逾時 0；連對 3 題起每題 +50，答錯歸零 |
| 題庫 | Google Sheet「OSH_ENV_QuizBank」（Laws / Questions / Config / Changelog 四分頁），編輯者：vic、Jamie、Sue |
| 架構 | GAS 定時把 status=active 的題目匯成 JSON → 前端單頁 PWA（GitHub Pages）；即時對戰與登入用 Firebase |
| 雲端 | 題庫 Sheet：https://docs.google.com/spreadsheets/d/1FuC3O7A6pC0b42tiT2F7PxBUysW3IwutPxJquaa8shg/edit ；Drive 資料夾「台灣職安環保知識王」 |
| 程式碼 | https://github.com/Civ077/taiwan-osh-quiz （public，main） |

## 上線狀態

| 項目 | 狀態 |
|---|---|
| 前端 | https://civ077.github.io/taiwan-osh-quiz/ （GitHub Pages，來源 `docs/`） |
| 題庫 API | 已部署 GAS v1：https://script.google.com/macros/s/AKfycbw8GLA29GyEC4hLyXCZoaRBrG3mgJl389Tye47b8XARo-2fKs3rY6Jbfcm6Uxe0ewDM/exec （`?ping=1` 測試、`?status=all` 含 draft）；程式在 `gas/Code.gs`，更新步驟見 `gas/部署清單_照著做.md` |
| Firebase | 專案 `taiwan-osh-quiz`（Spark 免費）：Realtime Database（asia-southeast1）＋匿名登入已啟用；設定在 `docs/firebase-config.js`，規則在 `firebase/database.rules.json`（`firebase deploy --only database`）。前端 v0.3 已接：連線對戰（隨機配對／房間碼／電腦）＋全站排行榜（solo/daily/pvp 各前 10） |

## 資料夾

```
法規對戰/
├─ README.md
├─ 法規原文/          從 law.moj.gov.tw 抓下的現行條文（HTML + 解析後 txt）＋ fetch_law.py / parse_law.py / find_pcode.py（查法規代碼）/ pcodes.json
└─ 題庫/
   ├─ batch1_*.py / batch2_*.py / batch3_*.py    各批題目原始碼（Python 資料）
   ├─ build_sheet.py                            驗證 → 洗牌選項 → 產出 xlsx + json
   ├─ OSH_ENV_QuizBank.xlsx                     上傳 Drive 的來源檔
   ├─ questions_all.json / questions_batchN.json
   └─ tsv/                                      貼進 Google Sheet 用的 TSV
```

## 題庫欄位（Questions 分頁）

`id, law_group, law_id, law, article, law_version, category, difficulty(1–3),
q_zh, a_zh–d_zh, q_en, a_en–d_en, answer(a–d), explain_zh, explain_en,
status(draft/reviewed/active), batch, reviewer, review_note`

- 每題附條號與法規版本日期；解析引用原條文摘要，方便審題時對照。
- 選項由 `build_sheet.py` 以固定種子洗牌，正確答案平均分布於 a–d。
- 新題先標 `draft`，審完改 `active` 才會進遊戲。

## 批次進度

| 批次 | 範圍 | 題數 | 狀態 |
|---|---|---|---|
| 1 | 職業安全衛生法（114/12/19）＋施行細則（115/6/26） | 129 | draft，待審 |
| 2 | 職業安全衛生設施規則（115/6/30）136 題、營造安全衛生設施標準（115/6/30）74 題、機械設備器具安全標準（111/5/11）37 題 | 247 | draft，待審 |
| 3 | 缺氧症預防規則（103/6/26）30 題、高架作業（103/6/25）9 題、高溫作業（103/7/1）17 題、異常氣壓（103/6/25）62 題、危害性化學品標示及通識規則（115/8/26；附表一、四自 118/1/1 施行）29 題、標示設置準則（103/7/2）11 題 | 158 | draft，待審 |
| 4 | 管理辦法、教育訓練、健康保護、危工場所、製程安全 | ~150 | 未開始 |
| 5 | 勞檢法系、災保法、母性保護、機器人、行政要點 | ~130 | 未開始 |
| 6 | 環保第一層（營建空污、噪音、水污、廢清、環評） | ~250 | 未開始 |
| 7 | 環保第二、三層 | ~150 | 未開始 |

## 重建題庫檔

```bash
python 題庫/build_sheet.py
```
