"""
core/bazi/analyzer.py
=====================
Static analysis of a BaZi chart:
  • Ten Gods (十神) for every stem/branch
  • Day-master strength (身强/身弱)
  • Pattern detection (格局)
  • Shensha (神煞) identification

Bugs fixed:
  B-01 — WUXING_MAP renamed to WUXING (single definition in constants)
  B-12 — Shensha now uses complete table including 禄神 and 羊刃
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional

from core.constants import (
    SHISHEN, CANGGAN, WUXING, TIANGAN_WUXING, DIZHI_WUXING,
    WUXING_SHENG, WUXING_KE, SHENSHA,
    get_wuxing_strength, TIANGAN_INDEX,
    MAJOR_PATTERNS, SPECIAL_PATTERNS,
)


# ─────────────────────────────────────────────────────────────
# Ten Gods
# ─────────────────────────────────────────────────────────────

def get_shishen(day_master: str, stem: str) -> str:
    """Return the Ten God name for *stem* relative to *day_master*."""
    return SHISHEN.get((day_master, stem), "")


def annotate_pillars(chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add shishen_gan / shishen_zhi to every pillar in the chart dict.
    Returns the mutated chart.
    """
    dm = chart["day_master"]
    for pk in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        p = chart[pk]
        p["shishen_gan"] = get_shishen(dm, p["tiangan"])
        # Ten God of branch = Ten God of its main (first) hidden stem
        main_hidden = CANGGAN.get(p["dizhi"], [])
        p["shishen_zhi"] = get_shishen(dm, main_hidden[0]) if main_hidden else ""
    return chart


def summarize_shishen(chart: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Count Ten God occurrences across all stems (天干) and hidden stems (藏干).
    Returns list of {shishen, count, stems} sorted by count descending.
    """
    dm = chart["day_master"]
    counter: Dict[str, Dict] = {}

    pillars = [chart["year_pillar"], chart["month_pillar"],
               chart["day_pillar"], chart["hour_pillar"]]

    for p in pillars:
        # Visible stems
        ss = get_shishen(dm, p["tiangan"])
        if ss:
            counter.setdefault(ss, {"count": 0, "stems": []})
            counter[ss]["count"] += 1
            counter[ss]["stems"].append(p["tiangan"])
        # Hidden stems
        for h in p.get("canggan", []):
            ss_h = get_shishen(dm, h)
            if ss_h:
                counter.setdefault(ss_h, {"count": 0, "stems": []})
                counter[ss_h]["count"] += 1
                counter[ss_h]["stems"].append(h)

    result = []
    month_dz = chart["month_pillar"]["dizhi"]
    for ss, info in counter.items():
        wx = TIANGAN_WUXING.get(info["stems"][0], "") if info["stems"] else ""
        result.append({
            "shishen": ss,
            "count":   info["count"],
            "stems":   info["stems"],
            "strength": get_wuxing_strength(wx, month_dz) if wx else "",
        })
    result.sort(key=lambda x: x["count"], reverse=True)
    return result


# ─────────────────────────────────────────────────────────────
# Day-master strength
# ─────────────────────────────────────────────────────────────

_HELP_SHISHEN  = {"比肩", "劫财", "正印", "偏印"}
_DRAIN_SHISHEN = {"食神", "伤官", "正财", "偏财", "正官", "七杀"}


def calculate_strength(chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate whether the day master is 身强 (strong) or 身弱 (weak).

    Algorithm:
      1. Check month-branch rooting (得令)
      2. Sum helper vs draining Ten Gods
      3. Classify as 强/弱/中和
    """
    dm = chart["day_master"]
    dm_wx = TIANGAN_WUXING[dm]
    month_dz = chart["month_pillar"]["dizhi"]

    # 1. 得令 — does day master's wuxing gain strength in birth month?
    monthly_strength = get_wuxing_strength(dm_wx, month_dz)
    deling = monthly_strength in ("旺", "相")

    # 2. Count helping vs draining stems (visible + hidden)
    help_score  = 0
    drain_score = 0
    pillars = [chart["year_pillar"], chart["month_pillar"],
               chart["day_pillar"], chart["hour_pillar"]]

    for p in pillars:
        stems = [p["tiangan"]] + p.get("canggan", [])
        for s in stems:
            ss = get_shishen(dm, s)
            if ss in _HELP_SHISHEN:
                help_score  += 1
            elif ss in _DRAIN_SHISHEN:
                drain_score += 1

    # 3. Classify
    if deling and help_score >= drain_score:
        label = "身强"
    elif not deling and drain_score > help_score + 1:
        label = "身弱"
    else:
        label = "中和"

    return {
        "strength":       label,
        "monthly_status": monthly_strength,
        "deling":         deling,
        "help_score":     help_score,
        "drain_score":    drain_score,
    }


# ─────────────────────────────────────────────────────────────
# Pattern detection (格局)
# ─────────────────────────────────────────────────────────────

def detect_pattern(chart: Dict[str, Any]) -> Dict[str, str]:
    """
    Detect the dominant BaZi pattern (格局).
    Priority: special patterns > month-branch major pattern.
    """
    dm     = chart["day_master"]
    dm_wx  = TIANGAN_WUXING[dm]
    m_p    = chart["month_pillar"]
    month_canggan = m_p.get("canggan", [])
    strength_info = calculate_strength(chart)

    # Special patterns require extreme day-master strength
    if strength_info["strength"] == "身弱" and strength_info["drain_score"] >= 6:
        # Count dominant Ten God
        ss_list = summarize_shishen(chart)
        top_ss = ss_list[0]["shishen"] if ss_list else ""
        if top_ss in ("正财", "偏财"):
            return {"pattern": "从财格", "desc": SPECIAL_PATTERNS[0]["desc"]}
        if top_ss in ("正官", "七杀"):
            return {"pattern": "从杀格", "desc": SPECIAL_PATTERNS[1]["desc"]}
        if top_ss in ("食神", "伤官"):
            return {"pattern": "从儿格", "desc": SPECIAL_PATTERNS[2]["desc"]}

    # Major patterns based on month hidden stem
    if month_canggan:
        main_stem = month_canggan[0]
        ss = get_shishen(dm, main_stem)
        if ss == "比肩":
            return {"pattern": "建禄格", "desc": SPECIAL_PATTERNS[0]["desc"]}
        if ss == "劫财":
            return {"pattern": "月刃格", "desc": SPECIAL_PATTERNS[1]["desc"]}
        if ss in MAJOR_PATTERNS:
            mp = MAJOR_PATTERNS[ss]
            return {"pattern": mp.get("name", ss + "格"), "desc": mp["desc"]}
        # Fallback: name it by its Ten God
        return {"pattern": ss + "格", "desc": MAJOR_PATTERNS.get(ss, {}).get("desc", "")}

    return {"pattern": "杂气格", "desc": "月支藏干杂，需综合论断"}


# ─────────────────────────────────────────────────────────────
# Shensha (神煞) — B-12 fixed: full table including 禄神/羊刃
# ─────────────────────────────────────────────────────────────

def find_shensha(chart: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Find all active Shensha (神煞) in the chart.
    Checks each pillar's DiZhi against the Shensha lookup table
    using the day-master TianGan as the reference key.

    Returns list of {name, dizhi, pillar}.
    """
    dm = chart["day_master"]
    year_dz  = chart["year_pillar"]["dizhi"]
    result: List[Dict[str, str]] = []

    pillar_map = {
        "年支": chart["year_pillar"]["dizhi"],
        "月支": chart["month_pillar"]["dizhi"],
        "日支": chart["day_pillar"]["dizhi"],
        "时支": chart["hour_pillar"]["dizhi"],
    }

    for sha_name, sha_data in SHENSHA.items():
        # 天乙贵人 / 文昌贵人 / 禄神 / 羊刃 — keyed by TianGan
        if dm in sha_data:
            active_branches = sha_data[dm]
            for pillar_label, dz in pillar_map.items():
                if dz in active_branches:
                    result.append({
                        "name":   sha_name,
                        "dizhi":  dz,
                        "pillar": pillar_label,
                    })

        # 驿马 / 华盖 — keyed by DiZhi (usually year or day branch)
        elif year_dz in sha_data:
            active_branches = sha_data[year_dz]
            for pillar_label, dz in pillar_map.items():
                if dz in active_branches:
                    result.append({
                        "name":   sha_name,
                        "dizhi":  dz,
                        "pillar": pillar_label,
                    })

    return result


# ─────────────────────────────────────────────────────────────
# Master analyze function
# ─────────────────────────────────────────────────────────────

def analyze_chart(chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run full static analysis on a chart dict (from build_chart).
    Mutates and returns the chart with analysis results attached.
    """
    annotate_pillars(chart)
    chart["shishen_summary"] = summarize_shishen(chart)
    chart["strength_info"]   = calculate_strength(chart)
    chart["strength"]        = chart["strength_info"]["strength"]
    chart["pattern_info"]    = detect_pattern(chart)
    chart["pattern"]         = chart["pattern_info"]["pattern"]
    chart["pattern_desc"]    = chart["pattern_info"]["desc"]
    chart["shensha"]         = find_shensha(chart)
    return chart
