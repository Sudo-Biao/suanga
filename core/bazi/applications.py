"""
core/bazi/applications.py
=========================
Applied BaZi readings: career, marriage, health, wealth, naming.

Bugs fixed:
  B-09 — All methods now use chart['day_pillar']['tiangan'] (the unified
          dict key) instead of the old bazi['日柱']['天干'] pattern.
  B-13 — shishen_analysis accessed by key 'shishen' not '数量'.
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional

from core.constants import (
    TIANGAN_WUXING, DIZHI_WUXING, WUXING_SHENG, WUXING_KE,
    LIUCHONG, LIUHE,
)


# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────

def _dm(chart: Dict) -> str:
    """Return the day master TianGan from a chart dict. (B-09 fix)"""
    return chart["day_master"]


def _dm_wx(chart: Dict) -> str:
    return TIANGAN_WUXING[_dm(chart)]


def _find_shishen(chart: Dict, target_ss: str) -> List[str]:
    """
    Return all stems with a given Ten God relationship. (B-13 fix)
    Uses shishen_summary list (not the old dict with '数量').
    """
    summary = chart.get("shishen_summary", [])
    for entry in summary:
        if entry.get("shishen") == target_ss:
            return entry.get("stems", [])
    return []


def _wuxing_count(chart: Dict) -> Dict[str, int]:
    """Count wuxing occurrences across all visible + hidden stems."""
    from core.constants import CANGGAN
    counts: Dict[str, int] = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pk in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        p = chart[pk]
        wx = TIANGAN_WUXING.get(p["tiangan"])
        if wx: counts[wx] += 1
        for h in p.get("canggan", []):
            wx_h = TIANGAN_WUXING.get(h)
            if wx_h: counts[wx_h] += 1
    return counts


# ─────────────────────────────────────────────────────────────
# Career analysis
# ─────────────────────────────────────────────────────────────

_CAREER_BY_WX: Dict[str, List[str]] = {
    "木": ["教育", "文化传媒", "园林绿化", "家具木材", "医疗（中医）"],
    "火": ["IT科技", "餐饮", "能源", "金融投资", "娱乐表演"],
    "土": ["地产建筑", "农业", "矿产", "物流仓储", "政府机关"],
    "金": ["金融银行", "冶金机械", "法律", "军警", "珠宝"],
    "水": ["贸易流通", "运输航运", "传媒通讯", "旅游", "饮品"],
}

_CAREER_BY_SHISHEN: Dict[str, str] = {
    "正官": "适合官场、管理职位，以德服人，仕途顺遂",
    "七杀": "适合军警、律法、竞技，权威气场强",
    "正财": "适合稳健行业，财务、会计、银行，踏实积累",
    "偏财": "适合商贸、投资、销售，善于把握机遇",
    "食神": "适合创意、餐饮、艺术，生活品质高",
    "伤官": "适合科技、创新、表演，才华横溢但需磨砺",
    "正印": "适合学术、教育、文化，贵人相助",
    "偏印": "适合偏门技艺、宗教、玄学，独辟蹊径",
}


def career_analysis(chart: Dict) -> Dict[str, Any]:
    """Return career recommendations based on day master wuxing and Ten Gods."""
    dm_wx = _dm_wx(chart)
    strength = chart.get("strength", "中和")

    # Lucky career wuxing = what benefits the day master
    if strength == "身强":
        # 身强喜克泄 — wealth/official wuxing is lucky
        lucky_wx = [WUXING_KE[dm_wx], WUXING_SHENG[dm_wx]]
    else:
        # 身弱喜生扶 — print/compare wuxing is lucky
        lucky_wx = [WUXING_KE.get(WUXING_KE.get(dm_wx, ""), ""), dm_wx]

    careers = []
    for wx in lucky_wx:
        careers.extend(_CAREER_BY_WX.get(wx, []))

    # Add Ten God specific advice (B-13 fix: use 'shishen' key not '数量')
    top_shishen_entries = chart.get("shishen_summary", [])[:2]
    ss_advice = []
    for entry in top_shishen_entries:
        ss = entry.get("shishen", "")
        if ss in _CAREER_BY_SHISHEN:
            ss_advice.append(_CAREER_BY_SHISHEN[ss])

    return {
        "topic":           "事业",
        "day_master":      _dm(chart),
        "day_master_wx":   dm_wx,
        "strength":        strength,
        "lucky_wuxing":    lucky_wx,
        "career_fields":   list(dict.fromkeys(careers))[:6],
        "shishen_advice":  ss_advice,
        "analysis": f"日主{_dm(chart)}，五行属{dm_wx}，{strength}。"
                    f"宜从事{lucky_wx[0] if lucky_wx else ''}行业，" +
                    (ss_advice[0] if ss_advice else "多元发展") + "。",
    }


# ─────────────────────────────────────────────────────────────
# Marriage / relationship analysis
# ─────────────────────────────────────────────────────────────

def marriage_analysis(chart: Dict, gender: str) -> Dict[str, Any]:
    """
    Return marriage/relationship analysis. (B-09 fix)
    Spouse star: 正财/偏财 for males, 正官/七杀 for females.
    """
    male = gender in ("male", "男")
    spouse_ss_main  = "正财" if male else "正官"
    spouse_ss_alt   = "偏财" if male else "七杀"

    spouse_stems_main = _find_shishen(chart, spouse_ss_main)  # B-13 fix
    spouse_stems_alt  = _find_shishen(chart, spouse_ss_alt)

    # Spouse branch = day pillar DiZhi (日支 represents spouse palace)
    spouse_palace = chart["day_pillar"]["dizhi"]   # B-09 fix

    # Clash with spouse palace?
    clashed_by = LIUCHONG.get(spouse_palace, "")
    clash_present = any(
        chart[pk]["dizhi"] == clashed_by
        for pk in ("year_pillar", "month_pillar", "hour_pillar")
        if clashed_by
    )

    # Marriage timing hint from year/hour pillar
    year_zhi = chart["year_pillar"]["dizhi"]
    hour_zhi = chart["hour_pillar"]["dizhi"]
    harmony = LIUHE.get(spouse_palace, "")
    harmony_present = harmony in (year_zhi, hour_zhi)

    if clash_present:
        marriage_quality = "日支受冲，婚姻易有波折，需多包容沟通"
    elif harmony_present:
        marriage_quality = "日支六合，婚姻和谐，伴侣关系稳定"
    elif spouse_stems_main:
        marriage_quality = f"命中有{spouse_ss_main}，婚缘较好，感情稳定"
    else:
        marriage_quality = "婚姻宫平稳，感情需缘分际合"

    return {
        "topic":           "婚姻",
        "spouse_palace":   spouse_palace,
        "spouse_stars":    spouse_stems_main + spouse_stems_alt,
        "clash_present":   clash_present,
        "harmony_present": harmony_present,
        "quality":         marriage_quality,
        "analysis":        marriage_quality,
        "advice": [
            "注重沟通与包容" if clash_present else "珍惜眼前缘分",
            f"配偶五行宜属{'金水' if _dm_wx(chart) in ('木','火') else '木火'}",
        ],
    }


# ─────────────────────────────────────────────────────────────
# Health analysis
# ─────────────────────────────────────────────────────────────

_WUXING_ORGANS: Dict[str, Dict[str, str]] = {
    "木": {"organ": "肝胆", "condition": "情绪急躁，易肝郁气滞", "advice": "保持情绪舒畅，忌酸辣刺激"},
    "火": {"organ": "心脑", "condition": "心脑血管、睡眠", "advice": "避免过度劳神，忌辛热食物"},
    "土": {"organ": "脾胃", "condition": "消化系统", "advice": "规律饮食，忌生冷"},
    "金": {"organ": "肺大肠", "condition": "呼吸系统", "advice": "注意防寒，忌辛辣"},
    "水": {"organ": "肾膀胱", "condition": "泌尿生殖", "advice": "注意保暖，忌过劳"},
}


def health_analysis(chart: Dict) -> Dict[str, Any]:
    """
    Return health analysis. (B-09 fix — uses chart dict keys, not 日柱 string)
    Weak wuxing elements indicate health vulnerabilities.
    """
    dm_wx   = _dm_wx(chart)
    wx_count = _wuxing_count(chart)

    # Find the weakest wuxing
    weakest = min(wx_count, key=wx_count.get)
    strongest = max(wx_count, key=wx_count.get)

    weak_info = _WUXING_ORGANS.get(weakest, {})
    dm_info   = _WUXING_ORGANS.get(dm_wx, {})

    return {
        "topic":          "健康",
        "day_master_wx":  dm_wx,
        "dm_organ":       dm_info.get("organ", ""),
        "dm_condition":   dm_info.get("condition", ""),
        "weak_element":   weakest,
        "weak_organ":     weak_info.get("organ", ""),
        "wx_distribution": wx_count,
        "analysis": (
            f"命局五行中{weakest}气最弱，需注意{weak_info.get('organ', '')}相关健康。"
            f"日主{_dm(chart)}属{dm_wx}，{dm_info.get('condition', '')}需特别关注。"
        ),
        "advice": [
            weak_info.get("advice", ""),
            dm_info.get("advice", ""),
            "保持规律作息，适量运动",
        ],
    }


# ─────────────────────────────────────────────────────────────
# Wealth analysis
# ─────────────────────────────────────────────────────────────

def wealth_analysis(chart: Dict) -> Dict[str, Any]:
    """Return wealth potential analysis."""
    dm_wx   = _dm_wx(chart)
    strength = chart.get("strength", "中和")

    # Wealth wuxing = what dm克
    wealth_wx = WUXING_KE.get(dm_wx, "")
    wealth_stems = (_find_shishen(chart, "正财") +
                    _find_shishen(chart, "偏财"))

    if strength == "身强" and len(wealth_stems) >= 2:
        level = "财运丰厚"
        desc  = "身强财多，财富积累能力强，适合主动经营"
    elif strength == "身强" and len(wealth_stems) == 1:
        level = "财运稳健"
        desc  = "身强有财，收入稳定，适合稳中求进"
    elif strength == "身弱" and len(wealth_stems) >= 2:
        level = "财来财去"
        desc  = "身弱财重，财富难以守住，需借助贵人"
    else:
        level = "财运平稳"
        desc  = "财星适中，量力而行，稳健理财为上"

    return {
        "topic":        "财运",
        "level":        level,
        "wealth_wx":    wealth_wx,
        "wealth_stems": wealth_stems,
        "analysis":     desc,
        "advice": [
            f"财星五行属{wealth_wx}，宜从事相关行业",
            "正财为主，偏财为辅，稳健优先",
        ],
    }
