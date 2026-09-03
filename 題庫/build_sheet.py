# -*- coding: utf-8 -*-
"""組裝題庫：讀 batchN_*.py → 驗證 → 洗牌選項 → 產出
   OSH_ENV_QuizBank.xlsx（Laws/Questions/Config/Changelog 四分頁，全部題目）
   questions_all.json（全部）、questions_batchN.json（各批）
   tsv/Questions_batchN.tsv（各批新增列，貼進 Google Sheet 用）
用法：python build_sheet.py            # 全部批次
"""
import re
import json, sys, os, importlib, random, glob, re
from pathlib import Path as _Path
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
def in_scope(lid):
    if lid.startswith("ENV"): return True
    i=int(lid[4:]); return i<=len(OSH_LAWS) and OSH_LAWS[i-1][3]>0
LAW_NAME = {k: v[0] for k, v in LAWS.items()}

# 批次 → 模組清單（依序編號）
BATCHES = {
 1: ["batch1_a", "batch1_b", "batch1_c"],
 2: ["batch2_a", "batch2_b", "batch2_c", "batch2_d"],
 3: ["batch3_a", "batch3_b", "batch3_c"],
 4: ["batch4_a", "batch4_b", "batch4_c", "batch4_d"],
 5: ["batch5_a", "batch5_b", "batch5_c", "batch5_d"],
 6: ["batch6_a", "batch6_b", "batch6_c", "batch6_d", "batch6_e"],
 7: ["batch7_a", "batch7_b", "batch7_c", "batch7_d", "batch7_e", "batch7_f", "batch7_g"],
 8: ["batch8_a", "batch8_b", "batch8_c", "batch8_d"],
 9: sorted(_p.stem for _p in _Path(__file__).parent.glob("batch9_*.py")),
 10: sorted(_p.stem for _p in _Path(__file__).parent.glob("batch10_*.py")),
 11: sorted(_p.stem for _p in _Path(__file__).parent.glob("batch11_*.py")),
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
 ("推行職業安全衛生優良單位及人員選拔作業要點","Directions for Selection of Outstanding OSH Units and Personnel","",1),
 ("違反職業安全衛生法及勞動檢查法案件處理要點","Directions for Handling Violations of the OSH Act and Labor Inspection Act","",1),
 ("勞動部重大災害通報及檢查處理要點","MOL Directions for Major Accident Notification and Inspection","",1),
 ("職業安全衛生顧問服務機構與其顧問服務人員之認可及管理規則","Rules for Accreditation and Management of OSH Consulting Institutions","N0060054",1),
 ("政府機關推動職業安全衛生業務績效評核及獎勵辦法","Regulations for Performance Evaluation and Rewards of Government OSH Promotion","N0060061",1),
 ("促進職業安全衛生文化獎勵及補助辦法","Regulations for Rewards and Subsidies to Promote OSH Culture","N0060055",1),
 ("製程安全評估定期實施辦法","Regulations for Periodic Process Safety Assessment","N0060050",1),
 ("勞工體格與健康檢查特定檢查項目檢驗機構指定及管理作業要點","Directions for Designation of Laboratories for Specific Health Examination Items","",1),
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
 ("勞工作業場所容許暴露標準","Standards of Permissible Exposure Limits at Job Sites","N0060004",3),
 ("勞工作業環境監測實施辦法","Regulations Governing Workplace Environment Monitoring","N0060033",3),
 ("危險性機械及設備安全檢查規則","Safety Inspection Rules for Dangerous Machinery and Equipment","N0060039",2),
 ("既有危險性機械及設備安全檢查規則","Safety Inspection Rules for Existing Dangerous Machinery and Equipment","N0060053",1),
 ("職場霸凌防治措施準則","Guidelines for Workplace Bullying Prevention Measures","N0060085",3),
 ("地方主管機關受理最高負責人職場霸凌事件申訴處理辦法","Regulations for Local Authorities Handling Bullying Complaints against Top Executives","N0060086",1),
 ("工程安全設計及整體工程統合管理辦法","Regulations on Engineering Safety Design and Integrated Project Management","N0060088",2),
 ("新化學物質登記管理辦法","Regulations on Registration of New Chemical Substances","N0060069",1),
 ("管制性化學品之指定及運作許可管理辦法","Regulations on Designation and Operating Permits of Controlled Chemicals","N0060068",1),
 ("優先管理化學品之指定及運作管理辦法","Regulations on Designation and Operation Management of Priority Management Chemicals","N0060064",1),
 ("機械設備器具安全資訊申報登錄辦法","Regulations on Safety Information Registration of Machinery, Equipment and Tools","N0060056",1),
 ("機械設備器具監督管理辦法","Regulations on Supervision and Management of Machinery, Equipment and Tools","N0060063",1),
 ("機械類產品型式驗證實施及監督管理辦法","Regulations on Type Certification of Machinery Products","N0060062",1),
 ("機械類產品申請先行放行辦法","Regulations on Advance Release of Machinery Products","N0060057",1),
 ("機械類產品申請免驗證辦法","Regulations on Exemption from Certification of Machinery Products","N0060059",1),
 ("構造規格特殊產品安全評估報告及檢驗辦法","Regulations on Safety Assessment Reports for Products of Special Construction","N0060060",1),
 ("安全標示與驗證合格標章使用及管理辦法","Regulations on Use of Safety Labels and Certification Marks","N0060058",1),
 ("固定式起重機安全檢查構造標準","Construction Standards for Safety Inspection of Fixed Cranes","N0070022",1),
 ("移動式起重機安全檢查構造標準","Construction Standards for Safety Inspection of Mobile Cranes","N0070021",1),
 ("升降機安全檢查構造標準","Construction Standards for Safety Inspection of Lifts","N0070017",1),
 ("吊籠安全檢查構造標準","Construction Standards for Safety Inspection of Gondolas","N0070023",1),
 ("壓力容器安全檢查構造標準","Construction Standards for Safety Inspection of Pressure Vessels","N0060055",1),
 ("林場安全衛生設施規則","Forestry Safety and Health Facilities Rules","N0060005",1),
 ("礦場職業衛生設施標準","Mine Occupational Health Facilities Standards","N0060003",1),
 ("船舶清艙解體職業安全規則","Occupational Safety Rules for Ship Tank Cleaning and Breaking","N0060031",1),
 ("勞工健康服務專業機構管理規則","Rules for Management of Labor Health Service Institutions","N0060087",1),
 ("勞工職業災害保險預防職業病健康檢查及健康追蹤檢查辦法","Regulations on Preventive Occupational Disease Health Examinations under Occupational Accident Insurance","N0060077",1),
 ("勞工職業災害保險職業病鑑定作業實施辦法","Regulations on Occupational Disease Determination under Occupational Accident Insurance","N0060080",1),
 ("職業災害勞工補助及核發辦法","Regulations on Subsidies for Workers with Occupational Accidents","N0060073",1),
 ("職業災害勞工申請器具照護失能及死亡補助辦法","Regulations on Aids, Care, Disability and Death Subsidies for Occupational Accident Workers","N0060076",1),
 ("職業災害勞工職業重建補助辦法","Regulations on Vocational Rehabilitation Subsidies for Occupational Accident Workers","N0060075",1),
 ("職業災害勞工職能復健專業機構認可管理及補助辦法","Regulations on Accreditation of Occupational Rehabilitation Institutions","N0060082",1),
 ("職業災害預防及職業災害勞工重建補助辦法","Regulations on Subsidies for Occupational Accident Prevention and Worker Rehabilitation","N0060081",1),
 ("職業災害預防補助辦法","Regulations on Occupational Accident Prevention Subsidies","N0060049",1),
 ("職業傷病診治醫療機構認可管理補助及職業傷病通報辦法","Regulations on Accreditation of Occupational Injury and Disease Medical Institutions and Notification","N0060083",1),
 ("直轄市及縣市政府辦理協助職業災害勞工重返職場補助辦法","Regulations on Local Government Subsidies for Return-to-Work of Occupational Accident Workers","N0060079",1),
 ("財團法人職業災害預防及重建中心監督及管理辦法","Regulations on Supervision of the Occupational Accident Prevention and Rehabilitation Center","N0060078",1),
 ("危險性機械或設備代行檢查機構管理規則","Rules for Management of Designated Inspection Agencies for Dangerous Machinery and Equipment","N0070018",1),
 ("勞動檢查員遴用及專業訓練辦法","Regulations on Recruitment and Training of Labor Inspectors","N0070006",1),
 ("勞動檢查員執行職務迴避辦法","Regulations on Recusal of Labor Inspectors","N0070005",1),
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
 ('空氣污染防制專責單位或專責人員設置及管理辦法','Regulations on Air Pollution Control Dedicated Units and Personnel','O0020106',2,1),
 ('固定污染源空氣污染物排放標準','Stationary Source Air Pollutant Emission Standards','O0020006',2,1),
 ('空氣品質標準','Air Quality Standards','O0020007',2,1),
 ('空氣品質嚴重惡化警告發布及緊急防制辦法','Regulations on Severe Air Quality Deterioration Warnings and Emergency Control','O0020015',1,1),
 ('室內空氣品質管理法','Indoor Air Quality Management Act','O0130001',2,1),
 ('室內空氣品質標準','Indoor Air Quality Standards','O0130005',1,1),
 ('固定污染源設置操作及燃料使用許可證管理辦法','Regulations on Stationary Source Installation, Operation and Fuel Use Permits','O0020012',1,1),
 ('空氣污染防制費收費辦法','Regulations on Air Pollution Control Fees','O0020027',1,1),
 ('揮發性有機物空氣污染管制及排放標準','VOC Air Pollution Control and Emission Standards','O0020030',1,1),
 ('鍋爐空氣污染物排放標準','Boiler Air Pollutant Emission Standards','O0020113',1,1),
 ('汽車停車怠速管理辦法','Regulations on Vehicle Idling Management','O0020086',1,1),
 ('空氣污染行為管制執行準則','Guidelines for Enforcement of Air Pollution Behavior Control','O0020036',1,1),
 ('空氣品質監測站設置及監測準則','Guidelines for Air Quality Monitoring Station Siting and Monitoring','O0020121',1,1),
 ('噪音管制法施行細則','Enforcement Rules of the Noise Control Act','O0030002',1,1),
 ('環境音量標準','Environmental Noise Standards','O0030014',2,1),
 ('噪音管制區劃定作業準則','Guidelines for Designating Noise Control Zones','O0030016',1,1),
 ('易發生噪音設施設置及操作許可辦法','Regulations on Permits for Noise-Prone Facilities','O0030007',1,1),
 ('機動車輛噪音管制標準','Motor Vehicle Noise Control Standards','O0030013',1,1),
 ('水污染防治法施行細則','Enforcement Rules of the Water Pollution Control Act','O0040002',1,1),
 ('地面水體分類及水質標準','Surface Water Classification and Quality Standards','O0040005',1,1),
 ('廢（污）水處理專責單位或人員設置及管理辦法','Regulations on Wastewater Treatment Dedicated Units and Personnel','O0040070',2,1),
 ('水污染防治措施計畫及許可申請審查管理辦法','Regulations on Water Pollution Control Plans and Permit Review','O0040055',1,1),
 ('事業或污水下水道系統排放廢（污）水緊急應變辦法','Regulations on Emergency Response for Wastewater Discharge','O0040049',1,1),
 ('飲用水管理條例','Drinking Water Management Act','O0040010',1,1),
 ('飲用水水質標準','Drinking Water Quality Standards','O0040019',1,1),
 ('土壤處理標準','Soil Treatment Standards','O0040031',1,1),
 ('廢棄物清理法施行細則','Enforcement Rules of the Waste Disposal Act','O0050036',1,1),
 ('有害事業廢棄物認定標準','Standards for Defining Hazardous Industrial Waste','O0050023',2,1),
 ('公民營廢棄物清除處理機構許可管理辦法','Regulations on Permits for Public and Private Waste Clearance and Disposal Organizations','O0050039',2,1),
 ('事業廢棄物清理計畫書審查管理辦法','Regulations on Review of Industrial Waste Disposal Plans','O0050084',1,1),
 ('廢棄物清理專業技術人員管理辦法','Regulations on Waste Disposal Professional Technicians','O0050053',1,1),
 ('一般廢棄物回收清除處理辦法','Regulations on General Waste Recycling, Clearance and Disposal','O0050024',1,1),
 ('應回收廢棄物責任業者管理辦法','Regulations on Responsible Enterprises for Recyclable Waste','O0050062',1,1),
 ('事業委託清理之相當注意義務認定準則','Guidelines on Due Care in Entrusting Waste Disposal','O0050085',1,1),
 ('環境部事業廢棄物再利用管理辦法','MOENV Regulations on Industrial Waste Reuse','O0050082',1,1),
 ('共通性事業廢棄物再利用管理辦法','Regulations on Reuse of Common Industrial Waste','O0050086',1,1),
 ('資源回收再利用法施行細則','Enforcement Rules of the Resource Recycling Act','O0050076',1,1),
 ('環境影響評估法施行細則','Enforcement Rules of the Environmental Impact Assessment Act','O0090002',1,1),
 ('開發行為應實施環境影響評估細目及範圍認定標準','Standards for Determining Development Activities Requiring EIA','O0090012',2,1),
 ('開發行為環境影響評估作業準則','Guidelines for EIA of Development Activities','O0090003',1,1),
 ('政府政策環境影響評估作業辦法','Regulations on Strategic Environmental Assessment of Government Policies','O0090029',1,1),
 ('毒性及關注化學物質管理法施行細則','Enforcement Rules of the Toxic and Concerned Chemical Substances Control Act','O0060013',1,2),
 ('毒性及關注化學物質危害預防及應變計畫作業辦法','Regulations on Hazard Prevention and Response Plans for Toxic and Concerned Chemicals','O0060035',2,2),
 ('毒性及關注化學物質專業技術管理人員設置及管理辦法','Regulations on Professional Technical Managers for Toxic and Concerned Chemicals','O0060046',2,2),
 ('毒性及關注化學物質標示與安全資料表管理辦法','Regulations on Labeling and SDS for Toxic and Concerned Chemicals','O0060037',1,2),
 ('毒性及關注化學物質運送管理辦法','Regulations on Transport of Toxic and Concerned Chemicals','O0060015',1,2),
 ('毒性及關注化學物質許可登記核可管理辦法','Regulations on Permits, Registration and Approval of Toxic and Concerned Chemicals','O0060038',1,2),
 ('毒性及關注化學物質運作與釋放量紀錄管理辦法','Regulations on Operation and Release Records of Toxic and Concerned Chemicals','O0060039',1,2),
 ('毒性及關注化學物質應變器材與偵測警報設備管理辦法','Regulations on Response Equipment and Detection Alarms for Toxic and Concerned Chemicals','O0060036',1,2),
 ('新化學物質及既有化學物質資料登錄辦法','Regulations on Registration of New and Existing Chemical Substances','O0060043',1,2),
 ('環境用藥管理法','Environmental Agents Control Act','O0060001',1,2),
 ('土壤及地下水污染整治法施行細則','Enforcement Rules of the Soil and Groundwater Pollution Remediation Act','O0110002',1,2),
 ('土壤污染管制標準','Soil Pollution Control Standards','O0110005',2,2),
 ('地下水污染管制標準','Groundwater Pollution Control Standards','O0110006',2,2),
 ('土壤污染監測標準','Soil Pollution Monitoring Standards','O0110012',1,2),
 ('地下水污染監測標準','Groundwater Pollution Monitoring Standards','O0110013',1,2),
 ('土壤及地下水污染場址初步評估暨處理等級評定辦法','Regulations on Preliminary Assessment and Grading of Contaminated Sites','O0110022',1,2),
 ('防止貯存系統污染地下水體設施及監測設備設置管理辦法','Regulations on Storage System Groundwater Protection Facilities and Monitoring','O0110010',1,2),
 ('氣候變遷因應法施行細則','Enforcement Rules of the Climate Change Response Act','O0020103',1,3),
 ('溫室氣體排放量盤查登錄及查驗管理辦法','Regulations on GHG Emission Inventory, Registration and Verification','O0020102',2,3),
 ('碳費收費辦法','Carbon Fee Collection Regulations','O0020139',2,3),
 ('自主減量計畫管理辦法','Regulations on Voluntary Reduction Plans','O0020140',1,3),
 ('溫室氣體減量額度交易拍賣及移轉管理辦法','Regulations on Trading, Auction and Transfer of GHG Reduction Credits','O0020138',1,3),
 ('溫室氣體自願減量專案管理辦法','Regulations on Voluntary GHG Reduction Projects','O0020137',1,3),
 ('溫室氣體排放量增量抵換管理辦法','Regulations on Offsetting Incremental GHG Emissions','O0020136',1,3),
 ('自願性產品碳足跡核定標示及管理辦法','Regulations on Voluntary Product Carbon Footprint Labeling','O0020142',1,3),
 ('環境教育法施行細則','Enforcement Rules of the Environmental Education Act','O0120002',1,3),
 ('環境講習執行辦法','Regulations on Environmental Lectures','O0120010',1,3),
 ('環境教育人員認證及管理辦法','Regulations on Certification of Environmental Education Personnel','O0120006',1,3),
 ('公害糾紛處理法施行細則','Enforcement Rules of the Public Nuisance Dispute Mediation Act','O0080002',1,3),
 ('環境保護專責及技術人員訓練管理辦法','Regulations on Training of Environmental Protection Dedicated and Technical Personnel','O0100006',2,3),
 ('環境檢驗測定機構管理辦法','Regulations on Environmental Testing Organizations','O0070001',1,3),
]

for _i,(_zh,_en,_code,_w) in enumerate(OSH_LAWS, start=1):
    LAWS.setdefault(f"OSH-{_i:02d}", (_zh,_en,"",_code))
for _i,(_zh,_en,_code,_w,_t) in enumerate(ENV_LAWS, start=1):
    LAWS.setdefault(f"ENV-{_i:02d}", (_zh,_en,"",_code))
LAW_NAME = {k: v[0] for k, v in LAWS.items()}
LAW_VER = {k: (v[2] or law_version_from_text(v[0])) for k, v in LAWS.items()}
LAW_EN = {k: v[1] for k, v in LAWS.items()}
LAW_CODE = {k: v[3] for k, v in LAWS.items()}

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

_ART_RE = re.compile(r'^第 [\d\-]+ 條', re.M)
def article_count(zh):
    p = os.path.join(os.path.dirname(HERE), "法規原文", zh + ".txt")
    try: return len(_ART_RE.findall(open(p, encoding="utf-8").read()))
    except Exception: return ""

def build_laws(qcount=None):
    qcount = qcount or {}
    rows = [["law_id","group","tier","name_zh","name_en","law_version","source_url","weight","note","articles","questions"]]
    for i,(zh,en,pcode,w) in enumerate(OSH_LAWS, start=1):
        lid = f"OSH-{i:02d}"; code = PCODES.get(zh) or ""
        tier = 1 if (1<=i<=17 or 34<=i<=50) else (2 if (i<=25 or i>=51) else 3)
        rows.append([lid,"OSH",tier,zh,en,LAW_VER.get(lid) or law_version_from_text(zh),law_url(code),(w if in_scope(lid) else 0),("" if in_scope(lid) else "不在指定範圍，暫不使用"),article_count(zh),qcount.get(lid,0)])
    for i,(zh,en,pcode,w,tier) in enumerate(ENV_LAWS, start=1):
        lid = f"ENV-{i:02d}"; code = PCODES.get(zh) or ""
        rows.append([lid,"ENV",tier,zh,en,law_version_from_text(zh),law_url(code),w,"",article_count(zh),qcount.get(lid,0)])
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
                key = (lid, qz.strip())   # 同題幹可跨法規出現（如固定式/移動式起重機同條文）
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
 ["2026-09-03","ENV-26..97","見各題 law_version","建立批次8：環保子法（空污專責人員、固定污染源排放標準、空品標準、室內空品、噪音細則、環境音量標準、水污細則、廢水專責人員、廢清細則、有害事業廢棄物認定、清除處理機構、環評細則、毒化物子法、土污標準、氣候法子法、環教子法…）","batch=8","初版 draft，待審","Claude Code"],
 ["2026-09-03","ENV-29..97, OSH-05/06","見各題 law_version","建立批次9：環保子法逐條出題（空污許可證/空污費/VOC/鍋爐/噪音/水體/飲用水/清除處理/回收再利用/環評認定/毒化物/環境用藥/土水監測/減量交易/碳足跡/環教人員/環檢機構等）＋職災勞工保護法","batch=9","初版 draft，待審","Claude Code"],
 ["2026-09-03","ENV-01..25","見各題 law_version","建立批次10：環保母法逐條出題（空污法/噪音法/水污法/廢清法/環評法/海污法/海岸法/海洋保育法/野保法/濕地法/土污法/毒化法/環境基本法/氣候法/環教法/資源循環推動法/公害糾紛法等）","batch=10","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-01..90","見各題 law_version","建立批次11：職安法規逐條補題（每一條文至少一題）","batch=11","初版 draft，待審","Claude Code"],
 ["2026-09-03","OSH-51..96, ENV-26..97","見各題 law_version","建立批次7：依全國法規資料庫「職業安全衛生目／勞動檢查目／環境部各目」總表補齊：新增 46 部職安法規、72 部環保子法（原文已抓齊）；批次7 起建立題目（霸凌準則、工程安全設計、容許暴露、環測、危險性機械設備檢查、化學品三辦法、機械產品申報登錄／型式驗證、健康服務機構、職業病鑑定、職災補助…）","batch=7","初版 draft，待審","Claude Code"],
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
    from collections import Counter
    laws_rows = build_laws(Counter(r[2] for r in qrows[1:]))
    wb = Workbook()
    ws = wb.active; ws.title = "Laws"
    for r in laws_rows: ws.append(r)
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
    open(os.path.join(HERE,"tsv","Laws.tsv"),"w",encoding="utf-8",newline="").write(tsv(laws_rows))
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
