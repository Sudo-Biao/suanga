"""
core/date_selection/selector.py
================================
Date selection (择日) logic.

Bug fixed:
  B-04 — knowledge_base import wrapped in try/except with graceful fallback.
"""
from __future__ import annotations
from datetime import date, timedelta
from typing import Dict, List, Any, Optional

from core.constants import (
    TIANGAN, DIZHI, TIANGAN_WUXING, DIZHI_WUXING,
    LIUCHONG, LIUHE, SHENSHA,
)
from core.calendar.ganzhi import ganzhi_from_index, _REF_DATE, _REF_DAY_IDX
from core.date_selection.twelve_officers import annotate_day, get_three_killings


# B-04 fix: graceful import of knowledge base
try:
    from knowledge.classical_texts import DATE_SELECTION_SUITABLE, DATE_SELECTION_AVOID
except ImportError:
    DATE_SELECTION_SUITABLE: Dict[str, List[str]] = {}
    DATE_SELECTION_AVOID:    Dict[str, List[str]] = {}


# ─────────────────────────────────────────────────────────────
# Weekday names
# ─────────────────────────────────────────────────────────────
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


# ─────────────────────────────────────────────────────────────
# Purpose → auspicious criteria
# ─────────────────────────────────────────────────────────────

PURPOSE_CRITERIA: Dict[str, Dict[str, Any]] = {
    "婚嫁": {
        "good_stars": ["生气", "延年", "天医"],
        "good_dizhi": ["子", "丑", "卯", "辰", "未", "申", "酉"],
        "avoid_dizhi": ["午", "寅", "戌"],
        "avoid_shishen": ["七杀"],
        "desc": "婚嫁宜选吉日，忌冲日主生肖，宜六合日",
    },
    "开业": {
        "good_stars": ["生气", "开门"],
        "good_dizhi": ["寅", "午", "亥", "子"],
        "avoid_dizhi": ["冲日主生肖"],
        "desc": "开业宜选生气旺盛之日，逢龙虎日大吉",
    },
    "动土": {
        "good_stars": ["天医", "延年"],
        "good_dizhi": ["辰", "戌", "丑", "未"],
        "avoid_dizhi": ["寅", "卯"],
        "desc": "动土宜选土旺之日，忌木旺日克土",
    },
    "搬家": {
        "good_stars": ["生气", "伏位"],
        "good_dizhi": ["子", "卯", "午", "酉"],
        "avoid_dizhi": ["冲", "刑"],
        "desc": "搬家宜选四正日，忌三煞方位",
    },
    "出行": {
        "good_stars": ["生气", "天医"],
        "good_dizhi": ["寅", "申", "巳", "亥"],
        "avoid_dizhi": ["死门", "凶方"],
        "desc": "出行宜选驿马旺日，忌五黄方位",
    },
    "求医": {
        "good_stars": ["天医"],
        "good_dizhi": ["子", "亥", "酉"],
        "avoid_dizhi": ["午", "未"],
        "desc": "求医宜天医吉日，忌死门凶日",
    },
}


# ─────────────────────────────────────────────────────────────
# Day quality scoring
# ─────────────────────────────────────────────────────────────

def _score_day(d: date, purpose: str,
               birth_year: Optional[int],
               birth_month: Optional[int],
               birth_day: Optional[int]) -> int:
    """
    Score a day 0–5 for the given purpose.
    Now integrates:
      - 《协纪辨方书》建除十二神吉凶
      - 黄道/黑道日加减分
    """
    delta = (d - _REF_DATE).days
    day_idx = (_REF_DAY_IDX + delta) % 60
    d_gan, d_zhi = ganzhi_from_index(day_idx)

    score = 3  # base

    criteria = PURPOSE_CRITERIA.get(purpose, {})

    # Bonus for good DiZhi
    if d_zhi in criteria.get("good_dizhi", []):
        score += 1

    # Penalty for avoid DiZhi
    if d_zhi in criteria.get("avoid_dizhi", []):
        score -= 1

    # Bonus for 六合 with birth day DiZhi
    if birth_day:
        birth_d = date(birth_year or 1990, birth_month or 1, birth_day)
        b_delta = (birth_d - _REF_DATE).days
        b_idx   = (_REF_DAY_IDX + b_delta) % 60
        _, b_zhi = ganzhi_from_index(b_idx)
        if LIUHE.get(d_zhi) == b_zhi:
            score += 1
        if LIUCHONG.get(d_zhi) == b_zhi:
            score -= 1

    # ── 《协纪辨方书》建除十二神加减分 ──────────────────────────
    try:
        from knowledge.date_classical import JIANSHEN_TWELVE, ZERI_EVENTS
        # We can't easily compute the 建除 officer here without month_zhi,
        # but we can use ZERI_EVENTS to check if d_zhi aligns with best/avoid dates
        event_rule = ZERI_EVENTS.get(purpose, {})
        best_day_text = event_rule.get("最佳日", "")
        ji_text = event_rule.get("忌", "")

        # 天干加分：天德/月德吉神（简化：甲丙壬庚日各加0.5分，取整）
        _TIANDEDAYS = {"丙", "壬", "甲", "庚", "乙", "辛", "丁", "癸"}
        if d_gan in _TIANDEDAYS and "天德" in best_day_text:
            score += 1

        # 建除吉凶（简化：成/开日+1，破/闭日-1）
        # 成日：旬序5（戊/癸）和特定支组合，简化为支逢子午卯酉+1
        if d_zhi in ("子", "午", "卯", "酉") and "成日" in best_day_text:
            score += 1
        if d_zhi in ("辰", "戌", "丑", "未") and "破日" in ji_text:
            score -= 1

    except Exception:
        pass

    return max(1, min(5, score))


def _get_suitable(d_zhi: str, purpose: str) -> List[str]:
    base = PURPOSE_CRITERIA.get(purpose, {}).get("desc", "")
    items = DATE_SELECTION_SUITABLE.get(purpose, []) or [base]
    if d_zhi in ("子", "午", "卯", "酉"):
        items = items + ["四正旺日，大利启动事宜"]
    return items[:3]


def _get_avoid(d_zhi: str, purpose: str) -> List[str]:
    return DATE_SELECTION_AVOID.get(purpose, ["忌冲克日主，避三煞方位"])[:2]


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def select_dates(
    purpose: str,
    year: int,
    month: int,
    birth_year: Optional[int] = None,
    birth_month: Optional[int] = None,
    birth_day: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Return auspicious days in the given year/month for the purpose.
    """
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    days: List[Dict[str, Any]] = []
    d = start
    while d < end:
        delta = (d - _REF_DATE).days
        day_idx = (_REF_DAY_IDX + delta) % 60
        d_gan, d_zhi = ganzhi_from_index(day_idx)

        score = _score_day(d, purpose, birth_year, birth_month, birth_day)

        # Get month dizhi for officer calculation (approximate from month number)
        month_dizhi_order = ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"]
        m_zhi = month_dizhi_order[(month - 1) % 12]

        officer_info = annotate_day(d, d_gan, d_zhi, m_zhi, year, purpose)
        score = max(1, min(5, score + officer_info["score_adjustment"]))

        days.append({
            "date":     d.isoformat(),
            "weekday":  WEEKDAYS[d.weekday()],
            "ganzhi":   d_gan + d_zhi,
            "quality":  score,
            "suitable": _get_suitable(d_zhi, purpose),
            "avoid":    _get_avoid(d_zhi, purpose),
            "notes":    f"{d_gan}{d_zhi}日，{'吉' if score >= 4 else '平' if score == 3 else '凶'}",
            "officer":  officer_info["officer"],
            "officer_nature": officer_info["officer_nature"],
            "officer_suit": officer_info["officer_suitability_for_purpose"],
            "officer_detail": officer_info["officer_detail"],
            "xiu":       officer_info["xiu"],
            "xiu_nature": officer_info["xiu_nature"],
            "is_year_breaker": officer_info["is_year_breaker"],
            "is_month_breaker": officer_info["is_month_breaker"],
            "breaker_warning": officer_info["breaker_warning"],
        })
        d += timedelta(days=1)

    auspicious  = [d for d in days if d["quality"] >= 4]
    inauspicious = [d["date"] for d in days if d["quality"] <= 2]

    best = max(auspicious, key=lambda x: x["quality"]) if auspicious else None

    criteria_desc = PURPOSE_CRITERIA.get(purpose, {}).get("desc", f"择{purpose}吉日")

    three_killings = get_three_killings(year)

    return {
        "purpose":         purpose,
        "month_summary":   f"{year}年{month}月{purpose}，{criteria_desc}",
        "auspicious_days": auspicious,
        "inauspicious_days": inauspicious,
        "best_day":        best,
        "three_killings":  three_killings,
    }
