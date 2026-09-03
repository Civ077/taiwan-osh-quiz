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
├─ 法規原文/          從 law.moj.gov.tw 抓下的現行條文（HTML + 解析後 txt）＋ fetch_law.py / find_pcode.py / pcodes.json
│   ├─ <法規>_附件.txt   各法規附表／附件全文（fetch_annex.py 下載 PDF/ODT 轉文字；圖片型附表另有人工抄錄）
│   └─ 附件/            原始附件檔（PDF/ODT 不進 git）與逐檔 txt
└─ 題庫/
   ├─ batch1_*.py … batch4_*.py                  各批題目原始碼（Python 資料）
   ├─ push_to_sheet.py                          透過 GAS v2 直接把 TSV 寫進 Sheet（免剪貼簿）
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

## 網頁功能（2026-09-03 更新）
- 首頁兩個大按鈕「🦺 職業安全衛生／🌱 環保」切換出題範圍；單人、每日挑戰、連線對戰（配對只找同範圍的人）、排行榜（`scores/<mode>_<OSH|ENV>`）全部各自獨立。
- Google Sheet 新增 **Articles** 分頁＝全部法規逐條原文（law_id／法規／條號／有無附表／條文），Laws 分頁多了 `articles`（條數）與 `questions`（題數）欄，缺漏一眼可見；灌入方式見 gas/部署清單_照著做.md v5。

## 職安法規範圍（使用者 2026-09-03 指定）

2026-09-03 再依全國法規資料庫「職業安全衛生目／勞動檢查目」總表補齊 46 部（收費標準 5 部與組織準則 1 部已移除不用）。原指定範圍：職安法、施行細則、管理辦法、教育訓練規則、健康保護規則、設施規則、營造標準、妊娠及未滿18歲認定標準、重體力、高架、高溫、精密、勞檢法、勞檢細則、立即危險認定標準、工業用機器人、母性健康保護辦法、危工辦法、化學品標示通識、缺氧、異常氣壓、性別平等工作法及細則、鉛、四烷基鉛、有機溶劑、特定化學物質、粉塵、化學品評估分級、鍋爐壓力容器、起重升降機具、碼頭裝卸、高壓氣體、勞動基準法及細則。
其餘職安法規之題目保留於 Sheet 但 `status = archived`（不進遊戲，Laws 權重 0）；名單在 `build_sheet.py` 的 `SCOPE_OSH`，要增減只要改那裡再 `python push_to_sheet.py status`。

## 批次進度

| 批次 | 範圍 | 題數 | 狀態 |
|---|---|---|---|
| 1 | 職業安全衛生法（114/12/19）＋施行細則（115/6/26） | 129 | draft，待審 |
| 2 | 職業安全衛生設施規則（115/6/30）136 題、營造安全衛生設施標準（115/6/30）74 題、機械設備器具安全標準（111/5/11）37 題 | 247 | draft，待審 |
| 3 | 缺氧症預防規則（103/6/26）30 題、高架作業（103/6/25）9 題、高溫作業（103/7/1）17 題、異常氣壓（103/6/25）62 題、危害性化學品標示及通識規則（115/8/26；附表一、四自 118/1/1 施行）29 題、標示設置準則（103/7/2）11 題 | 158 | draft，待審 |
| 4 | 職業安全衛生管理辦法（115/6/29）80 題、教育訓練規則（115/6/25）39 題、勞工健康保護規則（115/6/26）35 題、危險性工作場所審查及檢查辦法（109/7/17）23 題、製程安全評估定期實施辦法（109/7/17）12 題；含附表題（人員配置、訓練時數、特別危害健康作業、醫護配置） | 189 | draft，待審 |
| 5 | 勞動檢查法系（含細則、立即危險認定標準、要點）、災保法、母性保護、妊娠及未滿18歲認定標準、女性夜間、精密、重體力、工業用機器人、顧問機構、獎勵評核、健檢機構、性別平等工作法及細則 | 169 | draft（範圍外者 archived） |
| 6 | 使用者增列職安法規：鉛、四烷基鉛、有機溶劑、特定化學物質、粉塵、化學品評估分級、鍋爐壓力容器、起重升降機具、碼頭裝卸、高壓氣體、勞動基準法及細則 | 176 | draft，待審 |
| 7 | 依全國法規資料庫總表補齊之職安法規：容許暴露標準、環測辦法、危險性機械設備檢查規則（含既有）、職場霸凌準則及申訴辦法、工程安全設計辦法、化學品三辦法、機械產品申報登錄／監督管理／型式驗證／先行放行／免驗證／特殊產品／標示標章、健康服務機構、預防職業病健檢、職業病鑑定、職災補助系列（7 部）、代行檢查機構、勞檢員遴用及迴避、林場、礦場、船舶清艙、五部構造標準 | 196 | draft，待審 |
| 8 | 環保子法（空污專責人員、固定污染源排放標準、空品標準、室內空品法及標準、噪音細則、環境音量標準、水污細則…共 72 部原文已抓齊，題目陸續補） | 30（進行中） | draft |
| 7 | 環保第二、三層 | ~150 | 未開始 |

## 重建題庫檔

```bash
python 題庫/build_sheet.py
```
