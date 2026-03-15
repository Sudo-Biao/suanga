"""
core/bazi/chart.py
==================
Constructs the Four Pillars (四柱) of Destiny chart from a birth datetime.

All four pillar algorithms are verified against classical sources:
  • Year pillar  — 立春 (LiChun) as year boundary  ✓
  • Month pillar — 节 (Jié) boundaries + 五虎遁年起月法  (B-05, B-06 FIXED)
  • Day pillar   — reference date 1900-01-01 = 甲戌  ✓
  • Hour pillar  — 五鼠遁日起时法  ✓

This module contains ONLY construction logic — no interpretation.
"""
from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import Dict, Any, Tuple, List, Optional

from core.constants import (
    TIANGAN, DIZHI,
    TIANGAN_INDEX, DIZHI_INDEX,
    TIANGAN_WUXING, DIZHI_WUXING,
    CANGGAN, NAYIN,
    get_month_gan, get_hour_gan, hour_to_dizhi,
    JIE_TO_DIZHI,
)
from core.calendar.ganzhi import ganzhi_from_index, ganzhi_index
from core.calendar.solar_terms import (
    get_month_dizhi_at, lichun_of_year, get_jie_dates,
)


# ─────────────────────────────────────────────────────────────
# Reference constants
# ─────────────────────────────────────────────────────────────

# Day 0 reference: 1900-01-31 = 甲子 (index 0 in 60-cycle)
# 1900-01-01 = 甲戌 (index 10 in 60-cycle), verified against classic tables.
_REF_DATE    = date(1900, 1, 1)
_REF_DAY_IDX = 10    # 甲戌 = index 10 in 60-cycle


# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────

def _day_index(d: date) -> int:
    """Return 0-based 60-cycle index for the given calendar date."""
    delta = (d - _REF_DATE).days
    return (_REF_DAY_IDX + delta) % 60


def _year_ganzhi(dt: datetime) -> Tuple[str, str]:
    """
    Return (TianGan, DiZhi) for the Chinese year containing *dt*.
    Year boundary = 立春 (LiChun) of the Gregorian year.
    If dt is before LiChun, it belongs to the previous Chinese year.
    """
    lc = lichun_of_year(dt.year)
    if lc and dt < lc:
        # Before LiChun → previous Chinese year
        year_num = dt.year - 1
    else:
        year_num = dt.year

    # Chinese year 1984 = 甲子 (GanZhi index 0)
    idx = (year_num - 1984) % 60
    return ganzhi_from_index(idx)


def _month_ganzhi(dt: datetime, year_tiangan: str) -> Tuple[str, str]:
    """
    Return (TianGan, DiZhi) for the lunar month containing *dt*.

    DiZhi is determined by which Jié boundary has most recently passed.
    TianGan uses the 五虎遁年起月法 lookup (B-06 fixed).
    """
    month_dizhi = get_month_dizhi_at(dt)
    month_tiangan = get_month_gan(year_tiangan, month_dizhi)
    return month_tiangan, month_dizhi


def _day_ganzhi(dt: datetime) -> Tuple[str, str]:
    """Return (TianGan, DiZhi) for the calendar day of *dt*."""
    return ganzhi_from_index(_day_index(dt.date()))


def _hour_ganzhi(dt: datetime, day_tiangan: str) -> Tuple[str, str]:
    """Return (TianGan, DiZhi) for the hour of *dt*."""
    hour_dizhi   = hour_to_dizhi(dt.hour)
    hour_tiangan = get_hour_gan(day_tiangan, hour_dizhi)
    return hour_tiangan, hour_dizhi


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

def build_pillar(label: str, tiangan: str, dizhi: str) -> Dict[str, Any]:
    """Build a full pillar dict from stem + branch."""
    gz_name = tiangan + dizhi
    return {
        "label":       label,
        "tiangan":     tiangan,
        "dizhi":       dizhi,
        "nayin":       NAYIN.get(gz_name),
        "canggan":     CANGGAN.get(dizhi, []),
        "wuxing_gan":  TIANGAN_WUXING.get(tiangan),
        "wuxing_zhi":  DIZHI_WUXING.get(dizhi),
    }


def build_chart(
    year: int, month: int, day: int,
    hour: int, minute: int = 0,
) -> Dict[str, Any]:
    """
    Build the complete four-pillars chart for a birth datetime.

    Returns a plain dict with keys:
        year_pillar, month_pillar, day_pillar, hour_pillar,
        day_master, day_master_wuxing, birth_dt
    """
    dt = datetime(year, month, day, hour, minute)

    y_gan, y_zhi = _year_ganzhi(dt)
    m_gan, m_zhi = _month_ganzhi(dt, y_gan)
    d_gan, d_zhi = _day_ganzhi(dt)
    h_gan, h_zhi = _hour_ganzhi(dt, d_gan)

    return {
        "birth_dt":     dt.isoformat(),
        "year_pillar":  build_pillar("年柱", y_gan, y_zhi),
        "month_pillar": build_pillar("月柱", m_gan, m_zhi),
        "day_pillar":   build_pillar("日柱", d_gan, d_zhi),
        "hour_pillar":  build_pillar("时柱", h_gan, h_zhi),
        "day_master":   d_gan,
        "day_master_wuxing": TIANGAN_WUXING[d_gan],
    }


def get_all_stems_and_branches(chart: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Return (all_tiangan, all_dizhi) present in the chart
    including hidden stems (藏干) from each branch.
    """
    pillars = ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]
    tg: List[str] = []
    dz: List[str] = []
    hidden: List[str] = []

    for pk in pillars:
        p = chart[pk]
        tg.append(p["tiangan"])
        dz.append(p["dizhi"])
        hidden.extend(p.get("canggan", []))

    return tg + hidden, dz
