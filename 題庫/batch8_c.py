# -*- coding: utf-8 -*-
# 第 8 批（C）：廢（污）水處理專責單位或人員辦法、廢污水排放緊急應變辦法、飲用水管理條例、廢棄物清理法施行細則、
#              有害事業廢棄物認定標準、事業廢棄物清理計畫書審查管理辦法、環境影響評估法施行細則、
#              毒性及關注化學物質管理法施行細則、危害預防及應變計畫作業辦法、專業技術管理人員設置及管理辦法
# ※ 本批起四個選項刻意寫成相近長度，避免「最長的就是答案」。
WP = "ENV-46"; EM = "ENV-48"; DW = "ENV-49"; WD = "ENV-52"; HW = "ENV-53"; WPB = "ENV-55"
EIA = "ENV-63"; TR = "ENV-67"; TP = "ENV-68"; TM = "ENV-69"
Q = [
# ---------- 廢（污）水處理專責單位或人員設置及管理辦法（110/2/5） ----------
(WP,"第4條",2,"廢水專責-單位員額",
 "事業依附表一應設置廢（污）水處理專責單位者，其員額至少應有幾名專責人員？其中甲級幾名？",
 ["專責人員三人以上，含甲級二名以上，並由一名甲級人員擔任專責單位主管","專責人員二人以上，含甲級一名以上，並由該甲級人員擔任專責單位主管","專責人員五人以上，含甲級三名以上，並由負責人自行擔任專責單位主管","專責人員四人以上，含乙級二名以上，並由一名乙級人員擔任專責單位主管"],"a",
 "第2條：廢（污）水處理專責人員分甲級及乙級，應由經訓練合格取得證書者擔任。第3條：依附表一許可核准廢污水產生量規模、原廢污水所含附表二物質超過放流水標準或違規情事設置；新開發社區專用下水道服務戶數五百戶以下免設。第4條：專責單位員額至少專責人員三人，包括二名以上甲級，並由一名甲級擔任主管。第5條：得與空污專責單位合併設置並互兼。第7條：員工五十人以下者負責人得兼任。",
 "An enterprise required to set up a wastewater treatment dedicated unit must staff at least how many dedicated personnel, including how many Class A?",
 ["At least three dedicated personnel, including at least two Class A, one of whom heads the unit","At least two dedicated personnel, including at least one Class A, who also heads the unit","At least five dedicated personnel, including at least three Class A, headed by the owner","At least four dedicated personnel, including at least two Class B, one of whom heads the unit"],
 "Articles 2–7."),

(WP,"第9條",3,"廢水專責-代理人",
 "事業設置廢（污）水處理專責人員時，代理人設置及更動之規定為何？",
 ["應同時設置一名以上代理人，應設專責單位或負責人兼任者至少二名，更動後十五日內重新申請核定","應同時設置二名以上代理人，應設專責單位或負責人兼任者至少三名，更動後三十日內重新申請核定","得視需要設置代理人，應設專責單位者至少一名，更動後七日內向中央主管機關備查即可","應同時設置一名以上代理人，僅限甲級人員擔任，更動後六十日內向直轄市縣市主管機關備查"],"a",
 "第9條：應同時設置一名以上代理人；應設置廢污水處理專責單位或負責人兼任專責人員者至少二名；員額超過規定者得扣減同一級別代理人數；代理人應具參加同一級別以上訓練資格；更動應於更動日起十五日內重新申請核定。第10條：申請應檢附合格證書及勞健保查詢同意書等，採網路傳輸。第11條：得由代操作營運機構派任。第12條：取得證書後連續三年未設置者到職翌日起六個月內完成到職訓練。",
 "What are the rules on deputies when appointing wastewater dedicated personnel?",
 ["At least one deputy at the same time, at least two where a unit is required or the owner doubles as personnel, and re-filing within 15 days of any change","At least two deputies at the same time, at least three where a unit is required or the owner doubles as personnel, and re-filing within 30 days of any change","Deputies are optional, at least one where a unit is required, and any change is merely reported to the central authority within 7 days","At least one deputy who must be Class A, with changes reported to the local authority within 60 days"],
 "Articles 9–12."),

(WP,"第15條",3,"廢水專責-專職",
 "下列何種事業或污水下水道系統，其廢（污）水處理專責人員應至少一人專職負責業務？",
 ["應設專責單位者、應設甲乙級人員之公共或工業區污水下水道、服務二千戶以上之社區下水道、員工五百人以上者、三年內曾遭停工復工者","所有設有專責人員之事業，不分規模一律至少一人專職，負責人兼任者亦不得從事其他工作","應設專責單位者、服務一千戶以上之社區下水道、員工一百人以上之事業，以及一年內曾遭罰鍰之事業","僅限公共污水下水道系統及工業區專用下水道，其餘事業之專責人員得兼任其他法規之專責人員"],"a",
 "第15條：專責人員應於勞基法工作時間內常駐；應設專責單位之事業或污水下水道系統、應設甲級或乙級人員之公共污水下水道系統及工業區專用污水下水道系統、服務戶數二千戶以上之社區專用污水下水道系統、應設甲乙級人員且員工五百人以上之事業或其他指定地區專用下水道、三年內情節重大遭停工（業）申請復工者，至少一人專職（不得兼任環保法規以外之專責人員或無關工作，負責人兼任者除外）。第16條：半年內累積超過三十日未到職或一年內三次未備請假紀錄者不得繼續設置。",
 "Which enterprises or sewer systems must have at least one wastewater dedicated person working full-time on the job?",
 ["Those requiring a dedicated unit, public or industrial-park sewer systems requiring Class A/B personnel, community sewers serving 2,000+ households, enterprises with 500+ employees, and those resuming after a shutdown within 3 years","Every enterprise with dedicated personnel regardless of size, including owners who double as personnel, who may not do any other work","Those requiring a dedicated unit, community sewers serving 1,000+ households, enterprises with 100+ employees, and any enterprise fined within the past year","Only public sewer systems and industrial-park sewers; other enterprises' personnel may double as dedicated personnel under other laws"],
 "Articles 15–16."),

(WP,"第22條",2,"廢水專責-業務",
 "廢（污）水處理專責人員每日應簽章確認之事項為何？",
 ["監測連線傳輸設施與主管機關正常連線，以及處理設施重要參數、電度表及排放累計讀數","藥品使用量及污泥產生貯存清運量，以及放流水水質檢測報告之結果與適法性","廢污水收集處理排放管線之巡檢紀錄，以及放流口告示牌座標與採樣平台之維護情形","水污染防治許可證變更展延之申請文件，以及委託檢驗測定機構之採樣紀錄"],"a",
 "第22條：協助釐定收集處理改善並訂定故障應變計畫；協助辦理許可申請及檢測申報並簽章；依許可內容監督操作、簽章確認維修保養、每日簽章確認監測（視）及連線傳輸設施正常連線、每日簽章確認重要參數電度表及排放累計讀數、按次簽章確認藥品使用量及污泥產生貯存清運量並每月統計；監督巡檢管線及放流口採樣平台告示牌水量計測設施並簽章；監督委託檢測機構採樣並告知檢測結果適法性。第23條：不得妨礙參加在職訓練。第24、25條：違反者依水污法第48條第3、4項處罰。",
 "Which items must wastewater dedicated personnel sign off on every day?",
 ["That monitoring and data-link facilities stay connected to the authority, plus key treatment parameters, meter readings and cumulative discharge readings","Chemical consumption and sludge generation, storage and hauling volumes, plus the results and legality of effluent test reports","Inspection records of wastewater collection and discharge pipelines, plus maintenance of outlet signboard coordinates and sampling platforms","Permit amendment and extension applications, plus the sampling records of commissioned testing organizations"],
 "Article 22 (chemical and sludge volumes are signed per batch and totaled monthly; pipelines, outlets and sampling are supervised and signed)."),

# ---------- 事業或污水下水道系統排放廢（污）水緊急應變辦法（94/8/26） ----------
(EM,"第4條",2,"廢水緊急應變-通知時限",
 "事業排放廢污水於自來水水源等承受水體有嚴重危害之虞時，負責人應於多久內通知用水單位？多久內通知環保主管機關？",
 ["一小時內通知受污染水體之用水事業單位或民眾，三小時內通知當地環保主管機關","三小時內通知受污染水體之用水事業單位或民眾，一小時內通知當地環保主管機關","二小時內通知受污染水體之用水事業單位或民眾，二十四小時內通知當地環保主管機關","三十分鐘內通知受污染水體之用水事業單位或民眾，十二小時內通知中央環保主管機關"],"a",
 "第2條：適用承受水體為自來水水源、飲用水水源、灌溉渠道用水、漁業養殖用水。第3條：處理設施故障操作異常或意外致排放含有害健康物質、未經處理逕行排放或超過處理貯留能力影響水體用途，或化學物質運作場所災變救災產生大量廢污水直接排放者屬嚴重危害之虞。第4條：應立即停止排放、限制縮小污染範圍、一小時內通知用水事業單位管理單位或直接引用之民眾、三小時內通知當地環保主管機關。",
 "When a wastewater discharge threatens drinking or irrigation water sources, the responsible person must notify water users within, and the local environmental authority within:",
 ["1 hour for the affected water users or residents, 3 hours for the local environmental authority","3 hours for the affected water users or residents, 1 hour for the local environmental authority","2 hours for the affected water users or residents, 24 hours for the local environmental authority","30 minutes for the affected water users or residents, 12 hours for the central environmental authority"],
 "Articles 2–4."),

(EM,"第5條",3,"廢水緊急應變-執行方法",
 "廢污水緊急應變時，對受污染水體之採樣分析應包含哪些項目？頻率為何？",
 ["pH、溶氧、化學需氧量、導電度及製程含有之有害健康物質，每四小時一次至承受水體恢復背景值","pH、濁度、生化需氧量、氨氮及重金屬總量，每二小時一次至主管機關同意停止為止","溫度、溶氧、懸浮固體、總磷及大腸桿菌群，每六小時一次連續三日","pH、導電度、油脂、氰化物及製程含有之毒性物質，每日一次至放流水符合標準"],"a",
 "第5條：關閉放流口或設攔截阻隔設施；減少或停止生產；備妥暫時貯存設施否則停止作業；抑止排除異常故障並啟動備份裝置；執行污染控制；對受污染水體立即採樣分析 pH、溶氧、化學需氧量、導電度及製程中有害健康物質；於受影響區域每四小時採樣一次至恢復背景值並提供用水單位；鄰近有下水道者申請緊急納入或委託處理；無法排除者設管線排放於承受水體區域外；污水下水道系統通知納管用戶減少排放；以電話傳真書面通知；化學物質災變設截流收集暫存設施。第7條：屆期不執行由主管機關與目的事業主管機關協助執行。",
 "During a wastewater emergency, what must be sampled in the affected water body, and how often?",
 ["pH, dissolved oxygen, COD, conductivity and health-harmful substances from the process, every 4 hours until background levels return","pH, turbidity, BOD, ammonia and total heavy metals, every 2 hours until the authority allows stopping","Temperature, dissolved oxygen, suspended solids, total phosphorus and coliforms, every 6 hours for three days","pH, conductivity, oil and grease, cyanide and toxic process substances, once a day until effluent meets standards"],
 "Articles 5 and 7."),

# ---------- 飲用水管理條例（95/1/27） ----------
(DW,"第5條",2,"飲用水-水源保護區禁止行為",
 "在飲用水水源水質保護區或取水口一定距離內，下列何者屬禁止之污染水源水質行為？",
 ["非法砍伐林木、工業區開發或污染性工廠設立、營利飼養家畜家禽、新社區開發、高爾夫球場興建、土石採取探礦採礦","一般住宅之修繕、農民自用之小型菜園耕作、原住民部落自然增加之社區、經核准之道路開發","經主管機關核准之居民生活必要行為、既有合法建築物之使用、公共設施之維護、既有道路之修補","河川清淤疏濬、防洪堤防之興建、水土保持之植生工程、自來水事業之淨水設施設置"],"a",
 "第5條：保護區或取水口一定距離內不得有非法砍伐林木或開墾土地、工業區開發或污染性工廠設立、核能及能源開發及核廢料儲存處理場所、傾倒棄置垃圾灰渣土石污泥糞尿廢油廢化學品動物屍骸、以營利為目的飼養家畜家禽、新社區開發（原住民部落自然增加除外）、高爾夫球場興修擴建、土石採取及探礦採礦、達環評規模之鐵路捷運港灣機場開發、未經同意之河道變更及道路運動場開發、其他公告禁止行為；第1至9款及第12款為居民生活必要經核准者除外；範圍由地方擬訂報中央核定公告。第20條：違反處十萬元以上一百萬元以下罰鍰並通知禁止。第16條：經通知禁止不遵行者處一年以下有期徒刑得併科六萬元以下罰金。",
 "Which acts are prohibited within drinking water source protection zones or near intakes?",
 ["Illegal logging, industrial park development or polluting factories, commercial livestock raising, new community development, golf course construction, and quarrying or mining","Ordinary home repairs, small vegetable plots for farmers' own use, indigenous communities growing naturally, and approved road development","Residents' daily necessities approved by the authority, use of existing legal buildings, maintenance of public facilities, and repair of existing roads","River dredging, flood embankments, soil conservation planting, and installation of water utility treatment facilities"],
 "Articles 5, 16 and 20."),

(DW,"第16條",3,"飲用水-刑罰",
 "違反飲用水管理條例經通知禁止而不遵行者之處罰為何？因而致人於死者？",
 ["一年以下有期徒刑、拘役，得併科六萬元以下罰金；七年以下有期徒刑，得併科三十萬元以下罰金","三年以下有期徒刑、拘役，得併科十萬元以下罰金；十年以下有期徒刑，得併科五十萬元以下罰金","六個月以下有期徒刑、拘役，得併科三萬元以下罰金；五年以下有期徒刑，得併科十五萬元以下罰金","二年以下有期徒刑、拘役，得併科二十萬元以下罰金；無期徒刑或七年以上有期徒刑，得併科一百萬元以下罰金"],"a",
 "第16條：違反第5條第1項經通知禁止不遵行、違反第6條第1項經通知禁止作為水源不遵行、違反第11條第1項經通知禁止供飲用不遵行者，處一年以下有期徒刑拘役得併科六萬元以下罰金；致人於死者七年以下有期徒刑得併科三十萬元以下罰金，致重傷者五年以下有期徒刑得併科十五萬元以下罰金。第18條：使用非公告藥劑處一年以下有期徒刑或六萬元以下罰金。第19條：法人代表人等執行業務犯罪者法人亦科罰金。第24條：飲用水水質違反標準處六萬元以上六十萬元以下罰鍰並限期改善，屆期未改善按日連續處罰，情節重大禁止供飲用。",
 "Failing to comply after being ordered to stop under the Drinking Water Management Act is punished by, and if it causes death:",
 ["Up to 1 year imprisonment or detention, with a fine up to NT$60,000; up to 7 years imprisonment with a fine up to NT$300,000","Up to 3 years imprisonment or detention, with a fine up to NT$100,000; up to 10 years imprisonment with a fine up to NT$500,000","Up to 6 months imprisonment or detention, with a fine up to NT$30,000; up to 5 years imprisonment with a fine up to NT$150,000","Up to 2 years imprisonment or detention, with a fine up to NT$200,000; life or 7+ years imprisonment with a fine up to NT$1 million"],
 "Articles 16–19 and 24."),

(DW,"第23條",3,"飲用水-連續供水設備",
 "公私場所設置供公眾飲用之連續供水固定設備者，應辦理何事項？違反者處罰為何？",
 ["向地方主管機關申請登記始得使用、依規定維護並作成紀錄揭示、委託許可檢測機構定期採樣檢驗水質並記錄；違反處一萬元以上十萬元以下罰鍰並限期改善","向中央主管機關申請許可證始得使用、每月自行檢驗水質並公告、每年委託檢測機構抽驗一次；違反處五萬元以上五十萬元以下罰鍰並限期改善","向自來水事業申請核備始得使用、每季更換濾心並拍照存證、由專責人員每日檢測餘氯；違反處三萬元以上三十萬元以下罰鍰並得停用","向衛生主管機關申請登記始得使用、每半年清洗水塔並記錄、委託檢測機構每年檢驗一次；違反處六萬元以上六十萬元以下罰鍰並按日連續處罰"],"a",
 "第8條：經公告之公私場所設連續供水固定設備者應向直轄市縣市主管機關申請登記始得使用。第9條：應依規定維護並作成紀錄揭示保存。第12條：應依規定採樣檢驗水質並作成紀錄揭示備查，由取得許可證之環境檢驗測定機構辦理。第22條：未登記處一萬元以上十萬元以下罰鍰並限期補正。第23條：未維護記錄揭示或未採樣檢驗揭示者處一萬元以上十萬元以下罰鍰並限期改善，屆期按次處罰。第25條：規避妨礙拒絕查驗處三萬元以上三十萬元以下。第29條：公告前已設置者六個月內申請登記。",
 "Premises with fixed continuous water dispensers for public drinking must, and violations are fined:",
 ["Register with the local authority before use, maintain and post maintenance records, and have licensed testing organizations sample and test water quality periodically; NT$10,000–100,000 with a correction deadline","Obtain a license from the central authority before use, self-test water monthly and post results, and have a testing organization spot-check yearly; NT$50,000–500,000 with a correction deadline","File with the water utility before use, replace filters quarterly with photo records, and have dedicated staff test residual chlorine daily; NT$30,000–300,000 and possible suspension","Register with the health authority before use, clean tanks semi-annually with records, and have a testing organization test yearly; NT$60,000–600,000 with daily fines"],
 "Articles 8–12, 22–25 and 29."),

# ---------- 廢棄物清理法施行細則（108/11/6） ----------
(WD,"第11條",3,"廢清細則-自行清除處理",
 "廢棄物清理法第28條所稱事業「自行清除、處理」，包括下列何種情形？",
 ["以自有設施清除處理、以自有設施合併處理法人所屬各事業之廢棄物、租用合法運輸業車輛清除（隨車派員監控並攜帶員工證明）","以自有設施清除處理、委託取得許可之清除機構清除、由執行機關代為處理並繳納處理費用之情形","以自有設施清除處理、與鄰近事業共同委託處理機構處理、交由再利用機構再利用並登錄流向之情形","以自有設施清除處理、借用其他事業之處理設施處理、以任何車輛自行載運至掩埋場並取得收據之情形"],"a",
 "第11條：自行清除處理指以自有設施清除處理所產生之事業廢棄物、以自有設施合併清除處理該法人所屬各事業之廢棄物、租用合法運輸業車輛清除（應隨車派員監控管理攜帶員工證明文件，車輛符合貯存清除處理方法及設施標準）、其他經認定者；經執行機關同意委託處理指經直轄市縣市環保局同意；餘裕處理能量指焚化設施可處理量扣除操作保留量（可處理量百分之十）及指定清除地區一般廢棄物處理量後之剩餘。第9條：產生源證明文件為遞送聯單等，處理地點證明為合約影本。",
 "'Self-clearance and disposal' by an enterprise under Article 28 of the Waste Disposal Act includes:",
 ["Using its own facilities, jointly handling waste of all enterprises under the same legal person with its own facilities, or renting licensed transport vehicles with an accompanying employee carrying proof","Using its own facilities, entrusting a licensed clearance organization, or having the executing agency dispose of it while paying the treatment fee","Using its own facilities, jointly entrusting a treatment organization with neighboring enterprises, or sending waste to reuse organizations with flow registration","Using its own facilities, borrowing another enterprise's treatment facilities, or hauling with any vehicle to a landfill and keeping the receipt"],
 "Articles 9 and 11."),

(WD,"第12條",3,"廢清細則-清理計畫變更",
 "事業廢棄物清理計畫書所載資料異動而未致廢棄物性質改變或數量增加逾百分之多少者，得免辦理變更但應於幾日內申請異動備查？",
 ["未逾百分之十者免變更，應於事實發生後十五日內填寫異動申請書報請備查","未逾百分之二十者免變更，應於事實發生後三十日內填寫異動申請書報請備查","未逾百分之五者免變更，應於事實發生後七日內填寫異動申請書報請核准","未逾百分之十五者免變更，應於次年一月底前併同年度申報一併報請備查"],"a",
 "第12條：與事業廢棄物產生清理有關事項變更指新增或改變產品製造過程作業流程處理流程、回收貯存清除處理再利用方法或設施改變、原物料使用量產量營運擴增致廢棄物性質改變或數量增加者；基本資料原物料產品營運資料異動或流程新增改變而未致性質改變或數量增加逾百分之十者免變更，應於事實發生後十五日內填寫異動申請書報請備查；天災重大事故產生之非經常性廢棄物於清理前提出處置計畫書經核准者免變更。第15條：停工停業復工復業前應檢具改善證明及清理計畫書申請核准。第16條：涉製程或設施變更應先申請試車，試車期間三十日為限展延不超過六十日。",
 "Changes to a waste disposal plan that do not alter waste properties or increase quantity by more than what share are exempt from formal amendment but must be filed within:",
 ["10%; an alteration application filed for record within 15 days of the change","20%; an alteration application filed for record within 30 days of the change","5%; an alteration application filed for approval within 7 days of the change","15%; filed together with the annual report by the end of January the following year"],
 "Articles 12, 15–16."),

# ---------- 有害事業廢棄物認定標準（109/2/21） ----------
(HW,"第2條",2,"有害廢棄物-判定順序",
 "有害事業廢棄物依何順序判定？列表之有害事業廢棄物包括哪些？",
 ["先依列表、再依有害特性認定、最後依中央主管機關公告；列表者為製程有害事業廢棄物、混合五金廢料、生物醫療廢棄物","先依有害特性認定、再依列表、最後依地方主管機關公告；列表者為溶出毒性廢棄物、戴奧辛廢棄物、石綿廢棄物","先依中央主管機關公告、再依列表、最後依有害特性認定；列表者為毒性有害廢棄物、腐蝕性廢棄物、反應性廢棄物","先依事業自行申報、再依檢測機構認定、最後依列表；列表者為易燃性廢棄物、多氯聯苯廢棄物、廢容器"],"a",
 "第2條：依序為列表之有害事業廢棄物、有害特性認定之有害事業廢棄物、其他經中央主管機關公告者。第3條：列表者為製程有害事業廢棄物（附表一製程產生）、混合五金廢料（依清理階段危害特性判定，附表二）、生物醫療廢棄物（醫療機構醫事檢驗所生物安全二級以上實驗室等產生附表三所列）。第4條：有害特性認定者為毒性（毒化物第一至三類固液體廢棄物及直接接觸之廢容器）、溶出毒性（TCLP 萃出液超過附表四）、戴奧辛（總毒性當量超過 1.0 ng I-TEQ/g）、多氯聯苯（含量百萬分之五十以上）、腐蝕性、易燃性、反應性、石綿及其製品。",
 "In what order are hazardous industrial wastes determined, and what does the 'listed' category include?",
 ["Listed first, then hazard-characteristic determination, then central authority announcements; listed wastes are process wastes, mixed metal scrap and biomedical waste","Hazard characteristics first, then listing, then local authority announcements; listed wastes are leachate-toxic, dioxin and asbestos wastes","Central announcements first, then listing, then hazard characteristics; listed wastes are toxic, corrosive and reactive wastes","Self-declaration first, then testing organization determination, then listing; listed wastes are ignitable, PCB and container wastes"],
 "Articles 2–4."),

(HW,"第4條",3,"有害廢棄物-特性數值",
 "有害特性認定之腐蝕性事業廢棄物及易燃性事業廢棄物之判定數值為何？",
 ["廢液 pH 大於等於 12.5 或小於等於 2.0，或攝氏五十五度對鋼腐蝕速率每年超過 6.35 毫米；廢液閃火點小於攝氏六十度","廢液 pH 大於等於 11.0 或小於等於 3.0，或攝氏二十五度對鋼腐蝕速率每年超過 3.5 毫米；廢液閃火點小於攝氏三十八度","廢液 pH 大於等於 13.0 或小於等於 1.0，或攝氏五十五度對鋁腐蝕速率每年超過 6.35 毫米；廢液閃火點小於攝氏九十三度","廢液 pH 大於等於 12.0 或小於等於 2.5，或攝氏四十度對鋼腐蝕速率每年超過 1.0 毫米；廢液閃火點小於攝氏五十度"],"a",
 "第4條：腐蝕性指廢液 pH 大於等於 12.5 或小於等於 2.0，或攝氏五十五度時對鋼（S20C）腐蝕速率每年超過 6.35 毫米（固體於溶液狀態亦同）；易燃性指廢液閃火點小於攝氏六十度（乙醇體積濃度小於百分之二十四之酒類廢棄物除外）、固體常溫常壓下因摩擦吸水或自發反應起火、可釋出氧之廢強氧化劑；反應性指常溫常壓易爆炸、與水劇烈反應、含氰化物於 pH 2.0～12.5 產生 250 mg HCN/kg 以上、含硫化物產生 500 mg H₂S/kg 以上；戴奧辛總毒性當量超過 1.0 ng I-TEQ/g；多氯聯苯百萬分之五十以上；石綿含百分之一以上易飛散者。第5條：附表一列表者得檢具文件申請表列排除改列一般事業廢棄物，中間處理後有害性消失者得認定為一般事業廢棄物。",
 "The numeric criteria for corrosive and ignitable industrial waste are:",
 ["Liquid pH ≥ 12.5 or ≤ 2.0, or steel corrosion above 6.35 mm/year at 55°C; liquid flash point below 60°C","Liquid pH ≥ 11.0 or ≤ 3.0, or steel corrosion above 3.5 mm/year at 25°C; liquid flash point below 38°C","Liquid pH ≥ 13.0 or ≤ 1.0, or aluminum corrosion above 6.35 mm/year at 55°C; liquid flash point below 93°C","Liquid pH ≥ 12.0 or ≤ 2.5, or steel corrosion above 1.0 mm/year at 40°C; liquid flash point below 50°C"],
 "Articles 4–5 (also reactivity, dioxin 1.0 ng I-TEQ/g, PCB 50 ppm, asbestos 1%)."),

# ---------- 事業廢棄物清理計畫書審查管理辦法（114/7/10） ----------
(WPB,"第4條",2,"清理計畫書-內容",
 "事業廢棄物清理計畫書應載明之事項，下列何者正確？",
 ["事業基本資料、原物料使用量及產品產量、製程或作業流程、廢棄物種類數量性質及清理方式、廠區配置圖、遷廠停業破產時之清理計畫、有害廢棄物之緊急應變措施","事業基本資料、員工人數及組織圖、產品售價及營業額、廢棄物委託契約影本、環評審查結論全文、清除車輛照片、專責人員在職訓練證明","事業基本資料、廠房建照及使用執照、水污及空污許可證影本、廢棄物年度預算表、掩埋場地質報告、清除路線圖、負責人無犯罪紀錄證明","事業基本資料、股東名冊及資本額、進口原料報單、廢棄物採樣檢測報告、鄰近居民同意書、消防安檢證明、保險契約影本"],"a",
 "第3條：提送時機為新設新提重提變更異動展延，經核准後始得營運。第4條：應載明指定公告事業基本資料、原物料使用量及產品產量或營運狀況、產品製造或使用過程作業流程處理流程、事業廢棄物種類數量物理性質有害特性主要有害成分及清理方式、廠區配置圖、遷廠停歇業宣告破產時之清理計畫、產生有害事業廢棄物者之火災逸散洩漏緊急應變措施、其他指定事項。第5條：以電子簽章電子文件或書面一式二份向審核機關申請，檢附許可登記證明、負責人身分證明、專技人員證明、環評相關內容。第11條之1：申請前須繪製全廠空水廢毒污染流向示意圖。",
 "A waste disposal plan must state:",
 ["Basic data, raw material use and output, processes or workflows, waste types/quantities/properties and disposal methods, a site layout, a plan for relocation/closure/bankruptcy, and emergency measures for hazardous waste","Basic data, headcount and organization chart, product prices and revenue, copies of disposal contracts, the full EIA conclusion, photos of vehicles, and staff training certificates","Basic data, building and occupancy permits, copies of water and air permits, an annual waste budget, a landfill geology report, hauling routes, and a clean criminal record of the owner","Basic data, shareholder list and capital, import declarations, waste sampling reports, neighbors' consent, fire safety certificates, and insurance contracts"],
 "Articles 3–5 and 11-1."),

(WPB,"第9條",3,"清理計畫書-有效期限",
 "事業廢棄物清理計畫書之有效期限為幾年？展延應於何時申請？審核機關受理新設變更展延應於幾日內完成審查？",
 ["五年（首次依附表或公告方式收受不同廢棄物再利用者三年）；屆滿前四至六個月；四十五日內，得延長四十五日","三年（再利用者二年）；屆滿前二至三個月；三十日內，得延長三十日","十年（再利用者五年）；屆滿前六至九個月；六十日內，得延長六十日","五年（再利用者亦五年）；屆滿前一個月；二十五日內，得延長二十五日"],"a",
 "第9條：有效期限五年，首次依中央目的事業主管機關或中央主管機關再利用管理辦法附表或公告管理方式收受不同事業廢棄物再利用者三年；屆滿後繼續營運應於屆滿前四個月至六個月申請展延，每次五年（再利用者三年以上五年以下）；期限內辦理變更者自核准日重新起算；有第16條情形或一年內無再利用業務者得縮減至未滿三年。第11條：新設新提重提變更展延應通知七日內繳審查費並於四十五日內完成審查，必要時延長四十五日；異動二十五日內（得延長二十五日）；補正以三次為限總日數不超過三十日。第11條之2：固體再生燃料原料用途須經書面審查現場勘查及試運轉三階段，試運轉不超過二個月展延一次不超過一個月。",
 "A waste disposal plan is valid for, extension must be applied for, and review of new or amended plans is completed within:",
 ["5 years (3 years for first-time reuse of new waste types under listed methods); 4 to 6 months before expiry; 45 days, extendable by 45","3 years (2 years for reuse); 2 to 3 months before expiry; 30 days, extendable by 30","10 years (5 years for reuse); 6 to 9 months before expiry; 60 days, extendable by 60","5 years (also 5 for reuse); 1 month before expiry; 25 days, extendable by 25"],
 "Articles 9, 11 and 11-2."),

(WPB,"第16條",3,"清理計畫書-撤銷廢止",
 "指定公告事業有何情形，地方主管機關得移請審核機關撤銷或廢止其事業廢棄物清理計畫書？",
 ["違反同一規定一年內經二次限期改善仍違反、非法棄置有害事業廢棄物、未依核准計畫書清理嚴重污染環境、明知不實而申請申報或文書虛偽記載","逾期繳納審查費二次、未參加主管機關舉辦之說明會、未於期限內更新負責人聯絡電話、廠區配置圖未依比例繪製","三年內經一次警告、一般事業廢棄物委託未取得再利用許可之機構、未依規定保存遞送聯單一年、專責人員請假超過三十日","變更負責人未於三十日內申報、廢棄物數量減少逾百分之十未辦理異動、未設置廢棄物貯存區告示牌、未每季申報產出量"],"a",
 "第16條：違反第6條第9條或第13條同一規定一年內經二次限期改善仍繼續違反、非法棄置有害事業廢棄物、未依核准之清理計畫書貯存清除處理再利用嚴重污染環境、明知不實而申請申報不實或文書虛偽記載、其他情節重大者，得移請審核機關撤銷或廢止；許可登記執照經撤銷廢止註銷者計畫書失效；撤銷廢止或失效後應停止營運，廠內未清理廢棄物依主管機關指示辦理並自行負擔費用。第13條：應依核准之計畫書進行貯存清除處理再利用輸出入。第15條：遷廠停歇業破產清理完畢後應申請解除列管。",
 "A waste disposal plan may be revoked when the enterprise:",
 ["Keeps violating the same rule after two correction orders within a year, illegally dumps hazardous waste, seriously pollutes by ignoring the approved plan, or knowingly files false applications or records","Pays the review fee late twice, skips the authority's briefing sessions, fails to update the owner's phone number in time, or draws the site layout out of scale","Receives one warning within three years, entrusts general waste to an unlicensed reuse organization, keeps manifests for under a year, or has dedicated staff on leave over 30 days","Fails to report an owner change within 30 days, reduces waste by over 10% without filing, lacks a storage area signboard, or misses quarterly output reports"],
 "Articles 13–16."),

# ---------- 環境影響評估法施行細則（115/2/5） ----------
(EIA,"第6條",2,"環評細則-不良影響",
 "環境影響評估法第5條所稱「不良影響」，係指開發行為有下列何種情形？",
 ["引起水空氣土壤污染噪音振動惡臭廢棄物毒性物質地盤下陷或輻射公害、危害自然資源合理利用、破壞自然景觀或生態、破壞社會文化或經濟環境","增加地方政府稅收負擔、影響鄰近土地交易價格、改變當地居民之通勤路線、降低周邊商圈之營業額、變更都市計畫之分區使用","超過工程預算或工期延宕、施工廠商財務困難、承包商未投保工程險、施工人員未受安全訓練、工地未設置圍籬","未取得建造執照即施工、未召開地方說明會、未於報紙刊登公告、未提出替代方案、未繳納審查費用"],"a",
 "第6條：不良影響指引起水污染空氣污染土壤污染噪音振動惡臭廢棄物毒性物質污染地盤下陷或輻射污染公害現象、危害自然資源之合理利用、破壞自然景觀或生態環境、破壞社會文化或經濟環境、其他經中央主管機關公告者。第7條：開發單位指從事開發行為之自然人法人團體等。第8條：規劃指可行性研究先期作業準備申請許可等階段。第11條：環境影響說明書於開發審議或許可申請階段提出。第5條之1：委員會組織規程應含利益迴避，地方政府為開發單位時其機關委員應全數迴避。",
 "'Adverse impact' under Article 5 of the Environmental Impact Assessment Act means development that:",
 ["Causes water, air or soil pollution, noise, vibration, odor, waste, toxic substances, subsidence or radiation, harms rational use of natural resources, or damages landscapes, ecology, or social, cultural and economic environments","Raises local tax burdens, affects nearby land prices, changes residents' commuting routes, reduces business turnover nearby, or changes urban zoning","Exceeds the budget or schedule, involves contractors in financial trouble, lacks construction insurance, has untrained workers, or has no site fencing","Starts without a building permit, holds no local briefing, publishes no newspaper notice, offers no alternatives, or fails to pay review fees"],
 "Articles 5-1 to 11."),

(EIA,"第19條",3,"環評細則-第二階段",
 "環評法第8條所稱「對環境有重大影響之虞」應繼續進行第二階段環評，係指下列何種情形？",
 ["屬附表二所列開發行為經委員會審查認定，或經審查認定與周圍計畫顯著衝突、對環境資源保育類物種國民健康或他國環境有顯著不利影響、逾越環境品質標準、眾多居民遷移等","開發面積超過一公頃、投資金額超過新臺幣十億元、施工期程超過三年、位於直轄市範圍內、由外國企業投資者","經地方民意代表要求、經民眾連署達一千人、經媒體報導引起關注、經環保團體陳情、經開發單位主動申請者","目的事業主管機關未提出政策說明、開發單位補正逾期、審查費未繳納、環境影響說明書未附替代方案、公開說明會出席人數不足者"],"a",
 "第19條：對環境有重大影響之虞指依環評法第5條應實施環評且屬附表二所列開發行為經委員會審查認定，或不屬附表二但經審查認定與周圍相關計畫顯著不利衝突不相容、對環境資源或特性顯著不利影響、對保育類或珍貴稀有動植物棲息顯著不利影響、使當地環境顯著逾越環境品質標準或超過涵容能力、對眾多居民遷移權益或少數民族傳統生活方式顯著不利影響、對國民健康或安全顯著不利影響、對其他國家環境顯著不利影響、其他經主管機關認定；開發單位得於第一階段審查結論作成前書面自願進行第二階段。第16條：情形特殊指規模龐大影響廣泛或爭議性高非短時間能完成審查。第43條：審查結論分通過、有條件通過、應繼續第二階段、認定不應開發等。",
 "'Likely to have significant environmental impact' requiring a second-stage EIA means:",
 ["Projects listed in Appendix 2 as determined by the committee, or projects found to conflict with surrounding plans, significantly harm resources, protected species, public health or other countries' environments, exceed quality standards, or displace many residents","Projects over one hectare, over NT$1 billion, longer than three years, located in a municipality, or funded by foreign investors","Projects requested by local councilors, petitioned by 1,000 signatures, covered by the media, protested by environmental groups, or voluntarily applied for","Projects lacking a policy statement from the competent authority, late corrections, unpaid fees, no alternatives in the statement, or poorly attended briefings"],
 "Articles 16, 19 and 43."),

(EIA,"第22條",3,"環評細則-公開說明會",
 "開發單位舉行公開說明會，應於幾日前刊載新聞紙及公布於指定網站並通知有關機關？說明會後幾日內應作成紀錄函送並公布？",
 ["十日前刊載及通知，會後四十五日內作成紀錄函送並公布於指定網站至少三十日","三十日前刊載及通知，會後十五日內作成紀錄函送並公布於指定網站至少七日","七日前刊載及通知，會後三十日內作成紀錄函送並公布於指定網站至少六十日","十五日前刊載及通知，會後六十日內作成紀錄函送並公布於指定網站至少十四日"],"a",
 "第20條：適當地點指鄉鎮市區公所及村里辦公室、毗鄰公所、附近學校寺廟教堂市集、五百公尺內公共道路路側、其他認可處所，應擇五處以上陳列揭示並公布於指定網站至少三十日。第21條：刊載新聞紙應連續三日以上。第22條：公開說明會應於十日前將時間地點方式名稱場所刊載新聞紙及公布指定網站，並於適當地點公告及通知有關機關、當地及毗鄰公所、民意機關、村里長；會後四十五日內作成紀錄函送並公布至少三十日。第22條之1：範疇界定資料公布至少十四日，範疇界定會議七日前公布，完成後三十日內公布。第26條：公聽會十日前通知並公布至舉行翌日，紀錄三十日內公布。第30條：審查結論公告陳列至少十五日或刊載新聞紙連續五日以上。",
 "Public briefings on a development must be announced in newspapers, online and to relevant agencies how many days ahead, and minutes must be sent and posted within:",
 ["10 days ahead; minutes within 45 days, posted online for at least 30 days","30 days ahead; minutes within 15 days, posted online for at least 7 days","7 days ahead; minutes within 30 days, posted online for at least 60 days","15 days ahead; minutes within 60 days, posted online for at least 14 days"],
 "Articles 20–22-1, 26 and 30."),

(EIA,"第38條",3,"環評細則-重新辦理",
 "開發單位變更原申請內容有下列何種情形，應就變更部分重新辦理環境影響評估？",
 ["計畫產能規模擴增或路線延伸百分之十以上、土地使用變更涉及保護區綠帶緩衝區、降低環保設施處理等級或效率、對影響範圍內環境有加重影響之虞","計畫產能規模縮減或路線縮短百分之十以上、環保設施調整位置但不涉及承受水體、環境監測計畫變更、既有設備汰舊換新產能不變","開發基地內非環保設施局部調整位置、災害復原重建、法規容許誤差範圍內之變更、依環保法規修正執行公告之檢測方法","提升環保設施處理等級或效率、原基地範圍內產能降低、經主管機關認定對環境品質不生負面影響、變更開發單位名稱地址"],"a",
 "第36條：變更原申請內容指第6條第2項第1、4、5、8款或第11條第2項第1、4、5、8、10至12款內容變更；非環保設施局部調整位置、災害復原重建、法規容許誤差、依環保法規修正執行檢測方法、原基地內產能規模降低、提升環保設施等級效率、經認定不生負面影響者僅需備查。第37條：無須重新環評者提出環境影響差異分析報告，環保設施調整位置或功能、既有設備改變製程汰舊換新產能提升未達百分之十且污染總量未增加、環境監測計畫變更等得檢附變更內容對照表。第38條：產能規模擴增或路線延伸百分之十以上、土地使用變更涉及保護區綠帶緩衝區、降低環保設施處理等級或效率、對影響範圍內生活自然社會環境或保護對象有加重影響之虞、對環境品質維護有不利影響者應重新環評（第1、2款經主管機關及目的事業主管機關同意者除外）；完成並取得營運許可後規模擴增仍應依第5條實施環評。",
 "Changes to an approved development that require a new EIA for the changed part include:",
 ["Expanding capacity or scale or extending routes by 10% or more, land-use changes affecting protected zones or green buffers, lowering treatment level or efficiency of environmental facilities, or aggravating impacts within the affected area","Reducing capacity or shortening routes by 10% or more, relocating environmental facilities without changing receiving waters, changing the monitoring plan, or replacing old equipment at the same capacity","Locally repositioning non-environmental facilities on site, disaster reconstruction, changes within legal tolerances, or adopting newly announced test methods under environmental laws","Raising treatment level or efficiency, reducing capacity within the original site, changes the authority deems harmless to environmental quality, or changing the developer's name or address"],
 "Articles 36–38."),

# ---------- 毒性及關注化學物質管理法施行細則（108/9/3） ----------
(TR,"第10條",3,"毒化細則-緊急防治措施",
 "毒化法第41條所稱事故發生時運作人應採取之「緊急防治措施」，包括下列何者？",
 ["足以即時控制毒性或具危害性關注化學物質大量流布使其回復常態之污染防治措施、中止引起事故之部分或全部運作、減輕或防堵危害擴大之措施","立即向保險公司申報理賠並保存事故現場之影像紀錄、通知工會及員工家屬、暫停所有生產線並遣散現場人員、等待主管機關到場指示","一小時內向中央主管機關提出書面事故調查報告、召開記者會說明、對周邊居民發放慰問金、委託第三方進行環境監測三個月","停止一切化學物質之輸入及販賣、註銷相關許可證登記文件、將剩餘物質全部退回供應商、關閉運作場所六個月以上"],"a",
 "第2條：製造指調配加工合成分裝（自行使用時之調配加工分裝除外）。第3條：運送指以車輛船舶航空器載運裝卸。第9條：事故涉及二以上直轄市縣市由中央指定主管機關，運作人報知得僅向其中之一為之。第10條：緊急防治措施指足以即時控制毒性或指定公告具危害性關注化學物質大量流布使回復常態運作之污染防治措施、中止引起事故之部分或全部運作、減輕或防堵危害擴大之措施、其他主管機關規定之應變事項。第11條：必要時指已採措施仍未減輕防堵或未採措施情況急迫。第5、7條：停止運作指結束部分或全部運作，中止運作指中斷製造輸入販賣使用貯存。第8條：郵購及電子購物指廣播電視電話網際網路等不特定對象交易。",
 "'Emergency control measures' an operator must take when a toxic chemical incident occurs include:",
 ["Pollution controls that immediately contain large releases of toxic or hazardous concerned chemicals and restore normal operation, halting the operations causing the incident in part or whole, and measures that mitigate or block the spread of harm","Filing an insurance claim immediately while preserving site footage, notifying the union and employees' families, halting all production lines and dismissing site staff, and waiting for the authority's instructions on site","Submitting a written investigation report to the central authority within one hour, holding a press conference, paying condolence money to nearby residents, and commissioning three months of third-party monitoring","Stopping all imports and sales of chemicals, cancelling permits and registrations, returning all remaining substances to suppliers, and closing the site for at least six months"],
 "Articles 2–11."),

# ---------- 毒性及關注化學物質危害預防及應變計畫作業辦法（109/10/21） ----------
(TP,"第2條",2,"毒化應變計畫-應製作者",
 "何種運作人應製作廠（場）危害預防及應變計畫？何者應製作運送危害預防及應變計畫？",
 ["任一場所內單一毒性或具危害性關注化學物質任一日運作總量達分級運作量之製造輸入販賣使用貯存運作人；自行或委託運送須申報一般運送表單之所有人","任一場所內運作任何數量第一類毒性化學物質之製造輸入販賣使用貯存運作人；以車輛運送任何數量毒性化學物質之駕駛人","單一毒性化學物質年運作總量達一百公噸以上之製造及輸入運作人；委託運送而未與受託人訂定書面契約之所有人","同一場所運作二種以上毒性化學物質之製造使用運作人；跨越二以上直轄市縣市運送第三類毒性化學物質之運送業者"],"a",
 "第2條：危害預防及應變計畫分廠（場）及運送二類；相關運作人指製造輸入販賣使用貯存及運送第一至三類毒化物及指定公告具危害性關注化學物質之運作人及所有人；製造輸入販賣使用貯存運作人任一場所內單一物質任一日運作總量達分級運作量者應製作廠（場）計畫；所有人自行或委託運送符合運送管理辦法須申報一般運送表單者應製作運送計畫；同一場所運作多種者合併製作。第6條：申請許可證登記文件核可文件前應檢送廠（場）計畫報請地方主管機關備查，所有人應檢送運送計畫備查並告知受託運送人納入契約。",
 "Who must prepare a site hazard prevention and response plan, and who a transport plan?",
 ["Manufacturers, importers, sellers, users and storers whose daily quantity of a single toxic or hazardous concerned chemical at any site reaches the graded threshold; owners who transport, themselves or by contract, in cases requiring a general transport form","Manufacturers, importers, sellers, users and storers handling any quantity of Class 1 toxic chemicals at any site; drivers who carry any quantity of toxic chemicals by vehicle","Manufacturers and importers with annual operation of a single toxic chemical of 100 tonnes or more; owners who contract transport without a written contract","Manufacturers and users handling two or more toxic chemicals at one site; carriers transporting Class 3 toxic chemicals across two or more municipalities"],
 "Articles 2 and 6."),

(TP,"第3條",3,"毒化應變計畫-內容與演練",
 "廠（場）危害預防及應變計畫之災害防救訓練演練，無預警測試每年至少幾次？整體演練每年至少幾次？運作人應每幾年檢討計畫內容？",
 ["無預警測試每年至少二次，整體演練每年至少一次，每二年檢討計畫內容","無預警測試每年至少一次，整體演練每年至少二次，每三年檢討計畫內容","無預警測試每年至少四次，整體演練每半年至少一次，每年檢討計畫內容","無預警測試每季至少一次，整體演練每二年至少一次，每五年檢討計畫內容"],"a",
 "第3條：廠（場）計畫內容包括防災基本資料表、應變器材位置圖座落位置及敏感地區圖緊急疏散集結救援路線圖、危害預防（管理措施、事故預防、災害防救設備設施及第三類毒化物災害模擬分析、訓練演練教育宣導含無預警測試每年至少二次及整體演練每年至少一次、經費編列）、應變（指揮系統任務編組通報機制、警報發布、外部支援啟動、災害應變作為、人員搶救及災區隔離、環境復原、緊急疏散避難）。第4條：依附件計算商數大於一者另包含危害辨識控制失效後果消防防災緊急救護及場所外通報搶救復原疏散等，已提送製程安全評估報告或消防防護計畫者得代之。第7條：訓練演練紀錄保存三年；每二年檢討計畫；物質種類異動製程變更貯存方式容器變更運作總量變更致商數大於一者應於三十日內報請備查。第8條：發生事故應於半年內重新檢討報備。第9條：備查後十五日內隱匿個資公開於指定網站。",
 "Under a site hazard prevention and response plan, unannounced tests must be held at least how often, full drills at least how often, and the plan reviewed every:",
 ["At least twice a year, at least once a year, and reviewed every 2 years","At least once a year, at least twice a year, and reviewed every 3 years","At least four times a year, at least once every half year, and reviewed every year","At least once a quarter, at least once every 2 years, and reviewed every 5 years"],
 "Articles 3–4 and 7–9."),

# ---------- 毒性及關注化學物質專業技術管理人員設置及管理辦法（108/12/25） ----------
(TM,"第3條",3,"毒化專技人員-級別",
 "第一類至第三類毒性化學物質運作人設置專業技術管理人員之級別及人數規定為何？",
 ["單一物質任一日達一萬公噸或每年一百萬公噸以上者設甲乙級共二人以上（含甲級一人）；三百公噸以上未滿一萬公噸或每年九萬公噸以上者設甲級一人以上；達分級運作量未滿三百公噸者設乙級一人以上；單次公路運送氣體逾五十公斤液體逾一百公斤固體逾二百公斤者設丙級一人以上","單一物質任一日達五千公噸或每年五十萬公噸以上者設甲級二人以上；一百公噸以上未滿五千公噸者設甲級一人以上；達分級運作量未滿一百公噸者設丙級一人以上；單次公路運送氣體逾一百公斤液體逾二百公斤固體逾五百公斤者設乙級一人以上","單一物質任一日達一千公噸以上者設甲乙丙級各一人；三十公噸以上未滿一千公噸者設乙級一人以上；達分級運作量未滿三十公噸者由負責人兼任；單次公路運送任何數量者由駕駛人取得丙級證書","單一物質任一日達一萬公噸以上者設甲級三人以上；一千公噸以上未滿一萬公噸者設乙級二人以上；達分級運作量未滿一千公噸者設丙級一人以上；單次公路運送氣體逾二十公斤液體逾五十公斤固體逾一百公斤者設甲級一人以上"],"a",
 "第2條：專業技術管理人員分甲乙丙級，由中央主管機關訓練合格取得證書者擔任。第3條：單一物質製造使用貯存任一日達一萬公噸以上或每年達一百萬公噸以上者設甲乙級共二人以上其中至少一人甲級；任一日三百公噸以上未滿一萬公噸或每年九萬公噸以上未滿一百萬公噸者設甲級一人以上；任一日達分級運作量以上未滿三百公噸者設乙級一人以上；單次公路運送常溫常壓氣體逾五十公斤液體逾一百公斤固體逾二百公斤者設丙級一人以上；得由較高級別者為之，同時符合者依最高級別設置。第6條：應常駐專職；運作第一二類液體未滿十公噸固體未滿三百公噸者廠務主管或負責人得兼任乙級，得兼任丙級。第10、11條：離職異動代理不超過三個月（非離職者經核准可延至六個月）。",
 "Grades and numbers of professional technical managers required of Class 1–3 toxic chemical operators are:",
 ["10,000 t+ on any day or 1,000,000 t+/year: two or more Class A/B including one Class A; 300 t to under 10,000 t (or 90,000 t+/year): one or more Class A; graded threshold to under 300 t: one or more Class B; single road shipments over 50 kg gas, 100 kg liquid or 200 kg solid: one or more Class C","5,000 t+ on any day or 500,000 t+/year: two or more Class A; 100 t to under 5,000 t: one or more Class A; graded threshold to under 100 t: one or more Class C; single road shipments over 100 kg gas, 200 kg liquid or 500 kg solid: one or more Class B","1,000 t+ on any day: one each of Class A, B and C; 30 t to under 1,000 t: one or more Class B; graded threshold to under 30 t: the owner doubles as manager; any road shipment: the driver holds a Class C certificate","10,000 t+ on any day: three or more Class A; 1,000 t to under 10,000 t: two or more Class B; graded threshold to under 1,000 t: one or more Class C; single road shipments over 20 kg gas, 50 kg liquid or 100 kg solid: one or more Class A"],
 "Articles 2–3, 6, 10–11."),

(TM,"第12條",2,"毒化專技人員-業務",
 "甲、乙級毒化物專業技術管理人員應執行之業務為何？丙級？",
 ["依法製作運作及釋放量紀錄定期申報並保存、辦理容器包裝場所設施之毒性警語污染防制標示並備具安全資料表、其他製造使用貯存之污染防制及危害預防；丙級管理運送車輛即時追蹤系統並監督駕駛人隨車文件安全裝備及運送工具標示","每月向主管機關申報產品銷售量並保存五年、辦理員工健康檢查及作業環境監測、訂定消防防護計畫並每年演練；丙級負責採購化學物質並驗收入庫及管理倉儲","每年編製環境會計報告並公開、辦理化學物質之進口報關及檢驗、負責廢棄物委託清理契約之簽訂；丙級負責運送車輛之保養維修並保存里程紀錄","依法辦理毒化物許可證之申請展延並繳納規費、辦理鄰近居民之溝通協調及補償、負責事故保險之投保；丙級負責運送路線之規劃並向警察機關報備"],"a",
 "第12條：甲乙級應依毒化法第9條及第26條就運作及釋放量製作紀錄定期申報並保存、依第17條及第27條辦理容器包裝運作場所及設施之管理並標示毒性警語及污染防制事項並備具安全資料表置於易取得處、其他製造使用貯存之污染防制及危害預防工作；兼有運送而未設丙級者由甲乙級辦理丙級業務。第13條：丙級管理運送車輛依第40條裝置之即時追蹤系統維持正常操作、監督運送駕駛人隨車攜帶文件備具安全裝備及懸掛黏貼運送工具標示、其他運送之污染防制及危害預防。第14、15條：運作人違反者依第59條第10款處罰，人員違反第8條或一年內二次未製作申報紀錄未標示未監督者依第62條處罰。",
 "Class A and B toxic chemical technical managers are responsible for, and Class C managers for:",
 ["Keeping and periodically reporting operation and release records, managing containers, packaging, sites and facilities with toxicity warnings and pollution control labels plus safety data sheets, and other prevention duties; Class C keeps vehicle tracking systems running and supervises drivers' documents, safety gear and vehicle markings","Reporting monthly product sales to the authority and keeping them five years, arranging employee health checks and workplace monitoring, and drafting fire protection plans with annual drills; Class C purchases chemicals, inspects deliveries and manages warehousing","Preparing annual environmental accounting reports for disclosure, handling customs clearance and testing of chemicals, and signing waste disposal contracts; Class C maintains transport vehicles and keeps mileage logs","Applying for and renewing toxic chemical permits and paying fees, coordinating with and compensating nearby residents, and arranging accident insurance; Class C plans transport routes and files them with the police"],
 "Articles 12–15."),
]
