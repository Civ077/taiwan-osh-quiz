# -*- coding: utf-8 -*-
"""組裝題庫：讀 batchN_*.py → 驗證 → 洗牌選項 → 產出
   OSH_ENV_QuizBank.xlsx（Laws/Questions/Config/Changelog 四分頁，全部題目）
   questions_all.json（全部）、questions_batchN.json（各批）
   tsv/Questions_batchN.tsv（各批新增列，貼進 Google Sheet 用）
用法：python build_sheet.py            # 全部批次
"""
import json, sys, os, importlib, random, glob, re
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 法規主檔：law_id → (中文名, 英文名, 版本日期, pcode)
def law_version_from_text(zh):
    """從 法規原文/<名稱>.txt 第一行讀修正日期 → 民國115年6月26日"""
    f = os.path.join(os.path.dirname(HERE), "法規原文", zh + ".txt")
    if not os.path.exists(f): return ""
    m = re.search(r"修正日期：民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日", open(f, encoding="utf-8").readline())
    if m: return f"民國{int(m.group(1))}年{int(m.group(2))}月{int(m.group(3))}日"
    m = re.search(r"修正日期：民國\s*(\d+)\s*年\s*(\d+)\s*月", open(f, encoding="utf-8").readline())
    return f"民國{int(m.group(1))}年{int(m.group(2))}月" if m else ""


LAWS = {
 "OSH-01": ("職業安全衛生法","Occupational Safety and Health Act","民國114年12月19日","N0060001"),
 "OSH-02": ("職業安全衛生法施行細則","Enforcement Rules of the OSH Act","民國115年6月26日","N0060002"),
 "OSH-07": ("職業安全衛生設施規則","Occupational Safety and Health Facilities Rules","民國115年6月30日","N0060009"),
 "OSH-13": ("機械設備器具安全標準","Safety Standards for Machinery, Equipment and Tools","民國111年5月11日","N0060034"),
 "OSH-36": ("營造安全衛生設施標準","Construction Safety and Health Facilities Standards","民國115年6月30日","N0060014"),
 "OSH-34": ("缺氧症預防規則","Rules for Prevention of Hypoxia","民國103年6月26日","N0060020"),
 "OSH-15": ("高架作業勞工保護措施標準","Standards for Protective Measures for Laborers in Work at Height","民國103年6月25日","N0060029"),
 "OSH-14": ("高溫作業勞工作息時間標準","Standards for Work and Rest Time of Laborers in High-Temperature Work","民國103年7月1日","N0060007"),
 "OSH-18": ("異常氣壓危害預防標準","Standards for Prevention of Abnormal Pressure Hazards","民國103年6月25日","N0060026"),
 "OSH-12": ("危害性化學品標示及通識規則","Regulations on Labeling and Hazard Communication of Hazardous Chemicals","民國115年8月26日","N0060054"),
 "OSH-24": ("職業安全衛生標示設置準則","Guidelines for Installation of Occupational Safety and Health Signs","民國103年7月2日","N0060023"),
 "OSH-09": ("職業安全衛生管理辦法","Regulations of Occupational Safety and Health Management","民國115年6月29日","N0060027"),
 "OSH-11": ("職業安全衛生教育訓練規則","Occupational Safety and Health Education and Training Rules","民國115年6月25日","N0060010"),
 "OSH-10": ("勞工健康保護規則","Labor Health Protection Rules","民國115年6月26日","N0060022"),
 "OSH-08": ("危險性工作場所審查及檢查辦法","Regulations for Review and Inspection of Dangerous Workplaces","民國109年7月17日","N0070019"),
 "OSH-32": ("製程安全評估定期實施辦法","Regulations for Periodic Process Safety Assessment","民國109年7月17日","N0060071"),
 "OSH-03": ("勞動檢查法","Labor Inspection Act","民國109年6月10日","N0070001"),
 "OSH-04": ("勞動檢查法施行細則","Enforcement Rules of the Labor Inspection Act","民國112年12月7日","N0070004"),
 "OSH-35": ("勞工職業災害保險及保護法","Labor Occupational Accident Insurance and Protection Act","民國110年4月30日","N0050031"),
 "OSH-22": ("女性勞工母性健康保護實施辦法","Regulations for Implementing Maternal Health Protection of Female Laborers","民國113年5月31日","N0060065"),
 "OSH-20": ("妊娠與分娩後女性及未滿十八歲勞工禁止從事危險性或有害性工作認定標準","Standards for Identifying Dangerous or Harmful Work Prohibited for Pregnant/Postpartum Women and Laborers under 18","民國114年11月20日","N0060032"),
 "OSH-21": ("事業單位僱用女性勞工夜間工作場所必要之安全衛生設施標準","Standards for Safety and Health Facilities for Female Laborers Working at Night","民國104年3月31日","N0030011"),
 "OSH-16": ("精密作業勞工視機能保護設施標準","Standards for Visual Protection Facilities for Precision Work","民國103年6月30日","N0060012"),
 "OSH-17": ("重體力勞動作業勞工保護措施標準","Standards for Protective Measures for Heavy Physical Labor","民國103年6月30日","N0060016"),
 "OSH-23": ("工業用機器人危害預防標準","Standards for Prevention of Industrial Robot Hazards","民國107年2月14日","N0060025"),
 "OSH-25": ("勞動檢查法第二十八條所定勞工有立即發生危險之虞認定標準","Standards for Identifying Imminent Danger under Article 28 of the Labor Inspection Act","民國94年6月10日","N0070016"),
 "OSH-29": ("職業安全衛生顧問服務機構與其顧問服務人員之認可及管理規則","Rules for Accreditation and Management of OSH Consulting Institutions","民國113年10月31日","N0060066"),
 "OSH-31": ("促進職業安全衛生文化獎勵及補助辦法","Regulations for Rewards and Subsidies to Promote OSH Culture","民國103年11月28日","N0060035"),
 "OSH-30": ("政府機關推動職業安全衛生業務績效評核及獎勵辦法","Regulations for Performance Evaluation and Rewards of Government OSH Promotion","民國103年11月27日","N0060061"),
 "OSH-19": ("辦理勞工體格與健康檢查醫療機構認可及管理辦法","Regulations for Accreditation and Management of Medical Institutions for Labor Health Examinations","民國111年8月12日","N0060040"),
 "OSH-27": ("違反職業安全衛生法及勞動檢查法案件處理要點","Directions for Handling Violations of the OSH Act and Labor Inspection Act","民國115年7月1日","mol:FL024857"),
 "OSH-26": ("推行職業安全衛生優良單位及人員選拔作業要點","Directions for Selection of Outstanding OSH Units and Personnel","民國114年1月17日","mol:FL015052"),
 "OSH-33": ("勞工體格與健康檢查特定檢查項目檢驗機構指定及管理作業要點","Directions for Designation of Laboratories for Specific Health Examination Items","民國112年5月22日","mol:FL078462"),
 "OSH-28": ("勞動部重大災害通報及檢查處理要點","MOL Directions for Major Accident Notification and Inspection","民國110年9月","isha:022"),
 "OSH-37": ("性別平等工作法","Act of Gender Equality in Employment","民國112年8月16日","N0030014"),
 "OSH-38": ("性別平等工作法施行細則","Enforcement Rules of the Act of Gender Equality in Employment","民國115年4月8日","N0030015"),
 "OSH-39": ("鉛中毒預防規則","Lead Poisoning Prevention Rules","","N0060018"),
 "OSH-40": ("四烷基鉛中毒預防規則","Tetraalkyl Lead Poisoning Prevention Rules","","N0060019"),
 "OSH-41": ("高壓氣體勞工安全規則","Rules for Labor Safety in High-Pressure Gas","","N0060030"),
 "OSH-42": ("起重升降機具安全規則","Safety Rules for Cranes, Hoists and Lifting Equipment","","N0060013"),
 "OSH-43": ("危害性化學品評估及分級管理辦法","Regulations for Assessment and Tiered Management of Hazardous Chemicals","","N0060070"),
 "OSH-44": ("鍋爐及壓力容器安全規則","Safety Rules for Boilers and Pressure Vessels","","N0060011"),
 "OSH-45": ("粉塵危害預防標準","Standards for Prevention of Dust Hazards","","N0060021"),
 "OSH-46": ("碼頭裝卸安全衛生設施標準","Safety and Health Facilities Standards for Wharf Loading and Unloading","","N0060006"),
 "OSH-47": ("有機溶劑中毒預防規則","Organic Solvent Poisoning Prevention Rules","","N0060017"),
 "OSH-48": ("勞動基準法","Labor Standards Act","","N0030001"),
 "OSH-49": ("勞動基準法施行細則","Enforcement Rules of the Labor Standards Act","","N0030002"),
 "OSH-50": ("特定化學物質危害預防標準","Standards for Prevention of Hazards from Specified Chemical Substances","","N0060015"),
}
LAW_VER = {k: (v[2] or law_version_from_text(v[0])) for k, v in LAWS.items()}

# 使用者指定納入遊戲之職安法規（2026-09-03）；其他職安法規之題目保留但 status=archived，Laws 權重 0
SCOPE_OSH = {"OSH-01","OSH-02","OSH-09","OSH-11","OSH-10","OSH-07","OSH-36","OSH-20","OSH-17","OSH-15",
             "OSH-14","OSH-16","OSH-03","OSH-04","OSH-25","OSH-23","OSH-22","OSH-08","OSH-12","OSH-34","OSH-18","OSH-37","OSH-38","OSH-39","OSH-40","OSH-41","OSH-42","OSH-43","OSH-44","OSH-45","OSH-46","OSH-47","OSH-48","OSH-49","OSH-50"}
def in_scope(lid): return lid.startswith("ENV") or lid in SCOPE_OSH
LAW_NAME = {k: v[0] for k, v in LAWS.items()}

# 批次 → 模組清單（依序編號）
BATCHES = {
 1: ["batch1_a", "batch1_b", "batch1_c"],
 2: ["batch2_a", "batch2_b", "batch2_c", "batch2_d"],
 3: ["batch3_a", "batch3_b", "batch3_c"],
 4: ["batch4_a", "batch4_b", "batch4_c", "batch4_d"],
 5: ["batch5_a", "batch5_b", "batch5_c", "batch5_d"],
 6: ["batch6_a", "batch6_b", "batch6_c", "batch6_d", "batch6_e"],
}

# ---------- Laws 主檔（沿用批次 1 清單，另加 OSH-36 營造標準） ----------
OSH_LAWS = [
 ("職業安全衛生法","Occupational Safety and Health Act","N0060001",3),
 ("職業安全衛生法施行細則","Enforcement Rules of the OSH Act","N0060002",3),
 ("勞動檢查法","Labor Inspection Act","N0080001",2),
 ("勞動檢查法施行細則","Enforcement Rules of the Labor Inspection Act","N0080002",1),
 ("職業災害勞工保護法","Act for Protecting Workers of Occupational Accidents","N0060041",1),
 ("職業災害勞工保護法施行細則","Enforcement Rules of the Act for Protecting Workers of Occupational Accidents","N0060042",1),
 ("職業安全衛生設施規則","Occupational Safety and Health Facilities Rules","N0060009",3),
 ("危險性工作場所審查及檢查辦法","Regulations for Review and Inspection of Dangerous Workplaces","N0080006",2),
 ("職業安全衛生管理辦法","Regulations of Occupational Safety and Health Management","N0060003",3),
 ("勞工健康保護規則","Labor Health Protection Rules","N0060022",3),
 ("職業安全衛生教育訓練規則","Occupational Safety and Health Education and Training Rules","N0060008",3),
 ("危害性化學品標示及通識規則","Regulations on Labeling and Hazard Communication of Hazardous Chemicals","N0060052",2),
 ("機械設備器具安全標準","Safety Standards for Machinery, Equipment and Tools","N0060034",2),
 ("高溫作業勞工作息時間標準","Standards for Work and Rest Time of Laborers in High-Temperature Work","N0060019",2),
 ("高架作業勞工保護措施標準","Standards for Protective Measures for Laborers in Work at Height","N0060020",2),
 ("精密作業勞工視機能保護設施標準","Standards for Visual Protection Facilities for Precision Work","N0060012",1),
 ("重體力勞動作業勞工保護措施標準","Standards for Protective Measures for Heavy Physical Labor","N0060023",1),
 ("異常氣壓危害預防標準","Standards for Prevention of Abnormal Pressure Hazards","N0060004",2),
 ("辦理勞工體格與健康檢查醫療機構認可及管理辦法","Regulations for Accreditation and Management of Medical Institutions for Labor Health Examinations","N0060035",1),
 ("妊娠與分娩後女性及未滿十八歲勞工禁止從事危險性或有害性工作認定標準","Standards for Identifying Dangerous or Harmful Work Prohibited for Pregnant/Postpartum Women and Laborers under 18","N0060051",2),
 ("事業單位僱用女性勞工夜間工作場所必要之安全衛生設施標準","Standards for Safety and Health Facilities for Female Laborers Working at Night","N0060030",1),
 ("女性勞工母性健康保護實施辦法","Regulations for Implementing Maternal Health Protection of Female Laborers","N0060053",2),
 ("工業用機器人危害預防標準","Standards for Prevention of Industrial Robot Hazards","N0060007",1),
 ("職業安全衛生標示設置準則","Guidelines for Installation of Occupational Safety and Health Signs","N0060013",2),
 ("勞動檢查法第二十八條所定勞工有立即發生危險之虞認定標準","Standards for Identifying Imminent Danger under Article 28 of the Labor Inspection Act","N0080009",2),
 ("推行職業安全衛生優良單位及人員選拔作業要點","Directions for Selection of Outstanding OSH Units and Personnel","",0),
 ("違反職業安全衛生法及勞動檢查法案件處理要點","Directions for Handling Violations of the OSH Act and Labor Inspection Act","",1),
 ("勞動部重大災害通報及檢查處理要點","MOL Directions for Major Accident Notification and Inspection","",1),
 ("職業安全衛生顧問服務機構與其顧問服務人員之認可及管理規則","Rules for Accreditation and Management of OSH Consulting Institutions","N0060054",0),
 ("政府機關推動職業安全衛生業務績效評核及獎勵辦法","Regulations for Performance Evaluation and Rewards of Government OSH Promotion","N0060061",0),
 ("促進職業安全衛生文化獎勵及補助辦法","Regulations for Rewards and Subsidies to Promote OSH Culture","N0060055",0),
 ("製程安全評估定期實施辦法","Regulations for Periodic Process Safety Assessment","N0060050",1),
 ("勞工體格與健康檢查特定檢查項目檢驗機構指定及管理作業要點","Directions for Designation of Laboratories for Specific Health Examination Items","",0),
 ("缺氧症預防規則","Rules for Prevention of Hypoxia","N0060010",3),
 ("勞工職業災害保險及保護法","Labor Occupational Accident Insurance and Protection Act","N0060072",2),
 ("營造安全衛生設施標準","Construction Safety and Health Facilities Standards","N0060014",3),
 ("性別平等工作法","Act of Gender Equality in Employment","N0030014",1),
 ("性別平等工作法施行細則","Enforcement Rules of the Act of Gender Equality in Employment","N0030015",1),
 ("鉛中毒預防規則","Lead Poisoning Prevention Rules","N0060018",1),
 ("四烷基鉛中毒預防規則","Tetraalkyl Lead Poisoning Prevention Rules","N0060019",1),
 ("高壓氣體勞工安全規則","Rules for Labor Safety in High-Pressure Gas","N0060030",1),
 ("起重升降機具安全規則","Safety Rules for Cranes, Hoists and Lifting Equipment","N0060013",1),
 ("危害性化學品評估及分級管理辦法","Regulations for Assessment and Tiered Management of Hazardous Chemicals","N0060070",1),
 ("鍋爐及壓力容器安全規則","Safety Rules for Boilers and Pressure Vessels","N0060011",1),
 ("粉塵危害預防標準","Standards for Prevention of Dust Hazards","N0060021",1),
 ("碼頭裝卸安全衛生設施標準","Safety and Health Facilities Standards for Wharf Loading and Unloading","N0060006",1),
 ("有機溶劑中毒預防規則","Organic Solvent Poisoning Prevention Rules","N0060017",1),
 ("勞動基準法","Labor Standards Act","N0030001",1),
 ("勞動基準法施行細則","Enforcement Rules of the Labor Standards Act","N0030002",1),
 ("特定化學物質危害預防標準","Standards for Prevention of Hazards from Specified Chemical Substances","N0060015",1),
]
ENV_LAWS = [
 ("空氣污染防制法","Air Pollution Control Act","O0020001",3,1),
 ("空氣污染防制法施行細則","Enforcement Rules of the Air Pollution Control Act","O0020002",1,1),
 ("營建工程空氣污染防制設施管理辦法","Regulations on Air Pollution Control Facilities for Construction Projects","O0020021",3,1),
 ("固定污染源逸散性粒狀污染物空氣污染防制設施管理辦法","Regulations on Control Facilities for Fugitive Particulate Pollutants from Stationary Sources","O0020033",2,1),
 ("噪音管制法","Noise Control Act","O0030001",2,1),
 ("噪音管制標準","Noise Control Standards","O0030004",2,1),
 ("水污染防治法","Water Pollution Control Act","O0040001",2,1),
 ("放流水標準","Effluent Standards","O0040004",1,1),
 ("水污染防治措施及檢測申報管理辦法","Regulations on Water Pollution Control Measures and Monitoring Reporting","O0040030",1,1),
 ("廢棄物清理法","Waste Disposal Act","O0050001",3,1),
 ("事業廢棄物貯存清除處理方法及設施標準","Standards for Storage, Clearance and Disposal of Industrial Waste","O0050023",2,1),
 ("營建剩餘土石方處理方案","Construction Surplus Soil and Rock Disposal Program","",2,1),
 ("環境影響評估法","Environmental Impact Assessment Act","O0090001",2,1),
 ("海洋污染防治法","Marine Pollution Control Act","O0040026",2,2),
 ("海岸管理法","Coastal Zone Management Act","D0070212",1,2),
 ("海洋保育法","Marine Conservation Act","",1,2),
 ("野生動物保育法","Wildlife Conservation Act","M0120001",2,2),
 ("濕地保育法","Wetland Conservation Act","D0130001",1,2),
 ("土壤及地下水污染整治法","Soil and Groundwater Pollution Remediation Act","O0110001",1,2),
 ("毒性及關注化學物質管理法","Toxic and Concerned Chemical Substances Control Act","O0060001",1,2),
 ("環境基本法","Basic Environment Act","O0100001",1,3),
 ("氣候變遷因應法","Climate Change Response Act","O0020098",1,3),
 ("環境教育法","Environmental Education Act","O0120001",1,3),
 ("資源循環推動法","Resource Circulation Promotion Act","O0050049",1,3),
 ("公害糾紛處理法","Public Nuisance Dispute Mediation Act","O0100002",1,3),
]

PCODES = {}
try:
    PCODES = json.load(open(os.path.join(os.path.dirname(HERE), "法規原文", "pcodes.json"), encoding="utf-8"))   # 名稱→全國法規資料庫 pcode（find_pcode.py 查得）
except Exception:
    pass

def law_url(code):
    if not code: return "（尚無法規資料庫代碼）"
    if code.startswith("mol:"): return "https://laws.mol.gov.tw/FLAW/FLAWDAT01.aspx?id=" + code[4:]
    if code.startswith("moi:"): return "https://glrs.moi.gov.tw/LawContent.aspx?id=" + code[4:]
    if code.startswith("isha:"): return "http://law.isha.org.tw/ISHA_LAW/Pages/LawList.aspx?Lawid=" + code[5:]
    return f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={code}"

def build_laws():
    rows = [["law_id","group","tier","name_zh","name_en","law_version","source_url","weight","note"]]
    for i,(zh,en,pcode,w) in enumerate(OSH_LAWS, start=1):
        lid = f"OSH-{i:02d}"; code = PCODES.get(zh) or ""
        tier = 1 if (1<=i<=17 or i>=34) else (2 if i<=25 else 3)
        rows.append([lid,"OSH",tier,zh,en,LAW_VER.get(lid) or law_version_from_text(zh),law_url(code),(w if in_scope(lid) else 0),("" if in_scope(lid) else "不在指定範圍，暫不使用")])
    for i,(zh,en,pcode,w,tier) in enumerate(ENV_LAWS, start=1):
        lid = f"ENV-{i:02d}"; code = PCODES.get(zh) or ""
        rows.append([lid,"ENV",tier,zh,en,law_version_from_text(zh),law_url(code),w,""])
    return rows

# ---------- Questions ----------
Q_HEADER = ["id","law_group","law_id","law","article","law_version","category","difficulty",
            "q_zh","a_zh","b_zh","c_zh","d_zh","q_en","a_en","b_en","c_en","d_en",
            "answer","explain_zh","explain_en","status","batch","reviewer","review_note"]

def load_questions():
    rows = [Q_HEADER]; errs = []; seen = set(); n = 0
    per_batch = {}
    for bno, mods in sorted(BATCHES.items()):
        for m in mods:
            for t in importlib.import_module(m).Q:
                n += 1
                if len(t) != 11: errs.append(f"#{n} 欄位數={len(t)}"); continue
                lid,art,diff,cat,qz,oz,ans,ez,qe,oe,ee = t
                if len(oz)!=4 or len(oe)!=4: errs.append(f"#{n} 選項數不是4：{qz[:20]}")
                if ans not in "abcd": errs.append(f"#{n} 答案非a-d：{ans}")
                if diff not in (1,2,3): errs.append(f"#{n} 難度非1-3")
                if lid not in LAWS: errs.append(f"#{n} law_id 未知：{lid}")
                if len(set(oz))<4 or len(set(oe))<4: errs.append(f"#{n} 選項重複：{qz[:20]}")
                key = qz.strip()
                if key in seen: errs.append(f"#{n} 題目重複：{qz[:30]}")
                seen.add(key)
                qid = f"Q{n:04d}"
                order = [0,1,2,3]; random.Random(f"{qid}-osh-quiz").shuffle(order)
                oz2 = [oz[i] for i in order]; oe2 = [oe[i] for i in order]
                ans2 = "abcd"[order.index("abcd".index(ans))]
                row = [qid,"OSH",lid,LAW_NAME[lid],art,LAW_VER[lid],cat,diff,qz,*oz2,qe,*oe2,ans2,ez,ee,("draft" if in_scope(lid) else "archived"),bno,"",("" if in_scope(lid) else "不在使用者指定之職安法規範圍，暫不使用")]
                rows.append(row); per_batch.setdefault(bno, []).append(row)
    return rows, errs, per_batch

CONFIG = [
 ["key","value","說明 / Description"],
 ["questions_per_game",20,"每局題數 / questions per game"],
 ["seconds_per_question",15,"每題秒數 / seconds per question"],
 ["base_score",500,"答對基本分 / base score for a correct answer"],
 ["speed_bonus_max",500,"速度加分上限：base + max×(剩餘秒/總秒) / speed bonus = max × (remaining/total)"],
 ["wrong_score",0,"答錯或逾時得分 / score for wrong or timeout"],
 ["streak_start",3,"連對從第幾題起加成 / streak bonus starts at N consecutive correct"],
 ["streak_bonus",50,"連對每題加成 / bonus per question once streak active"],
 ["daily_questions",10,"每日挑戰題數 / daily challenge question count"],
 ["lobby_wait_seconds",10,"隨機配對等待秒數，逾時轉房間碼或 bot / matchmaking wait before fallback"],
 ["languages","zh,en","支援語言 / supported languages"],
 ["active_status","active","前端只抓此 status 的題目 / only questions with this status are exported"],
]
CHANGELOG = [
 ["date","law_id","law_version","change","affected_questions","action","done_by"],
 ["2026-09-03","OSH-01","民國114年12月19日","建立批次1：以全國法規資料庫現行條文出題（本法）","Q0001–Q0096","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-02","民國115年6月26日","建立批次1：以全國法規資料庫現行條文出題（施行細則，115/7/1 施行）","Q0097–Q0129","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-07","民國115年6月30日","建立批次2：職業安全衛生設施規則（115/7/1 施行，部分條文 116/1/1）","batch=2 之 OSH-07","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-36","民國115年6月30日","建立批次2：營造安全衛生設施標準（第11條之2 自 116/7/1 施行）；Laws 分頁新增 OSH-36","batch=2 之 OSH-36","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-13","民國111年5月11日","建立批次2：機械設備器具安全標準；Laws 分頁 OSH-13 來源網址修正為 N0060034","batch=2 之 OSH-13","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-39,40,42,43,44,45,46,47,48,49,50","見各題 law_version","建立批次6：鉛、四烷基鉛、有機溶劑、特定化學物質、粉塵、化學品評估分級、鍋爐壓力容器、起重升降機具、碼頭裝卸、勞動基準法及施行細則（使用者 2026-09-03 增列之職安範圍）","batch=6","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-03,04,35,22,20,21,16,17,23,25,29,31,30,19,27,26,33,28","見各題 law_version","建立批次5：勞動檢查法系（含施行細則、立即危險認定標準、違反案件處理要點、重大災害通報要點、優良單位選拔要點）、勞工職業災害保險及保護法、母性健康保護、妊娠及未滿十八歲禁止工作認定標準、女性夜間、精密、重體力、工業用機器人、顧問機構、文化獎勵、績效評核、健檢醫療機構認可、檢驗機構要點；Laws 分頁全部 61 部法規版本日期改由條文檔自動帶入","batch=5","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-09,11,10,08,32","見各題 law_version","建立批次4：職業安全衛生管理辦法（115/6/29）、教育訓練規則（115/6/25）、勞工健康保護規則（115/6/26）、危險性工作場所審查及檢查辦法（109/7/17）、製程安全評估定期實施辦法（109/7/17）","batch=4","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-34,15,14,18,12,24","見各題 law_version","建立批次3：缺氧症預防規則、高架作業、高溫作業、異常氣壓、危害性化學品標示及通識規則（115/8/26；附表一、四自 118/1/1 施行）、標示設置準則；Laws 分頁 source_url 全面改為法規資料庫查得之正確代碼","batch=3","初版 draft，待審","Claude Code"],
]

def style_header(ws):
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="16324F")
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
def autowidth(ws, maxw=60):
    for col in ws.columns:
        w = max((len(str(c.value)) if c.value is not None else 0) for c in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max(8, w*1.1), maxw)
def tsv(rows):
    out = []
    for r in rows:
        cells = []
        for c in r:
            s = '' if c is None else str(c)
            cells.append(s.replace('\t',' ').replace('\r',' ').replace('\n',' '))
        out.append('\t'.join(cells))
    return '\n'.join(out)

def main():
    qrows, errs, per_batch = load_questions()
    if errs:
        print("驗證錯誤："); [print(" ", e) for e in errs]; sys.exit(1)
    wb = Workbook()
    ws = wb.active; ws.title = "Laws"
    for r in build_laws(): ws.append(r)
    style_header(ws); autowidth(ws)
    ws = wb.create_sheet("Questions")
    for r in qrows: ws.append(r)
    style_header(ws); autowidth(ws, 50)
    ws = wb.create_sheet("Config")
    for r in CONFIG: ws.append(r)
    style_header(ws); autowidth(ws, 80)
    ws = wb.create_sheet("Changelog")
    for r in CHANGELOG: ws.append(r)
    style_header(ws); autowidth(ws, 70)
    wb.save(os.path.join(HERE, "OSH_ENV_QuizBank.xlsx"))
    keys = qrows[0]
    js = [dict(zip(keys, r)) for r in qrows[1:]]
    json.dump(js, open(os.path.join(HERE,"questions_all.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(HERE,"tsv"), exist_ok=True)
    for bno, rows in per_batch.items():
        json.dump([dict(zip(keys, r)) for r in rows], open(os.path.join(HERE,f"questions_batch{bno}.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
        open(os.path.join(HERE,"tsv",f"Questions_batch{bno}.tsv"),"w",encoding="utf-8",newline="").write(tsv(rows))
    open(os.path.join(HERE,"tsv","Questions.tsv"),"w",encoding="utf-8",newline="").write(tsv(qrows))   # 全部題目（含表頭），push_to_sheet.py sync 用
    open(os.path.join(HERE,"tsv","Laws.tsv"),"w",encoding="utf-8",newline="").write(tsv(build_laws()))
    open(os.path.join(HERE,"tsv","Changelog.tsv"),"w",encoding="utf-8",newline="").write(tsv(CHANGELOG))
    # 前端用精簡 JSON
    keep = ['id','law_id','law','article','law_version','category','difficulty','q_zh','a_zh','b_zh','c_zh','d_zh','q_en','a_en','b_en','c_en','d_en','answer','explain_zh','explain_en','status']
    js = [q for q in js if q.get('status') != 'archived']
    docs = os.path.join(os.path.dirname(HERE), "docs", "data", "questions.json")
    if os.path.isdir(os.path.dirname(docs)):
        json.dump({'generated':'2026-09-03','count':len(js),'questions':[{k:r[k] for k in keep} for r in js]}, open(docs,"w",encoding="utf-8"), ensure_ascii=False, separators=(',',':'))
    n = len(qrows)-1
    print(f"OK：{n} 題（{', '.join(f'批次{b}={len(r)}' for b,r in sorted(per_batch.items()))}）")
    print("依法規：", dict(Counter(r[2] for r in qrows[1:])))
    print("依難度：", dict(sorted(Counter(r[7] for r in qrows[1:]).items())))
    print("答案分布：", dict(sorted(Counter(r[18] for r in qrows[1:]).items())))
    for bno, rows in sorted(per_batch.items()):
        print(f"批次{bno} 題號 {rows[0][0]}–{rows[-1][0]}，答案分布", dict(sorted(Counter(r[18] for r in rows).items())))

if __name__ == "__main__":
    main()
