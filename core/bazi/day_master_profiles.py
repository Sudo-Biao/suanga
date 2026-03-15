"""
core/bazi/day_master_profiles.py
=================================
Professional-depth profiles for all 10 Heavenly Stem day masters.
Covers: personality, strengths/weaknesses, useful god (用神喜忌),
career tendencies, health focus, relationship style, color/direction/number.
"""
from __future__ import annotations
from typing import Dict, Any, List

# ─────────────────────────────────────────────────────────────
# Complete day-master profiles
# ─────────────────────────────────────────────────────────────

DAY_MASTER_PROFILES: Dict[str, Dict[str, Any]] = {
    "甲": {
        "element": "木", "yin_yang": "阳",
        "symbol": "参天大树",
        "title": "甲木日主 · 参天大树",
        "core_traits": "刚直不阿，志向高远，领导力强，富有责任感，处事雷厉风行",
        "strengths": ["领导魄力出众", "意志坚定，不轻易妥协", "富有开拓精神", "正直守信，重视原则"],
        "weaknesses": ["固执己见，难以变通", "易与人冲突，不善妥协", "过于理想化", "承压时容易折断"],
        "personality_detail": "甲木为阳木，如高大挺拔之乔木，有君子之风。性格直率，嫉恶如仇，不善于迂回策略。做事主动积极，但有时过于强势。内心深处渴望得到认可与尊重。",
        "career": {
            "best_fields": ["政界仕途", "企业管理", "法律司法", "医疗卫生（外科）", "教育行政", "军警"],
            "work_style": "擅长开创局面，适合担任领导岗位；不喜受制约，自由空间越大越能发挥",
            "wealth_approach": "正直求财，不善投机取巧，收入较稳定",
        },
        "health": {
            "vulnerable_organs": ["肝胆", "筋脉", "眼睛"],
            "common_issues": "肝火旺盛、眼疾、神经系统疾病、筋骨扭伤",
            "health_advice": "保持情绪平稳，忌怒；多做舒展性运动如瑜伽、太极；忌熬夜；宜食酸味、绿色蔬菜",
        },
        "relationships": {
            "style": "主动追求，重视承诺；对伴侣有较高要求；有时过于强势导致关系紧张",
            "ideal_partner_wx": "土（被木克，需要约束甲木的强势）或水（滋养木，相辅相成）",
            "male_spouse_star": "己土",
            "female_spouse_star": "庚金",
        },
        "lucky": {
            "colors": ["绿色", "青色", "黑色（水生木）"],
            "directions": ["东方（本气）", "北方（水生木）"],
            "numbers": [3, 8],
            "season": "春季",
        },
        "useful_god_guide": {
            "strong": "甲木身强，喜金（克木）、土（泄木）、火（食伤泄秀）为用神；忌水（太多生木更旺）、木（比劫争财）",
            "weak": "甲木身弱，喜水（印星生扶）、木（比劫帮身）为用神；忌金（克身）、土（财星耗身）、火（食伤盗气）",
            "neutral": "以月令为主，结合格局综合论断",
        },
    },

    "乙": {
        "element": "木", "yin_yang": "阴",
        "symbol": "柔弱花草",
        "title": "乙木日主 · 柔弱花草",
        "core_traits": "柔韧温和，善于变通，富有韧性，审时度势，处事圆滑",
        "strengths": ["善于交际，人缘极佳", "柔中带刚，韧性超强", "随机应变，适应力强", "心思细腻，富有艺术气质"],
        "weaknesses": ["意志力不如甲木坚定", "有时优柔寡断", "易受他人影响", "过于依赖外部环境"],
        "personality_detail": "乙木为阴木，如藤蔓花草，善于攀附向上。表面温柔，内心却有坚韧不拔的生命力。善于在复杂环境中找到生存之道，有很强的适应能力。",
        "career": {
            "best_fields": ["文学艺术", "美容美发", "外交公关", "教育培训", "中医养生", "设计创意"],
            "work_style": "适合辅助性、创意性工作；擅长团队协作；需要稳定的环境才能充分发挥",
            "wealth_approach": "善于利用人际关系求财，适合薪资型收入",
        },
        "health": {
            "vulnerable_organs": ["肝胆", "神经系统", "肌肉"],
            "common_issues": "肝郁气滞、焦虑抑郁倾向、头痛、颈椎问题",
            "health_advice": "注重情志调节，多接触大自然；避免久坐；宜食酸味食物；保持规律作息",
        },
        "relationships": {
            "style": "温柔体贴，善于经营感情；感情依赖性较强；对伴侣忠诚",
            "ideal_partner_wx": "火（木生火，相生）或水（水生木，有依靠）",
            "male_spouse_star": "戊土",
            "female_spouse_star": "庚金、辛金",
        },
        "lucky": {
            "colors": ["绿色", "青色", "黄色"],
            "directions": ["东方", "东南方"],
            "numbers": [3, 8],
            "season": "春季",
        },
        "useful_god_guide": {
            "strong": "乙木身强，喜庚辛金（克木）、戊己土（财星）、丙丁火（食伤）为用；忌壬癸水（印星更旺）",
            "weak": "乙木身弱，喜壬癸水（印星滋养）、甲乙木（比劫帮身）、寅卯辰（根气）为用；忌金（克伐）",
            "neutral": "春木当令身旺，以火土为用；冬木气弱，以水木为用",
        },
    },

    "丙": {
        "element": "火", "yin_yang": "阳",
        "symbol": "烈日骄阳",
        "title": "丙火日主 · 烈日骄阳",
        "core_traits": "热情开朗，慷慨大方，光明磊落，思维敏锐，行动力极强",
        "strengths": ["个人魅力超强，善于展现自我", "热情待人，感染力强", "思维活跃，创意丰富", "光明正大，不屑于阴谋"],
        "weaknesses": ["性格急躁，缺乏耐心", "冲动易怒", "有时过于张扬", "缺乏持续力，虎头蛇尾"],
        "personality_detail": "丙火为阳火，如烈日当空，光芒四射。生性热情奔放，善于社交，天生具有领袖气质。处事正大光明，嫉恶如仇，但有时失于莽撞。",
        "career": {
            "best_fields": ["演艺娱乐", "IT科技", "能源电力", "金融投资", "广告传媒", "餐饮业"],
            "work_style": "适合表现型、创意型工作；善于开拓，不适合细致繁琐的工作",
            "wealth_approach": "敢于冒险投资，财来财去，大起大落",
        },
        "health": {
            "vulnerable_organs": ["心脏", "小肠", "血液循环", "眼睛"],
            "common_issues": "心脑血管疾病、高血压、失眠、皮肤炎症",
            "health_advice": "避免过度兴奋激动；忌辛辣燥热食物；保证充足睡眠；宜食苦味食物如苦瓜",
        },
        "relationships": {
            "style": "主动热情，追求轰轰烈烈的爱情；但激情消退后易生厌倦",
            "ideal_partner_wx": "木（印星支持）或土（食伤泄秀，平衡火气）",
            "male_spouse_star": "辛金",
            "female_spouse_star": "壬水",
        },
        "lucky": {
            "colors": ["红色", "橙色", "紫色", "绿色（木生火）"],
            "directions": ["南方（本气）", "东方（木生火）"],
            "numbers": [2, 7],
            "season": "夏季",
        },
        "useful_god_guide": {
            "strong": "丙火身强，喜壬水（官星制火）、庚辛金（财星）、戊己土（食伤泄秀）为用；忌甲乙木（印星更旺）",
            "weak": "丙火身弱，喜甲乙木（印星生火）、丙丁火（比劫助身）为用；忌壬水（克制）、金（财多身弱）",
            "neutral": "夏季丙火旺，以水金为用；冬季丙火弱，需木火扶助",
        },
    },

    "丁": {
        "element": "火", "yin_yang": "阴",
        "symbol": "灯烛之火",
        "title": "丁火日主 · 灯烛之火",
        "core_traits": "温暖细腻，善解人意，直觉敏锐，内敛而有深度，艺术气质浓厚",
        "strengths": ["情感丰富，善于体察他人感受", "直觉力极强", "艺术天分高", "坚持不懈，锲而不舍"],
        "weaknesses": ["情绪化，易受外界影响", "思虑过多，容易焦虑", "有时过于内向", "经不起挫折打击"],
        "personality_detail": "丁火为阴火，如蜡烛之光，温暖而持久。性格温柔细腻，但内心深处有颇为坚韧的一面。对美好事物有超强感知力，常是艺术、文学领域的天才。",
        "career": {
            "best_fields": ["艺术文学", "心理咨询", "珠宝首饰", "中医针灸", "宗教哲学", "教育培训"],
            "work_style": "适合精细化工作；擅长独立钻研；需要情感认同感才能发挥最佳",
            "wealth_approach": "不善于大规模经营，适合技艺型收入",
        },
        "health": {
            "vulnerable_organs": ["心脏", "血液", "眼睛", "小肠"],
            "common_issues": "心血管疾病、贫血、神经衰弱、眼部问题",
            "health_advice": "保持情绪稳定；注意补血养心；避免过度用眼；宜食红色食物如红枣、枸杞",
        },
        "relationships": {
            "style": "深情专一，感情细腻丰富；对爱情理想化，易受伤",
            "ideal_partner_wx": "木（印星滋养）或土（食伤平衡，接地气）",
            "male_spouse_star": "庚金",
            "female_spouse_star": "壬水、癸水",
        },
        "lucky": {
            "colors": ["红色", "紫色", "粉色"],
            "directions": ["南方", "东方"],
            "numbers": [2, 7],
            "season": "夏季",
        },
        "useful_god_guide": {
            "strong": "丁火身强，喜壬癸水（官印为用）、庚辛金（财星）为用；忌乙木透干（枭印夺食）",
            "weak": "丁火身弱，喜甲乙木（印星）、丙丁火（比劫）为用；甲木最佳，无甲用乙",
            "neutral": "丁火喜甲木引通，最忌壬水混局",
        },
    },

    "戊": {
        "element": "土", "yin_yang": "阳",
        "symbol": "厚重山岳",
        "title": "戊土日主 · 厚重山岳",
        "core_traits": "稳重厚实，值得信赖，耐力超群，包容宽厚，守信重义",
        "strengths": ["极强的稳定性和耐久力", "包容心强，不计小节", "守信用，重承诺", "脚踏实地，实干精神"],
        "weaknesses": ["反应较慢，灵活性不足", "固执保守，难以接受新事物", "有时显得迟钝或固执", "过于谨慎导致错失机遇"],
        "personality_detail": "戊土为阳土，如高山巍峨，稳重厚实。性格沉稳，处事老成，是值得信赖的朋友。做事认真负责，但节奏较慢，不擅长灵活变通。",
        "career": {
            "best_fields": ["房地产建筑", "农业林业", "仓储物流", "政府机关", "金融银行（稳健型）", "矿产资源"],
            "work_style": "适合需要稳定性和耐力的岗位；执行力强；适合长期项目",
            "wealth_approach": "稳健积累，不喜冒险；适合固定资产投资",
        },
        "health": {
            "vulnerable_organs": ["脾胃", "肌肉", "消化系统"],
            "common_issues": "脾胃虚弱、消化不良、肥胖、糖尿病倾向、湿气重",
            "health_advice": "规律饮食，避免暴饮暴食；忌生冷食物；适度运动，避免久坐；多食黄色食物",
        },
        "relationships": {
            "style": "稳重踏实，感情忠诚；追求稳定安全的婚姻；有时表达感情不够直接",
            "ideal_partner_wx": "火（印星滋养）或木（官星约束，增添活力）",
            "male_spouse_star": "癸水",
            "female_spouse_star": "甲木",
        },
        "lucky": {
            "colors": ["黄色", "棕色", "橙色", "红色（火生土）"],
            "directions": ["中央", "西南方", "东北方"],
            "numbers": [5, 10],
            "season": "四季末（辰戌丑未月）",
        },
        "useful_god_guide": {
            "strong": "戊土身强，喜甲乙木（疏土为官杀）、壬癸水（财星）、庚辛金（食伤泄秀）为用",
            "weak": "戊土身弱，喜丙丁火（印星）、戊己土（比劫）为用；忌水多土荡、木多土崩",
            "neutral": "戊土以火为最重要的生扶，无丙火则多数身弱",
        },
    },

    "己": {
        "element": "土", "yin_yang": "阴",
        "symbol": "平原田地",
        "title": "己土日主 · 平原田地",
        "core_traits": "温柔体贴，善解人意，踏实勤劳，善于养育他人，谦虚谨慎",
        "strengths": ["细心耐心，善于照顾他人", "踏实勤勉，不辞辛苦", "谦虚低调，善于合作", "感性丰富，具有母性光辉"],
        "weaknesses": ["缺乏主见，容易优柔寡断", "过于保守，缺乏冒险精神", "有时过于谦卑，吃亏而不自知", "边界感弱，难以拒绝他人"],
        "personality_detail": "己土为阴土，如肥沃田地，滋养万物。性格温柔善良，乐于助人，但有时缺乏主见。心思细腻，善于察言观色，是天生的调和者。",
        "career": {
            "best_fields": ["医护卫生", "教育幼教", "农业食品", "社会工作", "秘书文职", "餐饮行业"],
            "work_style": "适合服务性、辅助性工作；执行力强但领导力一般",
            "wealth_approach": "保守理财，适合储蓄和固定收益型投资",
        },
        "health": {
            "vulnerable_organs": ["脾胃", "胰腺", "消化系统", "皮肤"],
            "common_issues": "消化功能弱、湿气重、皮肤问题、妇科（女性）",
            "health_advice": "忌食甜腻食物；注意祛湿；保持适量运动；多食健脾食物如薏米、山药",
        },
        "relationships": {
            "style": "温柔体贴，善于营造家庭温暖；感情付出多但有时换不来相应回报",
            "ideal_partner_wx": "火（印星）或木（疏通土气，增添活力）",
            "male_spouse_star": "壬水",
            "female_spouse_star": "甲木、乙木",
        },
        "lucky": {
            "colors": ["黄色", "米色", "棕色"],
            "directions": ["西南方", "东北方", "中央"],
            "numbers": [5, 10],
            "season": "四季末",
        },
        "useful_god_guide": {
            "strong": "己土身强，喜甲乙木（七杀制土）、壬癸水（财星）、庚辛金（食伤）为用",
            "weak": "己土身弱，喜丙丁火（印星）、己土（比劫）为用；甲己合化土时以水火调候",
            "neutral": "己土最喜丙火温暖，次喜甲木疏通，忌癸水泛滥",
        },
    },

    "庚": {
        "element": "金", "yin_yang": "阳",
        "symbol": "千锻精钢",
        "title": "庚金日主 · 千锻精钢",
        "core_traits": "刚强果断，义气重，行动力极强，嫉恶如仇，具有军人气质",
        "strengths": ["行动力强，雷厉风行", "义气深重，重情谊", "具有强烈正义感", "意志坚定，百折不挠"],
        "weaknesses": ["脾气刚烈，容易冲突", "缺乏变通，过于强硬", "感情用事，容易冲动", "有时过于强势，不近人情"],
        "personality_detail": "庚金为阳金，如百炼钢铁，刚强无比。性格直爽豪迈，义气当先。做事果断，有军人气质。但有时过于强硬，不懂变通，容易树敌。",
        "career": {
            "best_fields": ["军警消防", "冶金机械", "法律律师", "外科手术", "竞技体育", "金融期货"],
            "work_style": "适合需要决断力的岗位；执行力和行动力超强；不适合需要细心的文职",
            "wealth_approach": "敢于投资，行动迅速；但需防冲动亏损",
        },
        "health": {
            "vulnerable_organs": ["肺脏", "大肠", "皮肤", "骨骼"],
            "common_issues": "呼吸系统疾病、肠道问题、皮肤过敏、骨骼受伤",
            "health_advice": "注意保暖防寒；忌辛辣刺激；多做有氧运动；宜食白色食物如白木耳、莲藕",
        },
        "relationships": {
            "style": "重情义，对伴侣忠诚；但不擅长表达感情；有大男子主义倾向",
            "ideal_partner_wx": "火（克金，有约束）或水（金生水，泄秀）",
            "male_spouse_star": "乙木",
            "female_spouse_star": "丁火",
        },
        "lucky": {
            "colors": ["白色", "金色", "银色", "黄色（土生金）"],
            "directions": ["西方（本气）", "西北方", "西南方（土生金）"],
            "numbers": [4, 9],
            "season": "秋季",
        },
        "useful_god_guide": {
            "strong": "庚金身强，喜丁火（正官，淬炼成器）、甲乙木（财星）、壬水（食伤泄秀）为用",
            "weak": "庚金身弱，喜戊己土（印星生金）、庚辛金（比劫）为用；忌丁火（克身）、甲木（财重）",
            "neutral": "庚金最喜丁火煅炼，无丁则乏味；最忌多水泄气",
        },
    },

    "辛": {
        "element": "金", "yin_yang": "阴",
        "symbol": "珠玉宝石",
        "title": "辛金日主 · 珠玉宝石",
        "core_traits": "聪慧伶俐，外表温柔内心坚毅，自尊心强，有贵族气质，审美高雅",
        "strengths": ["聪明机智，反应敏捷", "审美品味高雅", "自尊心强，有骨气", "善于思考，逻辑严密"],
        "weaknesses": ["自尊心过强，容易受伤", "有时过于挑剔", "情绪化，腹中有委屈不易言说", "对外界评价过于敏感"],
        "personality_detail": "辛金为阴金，如珠玉宝石，外表圆润而内质坚硬。气质高雅，有贵族风范。聪明敏锐，但自尊心强，容易因他人言语而受伤。",
        "career": {
            "best_fields": ["珠宝首饰", "精密仪器", "医疗器械", "财务会计", "艺术美术", "音乐表演"],
            "work_style": "适合精细型工作；审美力强；适合独立工作或小团队",
            "wealth_approach": "精打细算，善于管理财务；但有时过于保守",
        },
        "health": {
            "vulnerable_organs": ["肺脏", "皮肤", "大肠", "鼻腔"],
            "common_issues": "呼吸道疾病、皮肤敏感、过敏症、鼻炎",
            "health_advice": "注意保护皮肤；避免空气污染；多食润肺食物；保持心情愉快，避免忧愁",
        },
        "relationships": {
            "style": "感情细腻，对伴侣有较高标准；忠诚但不轻易示弱",
            "ideal_partner_wx": "水（食伤泄秀，增添灵气）或土（印星稳定）",
            "male_spouse_star": "甲木",
            "female_spouse_star": "丙火",
        },
        "lucky": {
            "colors": ["白色", "金色", "粉色", "浅黄"],
            "directions": ["西方", "西北方"],
            "numbers": [4, 9],
            "season": "秋季",
        },
        "useful_god_guide": {
            "strong": "辛金身强，喜壬水（食神泄秀）、甲乙木（财星）、丙火（官星）为用",
            "weak": "辛金身弱，喜戊己土（印星）、庚辛金（比劫）为用；最忌丁火直克",
            "neutral": "辛金喜壬水洗淘，喜甲木疏财；丙火虽为正官，但辛金弱时需慎用",
        },
    },

    "壬": {
        "element": "水", "yin_yang": "阳",
        "symbol": "汪洋大海",
        "title": "壬水日主 · 汪洋大海",
        "core_traits": "聪慧过人，思维广博，善于谋划，适应力强，胸怀宽广，学习能力超强",
        "strengths": ["智慧超群，洞察力强", "包容性大，善于接纳不同观点", "学习能力极强", "临机应变，随机而动"],
        "weaknesses": ["有时过于散漫，缺乏专注", "多疑善变，不够专一", "主见不定，容易摇摆", "感情上花心"],
        "personality_detail": "壬水为阳水，如汪洋大海，深邃广博。智慧出众，学什么像什么，适应能力极强。胸怀宽广，善于接纳不同的人和事。但有时过于灵活，缺乏定力。",
        "career": {
            "best_fields": ["贸易流通", "传媒通讯", "外交旅游", "科研学术", "金融投资", "哲学宗教"],
            "work_style": "适合需要灵活变通的工作；不喜受束缚；跨行业能力强",
            "wealth_approach": "善于发现商机，但需防投机失败",
        },
        "health": {
            "vulnerable_organs": ["肾脏", "膀胱", "泌尿系统", "耳朵", "骨骼"],
            "common_issues": "肾虚肾亏、泌尿系统问题、腰痛、耳鸣",
            "health_advice": "注意保暖，尤其腰腹部；忌过劳；多食黑色食物如黑芝麻、黑豆；早睡养肾",
        },
        "relationships": {
            "style": "感情丰富，浪漫多情；但专一性稍差，感情经历复杂",
            "ideal_partner_wx": "木（水生木，泄秀）或金（金生水，印星支持）",
            "male_spouse_star": "丁火",
            "female_spouse_star": "戊土",
        },
        "lucky": {
            "colors": ["黑色", "深蓝", "白色（金生水）"],
            "directions": ["北方（本气）", "西方（金生水）"],
            "numbers": [1, 6],
            "season": "冬季",
        },
        "useful_god_guide": {
            "strong": "壬水身强，喜戊土（官杀制水）、丙丁火（财星）、甲乙木（食伤泄秀）为用",
            "weak": "壬水身弱，喜庚辛金（印星）、壬癸水（比劫）为用；申子辰三合水局亦佳",
            "neutral": "壬水喜戊土为堤坝，若无制则泛滥；喜庚金发源，则源源不绝",
        },
    },

    "癸": {
        "element": "水", "yin_yang": "阴",
        "symbol": "甘霖雨露",
        "title": "癸水日主 · 甘霖雨露",
        "core_traits": "聪明灵慧，善于观察，直觉敏锐，感情丰富，具有艺术家气质",
        "strengths": ["直觉力超强", "记忆力出众", "善于倾听，感同身受", "细腻敏感，富有创造力"],
        "weaknesses": ["感情脆弱，容易受伤", "优柔寡断，缺乏主见", "有时过于敏感多疑", "情绪起伏较大"],
        "personality_detail": "癸水为阴水，如雨露甘霖，润物无声。直觉敏锐，感受力极强，对他人情绪变化极为敏感。内心丰富细腻，是天生的艺术家和感性思考者。",
        "career": {
            "best_fields": ["心理咨询", "文学写作", "音乐艺术", "护理医疗", "哲学宗教", "科研探索"],
            "work_style": "适合需要感性和直觉的工作；需要安静的工作环境；协作能力强",
            "wealth_approach": "不擅长大规模经营，适合专业技能型收入",
        },
        "health": {
            "vulnerable_organs": ["肾脏", "泌尿系统", "生殖系统", "骨骼"],
            "common_issues": "肾虚、妇科疾病（女性）、关节炎、抑郁倾向",
            "health_advice": "注意补肾固本；保暖防寒；避免熬夜；保持情绪平稳；宜食黑色食物",
        },
        "relationships": {
            "style": "深情温柔，善解人意；感情细腻，容易患得患失",
            "ideal_partner_wx": "木（水生木，有归宿）或金（金生水，有依靠）",
            "male_spouse_star": "丙火",
            "female_spouse_star": "戊土、己土",
        },
        "lucky": {
            "colors": ["黑色", "深蓝", "藏青"],
            "directions": ["北方", "西方"],
            "numbers": [1, 6],
            "season": "冬季",
        },
        "useful_god_guide": {
            "strong": "癸水身强，喜戊土（官星制水）、丙丁火（财星）、甲乙木（食伤）为用；忌辛金泛水",
            "weak": "癸水身弱，喜庚辛金（印星生水）、壬癸水（比劫）为用",
            "neutral": "癸水最喜丙火为财，以庚辛金为印；戊土不透则水无制",
        },
    },
}


def get_day_master_profile(day_master: str) -> Dict[str, Any]:
    """Return the complete profile dict for a day master stem."""
    return DAY_MASTER_PROFILES.get(day_master, {})


# ─────────────────────────────────────────────────────────────
# Useful God Analysis (用神喜忌分析)
# ─────────────────────────────────────────────────────────────

def analyze_yong_shen(chart: dict) -> Dict[str, Any]:
    """
    Determine the Useful God (用神), Favorable Gods (喜神),
    and Taboo Gods (忌神/仇神) for a chart.
    
    Now integrates:
      - 《穷通宝鉴》调候用神（月令 × 日干）
      - 《子平真诠》格局用神
      - 《滴天髓》十天干喜忌论命
    """
    from core.constants import TIANGAN_WUXING, WUXING_SHENG, WUXING_KE
    dm = chart["day_master"]
    dm_wx = TIANGAN_WUXING[dm]
    month_dz = chart["month_pillar"]["dizhi"]
    strength = chart.get("strength", "中和")
    pattern  = chart.get("pattern", "")

    profile = DAY_MASTER_PROFILES.get(dm, {})
    guide = profile.get("useful_god_guide", {})

    # ── 1. 《穷通宝鉴》调候用神 ──────────────────────────────────
    tiao_hou_stem = ""   # 调候用神天干（如"癸"、"丙"）
    tiao_hou_desc = ""
    tiao_hou_wx   = ""
    try:
        from knowledge.bazi_classical import TIAO_HOU_TABLE
        tiao_hou_desc = TIAO_HOU_TABLE.get(dm, {}).get(month_dz, "")
        # Extract primary stem (first character that's a tiangan)
        _TIANGAN = "甲乙丙丁戊己庚辛壬癸"
        for ch in tiao_hou_desc:
            if ch in _TIANGAN:
                tiao_hou_stem = ch
                break
        if tiao_hou_stem:
            from core.constants import TIANGAN_WUXING
            tiao_hou_wx = TIANGAN_WUXING.get(tiao_hou_stem, "")
    except Exception:
        pass

    # ── 2. 《子平真诠》格局用神 ──────────────────────────────────
    gejv_info = {}
    gejv_yong_wx = ""
    try:
        from knowledge.bazi_classical import BAZIGE_SYSTEM
        gejv_data = BAZIGE_SYSTEM.get(pattern, {})
        if gejv_data:
            # Infer favorable wuxing from 喜 list
            xi_list = gejv_data.get("喜", [])
            for xi_item in xi_list:
                for wx, chars in {"木":["甲","乙","木"],"火":["丙","丁","火"],"土":["戊","己","土"],
                                  "金":["庚","辛","金"],"水":["壬","癸","水"]}.items():
                    if any(c in xi_item for c in chars):
                        gejv_yong_wx = wx
                        break
                if gejv_yong_wx:
                    break
            gejv_info = {
                "pattern":   pattern,
                "likes":     xi_list,
                "dislikes":  gejv_data.get("忌", []),
                "mouth":     gejv_data.get("口诀", ""),
            }
    except Exception:
        pass

    # ── 3. 《滴天髓》日干特性 ─────────────────────────────────────
    shigan_info = {}
    try:
        from knowledge.bazi_classical import SHIGAN_JIJUE
        shigan_info = SHIGAN_JIJUE.get(dm, {})
    except Exception:
        pass

    # ── 4. 综合推断用神五行 ──────────────────────────────────────
    # 优先级：调候 > 格局 > 强弱通用
    if tiao_hou_wx:
        yong_wx_final = tiao_hou_wx
        yong_source = f"《穷通宝鉴》调候：{tiao_hou_desc}"
    elif gejv_yong_wx:
        yong_wx_final = gejv_yong_wx
        yong_source = f"《子平真诠》{pattern}格局用神"
    elif strength == "身强":
        yong_wx_final = WUXING_KE.get(dm_wx, "")
        yong_source = "身强取官杀为用（扶抑用神）"
    else:
        yong_wx_final = WUXING_KE.get(WUXING_KE.get(dm_wx, ""), "")
        yong_source = "身弱取印绶为用（扶抑用神）"

    # Standard helper/drainer wuxing
    if strength == "身强":
        xi_wx   = WUXING_SHENG.get(dm_wx, "")
        ji_wx   = dm_wx
        chou_wx = WUXING_KE.get(WUXING_KE.get(dm_wx, ""), "")
        yong_desc = guide.get("strong", "")
    else:
        xi_wx   = dm_wx
        ji_wx   = WUXING_KE.get(dm_wx, "")
        chou_wx = WUXING_SHENG.get(dm_wx, "")
        yong_desc = guide.get("weak", "")

    WX_COLORS = {"木":"#27ae60","火":"#e74c3c","土":"#f39c12","金":"#95a5a6","水":"#3498db"}

    return {
        "yong_shen_wx":  yong_wx_final,
        "xi_shen_wx":    xi_wx,
        "ji_shen_wx":    ji_wx,
        "chou_shen_wx":  chou_wx,
        "strength":      strength,
        "analysis":      yong_desc or guide.get("neutral", ""),
        # 《穷通宝鉴》调候
        "tiao_hou": {
            "stem":   tiao_hou_stem,
            "wuxing": tiao_hou_wx,
            "desc":   tiao_hou_desc,
            "source": "《穷通宝鉴》",
        },
        # 《子平真诠》格局
        "gejv":     gejv_info,
        "yong_source": yong_source,
        # 《滴天髓》日干
        "shigan": {
            "jijue": shigan_info.get("口诀", ""),
            "xiji":  shigan_info.get("喜忌", ""),
        },
        "wuxing_colors": WX_COLORS,
        "recommendations": _get_yong_shen_recommendations(dm_wx, yong_wx_final, xi_wx, ji_wx),
    }



def _get_yong_shen_recommendations(dm_wx: str, yong: str, xi: str, ji: str) -> Dict[str, Any]:
    """Translate useful god wuxing into practical life recommendations."""
    from core.bazi.day_master_profiles import DAY_MASTER_PROFILES
    WX_DIRECTIONS = {"木": "东方", "火": "南方", "土": "中央/西南/东北", "金": "西方", "水": "北方"}
    WX_COLORS = {"木": "绿色/青色", "火": "红色/紫色", "土": "黄色/棕色", "金": "白色/金色", "水": "黑色/蓝色"}
    WX_SEASONS = {"木": "春季", "火": "夏季", "土": "四季末", "金": "秋季", "水": "冬季"}
    WX_CAREERS = {
        "木": "教育/文化/医疗/林业",
        "火": "科技/能源/餐饮/娱乐",
        "土": "地产/建筑/农业/政府",
        "金": "金融/法律/机械/军警",
        "水": "贸易/传媒/旅游/物流",
    }
    WX_NUMBERS = {"木": "3、8", "火": "2、7", "土": "5、10", "金": "4、9", "水": "1、6"}

    return {
        "lucky_direction": WX_DIRECTIONS.get(yong, "") + "（用神）",
        "lucky_color": WX_COLORS.get(yong, "") + "（用神）",
        "lucky_season": WX_SEASONS.get(yong, ""),
        "lucky_career": WX_CAREERS.get(yong, ""),
        "lucky_number": WX_NUMBERS.get(yong, ""),
        "avoid_direction": WX_DIRECTIONS.get(ji, "") + "（忌神）",
        "avoid_color": WX_COLORS.get(ji, "") + "（忌神）",
    }
