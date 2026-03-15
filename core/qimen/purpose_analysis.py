"""
core/qimen/purpose_analysis.py
================================
Purpose-specific QiMen DunJia analysis.
Provides professional advice for 6 major purposes:
  求财 / 感情 / 事业 / 出行 / 健康 / 学业

Also includes:
  • 三奇六仪 (Three Unusual + Six Ceremonies) stem interpretation
  • 伏吟/反吟 detection
  • Combined Star+Door+Deity interpretation matrix
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional

# ─────────────────────────────────────────────────────────────
# 1. 天干 (Stem) Detailed Meanings in QiMen Palaces
# ─────────────────────────────────────────────────────────────

QIMEN_STEM_MEANINGS: Dict[str, Dict[str, str]] = {
    "戊": {
        "category": "六仪", "nature": "吉",
        "desc": "戊为值符之宫，主贵人相助，诸事顺遂",
        "career": "利求官，有贵人提拔",
        "wealth": "可求财，正财有益",
        "detail": "戊土居中，主稳健。为六仪之首，与值符同宫，力量最强。利于求谋贵人，官事和顺。",
    },
    "己": {
        "category": "六仪", "nature": "凶",
        "desc": "己土阴柔，主隐秘、阴谋、口舌，诸事不明朗",
        "career": "阴险小人，防被欺骗",
        "wealth": "财路不明，暗中有损",
        "detail": "己土为阴，主遮掩隐藏。若与腾蛇同宫，主惊虚谎言；若与玄武同宫，主欺诈盗骗。",
    },
    "庚": {
        "category": "六仪", "nature": "凶",
        "desc": "庚金为白虎，主凶险、牢狱、阻格，诸事有碍",
        "career": "遇阻力大，有官非",
        "wealth": "财路受阻，不利求财",
        "detail": "庚金刚硬，主障碍阻格。凡事遇庚，必有阻碍。为六仪中最凶，主官司、刑伤、失败。",
    },
    "辛": {
        "category": "六仪", "nature": "凶",
        "desc": "辛金为刑伤之宿，主伤害、疾病、官司",
        "career": "有小人伤害，防刑伤",
        "wealth": "防财物损失，诉讼耗财",
        "detail": "辛金为刑，主伤残病痛。与白虎同宫更凶，主疾病灾祸。做事须防刀伤血光之灾。",
    },
    "壬": {
        "category": "六仪", "nature": "吉",
        "desc": "壬水为武曲，主财帛、贵人、智谋，利贸易商务",
        "career": "智谋过人，利商贸经营",
        "wealth": "正财偏财均可求",
        "detail": "壬水流动，主通达灵活。为六仪中求财最佳之星，利经商、贸易、出行、谋事。",
    },
    "癸": {
        "category": "六仪", "nature": "凶",
        "desc": "癸水为小耗，主阴私、小人、消耗",
        "career": "防小人背后使绊",
        "wealth": "财有小耗，宜守不宜进",
        "detail": "癸水为阴水，主阴私遮蔽。与玄武同宫主盗窃，与腾蛇同宫主虚惊，总体须防暗损。",
    },
    "乙": {
        "category": "三奇", "nature": "大吉",
        "desc": "乙奇为天乙，诸事皆吉，贵人相助，趋吉避凶",
        "career": "贵人提携，仕途亨通",
        "wealth": "财运大吉，偏财正财皆有",
        "detail": "乙为三奇之首（天奇）。见乙奇则诸事皆吉，贵人从四面八方而来，为奇门遁甲中最吉之干。",
    },
    "丙": {
        "category": "三奇", "nature": "大吉",
        "desc": "丙奇为地奇，主光明、文书、喜庆，大利功名",
        "career": "功名显达，文书顺利",
        "wealth": "进财有喜，但以正财为主",
        "detail": "丙为三奇之二（地奇）。丙奇光明磊落，利功名文书喜庆之事，但不如乙奇灵活。",
    },
    "丁": {
        "category": "三奇", "nature": "吉",
        "desc": "丁奇为人奇，主智慧、谋略、玄机，善处危局",
        "career": "聪明谋略得用，善化解危机",
        "wealth": "智取财富，善用谋略获利",
        "detail": "丁为三奇之末（人奇）。丁奇主谋略智慧，处危局而不乱。利出奇制胜之事，谋事宜密。",
    },
}

# ─────────────────────────────────────────────────────────────
# 2. 九星 Enriched Meanings
# ─────────────────────────────────────────────────────────────

STAR_DETAILED: Dict[str, Dict[str, Any]] = {
    "天蓬": {
        "nature": "凶", "element": "水", "palace": "坎一宫",
        "desc": "天蓬主盗贼、险阻、官司，出行遇险",
        "career": "防小人陷害，官非缠身", "wealth": "求财受阻，防被盗",
        "love": "感情有阻，易争吵", "health": "肾、泌尿系统需注意",
        "travel": "不宜出行，途中有险", "study": "学业受阻，难以专注",
    },
    "天芮": {
        "nature": "凶", "element": "土", "palace": "坤二宫",
        "desc": "天芮主疾病、小人、口舌",
        "career": "有小人背后作梗", "wealth": "财被耗散，防诈骗",
        "love": "感情不稳，口舌是非", "health": "脾胃、肌肉疾病注意",
        "travel": "出行有口舌，不顺利", "study": "需防同学竞争",
    },
    "天冲": {
        "nature": "吉", "element": "木", "palace": "震三宫",
        "desc": "天冲主奋发、争竞、进取，利武职、竞技",
        "career": "积极进取，升迁有望", "wealth": "主动求财，竞争获利",
        "love": "感情热烈，主动追求", "health": "肝胆功能需关注",
        "travel": "宜出行，行动力强", "study": "勤奋刻苦，成绩提升",
    },
    "天辅": {
        "nature": "吉", "element": "木", "palace": "巽四宫",
        "desc": "天辅主文昌、贵人、学问，利学业科举",
        "career": "贵人相助，文职晋升", "wealth": "文财两旺，利文化行业",
        "love": "感情稳定，有利婚事", "health": "整体健康，神经系统注意",
        "travel": "出行顺利，有贵人指路", "study": "学业大吉，考试利好",
    },
    "天禽": {
        "nature": "中", "element": "土", "palace": "中宫五",
        "desc": "天禽主中正、稳健，居中而定，随方化断",
        "career": "守成稳定，不宜冒进", "wealth": "稳中求财，保守理财",
        "love": "感情平稳，不急不躁", "health": "总体平稳，脾胃注意",
        "travel": "可行可不行，随缘而定", "study": "稳步提升，需持之以恒",
    },
    "天心": {
        "nature": "吉", "element": "金", "palace": "乾六宫",
        "desc": "天心主医卜、智慧、谋略，利求医问药",
        "career": "智慧谋略得用，适合策划", "wealth": "善谋财路，正偏财均有",
        "love": "理性处理感情，有贵人撮合", "health": "求医大吉，有良医妙药",
        "travel": "出行平安，有贵人照应", "study": "智慧出众，学习效率高",
    },
    "天柱": {
        "nature": "凶", "element": "金", "palace": "兑七宫",
        "desc": "天柱主破败、折损、口舌，百事不利",
        "career": "事业遇折，防背叛出卖", "wealth": "财运大损，慎防破财",
        "love": "感情破裂，口角争吵", "health": "肺部、皮肤、大肠注意",
        "travel": "不宜出行，途中有破损", "study": "学业退步，需重整状态",
    },
    "天任": {
        "nature": "吉", "element": "土", "palace": "艮八宫",
        "desc": "天任主稳固、田产、置业，利农业地产",
        "career": "稳健发展，适合长期经营", "wealth": "置业购房大吉，长期投资好",
        "love": "感情稳定踏实，适合谈婚论嫁", "health": "脾胃稳健，整体平稳",
        "travel": "出行平顺，适合回乡置业", "study": "踏实用功，成绩稳步提升",
    },
    "天英": {
        "nature": "中", "element": "火", "palace": "离九宫",
        "desc": "天英主文采、美誉、名声，利文职艺术",
        "career": "名声大振，适合文艺传媒", "wealth": "名利双收，但财来财去",
        "love": "感情浪漫热烈，外表吸引力强", "health": "心脑血管、眼睛注意",
        "travel": "出行顺利，名声在外", "study": "成绩出众，有望拔得头筹",
    },
}

# ─────────────────────────────────────────────────────────────
# 3. Purpose-Specific Analysis
#    For each purpose, find best palace + give targeted advice
# ─────────────────────────────────────────────────────────────

PURPOSE_LOGIC: Dict[str, Dict[str, Any]] = {
    "求财": {
        "title": "求财谋利", "icon": "💰",
        "best_doors": ["生门", "开门"],
        "best_stars": ["天辅", "天任", "天心"],
        "best_stems": ["乙", "丙", "壬"],
        "worst_doors": ["死门", "惊门"],
        "worst_stars": ["天蓬", "天柱"],
        "principle": "求财以生门为首选，次取开门、休门；九星以天辅、天任最佳；天干以壬水为财，乙奇最贵。趋生门方位行动，或以生门对应时辰出发。",
        "advanced": "正财宜生门+天任，偏财（投资）宜开门+天心。见庚、天蓬、死门则此财不可求。",
    },
    "感情": {
        "title": "感情婚姻", "icon": "❤️",
        "best_doors": ["休门", "开门"],
        "best_stars": ["天辅", "天英"],
        "best_stems": ["乙", "丙", "丁"],
        "worst_doors": ["死门", "伤门"],
        "worst_stars": ["天蓬", "天芮"],
        "principle": "婚姻感情以休门为用，主休养和合；六合神主和合最宜。天辅星利婚嫁，天英星主浪漫美丽。三奇乙丙丁出现，感情顺遂有贵人撮合。",
        "advanced": "见六合神+休门+乙奇，为感情大吉局。见腾蛇、白虎、死门则感情有险。",
    },
    "事业": {
        "title": "事业仕途", "icon": "🏆",
        "best_doors": ["开门", "生门"],
        "best_stars": ["天辅", "天冲", "天心"],
        "best_stems": ["乙", "丙"],
        "worst_doors": ["死门", "杜门"],
        "worst_stars": ["天蓬", "天柱"],
        "principle": "仕途功名以开门为首，主开展宏图；天辅星主文昌贵人；天冲星主奋发进取。乙奇、丙奇在开门宫，主升迁有望。",
        "advanced": "创业宜生门+天冲，晋升宜开门+天辅。见庚干、天蓬、死门方位，不宜正面谋事。",
    },
    "出行": {
        "title": "出行方位", "icon": "🧭",
        "best_doors": ["生门", "休门", "开门"],
        "best_stars": ["天辅", "天任", "天心"],
        "best_stems": ["乙", "壬"],
        "worst_doors": ["死门", "惊门"],
        "worst_stars": ["天蓬", "天柱", "天芮"],
        "principle": "出行以生门方位为最佳出发方向；天任星主平安回归；天心星主途中有贵人。见三吉门方位出发，诸事顺遂。",
        "advanced": "短途宜生门，远行宜开门+乙奇。见庚干、天蓬、惊门之方位，切忌前往。",
    },
    "健康": {
        "title": "求医问药", "icon": "🏥",
        "best_doors": ["休门", "开门"],
        "best_stars": ["天心", "天任"],
        "best_stems": ["丙", "乙"],
        "worst_doors": ["死门"],
        "worst_stars": ["天芮", "天蓬"],
        "principle": "求医问药首选天心星宫位（天心主医卜），次选天任（主稳固安康）。休门方向最利养病康复；死门方向切忌就医（主死局）。",
        "advanced": "慢性病宜天任+休门，急病宜天心+开门。见白虎+天芮+死门，病情危重。",
    },
    "学业": {
        "title": "学业考试", "icon": "📚",
        "best_doors": ["开门", "生门"],
        "best_stars": ["天辅", "天英"],
        "best_stems": ["丙", "丁", "乙"],
        "worst_doors": ["死门", "惊门"],
        "worst_stars": ["天柱", "天蓬"],
        "principle": "考学功名以天辅星为最佳，主文昌智慧；开门方向有利谋划；丙奇、丁奇主智慧大开。面向天辅星方位读书，或于吉时出发赴考。",
        "advanced": "应试宜天辅+开门+丙奇；见天柱、惊门，考场失利；见乙奇+天辅，必有贵人提携。",
    },
}

def get_purpose_analysis(layout: Dict[str, Any], purpose: str) -> Dict[str, Any]:
    """
    Given a QiMen layout and a purpose, return targeted professional advice.
    """
    logic = PURPOSE_LOGIC.get(purpose, PURPOSE_LOGIC["求财"])
    palaces = layout.get("palaces", [])

    # Score each palace for this purpose
    scored = []
    for p in palaces:
        if p.get("position") == 5:  # 中宫 skip
            continue
        score = 0
        reasons = []
        door = p.get("door", "")
        star = p.get("star", "")
        stem = p.get("stem", "")
        deity = p.get("deity", "")

        if door in logic["best_doors"]:
            score += 3
            reasons.append(f"{door}（吉门）")
        if door in logic["worst_doors"]:
            score -= 3
            reasons.append(f"{door}（凶门）")
        if star in logic["best_stars"]:
            score += 2
            reasons.append(f"{star}（利星）")
        if star in logic["worst_stars"]:
            score -= 2
            reasons.append(f"{star}（凶星）")
        if stem in logic["best_stems"]:
            score += 2
            reasons.append(f"{stem}（吉干）")
        if stem == "庚":
            score -= 3
            reasons.append("庚干（阻格）")

        # Check deity
        if deity in ("青龙", "九天", "六合", "值符"):
            score += 1
            reasons.append(f"{deity}（吉神）")
        elif deity in ("白虎", "玄武", "腾蛇"):
            score -= 1
            reasons.append(f"{deity}（凶神）")

        scored.append({
            **p,
            "purpose_score": score,
            "purpose_reasons": reasons,
        })

    scored.sort(key=lambda x: x["purpose_score"], reverse=True)
    best = [s for s in scored if s["purpose_score"] >= 2][:3]
    avoid = [s for s in scored if s["purpose_score"] <= -2][:2]

    # Build recommendation text
    if best:
        b = best[0]
        rec = (
            f"【{purpose}最佳方位】{b['palace_name']}（{b['door']} · {b['star']} · {b['stem']}干）"
            f"，原因：{'、'.join(b['purpose_reasons'][:3])}。"
        )
    else:
        rec = f"当前时局对{purpose}无明显吉方，宜静守待时。"

    if avoid:
        a = avoid[0]
        warn = f"【须回避方位】{a['palace_name']}（{'、'.join(a['purpose_reasons'][:2])}），切勿以此方向行事。"
    else:
        warn = ""

    return {
        "purpose": purpose,
        "icon": logic.get("icon", ""),
        "title": logic.get("title", purpose),
        "principle": logic.get("principle", ""),
        "advanced": logic.get("advanced", ""),
        "recommendation": rec,
        "warning": warn,
        "best_palaces": best,
        "avoid_palaces": avoid,
    }


# ─────────────────────────────────────────────────────────────
# 4. 伏吟/反吟 Detection
# ─────────────────────────────────────────────────────────────

def detect_fuyin_fanyin(ju_number: int, yang_dun: bool) -> Dict[str, Any]:
    """
    伏吟 (Fu Yin): Stars/Doors return to their natural palace positions.
    反吟 (Fan Yin): Stars/Doors are in the opposite positions.
    Both are unfavorable configurations.
    """
    # Simplified detection: 伏吟 occurs when the current layout mirrors the natural palace layout
    # In practice: when the Ju maps stars exactly to their home positions
    # Natural star homes: 天蓬→1, 天芮→2, 天冲→3, 天辅→4, 天禽→5, 天心→6, 天柱→7, 天任→8, 天英→9
    # 伏吟 happens when yang_dun ju=9 or yin_dun ju=1 (stars cycle back to original)

    is_fuyin = (yang_dun and ju_number == 9) or (not yang_dun and ju_number == 1)
    is_fanyin = (yang_dun and ju_number == 5) or (not yang_dun and ju_number == 5)

    if is_fuyin:
        return {
            "type": "伏吟",
            "detected": True,
            "desc": "伏吟局：星门回归本位，主事情停滞不前，动则不利，宜静守待时。所谋之事反复拖延，难有进展。",
            "severity": "凶",
        }
    if is_fanyin:
        return {
            "type": "反吟",
            "detected": True,
            "desc": "反吟局：星门与本位相冲相反，主急变、反覆、事与愿违。一切谋划都会朝相反方向发展，需格外谨慎。",
            "severity": "大凶",
        }
    return {"type": "无", "detected": False, "desc": "", "severity": "平"}


# ─────────────────────────────────────────────────────────────
# 5. Enrich layout with all purpose analyses and stem details
# ─────────────────────────────────────────────────────────────

def enrich_qimen_analysis(layout: Dict[str, Any]) -> Dict[str, Any]:
    """Add all enriched analyses to the layout."""
    palaces = layout.get("palaces", [])

    # Add detailed stem meanings to each palace
    for p in palaces:
        stem = p.get("stem", "")
        stem_info = QIMEN_STEM_MEANINGS.get(stem, {})
        p["stem_category"] = stem_info.get("category", "六仪")
        p["stem_nature"] = stem_info.get("nature", "平")
        p["stem_desc"] = stem_info.get("desc", "")
        p["stem_detail"] = stem_info.get("detail", "")

        # Add detailed star info
        star = p.get("star", "")
        star_info = STAR_DETAILED.get(star, {})
        p["star_detail"] = star_info

    # All 6 purpose analyses
    purpose_analyses = {}
    for purpose in PURPOSE_LOGIC.keys():
        purpose_analyses[purpose] = get_purpose_analysis(layout, purpose)

    # Fuyin/Fanyin check
    fuyin = detect_fuyin_fanyin(layout.get("ju_number", 1), layout.get("ju_type", "阳遁") == "阳遁")

    layout["purpose_analyses"] = purpose_analyses
    layout["fuyin_fanyin"] = fuyin
    layout["purposes"] = list(PURPOSE_LOGIC.keys())

    return layout
