"""
core/bazi/forecaster.py
=======================
Time-based fortune forecasting:
  • DaYun  (大运) — 10-year luck cycles
  • LiuNian (流年) — yearly fortune
  • LiuYue  (流月) — monthly fortune

Bugs fixed:
  B-07 — season quality now uses 旺/相/休/囚/死 vocabulary
  B-08 — DaYun start age uses exact solar-day-distance ÷ 3 method
  B-11 — DaYun GanZhi sequence starts correctly from the next Jié
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import math

from core.constants import (
    TIANGAN, DIZHI, TIANGAN_INDEX, DIZHI_INDEX,
    TIANGAN_WUXING, DIZHI_WUXING, WUXING,
    get_month_gan, get_wuxing_strength,
)
from core.calendar.ganzhi import ganzhi_from_index, ganzhi_index
from core.calendar.solar_terms import nearest_jie, get_jie_dates


# ─────────────────────────────────────────────────────────────
# DaYun start age (B-08 fixed)
# ─────────────────────────────────────────────────────────────

def _dayun_start_age(birth_dt: datetime, gender: str,
                     year_gan: str) -> float:
    """
    Calculate the exact DaYun start age using the traditional
    solar-day-distance ÷ 3 method.

    Rule:
      阳男 / 阴女 → forward direction (顺), count to next Jié
      阴男 / 阳女 → reverse direction (逆), count to previous Jié
    """
    from core.constants import TIANGAN_INDEX
    # Yin/Yang of year TianGan: even index = 阳 (甲丙戊庚壬), odd = 阴
    year_yang = (TIANGAN_INDEX[year_gan] % 2 == 0)
    male = gender in ("male", "男")

    forward = (year_yang and male) or (not year_yang and not male)

    prev_jie, next_jie = nearest_jie(birth_dt)

    if forward:
        target = next_jie
    else:
        target = prev_jie

    if target is None:
        return 8.0   # safe fallback

    delta_days = abs((target - birth_dt).total_seconds() / 86400)
    # Traditional: 3 days = 1 year, 1 day = 4 months
    age = delta_days / 3.0
    return round(age, 2)


# ─────────────────────────────────────────────────────────────
# DaYun sequence (B-11 fixed)
# ─────────────────────────────────────────────────────────────

def _dayun_direction(gender: str, year_gan: str) -> int:
    """Return +1 (forward/顺) or -1 (reverse/逆)."""
    from core.constants import TIANGAN_INDEX
    year_yang = (TIANGAN_INDEX[year_gan] % 2 == 0)
    male = gender in ("male", "男")
    forward = (year_yang and male) or (not year_yang and not male)
    return 1 if forward else -1


def calculate_dayun(chart: Dict[str, Any], gender: str,
                    birth_year: int, num_periods: int = 10) -> List[Dict[str, Any]]:
    """
    Calculate *num_periods* DaYun 10-year luck cycles.

    Starting point: the GanZhi immediately after (or before, if 逆)
    the month pillar's GanZhi in the 60-cycle.  (B-11 fix)
    """
    year_gan   = chart["year_pillar"]["tiangan"]
    month_gan  = chart["month_pillar"]["tiangan"]
    month_zhi  = chart["month_pillar"]["dizhi"]

    direction  = _dayun_direction(gender, year_gan)
    start_age  = _dayun_start_age(
        datetime.fromisoformat(chart["birth_dt"]), gender, year_gan
    )

    # Current 60-cycle index of the month pillar
    month_idx  = ganzhi_index(month_gan, month_zhi)

    dayun_list = []
    for i in range(num_periods):
        # Each period advances/retreats by (i+1) steps from month pillar
        idx = (month_idx + direction * (i + 1)) % 60
        dy_gan, dy_zhi = ganzhi_from_index(idx)

        period_start_age  = start_age + i * 10
        period_end_age    = start_age + (i + 1) * 10
        period_start_year = birth_year + math.floor(period_start_age)
        period_end_year   = birth_year + math.floor(period_end_age)

        # Quality — does the DaYun wuxing help or hinder the day master?
        dm_wx   = TIANGAN_WUXING[chart["day_master"]]
        dy_wx   = TIANGAN_WUXING[dy_gan]
        quality = _assess_quality(dm_wx, dy_wx, chart["strength"])

        dayun_list.append({
            "index":       i + 1,
            "tiangan":     dy_gan,
            "dizhi":       dy_zhi,
            "start_age":   round(period_start_age, 1),
            "end_age":     round(period_end_age, 1),
            "start_year":  period_start_year,
            "end_year":    period_end_year,
            "quality":     quality,
            "dm_shishen":  _shishen_label(chart["day_master"], dy_gan),
        })

    return dayun_list


def _shishen_label(dm: str, stem: str) -> str:
    from core.constants import SHISHEN
    return SHISHEN.get((dm, stem), "")


def _assess_quality(dm_wx: str, target_wx: str, strength: str) -> str:
    """
    Simple quality heuristic:
      身强 benefits from 克泄耗 (food/wealth/officer wuxing)
      身弱 benefits from 生扶 (印/比 wuxing)
    """
    from core.constants import WUXING_SHENG, WUXING_KE
    helps  = target_wx == WUXING_SHENG.get(WUXING_KE.get(dm_wx, ""), "") or target_wx == dm_wx
    drains = target_wx == WUXING_KE.get(dm_wx, "") or target_wx == WUXING_SHENG.get(dm_wx, "")

    if strength == "身强":
        if drains: return "吉"
        if helps:  return "凶"
    else:
        if helps:  return "吉"
        if drains: return "凶"
    return "平"


# ─────────────────────────────────────────────────────────────
# LiuNian (流年)
# ─────────────────────────────────────────────────────────────

def calculate_liunian(chart: Dict[str, Any], gender: str,
                      birth_year: int,
                      from_year: Optional[int] = None,
                      to_year: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Return yearly fortune for years [from_year, to_year].
    Defaults to birth_year through birth_year+80.
    """
    if from_year is None:
        from_year = birth_year
    if to_year is None:
        to_year = birth_year + 80

    dm = chart["day_master"]
    dm_wx = TIANGAN_WUXING[dm]
    strength = chart.get("strength", "中和")

    result = []
    for yr in range(from_year, to_year + 1):
        # 1984 = 甲子 year (index 0)
        idx = (yr - 1984) % 60
        ly_gan, ly_zhi = ganzhi_from_index(idx)
        ly_wx = TIANGAN_WUXING[ly_gan]
        quality = _assess_quality(dm_wx, ly_wx, strength)

        result.append({
            "year":        yr,
            "tiangan":     ly_gan,
            "dizhi":       ly_zhi,
            "age":         yr - birth_year,
            "shishen_gan": _shishen_label(dm, ly_gan),
            "shishen_zhi": _shishen_label(dm, DIZHI_WUXING.get(ly_zhi, "")),
            "quality":     quality,
            "summary":     _liunian_summary(dm, ly_gan, ly_zhi, quality),
        })
    return result


def _liunian_summary(dm: str, ly_gan: str, ly_zhi: str, quality: str) -> str:
    ss_gan = _shishen_label(dm, ly_gan)
    wx_gan = TIANGAN_WUXING.get(ly_gan, "")
    if quality == "吉":
        return f"{ly_gan}{ly_zhi}年，{ss_gan}临运，五行{wx_gan}旺，诸事顺遂"
    elif quality == "凶":
        return f"{ly_gan}{ly_zhi}年，{ss_gan}临运，五行{wx_gan}克身，需谨慎行事"
    return f"{ly_gan}{ly_zhi}年，{ss_gan}临运，运势平稳，宜守成待时"


# ─────────────────────────────────────────────────────────────
# LiuYue (流月) — B-07 fixed: uses 旺/相/休/囚/死
# ─────────────────────────────────────────────────────────────

def calculate_liuyue(chart: Dict[str, Any], year: int,
                     liunian_gan: str) -> List[Dict[str, Any]]:
    """
    Calculate 12 monthly fortunes for a given LiuNian year.

    Month DiZhi sequence: 寅(1)卯(2)…丑(12)
    Month TianGan: calculated by 五虎遁年起月法 using the LiuNian year's TianGan.
    (B-06/B-07 fixed)
    """
    dm = chart["day_master"]
    dm_wx = TIANGAN_WUXING[dm]
    strength = chart.get("strength", "中和")

    month_dizhi_seq = ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"]
    result = []

    for i, m_zhi in enumerate(month_dizhi_seq):
        m_gan = get_month_gan(liunian_gan, m_zhi)
        m_wx  = TIANGAN_WUXING[m_gan]
        # B-07 fix: use 旺/相/休/囚/死 for month season effect
        season_status = get_wuxing_strength(dm_wx, m_zhi)

        quality = _assess_quality(dm_wx, m_wx, strength)
        # Boost or reduce quality based on season
        if season_status == "旺":
            final_quality = "吉" if quality != "凶" else "平"
        elif season_status in ("囚", "死"):
            final_quality = "凶" if quality != "吉" else "平"
        else:
            final_quality = quality

        result.append({
            "month_num":    i + 1,
            "tiangan":      m_gan,
            "dizhi":        m_zhi,
            "shishen_gan":  _shishen_label(dm, m_gan),
            "season_status": season_status,
            "quality":      final_quality,
            "summary":      _liuyue_summary(m_gan, m_zhi, final_quality, season_status),
        })
    return result


def _liuyue_summary(m_gan: str, m_zhi: str, quality: str, status: str) -> str:
    if quality == "吉":
        return f"{m_gan}{m_zhi}月，日主{status}，月运顺畅"
    elif quality == "凶":
        return f"{m_gan}{m_zhi}月，日主{status}，月运有阻，宜低调"
    return f"{m_gan}{m_zhi}月，日主{status}，月运平稳"
