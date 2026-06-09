import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="淋巴瘤路径导航器",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGES = ["首页", "路径导航", "分类图谱", "治疗方案库"]
STAGES = ["未确诊", "检查中", "已确诊", "治疗中"]

LYMPHOMA_TYPES = [
    {
        "type": "DLBCL（弥漫大B细胞淋巴瘤）",
        "lineage": "B细胞 NHL",
        "tempo": "侵袭性",
        "tempo_score": 4,
        "urgency": 4,
        "watchful": 1,
        "summary": "较常见的侵袭性 B 细胞淋巴瘤，通常需要尽快评估并启动治疗。",
        "prognosis": "很多患者对一线免疫化疗有反应，有机会获得长期缓解；IPI 评分、分期、LDH、体能状态和分子特征会影响预后。",
        "treatment": "常见为免疫化疗；复发/难治时可考虑二线化疗、移植、CAR-T、双特异性抗体或靶向药。",
        "drugs": "利妥昔单抗、环磷酰胺、多柔比星、长春新碱、泼尼松；部分方案会讨论泊洛妥珠单抗、CAR-T、双特异性抗体等。",
    },
    {
        "type": "滤泡性淋巴瘤（FL）",
        "lineage": "B细胞 NHL",
        "tempo": "惰性",
        "tempo_score": 2,
        "urgency": 2,
        "watchful": 4,
        "summary": "常见惰性类型，部分患者可在医生评估下先观察随访。",
        "prognosis": "通常病程较慢，可长期管理；早期局限病灶有机会通过局部治疗获得较好控制，晚期更强调长期随访和复发管理。",
        "treatment": "无症状低负荷时可观察；有治疗指征时可用抗 CD20 抗体、免疫化疗、放疗或靶向/双特异性抗体。",
        "drugs": "利妥昔单抗、奥妥珠单抗、苯达莫司汀、来那度胺；复发后可能讨论 tazemetostat、mosunetuzumab、epcoritamab 等。",
    },
    {
        "type": "边缘区淋巴瘤（MZL/MALT）",
        "lineage": "B细胞 NHL",
        "tempo": "惰性",
        "tempo_score": 2,
        "urgency": 2,
        "watchful": 3,
        "summary": "可发生于胃、眼附属器、唾液腺等结外部位，治疗与部位和分期有关。",
        "prognosis": "多为惰性，局限期常有较好控制机会；结外部位、感染因素和复发模式会影响治疗选择。",
        "treatment": "可根据部位选择根除感染、放疗、抗 CD20 抗体、免疫化疗或 BTK 抑制剂。",
        "drugs": "利妥昔单抗、苯达莫司汀、苯丁酸氮芥；常见靶向药包括泽布替尼、伊布替尼。胃 MALT 可能先处理幽门螺杆菌。",
    },
    {
        "type": "CLL/SLL",
        "lineage": "B细胞 NHL",
        "tempo": "惰性",
        "tempo_score": 1,
        "urgency": 1,
        "watchful": 5,
        "summary": "同一疾病的白血病/淋巴瘤表现，很多早期患者以观察为主。",
        "prognosis": "病程差异很大；部分患者多年无需治疗，TP53/IGHV 等分子因素会显著影响风险。",
        "treatment": "无症状早期常观察；出现治疗指征后以 BTK 抑制剂、BCL-2 抑制剂联合抗 CD20 抗体等为常见选择。",
        "drugs": "阿可替尼、泽布替尼、伊布替尼、维奈克拉、奥妥珠单抗、利妥昔单抗。",
    },
    {
        "type": "套细胞淋巴瘤（MCL）",
        "lineage": "B细胞 NHL",
        "tempo": "多为侵袭性",
        "tempo_score": 3,
        "urgency": 3,
        "watchful": 2,
        "summary": "相对少见，临床行为差异较大，需要专科团队综合判断。",
        "prognosis": "通常较难完全治愈，但治疗选择越来越多；少数惰性表现可先观察，TP53 异常等提示更高风险。",
        "treatment": "可用免疫化疗、阿糖胞苷强化方案、维持治疗；复发后常考虑 BTK 抑制剂、CAR-T 或临床试验。",
        "drugs": "利妥昔单抗、苯达莫司汀、阿糖胞苷、环磷酰胺、多柔比星；泽布替尼、阿可替尼、伊布替尼、brexucabtagene autoleucel。",
    },
    {
        "type": "伯基特淋巴瘤",
        "lineage": "B细胞 NHL",
        "tempo": "高度侵袭性",
        "tempo_score": 5,
        "urgency": 5,
        "watchful": 1,
        "summary": "进展很快，通常需要紧急评估和强化治疗。",
        "prognosis": "属于高度侵袭性但可治性淋巴瘤，尽快启动足量强化治疗很关键；年龄、分期、LDH 和中枢受累会影响风险。",
        "treatment": "通常需要短疗程、高强度、多药联合化疗，并进行中枢神经系统预防或治疗。",
        "drugs": "利妥昔单抗、环磷酰胺、长春新碱、多柔比星、甲氨蝶呤、阿糖胞苷、依托泊苷等。",
    },
    {
        "type": "原发性中枢神经系统淋巴瘤（PCNSL）",
        "lineage": "B细胞 NHL",
        "tempo": "侵袭性",
        "tempo_score": 4,
        "urgency": 5,
        "watchful": 1,
        "summary": "通常为发生在脑、眼、脑脊液或脊髓的 DLBCL，需要神经肿瘤/血液肿瘤团队评估。",
        "prognosis": "预后受年龄、体能状态、免疫状态、病灶范围和是否能耐受大剂量甲氨蝶呤影响；年轻、体能较好者通常治疗机会更多。",
        "treatment": "一线常以大剂量甲氨蝶呤为基础，可联合利妥昔单抗、阿糖胞苷、替莫唑胺、噻替哌等；部分患者会考虑巩固治疗、放疗或自体移植。",
        "drugs": "大剂量甲氨蝶呤、亚叶酸救援、利妥昔单抗、阿糖胞苷、替莫唑胺、噻替哌、丙卡巴肼、长春新碱；复发时可能讨论伊布替尼等。",
    },
    {
        "type": "经典霍奇金淋巴瘤",
        "lineage": "霍奇金淋巴瘤",
        "tempo": "多为可治性",
        "tempo_score": 3,
        "urgency": 3,
        "watchful": 1,
        "summary": "常见于年轻成人或老年人，治疗通常以化疗、放疗或免疫治疗组合为主。",
        "prognosis": "总体属于治愈率较高的淋巴瘤之一；分期、B 症状、肿块大小和治疗反应会影响预后。",
        "treatment": "常见为联合化疗，部分早期患者联合受累野放疗；复发/难治时可考虑移植、PD-1 抑制剂或 CD30 靶向治疗。",
        "drugs": "多柔比星、博来霉素、长春碱、达卡巴嗪；brentuximab vedotin、纳武利尤单抗、帕博利珠单抗。",
    },
    {
        "type": "结节性淋巴细胞为主型 HL",
        "lineage": "霍奇金淋巴瘤",
        "tempo": "相对惰性",
        "tempo_score": 2,
        "urgency": 2,
        "watchful": 3,
        "summary": "较少见，治疗策略常与惰性 B 细胞淋巴瘤思路相近。",
        "prognosis": "通常进展较慢、预后较好，但可复发，少数可转化为侵袭性 B 细胞淋巴瘤。",
        "treatment": "局限期可考虑放疗或手术后观察；进展期或复发时可使用抗 CD20 抗体或免疫化疗。",
        "drugs": "利妥昔单抗；部分情况使用 R-CHOP 或类似 B 细胞淋巴瘤方案。",
    },
    {
        "type": "外周 T 细胞淋巴瘤（PTCL）",
        "lineage": "T/NK细胞 NHL",
        "tempo": "侵袭性",
        "tempo_score": 4,
        "urgency": 4,
        "watchful": 1,
        "summary": "包括多个亚型，通常需要专科医生根据病理亚型制定方案。",
        "prognosis": "总体比许多 B 细胞淋巴瘤更具挑战，预后强烈依赖具体亚型、分期、IPI/PIT 风险和治疗反应。",
        "treatment": "常用 CHOP 或 CHOEP 类方案，部分患者缓解后讨论自体移植；复发后可用表观遗传药物、抗体药物或临床试验。",
        "drugs": "环磷酰胺、多柔比星、长春新碱、泼尼松、依托泊苷；普拉曲沙、罗米地辛、贝利司他、西达本胺、brentuximab vedotin。",
    },
    {
        "type": "间变性大细胞淋巴瘤（ALCL）",
        "lineage": "T/NK细胞 NHL",
        "tempo": "侵袭性",
        "tempo_score": 4,
        "urgency": 4,
        "watchful": 1,
        "summary": "T 细胞淋巴瘤中的重要亚型，ALK 状态会影响判断。",
        "prognosis": "ALK 阳性通常预后较好；ALK 阴性、年龄较大或高分期提示风险更高。",
        "treatment": "CD30 阳性患者常讨论 brentuximab vedotin 联合化疗；复发时可考虑靶向治疗、移植或临床试验。",
        "drugs": "brentuximab vedotin、环磷酰胺、多柔比星、泼尼松；ALK 阳性复发时可能讨论克唑替尼等 ALK 抑制剂。",
    },
    {
        "type": "皮肤 T 细胞淋巴瘤（MF/SS）",
        "lineage": "T/NK细胞 NHL",
        "tempo": "多为慢性",
        "tempo_score": 2,
        "urgency": 2,
        "watchful": 3,
        "summary": "常以皮肤病变为主要表现，分期和皮肤受累范围很重要。",
        "prognosis": "早期蕈样肉芽肿常进展慢、可长期控制；Sézary 综合征或血液/淋巴结受累提示风险更高。",
        "treatment": "早期以皮肤定向治疗为主；进展期可用全身治疗、光疗、放疗、免疫调节或靶向药。",
        "drugs": "外用激素、氮芥凝胶、贝沙罗汀、干扰素、莫格利珠单抗、brentuximab vedotin、伏立诺他、罗米地辛。",
    },
    {
        "type": "结外 NK/T 细胞淋巴瘤",
        "lineage": "T/NK细胞 NHL",
        "tempo": "侵袭性",
        "tempo_score": 4,
        "urgency": 4,
        "watchful": 1,
        "summary": "常与 EBV 相关，可累及鼻腔等结外部位，需要专科方案。",
        "prognosis": "风险与分期、EBV DNA、局部/全身受累和治疗反应相关；晚期或复发难治病例挑战较大。",
        "treatment": "局限期常用放疗联合含门冬酰胺酶方案；进展期常用非蒽环类、多药联合方案，复发时可考虑免疫治疗。",
        "drugs": "培门冬酶或 L-门冬酰胺酶、吉西他滨、奥沙利铂、地塞米松、依托泊苷；部分复发病例讨论 PD-1 抑制剂。",
    },
]

TREATMENT_DETAILS = {
    "DLBCL（弥漫大B细胞淋巴瘤）": {
        "prognosis_detail": "属于侵袭性但可治性淋巴瘤。预后常结合 IPI 评分、年龄、分期、LDH、体能状态、结外受累、MYC/BCL2/BCL6 等分子特征以及中期/结束治疗 PET-CT 反应判断。",
        "standard_treatment": "目标通常是治愈或长期缓解。标准思路是先完成病理分型、分期和风险评估，再用含抗 CD20 抗体的全身治疗；高危中枢受累风险者会单独评估 CNS 预防或检查。",
        "first_line": "常见一线为 R-CHOP；部分患者会讨论 pola-R-CHP。局限期可能缩短疗程并结合放疗；老年或体弱患者可能使用减量方案，如 R-mini-CHOP。",
        "second_line": "复发/难治时根据复发时间和身体条件选择。适合强化治疗者可用挽救化疗后自体移植；早期复发或原发难治可考虑 CAR-T。不能移植或后线治疗可讨论双特异性抗体、抗体药物偶联物、来那度胺、tafasitamab、selinexor 等。",
    },
    "滤泡性淋巴瘤（FL）": {
        "prognosis_detail": "多数为惰性、长期管理型疾病。预后与 FLIPI 风险、分期、肿瘤负荷、症状、治疗反应和是否转化为 DLBCL 有关。",
        "standard_treatment": "标准思路不是所有人立刻治疗。无症状、低肿瘤负荷者可观察；出现症状、器官压迫、血细胞减少、快速进展或高肿瘤负荷时再治疗。",
        "first_line": "局限期可考虑受累部位放疗。进展期有治疗指征时常见选择包括利妥昔单抗或奥妥珠单抗联合苯达莫司汀、CHOP 或 CVP；部分低负荷患者可用单药抗 CD20 抗体。",
        "second_line": "复发后看缓解持续时间和既往方案。可换用免疫化疗、来那度胺联合利妥昔单抗、EZH2 抑制剂 tazemetostat、PI3K/其他靶向药、双特异性抗体或 CAR-T；疑似转化时需重新活检。",
    },
    "边缘区淋巴瘤（MZL/MALT）": {
        "prognosis_detail": "多为惰性，局限期常可获得长期控制。预后与原发部位、分期、感染或自身免疫背景、是否转化有关。",
        "standard_treatment": "先确认部位和驱动因素。胃 MALT 常先检测并根除幽门螺杆菌；局限病灶可用放疗；系统性或有症状疾病用抗 CD20 抗体或免疫化疗。",
        "first_line": "可根据场景使用观察、抗感染治疗、局部放疗、利妥昔单抗单药，或利妥昔单抗联合苯达莫司汀/CVP/苯丁酸氮芥等。",
        "second_line": "复发/难治时可考虑 BTK 抑制剂，如泽布替尼、伊布替尼，或换用免疫化疗、临床试验；局部复发仍可能使用局部治疗。",
    },
    "CLL/SLL": {
        "prognosis_detail": "病程差异很大。TP53 缺失/突变、IGHV 未突变、复杂核型、β2 微球蛋白、分期和淋巴细胞倍增速度都会影响风险。",
        "standard_treatment": "早期无症状通常观察，不因白细胞高就自动治疗。达到 iwCLL 治疗指征，如进行性贫血/血小板低、巨大或进展性淋巴结/脾大、明显 B 症状时再启动治疗。",
        "first_line": "现代一线常见为 BTK 抑制剂，如阿可替尼、泽布替尼、伊布替尼，或维奈克拉联合奥妥珠单抗。年轻且特定低风险患者在部分地区仍可能讨论 FCR，但已少于靶向方案。",
        "second_line": "复发后通常换用不同机制：既往 BTK 抑制剂后可用维奈克拉方案；既往维奈克拉后可用 BTK 抑制剂。多线后可考虑非共价 BTK 抑制剂、CAR-T 或临床试验。",
    },
    "套细胞淋巴瘤（MCL）": {
        "prognosis_detail": "多数为反复复发的侵袭性或中间型病程，少数白血病样非结节型可较惰性。MIPI、Ki-67、TP53 状态和治疗反应很关键。",
        "standard_treatment": "先区分是否需要立即治疗、是否适合强化方案。年轻体能好者常考虑含阿糖胞苷强化诱导和巩固；不适合强化者用较温和免疫化疗或靶向方案。",
        "first_line": "常见一线包括 BR、R-CHOP/R-DHAP 交替或 Nordic 类强化方案；适合者可自体移植巩固，并用利妥昔单抗维持。",
        "second_line": "复发后常用 BTK 抑制剂，如泽布替尼、阿可替尼、伊布替尼；后线可考虑 CAR-T、维奈克拉联合方案、非共价 BTK 抑制剂或临床试验。",
    },
    "伯基特淋巴瘤": {
        "prognosis_detail": "高度侵袭性但对强化治疗敏感。年龄、LDH、分期、肿瘤负荷、肾功能和中枢神经系统受累会影响风险。",
        "standard_treatment": "标准思路是紧急处理，高强度、多药、短疗程方案，并同时预防或治疗中枢神经系统受累；需严密处理肿瘤溶解综合征风险。",
        "first_line": "常见方案包括 CODOX-M/IVAC、DA-EPOCH-R 或 HyperCVAD/MA 等，常含利妥昔单抗、环磷酰胺、长春新碱、多柔比星、甲氨蝶呤、阿糖胞苷等。",
        "second_line": "复发/难治较困难，常需专科中心评估。可考虑挽救化疗、移植、CAR-T 或临床试验，具体依赖既往治疗和缓解情况。",
    },
    "原发性中枢神经系统淋巴瘤（PCNSL）": {
        "prognosis_detail": "预后与年龄、行动能力/体能状态、免疫状态、脑深部结构受累、脑脊液/眼受累、LDH 和是否能耐受大剂量甲氨蝶呤密切相关。年轻、KPS 较高或 ECOG 较低、能接受强化巩固者通常选择更多。",
        "functional_assessment": "有。PCNSL 常记录 ECOG/WHO 体能状态或 Karnofsky Performance Status（KPS）。一般可粗略理解为：ECOG 0-1 分或 KPS 70 分及以上，表示能自理、可进行多数日常活动；ECOG 2 分及以上或 KPS 低于 70 分，表示行动/自理能力受限，治疗强度和预后判断会受影响。IELSG 预后评分把 ECOG 超过 1 分或 KPS 低于 70 分作为不良因素之一；MSKCC 预后模型则主要看年龄和 KPS，将年龄 50 岁及以上且 KPS 低于 70 分归为更高风险组。",
        "standard_treatment": "标准思路是以能穿透中枢神经系统的大剂量甲氨蝶呤为核心，避免单纯按普通 DLBCL 的 R-CHOP 思路治疗。治疗需要监测肾功能、甲氨蝶呤清除和神经毒性。",
        "first_line": "常见一线为大剂量甲氨蝶呤为基础的联合方案，如 HD-MTX 联合利妥昔单抗、阿糖胞苷、替莫唑胺、丙卡巴肼、长春新碱或噻替哌。适合者可用自体移植或低剂量/延迟放疗等巩固策略。",
        "second_line": "复发/难治时可考虑再次使用 HD-MTX（若既往反应好且间隔较长）、阿糖胞苷/噻替哌类挽救方案、自体移植、全脑放疗、BTK 抑制剂如伊布替尼、免疫调节药或临床试验。",
    },
    "经典霍奇金淋巴瘤": {
        "prognosis_detail": "总体治愈率较高。预后受分期、B 症状、巨大肿块、血液指标、年龄和 PET 早期反应影响。",
        "standard_treatment": "标准思路按早期有利、早期不利和晚期分层，结合 PET 反应调整治疗强度，尽量兼顾治愈和减少远期毒性。",
        "first_line": "常见一线包括 ABVD；部分晚期或高风险患者会讨论 brentuximab vedotin 加 AVD 或 escalated BEACOPP。早期患者常结合受累部位放疗。",
        "second_line": "复发/难治时常用挽救化疗后自体移植。后线可用 brentuximab vedotin、PD-1 抑制剂如纳武利尤单抗或帕博利珠单抗，部分患者考虑异基因移植或临床试验。",
    },
    "结节性淋巴细胞为主型 HL": {
        "prognosis_detail": "通常预后较好、病程偏慢，但复发可较晚出现，少数可转化为侵袭性 B 细胞淋巴瘤。",
        "standard_treatment": "标准思路更接近 CD20 阳性惰性 B 细胞淋巴瘤，需要根据局限期、进展期和是否有转化风险选择治疗。",
        "first_line": "局限期可用放疗，部分极局限病灶可手术后观察；进展期或症状性疾病可用利妥昔单抗单药或 R-CHOP/R-CVP 等。",
        "second_line": "复发后可再次局部治疗、利妥昔单抗或免疫化疗；若转化为 DLBCL，则按侵袭性 B 细胞淋巴瘤治疗。",
    },
    "外周 T 细胞淋巴瘤（PTCL）": {
        "prognosis_detail": "多数亚型预后较 B 细胞淋巴瘤差，且异质性很强。具体亚型、IPI/PIT、分期、LDH、年龄、体能状态和是否完全缓解决定风险。",
        "standard_treatment": "标准思路是尽量获得完全缓解，并在合适患者中考虑一线缓解后的自体移植巩固；强烈建议在专科中心评估临床试验。",
        "first_line": "常见一线为 CHOP 或 CHOEP。CD30 阳性 PTCL，特别是 ALCL，可考虑 brentuximab vedotin 联合 CHP。",
        "second_line": "复发/难治时可用普拉曲沙、罗米地辛、贝利司他、西达本胺、吉西他滨类方案、brentuximab vedotin（CD30 阳性）或移植/临床试验。",
    },
    "间变性大细胞淋巴瘤（ALCL）": {
        "prognosis_detail": "ALK 阳性通常比 ALK 阴性预后更好。系统性 ALCL 与原发皮肤 ALCL 是不同临床场景，不能简单混在一起判断。",
        "standard_treatment": "系统性 ALCL 按侵袭性 T 细胞淋巴瘤治疗；原发皮肤 ALCL 若局限，常以局部治疗为主。",
        "first_line": "系统性 CD30 阳性 ALCL 常见一线为 brentuximab vedotin 联合 CHP；也可用 CHOP/CHOEP。局限皮肤病灶可手术或放疗。",
        "second_line": "复发/难治可用 brentuximab vedotin（若未用过或仍适合）、ALK 抑制剂如克唑替尼（ALK 阳性）、挽救化疗、移植或临床试验。",
    },
    "皮肤 T 细胞淋巴瘤（MF/SS）": {
        "prognosis_detail": "早期 MF 常可长期控制；肿瘤期、红皮病、血液受累或 Sézary 综合征提示更高风险。",
        "standard_treatment": "标准思路按皮肤局限程度和是否有血液/淋巴结/内脏受累分层，早期优先皮肤定向治疗，进展期再用全身治疗。",
        "first_line": "早期常用外用激素、氮芥凝胶、光疗、局部放疗、全皮肤电子束等。进展期可用贝沙罗汀、干扰素、体外光分离疗法（ECP）等。",
        "second_line": "复发/进展可考虑莫格利珠单抗、brentuximab vedotin（CD30 阳性）、伏立诺他、罗米地辛、吉西他滨、脂质体多柔比星或临床试验。",
    },
    "结外 NK/T 细胞淋巴瘤": {
        "prognosis_detail": "预后与分期、局部侵犯、EBV DNA、LDH、全身炎症状态和治疗反应相关。晚期和复发难治病例风险较高。",
        "standard_treatment": "标准思路避免单纯蒽环类 CHOP，因为效果通常不理想；常采用放疗联合含门冬酰胺酶的方案，并监测 EBV DNA。",
        "first_line": "局限期常见为放疗联合含培门冬酶/L-门冬酰胺酶方案，如 DDGP、SMILE、P-GEMOX 等。进展期常用系统性含门冬酰胺酶多药方案。",
        "second_line": "复发/难治可考虑 PD-1 抑制剂、挽救化疗、造血干细胞移植或临床试验，需专科中心评估。",
    },
}

TREATMENT_LIBRARY = {
    "hd-mtx": {
        "name": "HD-MTX（大剂量甲氨蝶呤）",
        "aliases": ["HD-MTX", "大剂量甲氨蝶呤", "甲氨蝶呤"],
        "category": "中枢穿透化疗",
        "summary": "PCNSL 等中枢神经系统相关淋巴瘤治疗的核心药物之一，需要住院、补液碱化、血药浓度监测和亚叶酸救援。",
        "used_for": "原发性中枢神经系统淋巴瘤、部分高危或中枢受累淋巴瘤。",
        "what_it_includes": "甲氨蝶呤大剂量静脉给药；通常配合水化、尿液碱化、亚叶酸救援，并监测甲氨蝶呤清除。",
        "how_it_is_given": "多在住院环境完成。医生会根据肾功能、年龄、体能状态和合并用药调整剂量与支持治疗。",
        "monitoring": "肾功能、肝功能、血常规、黏膜炎、药物相互作用、甲氨蝶呤血药浓度和神经系统症状。",
        "side_effects": "口腔黏膜炎、骨髓抑制、肝肾功能异常、感染风险、恶心、皮疹；清除延迟时风险更高。",
        "sources": [
            ("NCI PCNSL Treatment PDQ", "https://www.cancer.gov/types/lymphoma/hp/primary-cns-lymphoma-treatment-pdq"),
            ("NCI Methotrexate Drug Dictionary", "https://www.cancer.gov/publications/dictionaries/cancer-drug/def/methotrexate"),
        ],
    },
    "r-chop": {
        "name": "R-CHOP",
        "aliases": ["R-CHOP", "R-mini-CHOP"],
        "category": "免疫化疗",
        "summary": "经典 B 细胞淋巴瘤免疫化疗方案，常用于 DLBCL 等。R 代表利妥昔单抗，CHOP 代表四个化疗/激素成分。",
        "used_for": "DLBCL、部分滤泡性淋巴瘤、边缘区淋巴瘤、套细胞淋巴瘤、NLPHL 等场景。",
        "what_it_includes": "利妥昔单抗、环磷酰胺、多柔比星、长春新碱、泼尼松。",
        "how_it_is_given": "通常按周期给药，周期数取决于病种、分期、疗效评估和耐受性。",
        "monitoring": "血常规、感染风险、心功能、周围神经病变、肝肾功能、乙肝筛查/再激活风险。",
        "side_effects": "骨髓抑制、感染、脱发、恶心、乏力、周围神经病变、心脏毒性风险、激素相关反应。",
        "sources": [
            ("NCI R-CHOP", "https://www.cancer.gov/about-cancer/treatment/drugs/r-chop"),
            ("NCI R-CHOP Regimen Dictionary", "https://www.cancer.gov/publications/dictionaries/cancer-drug/def/r-chop-regimen"),
        ],
    },
    "pola-r-chp": {
        "name": "pola-R-CHP",
        "aliases": ["pola-R-CHP", "泊洛妥珠单抗"],
        "category": "抗体药物偶联物联合免疫化疗",
        "summary": "在 R-CHOP 骨架中用泊洛妥珠单抗替代长春新碱的一类方案，部分 DLBCL 患者会被讨论。",
        "used_for": "部分新诊断 DLBCL 或高级别 B 细胞淋巴瘤场景，需由专科医生按风险和可及性判断。",
        "what_it_includes": "泊洛妥珠单抗、利妥昔单抗、环磷酰胺、多柔比星、泼尼松。",
        "how_it_is_given": "按周期静脉治疗，常需联合预防感染和血象支持策略。",
        "monitoring": "血常规、感染、周围神经病变、肝功能、输注反应和心功能。",
        "side_effects": "中性粒细胞减少、感染、周围神经病变、乏力、恶心、脱发等。",
        "sources": [
            ("NCI Polatuzumab Vedotin Drug Dictionary", "https://www.cancer.gov/publications/dictionaries/cancer-drug/def/polatuzumab-vedotin"),
            ("NCI Aggressive B-Cell NHL PDQ", "https://www.cancer.gov/types/lymphoma/hp/aggressive-b-cell-lymphoma-treatment-pdq"),
        ],
    },
    "car-t": {
        "name": "CAR-T 细胞治疗",
        "aliases": ["CAR-T"],
        "category": "细胞治疗",
        "summary": "采集患者 T 细胞，经工程化改造后回输，让其识别肿瘤细胞。常用于部分复发/难治 B 细胞淋巴瘤。",
        "used_for": "复发/难治 DLBCL、滤泡性淋巴瘤、套细胞淋巴瘤等部分适应证。",
        "what_it_includes": "白细胞采集、细胞制造、桥接治疗评估、淋巴清除化疗、CAR-T 回输和严密观察。",
        "how_it_is_given": "通常在有经验的中心完成。回输后需监测 CRS 和 ICANS 等免疫相关毒性。",
        "monitoring": "发热、低血压、缺氧、神经系统症状、感染、血细胞减少、免疫球蛋白水平。",
        "side_effects": "细胞因子释放综合征（CRS）、神经毒性（ICANS）、感染、长期血细胞减少、低免疫球蛋白。",
        "sources": [
            ("NCI CAR T Cells", "https://www.cancer.gov/about-cancer/treatment/research/car-t-cells"),
            ("NCI T-cell Transfer Therapy", "https://www.cancer.gov/about-cancer/treatment/types/immunotherapy/t-cell-transfer-therapy"),
        ],
    },
    "autologous-transplant": {
        "name": "自体造血干细胞移植",
        "aliases": ["自体移植", "自体造血干细胞移植"],
        "category": "巩固/挽救治疗",
        "summary": "先采集患者自己的造血干细胞，再给予大剂量化疗，随后回输干细胞帮助骨髓恢复。",
        "used_for": "部分复发敏感 DLBCL、MCL 一线巩固、PCNSL 巩固、霍奇金淋巴瘤复发后等。",
        "what_it_includes": "动员采集、自体干细胞冻存、大剂量预处理化疗、干细胞回输、感染和血象支持。",
        "how_it_is_given": "通常需要住院或移植中心密切管理，适合性取决于年龄、体能、器官功能和疾病控制情况。",
        "monitoring": "感染、出血、黏膜炎、肝肾功能、营养、血象恢复和长期复发风险。",
        "side_effects": "短期骨髓抑制、感染、口腔/胃肠黏膜炎、乏力；长期可能有生育、二次肿瘤或器官毒性问题。",
        "sources": [
            ("NCI Adult NHL Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-nhl-treatment-pdq"),
            ("NCI Stem Cell Transplant", "https://www.cancer.gov/about-cancer/treatment/types/stem-cell-transplant"),
        ],
    },
    "allogeneic-transplant": {
        "name": "异基因造血干细胞移植",
        "aliases": ["异基因移植", "异基因造血干细胞移植"],
        "category": "高风险后线治疗",
        "summary": "使用供者造血干细胞重建造血和免疫系统，风险更高，通常只在特定复发/难治或高危场景讨论。",
        "used_for": "部分复发/难治 T 细胞淋巴瘤、霍奇金淋巴瘤、NK/T 细胞淋巴瘤等。",
        "what_it_includes": "供者匹配、预处理、供者干细胞回输、免疫抑制、移植物抗宿主病预防和长期随访。",
        "how_it_is_given": "需要移植中心系统评估，不是多数患者的常规早期治疗。",
        "monitoring": "感染、移植物抗宿主病、复发、器官毒性、免疫重建和长期生活质量。",
        "side_effects": "严重感染、GVHD、器官损伤、治疗相关死亡风险、长期免疫抑制相关问题。",
        "sources": [
            ("NCI Stem Cell Transplant", "https://www.cancer.gov/about-cancer/treatment/types/stem-cell-transplant"),
            ("NCI Adult NHL Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-nhl-treatment-pdq"),
        ],
    },
    "anti-cd20": {
        "name": "抗 CD20 单抗",
        "aliases": ["利妥昔单抗", "奥妥珠单抗", "抗 CD20"],
        "category": "靶向免疫治疗",
        "summary": "针对 B 细胞表面 CD20 的抗体，是许多 B 细胞淋巴瘤方案的基础成分。",
        "used_for": "DLBCL、FL、MZL、MCL、CLL/SLL、NLPHL 等 CD20 阳性疾病。",
        "what_it_includes": "常见药物包括利妥昔单抗、奥妥珠单抗等，可单用或联合化疗/靶向药。",
        "how_it_is_given": "静脉或皮下注射形式取决于药物和地区可及性，首次用药需关注输注反应。",
        "monitoring": "乙肝筛查、输注反应、感染风险、免疫球蛋白水平、血常规。",
        "side_effects": "发热寒战、皮疹、低血压、感染风险、乙肝再激活、罕见严重皮肤或神经系统反应。",
        "sources": [
            ("NCI Rituximab", "https://www.cancer.gov/about-cancer/treatment/drugs/rituximab"),
            ("NCI Obinutuzumab", "https://www.cancer.gov/about-cancer/treatment/drugs/obinutuzumab"),
        ],
    },
    "btk-inhibitor": {
        "name": "BTK 抑制剂",
        "aliases": ["BTK", "泽布替尼", "阿可替尼", "伊布替尼"],
        "category": "口服靶向药",
        "summary": "阻断 B 细胞受体信号通路，常用于 CLL/SLL、MCL、MZL 等 B 细胞淋巴瘤。",
        "used_for": "CLL/SLL、套细胞淋巴瘤、边缘区淋巴瘤，PCNSL 复发时也可能讨论伊布替尼。",
        "what_it_includes": "伊布替尼、阿可替尼、泽布替尼等。",
        "how_it_is_given": "多为口服连续用药，需注意合并用药和出血/心律风险。",
        "monitoring": "出血风险、房颤或心律问题、血压、感染、血细胞计数、药物相互作用。",
        "side_effects": "腹泻、皮疹、出血倾向、感染、房颤/高血压风险、肌肉关节痛。",
        "sources": [
            ("NCI Ibrutinib", "https://www.cancer.gov/about-cancer/treatment/drugs/ibrutinib"),
            ("NCI Zanubrutinib", "https://www.cancer.gov/about-cancer/treatment/drugs/zanubrutinib"),
        ],
    },
    "venetoclax": {
        "name": "维奈克拉（BCL-2 抑制剂）",
        "aliases": ["维奈克拉", "venetoclax", "BCL-2"],
        "category": "口服靶向药",
        "summary": "通过抑制 BCL-2 促进肿瘤细胞凋亡，常用于 CLL/SLL，也会在部分 MCL 等场景讨论。",
        "used_for": "CLL/SLL，部分复发/难治 MCL 或联合方案研究。",
        "what_it_includes": "维奈克拉单药或联合抗 CD20 抗体等。",
        "how_it_is_given": "通常需要逐步加量以降低肿瘤溶解综合征风险。",
        "monitoring": "肿瘤溶解综合征、肾功能、电解质、血常规、感染。",
        "side_effects": "中性粒细胞减少、感染、腹泻、恶心、贫血、肿瘤溶解综合征。",
        "sources": [
            ("NCI Venetoclax", "https://www.cancer.gov/about-cancer/treatment/drugs/venetoclax"),
            ("NCI CLL Treatment PDQ", "https://www.cancer.gov/types/leukemia/patient/cll-treatment-pdq"),
        ],
    },
    "bendamustine": {
        "name": "苯达莫司汀联合方案（BR 等）",
        "aliases": ["苯达莫司汀", "BR"],
        "category": "免疫化疗",
        "summary": "苯达莫司汀常与利妥昔单抗或奥妥珠单抗联合，用于多种惰性 B 细胞淋巴瘤和 MCL。",
        "used_for": "FL、MZL、MCL、部分 CLL/SLL 等。",
        "what_it_includes": "苯达莫司汀加抗 CD20 单抗时常称 BR 或 obinutuzumab-bendamustine。",
        "how_it_is_given": "按周期静脉治疗，方案强度和周期数由医生按病种和耐受性决定。",
        "monitoring": "血常规、感染、皮疹、肝肾功能、乙肝筛查、长期免疫抑制。",
        "side_effects": "骨髓抑制、感染、乏力、恶心、皮疹、发热。",
        "sources": [
            ("NCI Bendamustine", "https://www.cancer.gov/about-cancer/treatment/drugs/bendamustinehydrochloride"),
            ("NCI Adult NHL Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-nhl-treatment-pdq"),
        ],
    },
    "abvd": {
        "name": "ABVD",
        "aliases": ["ABVD"],
        "category": "霍奇金淋巴瘤化疗",
        "summary": "经典霍奇金淋巴瘤常用一线方案之一。",
        "used_for": "经典霍奇金淋巴瘤。",
        "what_it_includes": "多柔比星、博来霉素、长春碱、达卡巴嗪。",
        "how_it_is_given": "按周期给药，常结合 PET 反应和分期决定疗程及是否加放疗。",
        "monitoring": "肺功能/呼吸症状、心功能、血常规、感染、周围神经病变、恶心乏力。",
        "side_effects": "骨髓抑制、感染、恶心、脱发、肺毒性风险、心脏毒性风险、神经病变。",
        "sources": [
            ("NCI ABVD", "https://www.cancer.gov/about-cancer/treatment/drugs/abvd"),
            ("NCI Hodgkin Lymphoma Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-hodgkin-treatment-pdq"),
        ],
    },
    "chop-choep": {
        "name": "CHOP / CHOEP",
        "aliases": ["CHOP", "CHOEP"],
        "category": "T 细胞淋巴瘤常用化疗骨架",
        "summary": "CHOP 是多种淋巴瘤常见化疗骨架；CHOEP 是在 CHOP 基础上加入依托泊苷。",
        "used_for": "PTCL、ALCL，以及部分 B 细胞淋巴瘤联合抗 CD20 后形成 R-CHOP。",
        "what_it_includes": "CHOP：环磷酰胺、多柔比星、长春新碱、泼尼松；CHOEP 另加依托泊苷。",
        "how_it_is_given": "按周期给药，是否加依托泊苷取决于年龄、体能、亚型和医生判断。",
        "monitoring": "血常规、感染、心功能、周围神经病变、肝肾功能、恶心和脱发。",
        "side_effects": "骨髓抑制、感染、脱发、恶心、乏力、神经病变、心脏毒性风险。",
        "sources": [
            ("NCI CHOP", "https://www.cancer.gov/about-cancer/treatment/drugs/chop"),
            ("NCI Adult NHL Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-nhl-treatment-pdq"),
        ],
    },
    "pd-1": {
        "name": "PD-1 抑制剂",
        "aliases": ["PD-1", "纳武利尤单抗", "帕博利珠单抗"],
        "category": "免疫检查点抑制剂",
        "summary": "解除免疫刹车，让 T 细胞更容易攻击肿瘤。常在复发/难治霍奇金淋巴瘤和部分 NK/T 细胞淋巴瘤中讨论。",
        "used_for": "复发/难治经典霍奇金淋巴瘤、部分结外 NK/T 细胞淋巴瘤等。",
        "what_it_includes": "常见药物包括纳武利尤单抗、帕博利珠单抗等。",
        "how_it_is_given": "静脉给药，治疗期间需要关注免疫相关不良反应。",
        "monitoring": "甲状腺、肝肺肾、肠炎、皮疹、内分泌异常、免疫性肺炎等。",
        "side_effects": "皮疹、腹泻、肝炎、肺炎、甲状腺异常、乏力；严重免疫毒性需及时处理。",
        "sources": [
            ("NCI Nivolumab", "https://www.cancer.gov/about-cancer/treatment/drugs/nivolumab"),
            ("NCI Pembrolizumab", "https://www.cancer.gov/about-cancer/treatment/drugs/pembrolizumab"),
        ],
    },
    "brentuximab": {
        "name": "Brentuximab Vedotin（CD30 ADC）",
        "aliases": ["brentuximab vedotin", "CD30"],
        "category": "抗体药物偶联物",
        "summary": "靶向 CD30 的抗体药物偶联物，常用于经典霍奇金淋巴瘤和 CD30 阳性 T 细胞淋巴瘤相关场景。",
        "used_for": "经典霍奇金淋巴瘤、ALCL、部分 CD30 阳性 PTCL 或 CTCL。",
        "what_it_includes": "抗 CD30 抗体与细胞毒药物 MMAE 偶联。",
        "how_it_is_given": "静脉给药，可单用或与化疗联合，具体取决于病种和线数。",
        "monitoring": "周围神经病变、血常规、感染、肝功能、输注反应。",
        "side_effects": "周围神经病变、乏力、恶心、感染、血细胞减少、皮疹。",
        "sources": [
            ("NCI Brentuximab Vedotin", "https://www.cancer.gov/about-cancer/treatment/drugs/brentuximabvedotin"),
            ("NCI Hodgkin Lymphoma Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-hodgkin-treatment-pdq"),
        ],
    },
    "radiation": {
        "name": "放疗",
        "aliases": ["放疗", "全脑放疗", "局部放疗", "受累部位放疗"],
        "category": "局部治疗",
        "summary": "用高能射线控制局部病灶，可用于局限期、残留病灶、症状缓解或特定中枢/皮肤场景。",
        "used_for": "局限期 FL/MZL/HL，PCNSL 巩固或复发，全皮肤电子束治疗 CTCL 等。",
        "what_it_includes": "受累部位放疗、全脑放疗、全皮肤电子束等不同形式。",
        "how_it_is_given": "通常分多次完成，剂量和范围由放疗科按病种、部位和治疗目标规划。",
        "monitoring": "局部皮肤/黏膜反应、疲劳、器官特异毒性、长期二次肿瘤和认知影响风险。",
        "side_effects": "疲劳、皮肤反应、局部炎症；脑部放疗需关注认知和神经毒性。",
        "sources": [
            ("NCI Radiation Therapy", "https://www.cancer.gov/about-cancer/treatment/types/radiation-therapy"),
            ("NCI Adult NHL Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-nhl-treatment-pdq"),
        ],
    },
    "bispecific": {
        "name": "双特异性抗体",
        "aliases": ["双特异性抗体", "mosunetuzumab", "epcoritamab"],
        "category": "免疫治疗",
        "summary": "同时连接 T 细胞和肿瘤细胞，帮助免疫系统攻击淋巴瘤，常用于部分复发/难治 B 细胞淋巴瘤。",
        "used_for": "复发/难治 FL、DLBCL 等部分 B 细胞淋巴瘤。",
        "what_it_includes": "例如 mosunetuzumab、epcoritamab、glofitamab 等，适应证随地区和时间变化。",
        "how_it_is_given": "多采用递增剂量或分步给药以降低 CRS 风险。",
        "monitoring": "CRS、神经毒性、感染、血细胞减少、低免疫球蛋白。",
        "side_effects": "发热、CRS、感染、乏力、血细胞减少、注射/输注反应。",
        "sources": [
            ("NCI Epcoritamab", "https://www.cancer.gov/about-cancer/treatment/drugs/epcoritamab-bysp"),
            ("NCI Mosunetuzumab", "https://www.cancer.gov/about-cancer/treatment/drugs/mosunetuzumab-axgb"),
        ],
    },
    "asparaginase": {
        "name": "含门冬酰胺酶方案",
        "aliases": ["门冬酰胺酶", "培门冬酶", "L-门冬酰胺酶", "DDGP", "SMILE", "P-GEMOX"],
        "category": "NK/T 细胞淋巴瘤方案",
        "summary": "结外 NK/T 细胞淋巴瘤常用的重要药物类别，常与放疗或其他化疗药联合。",
        "used_for": "结外 NK/T 细胞淋巴瘤。",
        "what_it_includes": "培门冬酶或 L-门冬酰胺酶，可组合成 DDGP、SMILE、P-GEMOX 等方案。",
        "how_it_is_given": "按方案周期给药，常需监测凝血、肝胰功能和过敏反应。",
        "monitoring": "肝功能、胰腺炎、凝血功能、血糖、过敏反应、感染。",
        "side_effects": "过敏、胰腺炎、肝功能异常、凝血异常、血糖升高、感染。",
        "sources": [
            ("NCI Adult NHL Treatment PDQ", "https://www.cancer.gov/types/lymphoma/patient/adult-nhl-treatment-pdq"),
            ("NCI Asparaginase Drug Dictionary", "https://www.cancer.gov/publications/dictionaries/cancer-drug/def/asparaginase"),
        ],
    },
}

DRUG_LIBRARY = {
    "methotrexate": {
        "name": "甲氨蝶呤（MTX）",
        "effect": "抗代谢化疗药，干扰叶酸代谢和 DNA 合成；大剂量时可进入中枢神经系统，是 PCNSL 的核心药物。",
        "common_uses": "PCNSL、CNS 受累或预防、部分高强度淋巴瘤方案。",
        "side_effects": "口腔黏膜炎、骨髓抑制、感染风险、肝肾功能异常、恶心、皮疹；清除延迟时毒性会明显增加。",
        "monitoring": "甲氨蝶呤血药浓度、肾功能、尿液碱化/水化、血常规、肝功能、药物相互作用。",
    },
    "leucovorin": {
        "name": "亚叶酸（Leucovorin）",
        "effect": "不是抗癌药本身，而是 MTX 后的“救援”药，用来帮助正常细胞从叶酸通路抑制中恢复。",
        "common_uses": "大剂量甲氨蝶呤治疗后的救援支持。",
        "side_effects": "通常耐受较好；少数可有胃肠不适、皮疹或过敏反应。",
        "monitoring": "按 MTX 浓度和肾功能调整救援时间和剂量。",
    },
    "rituximab": {
        "name": "利妥昔单抗",
        "effect": "抗 CD20 单抗，帮助免疫系统识别并清除 CD20 阳性 B 细胞。",
        "common_uses": "DLBCL、FL、MZL、MCL、CLL/SLL、NLPHL 等 CD20 阳性 B 细胞淋巴瘤。",
        "side_effects": "输注反应、发热寒战、皮疹、低血压、感染风险、乙肝再激活；罕见严重皮肤反应或 PML。",
        "monitoring": "乙肝筛查、输注反应、血常规、感染、免疫球蛋白水平。",
    },
    "obinutuzumab": {
        "name": "奥妥珠单抗",
        "effect": "抗 CD20 单抗，作用目标与利妥昔单抗相近，可用于部分惰性 B 细胞淋巴瘤或 CLL/SLL 方案。",
        "common_uses": "FL、CLL/SLL 等。",
        "side_effects": "输注反应、感染、血细胞减少、乙肝再激活风险。",
        "monitoring": "乙肝筛查、输注反应、血常规、感染。",
    },
    "cyclophosphamide": {
        "name": "环磷酰胺",
        "effect": "烷化剂化疗药，通过损伤 DNA 杀伤快速分裂细胞。",
        "common_uses": "R-CHOP、CHOP/CHOEP、HyperCVAD 等多种淋巴瘤方案。",
        "side_effects": "骨髓抑制、感染、恶心、脱发、出血性膀胱炎、生育影响。",
        "monitoring": "血常规、尿路症状、水化、肝肾功能、感染。",
    },
    "doxorubicin": {
        "name": "多柔比星",
        "effect": "蒽环类化疗药，干扰 DNA 复制并造成 DNA 损伤。",
        "common_uses": "R-CHOP、CHOP/CHOEP、ABVD 等。",
        "side_effects": "骨髓抑制、脱发、恶心、口腔炎、心脏毒性风险、尿液短暂变红。",
        "monitoring": "心功能评估、累计剂量、血常规、肝功能。",
    },
    "bleomycin": {
        "name": "博来霉素",
        "effect": "抗肿瘤抗生素类化疗药，可造成 DNA 损伤，是 ABVD 的组成之一。",
        "common_uses": "经典霍奇金淋巴瘤 ABVD 方案。",
        "side_effects": "肺毒性风险、发热、皮肤色素沉着、口腔炎、过敏反应。",
        "monitoring": "咳嗽、气短、肺功能/影像、氧疗暴露风险、皮肤反应。",
    },
    "vinblastine": {
        "name": "长春碱",
        "effect": "长春花碱类化疗药，干扰微管形成并抑制细胞分裂。",
        "common_uses": "经典霍奇金淋巴瘤 ABVD 方案。",
        "side_effects": "骨髓抑制、便秘、神经病变、脱发、口腔炎。",
        "monitoring": "血常规、便秘、神经症状、感染。",
    },
    "dacarbazine": {
        "name": "达卡巴嗪",
        "effect": "烷化剂类化疗药，通过 DNA 损伤杀伤肿瘤细胞。",
        "common_uses": "经典霍奇金淋巴瘤 ABVD 方案。",
        "side_effects": "恶心呕吐、骨髓抑制、乏力、肝功能异常、光敏感。",
        "monitoring": "止吐支持、血常规、肝功能、感染。",
    },
    "vincristine": {
        "name": "长春新碱",
        "effect": "长春花碱类化疗药，干扰微管形成，使肿瘤细胞难以分裂。",
        "common_uses": "R-CHOP、CHOP、HyperCVAD、部分 PCNSL 联合方案。",
        "side_effects": "周围神经病变、便秘、手脚麻木、肌无力、下颌痛；骨髓抑制相对较轻。",
        "monitoring": "神经症状、便秘/肠梗阻风险、药物相互作用；不可鞘内注射。",
    },
    "prednisone": {
        "name": "泼尼松/糖皮质激素",
        "effect": "可直接诱导部分淋巴瘤细胞凋亡，也能减轻炎症和肿瘤相关症状。",
        "common_uses": "R-CHOP、CHOP、CVP 等方案。",
        "side_effects": "血糖升高、失眠、胃部不适、情绪变化、感染风险、肌肉无力、长期骨质疏松。",
        "monitoring": "血糖、感染、胃保护、睡眠和情绪、血压。",
    },
    "cytarabine": {
        "name": "阿糖胞苷",
        "effect": "抗代谢化疗药，干扰 DNA 合成；高剂量时可用于中枢相关或高强度淋巴瘤方案。",
        "common_uses": "PCNSL、MCL 强化方案、伯基特淋巴瘤、高强度挽救方案。",
        "side_effects": "骨髓抑制、感染、发热、结膜炎、肝功能异常；高剂量时可有小脑毒性。",
        "monitoring": "血常规、感染、肝肾功能、眼部保护、小脑症状。",
    },
    "etoposide": {
        "name": "依托泊苷",
        "effect": "拓扑异构酶 II 抑制剂，干扰 DNA 修复和复制。",
        "common_uses": "CHOEP、HyperCVAD/MA、部分 NK/T 细胞淋巴瘤或挽救方案。",
        "side_effects": "骨髓抑制、感染、脱发、恶心、低血压或输注反应。",
        "monitoring": "血常规、感染、输注反应、肝肾功能。",
    },
    "temozolomide": {
        "name": "替莫唑胺",
        "effect": "口服烷化剂，可进入中枢神经系统，部分 PCNSL 方案或复发场景会讨论。",
        "common_uses": "PCNSL 联合或复发治疗场景。",
        "side_effects": "骨髓抑制、恶心、乏力、便秘、感染风险。",
        "monitoring": "血常规、感染、肝功能、恶心控制。",
    },
    "thiotepa": {
        "name": "噻替哌",
        "effect": "烷化剂，能穿透中枢神经系统，常用于 PCNSL 巩固或移植预处理方案。",
        "common_uses": "PCNSL 强化/巩固、自体移植预处理。",
        "side_effects": "骨髓抑制、黏膜炎、感染、皮肤反应、肝功能异常。",
        "monitoring": "血常规、感染、皮肤护理、肝肾功能。",
    },
    "procarbazine": {
        "name": "丙卡巴肼",
        "effect": "烷化样化疗药，可用于部分中枢神经系统淋巴瘤联合方案。",
        "common_uses": "PCNSL 联合方案、部分脑肿瘤方案。",
        "side_effects": "骨髓抑制、恶心、疲劳、肝功能异常；与酒精和部分食物/药物有相互作用风险。",
        "monitoring": "血常规、肝功能、饮食和药物相互作用、感染。",
    },
    "bendamustine": {
        "name": "苯达莫司汀",
        "effect": "兼有烷化剂和嘌呤类似物特点的化疗药，常与抗 CD20 单抗联合。",
        "common_uses": "FL、MZL、MCL、CLL/SLL 等。",
        "side_effects": "骨髓抑制、感染、皮疹、恶心、乏力、发热。",
        "monitoring": "血常规、感染、皮疹、肝肾功能、乙肝筛查。",
    },
    "btk": {
        "name": "BTK 抑制剂（伊布替尼/阿可替尼/泽布替尼）",
        "effect": "阻断 B 细胞受体信号通路，抑制恶性 B 细胞生存和增殖。",
        "common_uses": "CLL/SLL、MCL、MZL；部分 PCNSL 复发场景会讨论伊布替尼。",
        "side_effects": "出血倾向、感染、腹泻、皮疹、肌肉关节痛；部分药物有房颤或高血压风险。",
        "monitoring": "出血、心律/血压、感染、血常规、药物相互作用。",
    },
    "venetoclax": {
        "name": "维奈克拉",
        "effect": "BCL-2 抑制剂，促进依赖 BCL-2 的肿瘤细胞凋亡。",
        "common_uses": "CLL/SLL，部分复发 MCL 或联合研究场景。",
        "side_effects": "中性粒细胞减少、感染、腹泻、恶心、贫血、肿瘤溶解综合征。",
        "monitoring": "逐步加量、肿瘤溶解风险、电解质、肾功能、血常规。",
    },
    "lenalidomide": {
        "name": "来那度胺",
        "effect": "免疫调节药，影响肿瘤微环境并增强免疫抗肿瘤作用。",
        "common_uses": "FL 复发方案、部分 DLBCL 或 MCL 场景。",
        "side_effects": "血细胞减少、皮疹、腹泻/便秘、疲劳、血栓风险、胎儿致畸风险。",
        "monitoring": "血常规、血栓风险、皮疹、肾功能、妊娠防护要求。",
    },
    "brentuximab": {
        "name": "Brentuximab Vedotin",
        "effect": "靶向 CD30 的抗体药物偶联物，将细胞毒药物递送到 CD30 阳性细胞。",
        "common_uses": "经典霍奇金淋巴瘤、ALCL、CD30 阳性 PTCL/CTCL。",
        "side_effects": "周围神经病变、血细胞减少、感染、乏力、恶心、皮疹。",
        "monitoring": "神经症状、血常规、感染、肝功能。",
    },
    "pd1": {
        "name": "PD-1 抑制剂（纳武利尤单抗/帕博利珠单抗）",
        "effect": "解除免疫检查点抑制，使 T 细胞更容易攻击肿瘤。",
        "common_uses": "复发/难治经典霍奇金淋巴瘤、部分 NK/T 细胞淋巴瘤等。",
        "side_effects": "免疫相关皮疹、肠炎、肝炎、肺炎、甲状腺/内分泌异常、乏力。",
        "monitoring": "肝肾功能、甲状腺功能、肺部症状、腹泻、皮疹和其他免疫毒性。",
    },
    "polatuzumab": {
        "name": "泊洛妥珠单抗",
        "effect": "靶向 CD79b 的抗体药物偶联物，向 B 细胞淋巴瘤细胞递送细胞毒药物。",
        "common_uses": "DLBCL 的部分一线或复发/难治方案。",
        "side_effects": "周围神经病变、血细胞减少、感染、腹泻、乏力。",
        "monitoring": "血常规、感染、神经病变、肝功能。",
    },
    "asparaginase": {
        "name": "门冬酰胺酶/培门冬酶",
        "effect": "分解血液中的门冬酰胺，使部分肿瘤细胞缺乏生长所需氨基酸。",
        "common_uses": "结外 NK/T 细胞淋巴瘤含门冬酰胺酶方案。",
        "side_effects": "过敏、胰腺炎、肝功能异常、凝血异常、血糖升高、感染。",
        "monitoring": "肝功能、胰腺炎症状、凝血功能、血糖、过敏反应。",
    },
}

TOPIC_DRUGS = {
    "hd-mtx": ["methotrexate", "leucovorin", "rituximab", "cytarabine", "temozolomide", "thiotepa", "procarbazine"],
    "r-chop": ["rituximab", "cyclophosphamide", "doxorubicin", "vincristine", "prednisone"],
    "pola-r-chp": ["polatuzumab", "rituximab", "cyclophosphamide", "doxorubicin", "prednisone"],
    "car-t": [],
    "autologous-transplant": ["thiotepa", "cyclophosphamide", "cytarabine"],
    "allogeneic-transplant": ["cyclophosphamide"],
    "anti-cd20": ["rituximab", "obinutuzumab"],
    "btk-inhibitor": ["btk"],
    "venetoclax": ["venetoclax"],
    "bendamustine": ["bendamustine", "rituximab", "obinutuzumab"],
    "abvd": ["doxorubicin", "bleomycin", "vinblastine", "dacarbazine"],
    "chop-choep": ["cyclophosphamide", "doxorubicin", "vincristine", "prednisone", "etoposide"],
    "pd-1": ["pd1"],
    "brentuximab": ["brentuximab"],
    "radiation": [],
    "bispecific": [],
    "asparaginase": ["asparaginase"],
}

SIDE_EFFECT_GUIDE = {
    "infection": {
        "name": "发热 / 感染 / 中性粒细胞低",
        "watch_for": "体温升高、寒战、咳嗽、咽痛、尿痛、皮肤红肿、口腔溃疡加重，或精神状态变差。",
        "what_to_do": "治疗期间发热要尽快联系医生或急诊，尤其是化疗后白细胞低的时期。不要自行硬扛或只吃退烧药观察。",
        "team_may_do": "医生可能安排血常规、血培养、影像检查、经验性抗生素、升白针或住院观察。",
    },
    "low_counts": {
        "name": "血象下降 / 贫血 / 血小板低",
        "watch_for": "乏力、气短、头晕、牙龈或鼻出血、皮肤瘀斑、黑便，或月经明显增多。",
        "what_to_do": "按计划复查血常规；有出血、明显气短或极度乏力时及时就医。避免自行使用阿司匹林、布洛芬等可能增加出血风险的药物。",
        "team_may_do": "医生可能调整治疗时间或剂量，使用升白针、输红细胞/血小板，或处理感染和出血风险。",
    },
    "nausea": {
        "name": "恶心 / 呕吐 / 食欲差",
        "watch_for": "吃不下、喝不下、尿量减少、体重快速下降、持续呕吐或无法服药。",
        "what_to_do": "按医生开的止吐药规律使用；少量多餐、补液。若 24 小时内多次呕吐或无法饮水，应联系医生。",
        "team_may_do": "医生可能调整止吐方案，补液，检查电解质，或评估是否有感染、肠梗阻、药物反应等原因。",
    },
    "mucositis": {
        "name": "口腔溃疡 / 黏膜炎",
        "watch_for": "口腔疼痛、吞咽困难、白斑、出血、口腔异味，或疼痛导致无法进食饮水。",
        "what_to_do": "保持口腔清洁，使用医生建议的漱口液；避免酒精漱口水、辛辣和过烫食物。严重疼痛或发热要及时联系医生。",
        "team_may_do": "医生可能给予止痛、抗感染、营养支持、补液，必要时调整治疗节奏。",
    },
    "neuropathy": {
        "name": "手脚麻木 / 周围神经病变",
        "watch_for": "手脚麻、刺痛、烧灼感、走路不稳、拿东西困难、便秘加重。",
        "what_to_do": "尽早告诉医生，不要等到影响走路或精细动作。注意防跌倒、防烫伤，避免自行加用镇痛药。",
        "team_may_do": "医生可能评估长春新碱、brentuximab、泊洛妥珠单抗等相关药物，调整剂量或更换方案，并给予疼痛/康复支持。",
    },
    "crs_icans": {
        "name": "CRS / 神经毒性（CAR-T、双特异性抗体相关）",
        "watch_for": "发热、低血压、呼吸困难、缺氧、意识模糊、嗜睡、说话困难、抽搐或严重头痛。",
        "what_to_do": "这是需要治疗中心快速处理的情况。CAR-T 或双特异性抗体治疗后出现发热或神经症状，应立即联系治疗团队或急诊。",
        "team_may_do": "医生会按严重程度监测生命体征，可能使用托珠单抗、激素、抗癫痫药、补液、吸氧或 ICU 支持。",
    },
    "immune": {
        "name": "免疫相关炎症（PD-1 等免疫治疗）",
        "watch_for": "持续腹泻、咳嗽气短、皮疹、黄疸、严重乏力、头痛、视物异常、甲状腺或血糖异常表现。",
        "what_to_do": "免疫相关副作用可在用药中或停药后出现。不要自行用激素掩盖症状，应尽快联系肿瘤医生。",
        "team_may_do": "医生可能暂停免疫治疗，检查受累器官，使用糖皮质激素或其他免疫抑制治疗。",
    },
    "kidney_mtx": {
        "name": "MTX 清除延迟 / 肾功能异常",
        "watch_for": "尿量减少、水肿、恶心加重、口腔炎明显、血肌酐升高或甲氨蝶呤血药浓度下降慢。",
        "what_to_do": "大剂量 MTX 期间不要自行加用可能影响肾功能或 MTX 清除的药物；按医嘱补液、碱化和抽血监测。",
        "team_may_do": "医生会根据 MTX 浓度调整亚叶酸救援、补液碱化，必要时使用解救药物或肾脏支持。",
    },
    "heart": {
        "name": "心脏毒性 / 心律问题",
        "watch_for": "胸闷、气短、心悸、下肢水肿、活动耐量明显下降。",
        "what_to_do": "出现胸痛、明显气短或晕厥应急诊。接受蒽环类或 BTK 抑制剂时，应把既往心脏病史告诉医生。",
        "team_may_do": "医生可能安排心电图、心超、心肌标志物，调整蒽环类剂量或处理房颤/高血压等问题。",
    },
    "lung": {
        "name": "肺毒性 / 呼吸症状",
        "watch_for": "新发或加重的咳嗽、气短、低氧、胸闷，尤其是使用博来霉素或免疫治疗后。",
        "what_to_do": "不要把持续气短简单当作体力差。新发呼吸症状应尽快联系医生。",
        "team_may_do": "医生可能做胸部影像、肺功能、感染排查，并考虑停药、激素或抗感染治疗。",
    },
    "gvhd": {
        "name": "移植物抗宿主病（异基因移植相关）",
        "watch_for": "皮疹、腹泻、黄疸、口干眼干、肝功能异常，或皮肤变硬。",
        "what_to_do": "异基因移植后任何新皮疹、腹泻或黄疸都应尽快联系移植团队。",
        "team_may_do": "移植团队可能调整免疫抑制剂，使用激素或其他抗 GVHD 治疗，并排查感染。",
    },
}

TOPIC_SIDE_EFFECTS = {
    "hd-mtx": ["kidney_mtx", "mucositis", "low_counts", "infection", "nausea"],
    "r-chop": ["infection", "low_counts", "nausea", "neuropathy", "heart"],
    "pola-r-chp": ["infection", "low_counts", "neuropathy", "heart", "nausea"],
    "car-t": ["crs_icans", "infection", "low_counts"],
    "autologous-transplant": ["infection", "low_counts", "mucositis", "nausea"],
    "allogeneic-transplant": ["infection", "low_counts", "mucositis", "gvhd"],
    "anti-cd20": ["infection"],
    "btk-inhibitor": ["infection", "heart", "low_counts"],
    "venetoclax": ["low_counts", "infection", "nausea"],
    "bendamustine": ["infection", "low_counts", "nausea", "mucositis"],
    "abvd": ["infection", "low_counts", "nausea", "heart", "lung", "neuropathy"],
    "chop-choep": ["infection", "low_counts", "nausea", "heart", "neuropathy"],
    "pd-1": ["immune", "lung"],
    "brentuximab": ["neuropathy", "infection", "low_counts"],
    "radiation": ["mucositis", "lung"],
    "bispecific": ["crs_icans", "infection", "low_counts"],
    "asparaginase": ["infection", "nausea", "low_counts"],
}

RISK_SURVIVAL = {
    "DLBCL（弥漫大B细胞淋巴瘤）": {
        "risk_grade": "高危倾向：侵袭性，可治愈但需要尽快规范治疗",
        "five_year": "总体约 65-75%；SEER 分期不同差异明显，局限期通常更高，远处/广泛期更低。",
    },
    "滤泡性淋巴瘤（FL）": {
        "risk_grade": "低-中危倾向：多为惰性，需长期管理",
        "five_year": "总体常约 88-95%；早期和低肿瘤负荷通常更好，早期进展 POD24 或转化后风险升高。",
    },
    "边缘区淋巴瘤（MZL/MALT）": {
        "risk_grade": "低-中危倾向：多为惰性，部位和分期影响很大",
        "five_year": "总体常约 80-90%；局限 MALT 型通常较好，转化或播散后风险升高。",
    },
    "CLL/SLL": {
        "risk_grade": "低-中危倾向：很多患者多年观察，但高危遗传学可明显改变风险",
        "five_year": "总体约 88-90%；TP53 异常、IGHV 未突变等提示更高风险。",
    },
    "套细胞淋巴瘤（MCL）": {
        "risk_grade": "中-高危倾向：多数需系统治疗，复发风险较高",
        "five_year": "传统总体约 50-70%；年轻、低 MIPI、Ki-67 低、无 TP53 异常者更好。",
    },
    "伯基特淋巴瘤": {
        "risk_grade": "很高危但可治性：进展极快，需要紧急强化治疗",
        "five_year": "成人总体常约 55-70%，儿童/青少年和低危患者更高；中枢受累、LDH 高、肿瘤负荷大风险更高。",
    },
    "原发性中枢神经系统淋巴瘤（PCNSL）": {
        "risk_grade": "高危倾向：中枢部位特殊，治疗依赖能否耐受 HD-MTX",
        "five_year": "总体约 30-50%；年轻、体能好、能接受 HD-MTX 和巩固治疗者可明显更好。",
    },
    "经典霍奇金淋巴瘤": {
        "risk_grade": "中危但高度可治：总体治愈率较高",
        "five_year": "美国总体约 89%；早期通常更高，晚期、高 IPS 或治疗反应差者较低。",
    },
    "结节性淋巴细胞为主型 HL": {
        "risk_grade": "低-中危倾向：多为慢性/惰性，但可晚期复发或转化",
        "five_year": "通常 >90%；长期随访重点是复发和少数转化为侵袭性 B 细胞淋巴瘤。",
    },
    "外周 T 细胞淋巴瘤（PTCL）": {
        "risk_grade": "高危倾向：异质性强，很多亚型预后较差",
        "five_year": "常约 30-45%；具体取决于 PTCL-NOS、AITL、ALK 状态、分期、IPI/PIT 和治疗反应。",
    },
    "间变性大细胞淋巴瘤（ALCL）": {
        "risk_grade": "中-高危倾向：ALK 阳性通常好于 ALK 阴性",
        "five_year": "ALK 阳性常约 70-80%；ALK 阴性常约 40-60%，并受 IPI、年龄和分期影响。",
    },
    "皮肤 T 细胞淋巴瘤（MF/SS）": {
        "risk_grade": "低-高危跨度大：早期 MF 慢性可控，Sézary 或血液受累风险高",
        "five_year": "早期 MF 可 >85-90%；肿瘤期、红皮病或 Sézary 综合征明显更低。",
    },
    "结外 NK/T 细胞淋巴瘤": {
        "risk_grade": "高危倾向：EBV 相关，局限期和晚期差异大",
        "five_year": "总体常约 40-60%；局限期联合放疗和含门冬酰胺酶方案较好，晚期/复发难治较差。",
    },
}

GLOSSARY = {
    "B 症状": "发热、盗汗、体重下降三类全身症状，会影响分期和风险判断。",
    "结外受累": "淋巴结以外器官受累，例如胃、皮肤、骨髓、中枢神经系统等。",
    "LDH": "乳酸脱氢酶，常作为肿瘤负荷或疾病活跃度的辅助指标，不是特异性诊断指标。",
    "IHC / 免疫组化": "在病理切片上用抗体染色，看肿瘤细胞表达哪些标志物。",
    "流式细胞术": "用新鲜细胞样本分析细胞表面/胞内标志，帮助判断细胞来源、克隆性和异常表型。",
    "FISH": "荧光原位杂交，用来查 MYC、BCL2、BCL6、CCND1 等基因重排或拷贝数异常。",
    "NGS": "二代测序，可检测多个基因突变，如 TP53、MYD88、EZH2、CD79B 等。",
    "Ki-67": "增殖指数，粗略反映肿瘤细胞增殖活跃程度，数值高常提示进展较快。",
    "MYC/BCL2/BCL6": "部分侵袭性 B 细胞淋巴瘤会检查这些基因重排；双打击/三打击通常提示更高风险。",
    "TP53": "重要抑癌基因，异常时常提示治疗难度更高。",
    "SUVmax": "PET-CT 上病灶 FDG 摄取强度的数值，不能单独诊断淋巴瘤或复发。",
    "Deauville 评分": "PET-CT 疗效评估常用 1-5 分法，用病灶摄取与纵隔、肝脏比较。",
    "CR / PR": "CR 是完全缓解，PR 是部分缓解。",
    "复发 / 难治": "复发指缓解后再次出现疾病；难治指治疗后未达到预期缓解或很快进展。",
    "CNS / CSF": "CNS 是中枢神经系统；CSF 是脑脊液，通常通过腰穿获取。",
    "ECOG / WHO PS": "体能状态评分，0 分表示完全正常，1 分表示能做轻体力活动，2 分表示能自理但不能工作，3-4 分表示明显卧床或完全不能自理。",
    "KPS": "Karnofsky 行动能力评分，100 表示完全正常，70 通常表示能自理但不能从事正常工作，低于 70 常提示需要更多照护。",
    "IELSG 评分": "PCNSL 常用预后模型之一，综合年龄、体能状态、LDH、脑脊液蛋白和脑深部结构受累等因素。",
    "MSKCC 评分": "PCNSL 的简化预后模型，主要依据年龄和 KPS 把患者分为不同风险组。",
    "Bulky": "大肿块病灶，具体阈值随病种和指南不同而变化，常影响治疗策略。",
}

GENOTYPE_GUIDE = [
    {
        "name": "MYC / BCL2 / BCL6 重排",
        "seen_in": "DLBCL、高级别 B 细胞淋巴瘤",
        "meaning": "FISH 检测到 MYC 合并 BCL2 和/或 BCL6 重排时，可能提示“双打击/三打击”高级别 B 细胞淋巴瘤。",
        "why_it_matters": "通常提示更高风险，医生可能考虑更强化方案或更密切评估；单纯蛋白高表达不等同于基因重排。",
    },
    {
        "name": "MYD88 L265P",
        "seen_in": "淋巴浆细胞淋巴瘤/华氏巨球蛋白血症、部分 PCNSL、部分 ABC 型 DLBCL",
        "meaning": "常见的信号通路激活突变，可支持某些诊断方向，但不能单独确诊。",
        "why_it_matters": "在部分疾病中有助于分型，并可能影响 BTK 抑制剂等靶向治疗讨论。",
    },
    {
        "name": "CD79B",
        "seen_in": "ABC 型 DLBCL、PCNSL 等",
        "meaning": "B 细胞受体信号通路相关基因突变，可与 MYD88 等共同出现。",
        "why_it_matters": "提示 BCR/NF-kB 通路活跃，部分复发难治场景可能影响靶向药或临床试验选择。",
    },
    {
        "name": "TP53 缺失/突变",
        "seen_in": "CLL/SLL、MCL、DLBCL 等多种淋巴瘤",
        "meaning": "TP53 是重要抑癌基因，异常通常提示肿瘤更难被常规治疗控制。",
        "why_it_matters": "常用于风险分层；在 CLL/SLL、MCL 等疾病里会明显影响一线方案选择。",
    },
    {
        "name": "t(11;14) / CCND1-IGH",
        "seen_in": "套细胞淋巴瘤（MCL）",
        "meaning": "导致 Cyclin D1 过表达，是 MCL 的典型遗传学特征之一。",
        "why_it_matters": "有助于确认 MCL 诊断；通常会结合 Cyclin D1、SOX11、CD5 等免疫表型判断。",
    },
    {
        "name": "EZH2",
        "seen_in": "滤泡性淋巴瘤、部分 DLBCL",
        "meaning": "表观遗传调控相关基因突变，在部分生发中心来源 B 细胞淋巴瘤中可见。",
        "why_it_matters": "复发 FL 中可能影响 EZH2 抑制剂 tazemetostat 的讨论，但治疗仍需结合整体病情。",
    },
    {
        "name": "BCL2 t(14;18)",
        "seen_in": "滤泡性淋巴瘤",
        "meaning": "经典 FL 常见遗传改变，可导致 BCL2 抗凋亡蛋白表达增加。",
        "why_it_matters": "支持 FL 诊断，但不是所有 FL 都有，也不能单独替代形态和免疫组化。",
    },
    {
        "name": "ALK 重排",
        "seen_in": "ALK 阳性间变性大细胞淋巴瘤（ALCL）",
        "meaning": "ALK 基因重排导致 ALK 蛋白异常表达。",
        "why_it_matters": "ALK 阳性 ALCL 通常预后较 ALK 阴性更好；复发时可能讨论 ALK 抑制剂。",
    },
    {
        "name": "EBV / EBER 阳性",
        "seen_in": "结外 NK/T 细胞淋巴瘤、部分霍奇金淋巴瘤、免疫缺陷相关淋巴增殖性疾病",
        "meaning": "EBER 原位杂交通常用于检测肿瘤细胞内 EBV 相关信号。",
        "why_it_matters": "对 NK/T 细胞淋巴瘤等诊断很关键；血 EBV DNA 也可用于部分疾病监测。",
    },
    {
        "name": "DUSP22 / TP63 重排",
        "seen_in": "ALK 阴性 ALCL",
        "meaning": "ALK 阴性 ALCL 中可见的分子亚组。",
        "why_it_matters": "DUSP22 重排通常提示较好预后，TP63 重排常提示较差预后，但检测可及性和解释需依赖专科病理。",
    },
]


def set_page(page_name: str) -> None:
    current = st.session_state.get("page")
    if current in PAGES and current != page_name:
        st.session_state.previous_page = current
    st.session_state.page = page_name


def current_page() -> str:
    if "page" not in st.session_state or st.session_state.page not in PAGES:
        st.session_state.page = "首页"
    return st.session_state.page


def inject_styles() -> None:
    st.markdown(
        """
<style>
:root {
    --bg: #f6f8fb;
    --surface: #ffffff;
    --surface-soft: #eef5f3;
    --text: #17202a;
    --muted: #617080;
    --line: #dce5ea;
    --teal: #0f766e;
    --teal-dark: #115e59;
    --blue: #2563eb;
    --amber: #b45309;
    --rose: #be123c;
    --green: #15803d;
    --shadow: 0 14px 40px rgba(21, 37, 54, 0.08);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.11), transparent 28rem),
        linear-gradient(180deg, #f9fbfc 0%, var(--bg) 100%);
    color: var(--text);
}

section[data-testid="stSidebar"] {
    background: #102027;
}

section[data-testid="stSidebar"] * {
    color: #eff6f8;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 8px;
    margin: 6px 0;
    padding: 10px 12px;
}

.main .block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    letter-spacing: 0;
    color: var(--text);
}

p, li, label, .stMarkdown {
    color: var(--text);
}

.app-shell {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.hero {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    padding: 34px;
    min-height: 260px;
    background:
        linear-gradient(120deg, rgba(16, 32, 39, 0.92), rgba(15, 118, 110, 0.77)),
        url("https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=1600&q=80");
    background-size: cover;
    background-position: center;
    box-shadow: var(--shadow);
}

.hero h1 {
    max-width: 680px;
    margin: 0 0 14px;
    color: #ffffff;
    font-size: 3.4rem;
    line-height: 1.06;
}

.hero p {
    max-width: 660px;
    margin: 0;
    color: #dbeafe;
    font-size: 1.08rem;
    line-height: 1.8;
}

.hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 26px;
}

.section-title {
    margin: 10px 0 4px;
    font-size: 1.45rem;
    font-weight: 750;
}

.subtle {
    color: var(--muted);
    font-size: 0.96rem;
    line-height: 1.7;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
}

.grid.two {
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.card {
    height: 100%;
    padding: 22px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    box-shadow: 0 10px 28px rgba(21, 37, 54, 0.06);
}

.card h3 {
    margin: 0 0 10px;
    font-size: 1.12rem;
}

.card p {
    margin: 0;
    color: var(--muted);
    line-height: 1.7;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    color: var(--teal-dark);
    font-size: 0.82rem;
    font-weight: 760;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.notice {
    padding: 16px 18px;
    border-left: 4px solid var(--teal);
    border-radius: 8px;
    background: #ecfdf5;
    color: #164e3b;
    line-height: 1.7;
}

.danger-note {
    padding: 16px 18px;
    border-left: 4px solid var(--rose);
    border-radius: 8px;
    background: #fff1f2;
    color: #7f1d1d;
    line-height: 1.7;
}

.workbench {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 16px;
    margin: 18px 0;
}

.route-card {
    padding: 18px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #ffffff;
    box-shadow: 0 10px 26px rgba(21, 37, 54, 0.05);
}

.route-card h3 {
    margin: 0 0 10px;
    font-size: 1.08rem;
}

.route-card ol {
    margin: 0;
    padding-left: 1.2rem;
    color: var(--muted);
    line-height: 1.75;
}

.stat-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 14px 0 2px;
}

.stat {
    padding: 14px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #ffffff;
}

.stat strong {
    display: block;
    margin-bottom: 3px;
    color: var(--text);
    font-size: 1.05rem;
}

.stat span {
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.45;
}

.stage-panel {
    padding: 26px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--surface);
    box-shadow: var(--shadow);
}

.stage-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 18px;
}

.stage-header h2 {
    margin: 0;
    font-size: 1.55rem;
}

.pill {
    display: inline-flex;
    align-items: center;
    min-height: 34px;
    padding: 6px 12px;
    border-radius: 999px;
    background: #e0f2fe;
    color: #075985;
    font-size: 0.86rem;
    font-weight: 700;
    white-space: nowrap;
}

.steps {
    display: grid;
    gap: 10px;
    margin-top: 14px;
}

.step {
    display: grid;
    grid-template-columns: 34px minmax(0, 1fr);
    gap: 12px;
    align-items: start;
    padding: 14px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #fbfdfe;
}

.step strong {
    display: block;
    margin-bottom: 3px;
    color: var(--text);
}

.step span {
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: var(--surface-soft);
    color: var(--teal-dark);
    font-weight: 800;
}

.callout {
    margin-top: 16px;
    padding: 16px;
    border-radius: 8px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #7c2d12;
}

.taxonomy {
    display: grid;
    grid-template-columns: 1fr 1.2fr 1fr;
    gap: 12px;
    align-items: stretch;
    margin: 18px 0;
}

.taxonomy-node {
    padding: 18px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #ffffff;
    box-shadow: 0 10px 24px rgba(21, 37, 54, 0.05);
}

.taxonomy-node.root {
    background: #102027;
}

.taxonomy-node.root h3,
.taxonomy-node.root p {
    color: #ffffff;
}

.taxonomy-node h3 {
    margin: 0 0 8px;
    font-size: 1.05rem;
}

.taxonomy-node p {
    margin: 0;
    color: var(--muted);
    line-height: 1.65;
}

.mini-list {
    display: grid;
    gap: 8px;
    margin-top: 10px;
}

.mini-list span {
    display: block;
    padding: 9px 10px;
    border-radius: 8px;
    background: #f8fafc;
    color: var(--text);
    font-weight: 650;
}

.chart-panel {
    padding: 18px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.92);
    box-shadow: 0 10px 28px rgba(21, 37, 54, 0.05);
}

.chart-panel h3 {
    margin: 0 0 4px;
    font-size: 1.02rem;
}

.topic-strip {
    margin-top: 14px;
    padding: 14px;
    border: 1px solid #cfe4e1;
    border-radius: 8px;
    background: #f0fdfa;
}

.topic-strip h4 {
    margin: 0 0 8px;
    color: var(--teal-dark);
    font-size: 0.95rem;
}

.drug-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.drug-card {
    padding: 16px;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: #ffffff;
}

.drug-card h3 {
    margin: 0 0 8px;
    font-size: 1rem;
}

.drug-card p {
    margin: 0 0 8px;
    color: var(--muted);
    line-height: 1.65;
}

.drug-card p:last-child {
    margin-bottom: 0;
}

.dlbcl-banner {
    padding: 28px;
    border-radius: 8px;
    background: linear-gradient(135deg, #102027, #0f766e);
    box-shadow: var(--shadow);
}

.dlbcl-banner h1,
.dlbcl-banner p {
    color: #ffffff;
}

.dlbcl-banner p {
    max-width: 760px;
    margin-bottom: 0;
    line-height: 1.75;
}

div.stButton > button {
    min-height: 42px;
    border-radius: 8px;
    border: 1px solid rgba(15, 118, 110, 0.25);
    background: var(--teal);
    color: #ffffff;
    font-weight: 740;
    box-shadow: 0 8px 18px rgba(15, 118, 110, 0.18);
}

div.stButton > button p {
    color: #ffffff;
    font-weight: 740;
}

div.stButton > button:hover {
    border-color: var(--teal-dark);
    background: var(--teal-dark);
    color: #ffffff;
}

div.stButton > button:hover p {
    color: #ffffff;
}

div.stButton > button:disabled,
div.stButton > button:disabled:hover {
    background: #eef2f6;
    border-color: #d8e2e8;
    color: #526271;
    box-shadow: none;
}

div.stButton > button:disabled p,
div.stButton > button:disabled:hover p {
    color: #526271;
}

div[data-testid="stRadio"] > label,
div[data-testid="stSelectbox"] > label {
    font-weight: 750;
    color: var(--text);
}

@media (max-width: 780px) {
    .main .block-container {
        padding: 0.75rem 0.75rem 5rem;
        max-width: 100%;
    }

    .hero {
        padding: 22px;
        min-height: 230px;
        background-position: center;
    }

    .hero h1,
    .dlbcl-banner h1 {
        font-size: 2rem;
        line-height: 1.12;
    }

    .hero p,
    .dlbcl-banner p {
        font-size: 0.98rem;
        line-height: 1.65;
    }

    .dlbcl-banner {
        padding: 22px;
    }

    .grid,
    .grid.two {
        grid-template-columns: 1fr;
    }

    .stage-header {
        flex-direction: column;
    }

    .taxonomy,
    .stat-row,
    .workbench,
    .drug-grid {
        grid-template-columns: 1fr;
    }

    .card,
    .route-card,
    .stage-panel,
    .taxonomy-node,
    .chart-panel,
    .drug-card {
        padding: 16px;
    }

    .section-title {
        font-size: 1.18rem;
        margin-top: 16px;
    }

    .step {
        grid-template-columns: 30px minmax(0, 1fr);
        padding: 12px;
    }

    .step span {
        width: 30px;
        height: 30px;
    }

    div.stButton > button {
        min-height: 46px;
        padding-left: 8px;
        padding-right: 8px;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }

    div[data-testid="stTabs"] [role="tablist"] {
        overflow-x: auto;
        flex-wrap: nowrap;
        gap: 0.25rem;
        padding-bottom: 4px;
    }

    div[data-testid="stTabs"] [role="tab"] {
        min-width: max-content;
        padding-left: 10px;
        padding-right: 10px;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        overflow-x: auto;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 12px;
    }
}

@media (max-width: 420px) {
    .main .block-container {
        padding-left: 0.55rem;
        padding-right: 0.55rem;
    }

    .hero,
    .dlbcl-banner {
        padding: 18px;
    }

    .hero h1,
    .dlbcl-banner h1 {
        font-size: 1.75rem;
    }

    .card h3,
    .route-card h3,
    .drug-card h3 {
        font-size: 1rem;
    }

    .notice,
    .danger-note,
    .callout {
        padding: 13px 14px;
    }

    div[data-testid="stTabs"] [role="tab"] {
        font-size: 0.92rem;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str, eyebrow: str = "") -> None:
    st.markdown(
        f"""
<div class="card">
    {f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ''}
    <h3>{title}</h3>
    <p>{body}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def page_intro(title: str, body: str, eyebrow: str = "") -> None:
    st.markdown(
        f"""
<div class="dlbcl-banner">
    {f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ''}
    <h1>{title}</h1>
    <p>{body}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_global_nav() -> None:
    page_now = current_page()
    previous = st.session_state.get("previous_page")
    cols = st.columns(4)
    with cols[0]:
        if st.button("首页", use_container_width=True, disabled=page_now == "首页"):
            set_page("首页")
            st.rerun()
    with cols[1]:
        can_go_back = previous in PAGES and previous != page_now
        if st.button("返回上一页", use_container_width=True, disabled=not can_go_back):
            set_page(previous)
            st.rerun()
    with cols[2]:
        if st.button("路径导航", use_container_width=True, disabled=page_now == "路径导航"):
            set_page("路径导航")
            st.rerun()
    with cols[3]:
        if st.button("方案库", use_container_width=True, disabled=page_now == "治疗方案库"):
            set_page("治疗方案库")
            st.rerun()


def step(number: int, title: str, body: str) -> str:
    return (
        '<div class="step">'
        f'<span>{number}</span>'
        f'<div><strong>{title}</strong><p class="subtle">{body}</p></div>'
        '</div>'
    )


def lymphoma_frame() -> pd.DataFrame:
    rows = []
    for item in LYMPHOMA_TYPES:
        row = item.copy()
        row.update(TREATMENT_DETAILS.get(item["type"], {}))
        row.update(RISK_SURVIVAL.get(item["type"], {}))
        rows.append(row)
    return pd.DataFrame(rows)


def set_treatment_topic(topic_id: str, return_page: str | None = None) -> None:
    st.session_state.treatment_topic = topic_id
    if return_page:
        st.session_state.return_page = return_page
    set_page("治疗方案库")


def current_treatment_topic() -> str:
    topic = st.session_state.get("treatment_topic", "hd-mtx")
    return topic if topic in TREATMENT_LIBRARY else "hd-mtx"


def relevant_treatment_topics(row: pd.Series) -> list[str]:
    text = " ".join(
        str(row.get(field, ""))
        for field in ["standard_treatment", "first_line", "second_line", "drugs", "treatment"]
    ).lower()
    topics = []
    for topic_id, topic in TREATMENT_LIBRARY.items():
        aliases = [topic["name"], *topic["aliases"]]
        if any(alias.lower() in text for alias in aliases):
            topics.append(topic_id)

    # Keep the most clinically recognizable topics near the front.
    priority = [
        "hd-mtx",
        "r-chop",
        "pola-r-chp",
        "car-t",
        "autologous-transplant",
        "allogeneic-transplant",
        "anti-cd20",
        "bendamustine",
        "btk-inhibitor",
        "venetoclax",
        "abvd",
        "chop-choep",
        "pd-1",
        "brentuximab",
        "radiation",
        "bispecific",
        "asparaginase",
    ]
    return sorted(set(topics), key=lambda item: priority.index(item) if item in priority else 999)


def render_treatment_topic_buttons(topic_ids: list[str], prefix: str) -> None:
    if not topic_ids:
        return

    st.markdown(
        """
<div class="topic-strip">
    <h4>相关方案详细介绍</h4>
</div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    safe_prefix = "".join(char if char.isalnum() else "_" for char in prefix)
    for index, topic_id in enumerate(topic_ids):
        topic = TREATMENT_LIBRARY[topic_id]
        with columns[index % 3]:
            if st.button(topic["name"], key=f"{safe_prefix}_{topic_id}", use_container_width=True):
                set_treatment_topic(topic_id, current_page())
                st.rerun()


def render_drug_details(topic_id: str) -> None:
    drug_ids = TOPIC_DRUGS.get(topic_id, [])
    if not drug_ids:
        st.markdown(
            """
<div class="notice">
    这个条目主要是治疗技术或治疗类别，不是单一药物方案；具体用药会随中心流程和个人情况变化。
</div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown('<p class="section-title">常见用药：功效与副作用</p>', unsafe_allow_html=True)
    for start in range(0, len(drug_ids), 2):
        cols = st.columns(2)
        for offset, drug_id in enumerate(drug_ids[start:start + 2]):
            drug = DRUG_LIBRARY[drug_id]
            with cols[offset]:
                st.markdown(
                    f"""
<div class="drug-card">
    <h3>{drug["name"]}</h3>
    <p><strong>功效：</strong>{drug["effect"]}</p>
    <p><strong>用途：</strong>{drug["common_uses"]}</p>
    <p><strong>副作用：</strong>{drug["side_effects"]}</p>
    <p><strong>监测：</strong>{drug["monitoring"]}</p>
</div>
                    """,
                    unsafe_allow_html=True,
                )


def render_side_effect_management(topic_id: str) -> None:
    side_effect_ids = TOPIC_SIDE_EFFECTS.get(topic_id, [])
    if not side_effect_ids:
        return

    st.markdown('<p class="section-title">常见副作用和处理方案</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="notice">
    以下是科普级处理思路，不替代医生医嘱。治疗期间出现发热、呼吸困难、意识改变、持续呕吐、出血不止或严重腹泻，应及时联系治疗团队或急诊。
</div>
        """,
        unsafe_allow_html=True,
    )
    for side_effect_id in side_effect_ids:
        item = SIDE_EFFECT_GUIDE[side_effect_id]
        with st.expander(item["name"]):
            st.markdown(f'**需要留意：** {item["watch_for"]}')
            st.markdown(f'**患者可以做：** {item["what_to_do"]}')
            st.markdown(f'**医生可能处理：** {item["team_may_do"]}')


def render_treatment_detail(topic_id: str) -> None:
    topic = TREATMENT_LIBRARY[topic_id]
    page_intro(topic["name"], topic["summary"], topic["category"])

    overview_tab, drug_tab, side_tab, ref_tab = st.tabs(["方案概览", "常见用药", "副作用处理", "参考链接"])
    with overview_tab:
        col1, col2 = st.columns(2)
        with col1:
            card("常用于", topic["used_for"], "Where it fits")
        with col2:
            card("包含什么", topic["what_it_includes"], "Components")

        col3, col4 = st.columns(2)
        with col3:
            card("通常怎么进行", topic["how_it_is_given"], "How")
        with col4:
            card("需要重点监测", topic["monitoring"], "Monitoring")

        st.markdown(
            f"""
<div class="danger-note">
    <strong>常见风险/副作用：</strong>{topic["side_effects"]}
</div>
            """,
            unsafe_allow_html=True,
        )
    with drug_tab:
        render_drug_details(topic_id)
    with side_tab:
        render_side_effect_management(topic_id)
    with ref_tab:
        for label, url in topic["sources"]:
            st.markdown(f"- [{label}]({url})")


def render_lineage_chart(df: pd.DataFrame) -> None:
    counts = (
        df.groupby("lineage", as_index=False)
        .size()
        .rename(columns={"size": "示例数量"})
        .sort_values("示例数量", ascending=False)
    )
    chart = (
        alt.Chart(counts)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X("示例数量:Q", title="本页列出的示例数量"),
            y=alt.Y("lineage:N", title="", sort="-x"),
            color=alt.Color(
                "lineage:N",
                title="分类",
                scale=alt.Scale(range=["#0f766e", "#2563eb", "#b45309"]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("lineage:N", title="分类"),
                alt.Tooltip("示例数量:Q", title="示例数量"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(chart, use_container_width=True)


def render_tempo_chart(df: pd.DataFrame) -> None:
    chart = (
        alt.Chart(df)
        .mark_circle(size=150, opacity=0.84, stroke="#ffffff", strokeWidth=1.5)
        .encode(
            x=alt.X("tempo_score:Q", title="疾病进展速度示意（1 慢 - 5 快）", scale=alt.Scale(domain=[0.5, 5.5])),
            y=alt.Y("urgency:Q", title="就诊/治疗紧迫度示意（1 低 - 5 高）", scale=alt.Scale(domain=[0.5, 5.5])),
            color=alt.Color(
                "lineage:N",
                title="分类",
                scale=alt.Scale(range=["#0f766e", "#2563eb", "#b45309"]),
            ),
            tooltip=[
                alt.Tooltip("type:N", title="类型"),
                alt.Tooltip("lineage:N", title="分类"),
                alt.Tooltip("tempo:N", title="临床节奏"),
                alt.Tooltip("summary:N", title="提示"),
            ],
        )
        .properties(height=300)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


def render_watchful_chart(df: pd.DataFrame) -> None:
    chart = (
        alt.Chart(df.sort_values("watchful", ascending=False))
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
        .encode(
            x=alt.X("watchful:Q", title="观察随访可能性示意（1 低 - 5 高）", scale=alt.Scale(domain=[0, 5])),
            y=alt.Y("type:N", title="", sort="-x"),
            color=alt.Color(
                "lineage:N",
                title="分类",
                scale=alt.Scale(range=["#0f766e", "#2563eb", "#b45309"]),
            ),
            tooltip=[
                alt.Tooltip("type:N", title="类型"),
                alt.Tooltip("watchful:Q", title="观察随访可能性"),
                alt.Tooltip("summary:N", title="提示"),
            ],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def render_subtype_pathway(row: pd.Series) -> None:
    detail_col1, detail_col2 = st.columns([0.9, 1.1])
    functional_assessment = row.get("functional_assessment")
    functional_html = ""
    if isinstance(functional_assessment, str) and functional_assessment:
        functional_html = (
            f'<br><p><strong>行动能力/体能状态评估：</strong>'
            f'{functional_assessment}</p>'
        )
    with detail_col1:
        st.markdown(
            f"""
<div class="card">
    <div class="eyebrow">{row["lineage"]} · {row["tempo"]}</div>
    <h3>{row["type"]}</h3>
    <p>{row["summary"]}</p>
    <br>
    <p><strong>危险程度：</strong>{row["risk_grade"]}</p>
    <p><strong>五年生存率统计：</strong>{row["five_year"]}</p>
    <p><strong>统计口径提醒：</strong>这是人群统计范围，不等于个人预后；个人风险需结合分期、年龄、体能、分子病理、治疗反应和合并症。</p>
    <br>
    <p><strong>预后：</strong>{row["prognosis_detail"]}</p>
{functional_html}
</div>
            """,
            unsafe_allow_html=True,
        )
    with detail_col2:
        st.markdown(
            f"""
<div class="card">
    <div class="eyebrow">Treatment pathway</div>
    <h3>治疗方案</h3>
    <p><strong>标准治疗思路：</strong>{row["standard_treatment"]}</p>
    <br>
    <p><strong>一线方案：</strong>{row["first_line"]}</p>
    <br>
    <p><strong>二线 / 复发难治方案：</strong>{row["second_line"]}</p>
    <br>
    <p><strong>常见药物/方案成分：</strong>{row["drugs"]}</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    render_treatment_topic_buttons(relevant_treatment_topics(row), prefix=str(row["type"]))


def render_pre_diagnosis_details() -> None:
    st.markdown('<p class="section-title">常见症状</p>', unsafe_allow_html=True)
    symptom_tab, warning_tab = st.tabs(["症状线索", "何时尽快就医"])
    with symptom_tab:
        col1, col2, col3 = st.columns(3)
        with col1:
            card("淋巴结变化", "颈部、腋窝、腹股沟等部位无痛性肿大；如果持续增大、质地硬、固定不动或锁骨上淋巴结肿大，应尽快就诊。", "Lymph nodes")
        with col2:
            card("B 症状", "原因不明发热、夜间盗汗到浸湿衣物、6 个月内非刻意体重下降超过约 10%。这些信息会影响分期和风险判断。", "B symptoms")
        with col3:
            card("全身表现", "持续疲劳、皮肤瘙痒、食欲下降、腹胀或脾大、反复感染、瘀斑出血，也可能和血液系统问题有关。", "Systemic")
        card("压迫或结外症状", "胸闷咳嗽、气短、腹痛腹胀、骨痛、皮肤结节、头痛或神经功能改变，可能提示胸腹腔或结外部位受累。", "Extranodal")
    with warning_tab:
        st.markdown(
            """
<div class="danger-note">
    这些症状并不等于淋巴瘤，也可能来自感染、自身免疫病或其他肿瘤。关键是持续、进展、伴随 B 症状或影响器官功能时，尽快让医生评估。
</div>
            """,
            unsafe_allow_html=True,
        )


def render_testing_details() -> None:
    st.markdown('<p class="section-title">检查阶段：更具体要看什么</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="notice">
    淋巴瘤诊断通常不是靠一个血液指标或一次 PET-CT 完成，而是把症状、体检、影像、活检病理、免疫表型和必要的遗传学检测拼在一起判断。
</div>
        """,
        unsafe_allow_html=True,
    )

    baseline_tab, pathology_tab, pet_tab = st.tabs(["基础检查", "病理/基因", "PET-CT"])
    with baseline_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
<div class="card">
    <div class="eyebrow">Baseline workup</div>
    <h3>基础检查</h3>
    <p><strong>血液：</strong>血常规、肝肾功能、LDH、尿酸、电解质、β2 微球蛋白、感染筛查等。</p>
    <p><strong>体格检查：</strong>淋巴结区域、肝脾大小、皮肤、神经系统表现。</p>
    <p><strong>骨髓：</strong>部分类型或影像提示时会做骨髓穿刺/活检。</p>
</div>
            """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
<div class="card">
    <div class="eyebrow">Tissue is key</div>
    <h3>活检和病理</h3>
    <p><strong>首选：</strong>能取到足够组织的切除活检或粗针活检；细针穿刺有时不足以完成分型。</p>
    <p><strong>病理报告：</strong>通常包括形态学、免疫组化、增殖指数、必要时流式、FISH、PCR 或 NGS。</p>
    <p><strong>会诊：</strong>结果不典型或治疗重大时，病理会诊很常见。</p>
</div>
            """,
                unsafe_allow_html=True,
            )

    with pathology_tab:
        path_cols = st.columns(3)
        with path_cols[0]:
            card("免疫组化 IHC", "常见标志包括 CD20、CD3、CD5、CD10、BCL6、MUM1、BCL2、Cyclin D1、SOX11、CD30、Ki-67、EBER 等，用来判断细胞来源和亚型。", "IHC")
        with path_cols[1]:
            card("流式细胞术", "看单个细胞表达哪些标志物，帮助判断 B/T/NK 来源、轻链限制、异常抗原表达和克隆性。它常作为病理分型的辅助证据。", "Flow")
        with path_cols[2]:
            card("FISH / 基因检测", "常见关注 MYC、BCL2、BCL6 重排，t(11;14)/CCND1-IGH，ALK，TP53、MYD88、EZH2、CARD11、CD79B 等；不是每个人都需要同一套检测。", "Genetics")

        render_genotype_guide()

        st.markdown('<p class="section-title">流式细胞术：样本从哪里来</p>', unsafe_allow_html=True)
        flow_cols = st.columns(3)
        with flow_cols[0]:
            card("外周血", "血液里已有异常淋巴细胞时可做，常见于 CLL/SLL、白血病样表现或血液受累评估。", "Blood")
        with flow_cols[1]:
            card("骨髓样本", "通过骨髓穿刺/活检取得，用于判断骨髓是否受累，尤其在分期、血细胞异常或某些亚型中常见。", "Bone marrow")
        with flow_cols[2]:
            card("脑脊液 CSF", "通过腰穿取得，用于怀疑中枢神经系统受累、PCNSL、头痛/神经症状或高危 CNS 风险评估。", "CSF")
        flow_cols_2 = st.columns(2)
        with flow_cols_2[0]:
            card("淋巴结/肿块新鲜组织", "粗针或切除活检取得的新鲜组织可送流式；但最终分型仍依赖组织结构、形态学和免疫组化。", "Tissue")
        with flow_cols_2[1]:
            card("胸腹水等体液", "胸水、腹水、玻璃体液等也可做流式，用于判断是否有淋巴瘤细胞受累。", "Body fluid")

    with pet_tab:
        pet_col1, pet_col2 = st.columns([1, 1])
        with pet_col1:
            st.markdown(
                """
<div class="card">
    <div class="eyebrow">Staging</div>
    <h3>分期看范围，不只看 SUV</h3>
    <p>PET-CT 用 FDG 摄取显示代谢活跃病灶，帮助判断淋巴结区域、结外器官、骨髓等是否受累。</p>
    <p><strong>I 期：</strong>单一区域；<strong>II 期：</strong>膈肌同侧多个区域；<strong>III 期：</strong>膈肌两侧；<strong>IV 期：</strong>弥漫性结外器官受累。</p>
    <p>医生还会看肿块大小、是否 bulky、结外受累、B 症状、LDH 和病理亚型。</p>
</div>
            """,
                unsafe_allow_html=True,
            )
        with pet_col2:
            st.markdown(
                """
<div class="card">
    <div class="eyebrow">Response</div>
    <h3>Deauville 评分</h3>
    <p><strong>1：</strong>无异常摄取；<strong>2：</strong>摄取不高于纵隔血池；<strong>3：</strong>高于纵隔但不高于肝脏；<strong>4：</strong>中度高于肝脏；<strong>5：</strong>明显高于肝脏或出现新病灶。</p>
    <p>对于多数 FDG 高摄取淋巴瘤，治疗后 Deauville 1-3 常被视为完全代谢缓解；4-5 需要结合治疗时间点、炎症、感染和病灶位置综合判断。</p>
    <p>SUVmax 不能单独决定诊断或复发，报告里的分布、CT 结构改变和对比前片更重要。</p>
</div>
            """,
                unsafe_allow_html=True,
            )


def render_glossary() -> None:
    st.markdown('<p class="section-title">术语小词典</p>', unsafe_allow_html=True)
    terms = list(GLOSSARY.items())
    for start in range(0, len(terms), 2):
        cols = st.columns(2)
        for offset, (term, explanation) in enumerate(terms[start:start + 2]):
            with cols[offset]:
                card(term, explanation, "Term")


def render_genotype_guide() -> None:
    st.markdown('<p class="section-title">常见基因型 / 分子标志说明</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="notice">
    基因型结果通常用于辅助诊断、风险分层和治疗选择。它不能脱离病理形态、免疫组化、分期和临床表现单独解读。
</div>
        """,
        unsafe_allow_html=True,
    )
    for item in GENOTYPE_GUIDE:
        with st.expander(item["name"]):
            st.markdown(f'**常见于：** {item["seen_in"]}')
            st.markdown(f'**是什么意思：** {item["meaning"]}')
            st.markdown(f'**为什么重要：** {item["why_it_matters"]}')


inject_styles()

with st.sidebar:
    st.markdown("### 淋巴瘤路径导航器")
    st.caption("给患者和家属看的简明科普导航")
    selected = st.radio("导航", PAGES, index=PAGES.index(current_page()), label_visibility="collapsed")
    set_page(selected)
    st.markdown("---")
    st.caption("仅供健康科普参考，不能替代医生诊断或治疗建议。")


page = current_page()
render_global_nav()


if page == "首页":
    st.markdown(
        """
<div class="hero">
    <div class="eyebrow">Patient education navigator</div>
    <h1>淋巴瘤路径导航器</h1>
    <p>把“现在该做什么”拆成更清楚的步骤：识别症状、完成关键检查、理解分型分期、比较治疗方案和处理副作用。</p>
</div>
<div class="stat-row">
    <div class="stat"><strong>4 个阶段</strong><span>未确诊、检查中、已确诊、治疗中</span></div>
    <div class="stat"><strong>13 类亚型</strong><span>B 细胞、T/NK 细胞、霍奇金淋巴瘤</span></div>
    <div class="stat"><strong>17 个方案</strong><span>MTX、R-CHOP、CAR-T、移植等</span></div>
    <div class="stat"><strong>支持处理</strong><span>发热、血象低、恶心、CRS 等</span></div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hero-actions">', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        if st.button("开始路径导航", use_container_width=True):
            set_page("路径导航")
            st.rerun()
    with col_b:
        if st.button("查看分类图谱", use_container_width=True):
            set_page("分类图谱")
            st.rerun()
    with col_c:
        if st.button("治疗方案库", use_container_width=True):
            set_page("治疗方案库")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
<div class="workbench">
    <div class="route-card">
        <div class="eyebrow">Start here</div>
        <h3>推荐使用顺序</h3>
        <ol>
            <li>先进入路径导航，按当前阶段看重点。</li>
            <li>拿到病理后，在已确诊阶段选择亚型。</li>
            <li>点相关治疗方案，查看药物和副作用处理。</li>
            <li>需要横向比较时，再看分类图谱。</li>
        </ol>
    </div>
    <div class="route-card">
        <div class="eyebrow">Safety</div>
        <h3>需要尽快联系医生</h3>
        <ol>
            <li>发热、寒战、呼吸困难或意识改变。</li>
            <li>淋巴结快速增大、胸闷气短或神经症状。</li>
            <li>治疗后出血不止、严重腹泻或无法饮水。</li>
        </ol>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="notice">
    如果出现持续淋巴结肿大、原因不明发热、盗汗或体重下降，请尽快到血液科、肿瘤科或相关专科就诊。
</div>
        """,
        unsafe_allow_html=True,
    )


elif page == "路径导航":
    page_intro("路径导航", "选择最接近你目前情况的阶段。页面先给下一步重点，再展开症状、检查、病理、PET-CT、治疗和副作用处理。", "Care pathway")

    stage = st.radio("当前阶段", STAGES, horizontal=True)

    stage_content = {
        "未确诊": {
            "tag": "先确认风险",
            "title": "未确诊阶段",
            "intro": "这个阶段最重要的是识别持续或进展性症状，把线索交给专科医生判断，不要只靠网络信息自我诊断。",
            "steps": [
                ("记录症状", "写下淋巴结位置、大小变化，以及发热、盗汗、体重下降、瘙痒、乏力等情况。"),
                ("预约专科", "优先考虑血液科、肿瘤科，或由全科/内科医生转诊。"),
                ("准备资料", "带上既往影像、化验单、用药史和过敏史。"),
            ],
            "callout": "持续增大、质地较硬、无痛性淋巴结，或伴随全身症状时，应尽快就医。",
        },
        "检查中": {
            "tag": "等待结果",
            "title": "检查阶段",
            "intro": "检查中的焦虑很常见。关键是确认是否有足够组织做分型，并用影像和实验室检查完成分期与风险评估。",
            "steps": [
                ("确认活检", "活检是确诊和分型的关键，尽量取得足够组织完成免疫组化和必要遗传学检测。"),
                ("整理影像", "CT、PET-CT、超声等用于判断病灶分布、结外受累和治疗前基线。"),
                ("追踪病理", "询问是否包含 IHC、流式、FISH、PCR/NGS，以及是否需要病理会诊。"),
            ],
            "callout": "如果病理结果只写“可疑”或“倾向”，可以询问医生是否需要补取组织、补做检测或病理会诊。",
        },
        "已确诊": {
            "tag": "制定方案",
            "title": "已确诊阶段",
            "intro": "确诊后不要只看一个疾病名称，还要理解分型、分期、风险评估和身体基础情况。",
            "steps": [
                ("确认分型", "不同淋巴瘤类型治疗节奏差异很大。"),
                ("完成分期", "医生通常会结合影像、骨髓或实验室检查评估疾病范围。"),
                ("讨论治疗", "把疗效目标、周期安排、常见副作用和复查计划问清楚。"),
            ],
            "callout": "如果已经知道病理亚型，可以在下方查看预后、治疗路径和相关方案详情。",
        },
        "治疗中": {
            "tag": "管理治疗",
            "title": "治疗阶段",
            "intro": "治疗期间的目标是按计划完成疗程，同时及时处理感染、发热、血象下降等风险。",
            "steps": [
                ("记录反应", "记录发热、乏力、恶心、疼痛、皮疹等变化。"),
                ("按时复查", "遵医嘱完成血常规、肝肾功能和影像评估。"),
                ("及时沟通", "出现发热、严重腹泻、呼吸困难等情况应及时联系医生。"),
            ],
            "callout": "不要自行停药或调整方案；任何补充剂、草药或新药都应先告知医生。",
        },
    }

    data = stage_content[stage]
    st.markdown(
        (
            '<div class="stage-panel">'
            '<div class="stage-header">'
            '<div>'
            f'<div class="eyebrow">{data["tag"]}</div>'
            f'<h2>{data["title"]}</h2>'
            f'<p class="subtle">{data["intro"]}</p>'
            '</div>'
            f'<div class="pill">{stage}</div>'
            '</div>'
            '<div class="steps">'
            f'{"".join(step(i + 1, title, body) for i, (title, body) in enumerate(data["steps"]))}'
            '</div>'
            f'<div class="callout">{data["callout"]}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    if stage == "未确诊":
        render_pre_diagnosis_details()

    elif stage == "检查中":
        render_testing_details()
        render_glossary()

    if stage == "已确诊":
        df = lymphoma_frame()
        lymphoma = st.selectbox(
            "如果已经知道类型，可以选择查看预后和治疗路径",
            ["不清楚"] + df["type"].tolist(),
        )

        if lymphoma == "不清楚":
            st.info("如果病理报告还没有明确亚型，下一步重点是确认完整病理、免疫组化、必要的分子检测和分期评估。")
        else:
            selected_row = df[df["type"] == lymphoma].iloc[0]
            st.markdown('<p class="section-title">分型后的治疗路径</p>', unsafe_allow_html=True)
            render_subtype_pathway(selected_row)


elif page == "分类图谱":
    df = lymphoma_frame()

    page_intro("分类图谱", "淋巴瘤不是一个单一疾病。先看大类和细胞来源，再结合惰性/侵袭性、分期、病理和患者情况制定方案。", "Classification")

    st.markdown(
        """
<div class="taxonomy">
    <div class="taxonomy-node root">
        <div class="eyebrow">Root</div>
        <h3>淋巴瘤</h3>
        <p>起源于淋巴细胞的血液系统肿瘤，确诊依赖病理活检。</p>
    </div>
    <div class="taxonomy-node">
        <div class="eyebrow">Major groups</div>
        <h3>先分大类</h3>
        <div class="mini-list">
            <span>霍奇金淋巴瘤（HL）</span>
            <span>非霍奇金淋巴瘤（NHL）</span>
        </div>
    </div>
    <div class="taxonomy-node">
        <div class="eyebrow">Cell lineage</div>
        <h3>再看来源</h3>
        <div class="mini-list">
            <span>B 细胞</span>
            <span>T 细胞 / NK 细胞</span>
            <span>经典 HL / NLPHL</span>
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="notice">
    下方图表是帮助理解分类和临床节奏的教育示意图，不代表个人预后，也不等同于真实发病率统计。
</div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("参考来源"):
        st.markdown(
            """
- [NCI Adult Non-Hodgkin Lymphoma Treatment PDQ](https://www.cancer.gov/types/lymphoma/patient/adult-nhl-treatment-pdq)
- [NCI Aggressive B-Cell Non-Hodgkin Lymphoma Treatment PDQ](https://www.cancer.gov/types/lymphoma/hp/aggressive-b-cell-lymphoma-treatment-pdq)
- [American Cancer Society: Types of B-cell Lymphoma](https://www.cancer.org/cancer/types/non-hodgkin-lymphoma/about/b-cell-lymphoma.html)
- [Leukemia & Lymphoma Society: T-cell Lymphomas](https://www.lls.org/article/t-cell-lymphomas-tcl)
            """
        )

    st.markdown('<p class="section-title">图示对比</p>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns([1, 1.25])
    with chart_col1:
        st.markdown('<div class="chart-panel"><h3>本页示例覆盖</h3><p class="subtle">按大类统计当前列出的示例亚型数量。</p>', unsafe_allow_html=True)
        render_lineage_chart(df)
        st.markdown("</div>", unsafe_allow_html=True)
    with chart_col2:
        st.markdown('<div class="chart-panel"><h3>临床节奏示意</h3><p class="subtle">越靠右上，越倾向需要更快专科评估。</p>', unsafe_allow_html=True)
        render_tempo_chart(df)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-panel"><h3>观察随访可能性示意</h3><p class="subtle">某些惰性类型在无症状、低负荷时可能先观察；具体必须由医生判断。</p>', unsafe_allow_html=True)
    render_watchful_chart(df)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<p class="section-title">亚型速查</p>', unsafe_allow_html=True)
    lineage_filter = st.segmented_control(
        "筛选分类",
        ["全部", "B细胞 NHL", "T/NK细胞 NHL", "霍奇金淋巴瘤"],
        default="全部",
    )
    display_df = df if lineage_filter == "全部" else df[df["lineage"] == lineage_filter]
    subtype_options = display_df["type"].tolist()
    default_subtype = "原发性中枢神经系统淋巴瘤（PCNSL）"
    subtype_index = subtype_options.index(default_subtype) if default_subtype in subtype_options else 0
    selected_subtype = st.selectbox("选择一个亚型查看详情", subtype_options, index=subtype_index)
    selected_row = display_df[display_df["type"] == selected_subtype].iloc[0]
    render_subtype_pathway(selected_row)

    with st.expander("打开亚型总览表"):
        st.dataframe(
            display_df[
                [
                    "type",
                    "lineage",
                    "tempo",
                    "risk_grade",
                    "five_year",
                    "summary",
                    "prognosis_detail",
                    "standard_treatment",
                    "first_line",
                    "second_line",
                    "drugs",
                ]
            ],
            column_config={
                "type": "亚型",
                "lineage": "大类",
                "tempo": "临床节奏",
                "risk_grade": "危险程度",
                "five_year": "五年生存率统计",
                "summary": "一句话理解",
                "prognosis_detail": "预后",
                "standard_treatment": "标准治疗思路",
                "first_line": "一线方案",
                "second_line": "二线/复发难治方案",
                "drugs": "常见药/方案成分",
            },
            hide_index=True,
            use_container_width=True,
        )

    with st.expander("打开全部亚型文字说明"):
        for row in display_df.to_dict("records"):
            st.markdown(f'**{row["type"]} · {row["tempo"]}**')
            st.write(row["summary"])
            st.caption(f'分类：{row["lineage"]} · 进展速度示意：{row["tempo_score"]}/5 · 紧迫度示意：{row["urgency"]}/5')
            st.markdown("---")

    with st.expander("打开术语小词典"):
        render_glossary()


elif page == "治疗方案库":
    selected_topic = current_treatment_topic()
    topic_names = {topic_id: topic["name"] for topic_id, topic in TREATMENT_LIBRARY.items()}
    topic_ids = list(TREATMENT_LIBRARY.keys())

    st.title("治疗方案库")
    return_page = st.session_state.get("return_page")
    if return_page in PAGES and return_page != "治疗方案库":
        if st.button(f"返回{return_page}", use_container_width=False, key="return_source_page"):
            set_page(return_page)
            st.rerun()
    st.markdown(
        '<p class="subtle">这里是站内科普页，用来解释方案是什么、常用于哪里、需要监测什么。具体用药和剂量必须由医生按个人情况决定。</p>',
        unsafe_allow_html=True,
    )

    selected_name = st.selectbox(
        "选择方案",
        [topic_names[topic_id] for topic_id in topic_ids],
        index=topic_ids.index(selected_topic),
    )
    selected_topic = next(topic_id for topic_id, name in topic_names.items() if name == selected_name)
    st.session_state.treatment_topic = selected_topic
    render_treatment_detail(selected_topic)
