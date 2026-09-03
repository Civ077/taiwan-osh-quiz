# -*- coding: utf-8 -*-
"""組裝題庫：讀 batch1_*.py → 驗證 → 產出 OSH_ENV_QuizBank.xlsx（Laws/Questions/Config/Changelog 四分頁）＋ questions.json"""
import json, sys, os, importlib
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LAW_VER = {"OSH-01": "民國114年12月19日", "OSH-02": "民國115年6月26日"}
LAW_NAME = {"OSH-01": ("職業安全衛生法", "Occupational Safety and Health Act"),
            "OSH-02": ("職業安全衛生法施行細則", "Enforcement Rules of the Occupational Safety and Health Act")}

# ---------- Laws 主檔 ----------
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
 ("機械設備器具安全標準","Safety Standards for Machinery, Equipment and Tools","N0060012",2),
 ("高溫作業勞工作息時間標準","Standards for Work and Rest Time of Laborers in High-Temperature Work","N0060019",2),
 ("高架作業勞工保護措施標準","Standards for Protective Measures for Laborers in Work at Height","N0060020",2),
 ("精密作業勞工視機能保護設施標準","Standards for Visual Protection Facilities for Precision Work","N0060021",1),
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
 ("政府機關推動職業安全衛生業務績效評核及獎勵作業要點","Directions for Performance Evaluation of Government OSH Promotion","",0),
 ("促進職業安全衛生文化獎勵及補助辦法","Regulations for Rewards and Subsidies to Promote OSH Culture","N0060055",0),
 ("製程安全評估定期實施辦法","Regulations for Periodic Process Safety Assessment","N0060050",1),
 ("勞工體格與健康檢查特定檢查項目檢驗機構指定及管理作業要點","Directions for Designation of Laboratories for Specific Health Examination Items","",0),
 ("缺氧症預防規則","Rules for Prevention of Hypoxia","N0060010",3),
 ("勞工職業災害保險及保護法","Labor Occupational Accident Insurance and Protection Act","N0060072",2),
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
 ("資源循環利用法","Resource Recycling Act","O0050049",1,3),
 ("公害糾紛處理法","Public Nuisance Dispute Mediation Act","O0100002",1,3),
]

def build_laws():
    rows = [["law_id","group","tier","name_zh","name_en","law_version","source_url","weight","note"]]
    for i,(zh,en,pcode,w) in enumerate(OSH_LAWS, start=1):
        lid = f"OSH-{i:02d}"
        url = f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={pcode}" if pcode else "https://law.isha.org.tw/ISHA_LAW/"
        tier = 1 if (1<=i<=17 or i in (34,35)) else (2 if i<=25 else 3)
        rows.append([lid,"OSH",tier,zh,en,LAW_VER.get(lid,""),url,w,""])
    for i,(zh,en,pcode,w,tier) in enumerate(ENV_LAWS, start=1):
        lid = f"ENV-{i:02d}"
        url = f"https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={pcode}" if pcode else ""
        rows.append([lid,"ENV",tier,zh,en,"",url,w,""])
    return rows

# ---------- Questions ----------
Q_HEADER = ["id","law_group","law_id","law","article","law_version","category","difficulty",
            "q_zh","a_zh","b_zh","c_zh","d_zh","q_en","a_en","b_en","c_en","d_en",
            "answer","explain_zh","explain_en","status","batch","reviewer","review_note"]

def load_questions():
    allq = []
    for m in ("batch1_a","batch1_b","batch1_c"):
        mod = importlib.import_module(m)
        allq.extend(mod.Q)
    errs = []
    rows = [Q_HEADER]
    seen = set()
    for n,t in enumerate(allq, start=1):
        if len(t) != 11: errs.append(f"#{n} 欄位數={len(t)}"); continue
        lid,art,diff,cat,qz,oz,ans,ez,qe,oe,ee = t
        if len(oz)!=4 or len(oe)!=4: errs.append(f"#{n} 選項數不是4：{qz[:20]}")
        if ans not in "abcd": errs.append(f"#{n} 答案非a-d：{ans}")
        if diff not in (1,2,3): errs.append(f"#{n} 難度非1-3")
        if lid not in LAW_VER: errs.append(f"#{n} law_id 未知：{lid}")
        key = qz.strip()
        if key in seen: errs.append(f"#{n} 題目重複：{qz[:30]}")
        seen.add(key)
        qid = f"Q{n:04d}"
        # 固定種子洗牌選項，讓正確答案平均分布在 a–d（中英同步）
        import random
        order = [0,1,2,3]; random.Random(f"{qid}-osh-quiz").shuffle(order)
        oz2 = [oz[i] for i in order]; oe2 = [oe[i] for i in order]
        ans2 = "abcd"[order.index("abcd".index(ans))]
        rows.append([qid,"OSH",lid,LAW_NAME[lid][0],art,LAW_VER[lid],cat,diff,
                     qz,*oz2,qe,*oe2,ans2,ez,ee,"draft",1,"",""])
    return rows, errs

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

def main():
    qrows, errs = load_questions()
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
    out = os.path.join(HERE, "OSH_ENV_QuizBank.xlsx")
    wb.save(out)
    # JSON（前端用）
    keys = qrows[0]
    js = [dict(zip(keys, r)) for r in qrows[1:]]
    with open(os.path.join(HERE,"questions_batch1.json"),"w",encoding="utf-8") as f:
        json.dump(js, f, ensure_ascii=False, indent=1)
    n = len(qrows)-1
    from collections import Counter
    print(f"OK：{n} 題 → {out}")
    print("依法規：", dict(Counter(r[2] for r in qrows[1:])))
    print("依難度：", dict(sorted(Counter(r[7] for r in qrows[1:]).items())))
    print("答案分布：", dict(sorted(Counter(r[18] for r in qrows[1:]).items())))
    print("類別：", dict(Counter(r[6] for r in qrows[1:])))

if __name__ == "__main__":
    main()
