"""
core/calendar/solar_terms.py
=============================
Wrappers around the lunarcalendar library's solarterms data.
Provides clean access to 节气 (Jié) boundaries used in pillar
calculations, DaYun distance, etc.

All datetime objects returned are timezone-naive local time.
"""
from datetime import datetime, date
from typing import Optional, Tuple, List

try:
    from lunarcalendar.solarterm import solarterms as _raw_solarterms
    _SOLARTERMS_AVAILABLE = True
except ImportError:
    _SOLARTERMS_AVAILABLE = False


# 24 solar term names in order (小寒 first, matching the library's index)
SOLAR_TERM_NAMES: List[str] = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分",
    "清明", "谷雨", "立夏", "小满", "芒种", "夏至",
    "小暑", "大暑", "立秋", "处暑", "白露", "秋分",
    "寒露", "霜降", "立冬", "小雪", "大雪", "冬至",
]

# Jié (节) — the 12 terms that open a new lunar month
JIE_NAMES: List[str] = [
    "小寒", "立春", "惊蛰", "清明", "立夏", "芒种",
    "小暑", "立秋", "白露", "寒露", "立冬", "大雪",
]


def _get_solarterm_dt(year: int, name: str) -> Optional[datetime]:
    """
    Return the datetime of *name* solar term in *year*.
    Returns None if the lunarcalendar library is unavailable.
    """
    if not _SOLARTERMS_AVAILABLE:
        return None
    idx = SOLAR_TERM_NAMES.index(name)
    try:
        st = _raw_solarterms(year)
        # The library returns a list of 24 (date, time) tuples
        entry = st[idx]
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            d, t = entry[0], entry[1]
            if isinstance(d, date) and isinstance(t, str):
                h, m = map(int, t.split(":")[:2])
                return datetime(d.year, d.month, d.day, h, m)
            if isinstance(d, datetime):
                return d
        if isinstance(entry, datetime):
            return entry
    except Exception:
        pass
    return None


def get_jie_dates(year: int) -> List[Tuple[str, datetime]]:
    """
    Return list of (jie_name, datetime) for all 12 Jié in *year*,
    sorted chronologically.
    """
    result = []
    for name in JIE_NAMES:
        dt = _get_solarterm_dt(year, name)
        if dt:
            result.append((name, dt))
    result.sort(key=lambda x: x[1])
    return result


def get_month_dizhi_at(dt: datetime) -> str:
    """
    Return the lunar-month DiZhi branch for a given datetime,
    determined by which Jié boundary has most recently passed.
    Falls back to a simple solar-month approximation if the
    library is unavailable.
    """
    from core.constants import JIE_TO_DIZHI

    # Check current and previous year's Jié list
    for year in (dt.year, dt.year - 1):
        for name, jie_dt in reversed(get_jie_dates(year)):
            if dt >= jie_dt:
                return JIE_TO_DIZHI[name]

    # Fallback: rough solar month → DiZhi
    _FALLBACK = ["丑","寅","卯","辰","巳","午","未","申","酉","戌","亥","子"]
    return _FALLBACK[dt.month - 1]


def nearest_jie(dt: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Return (previous_jie_dt, next_jie_dt) bracketing *dt*.
    Used for DaYun distance calculation (B-08 fix).
    """
    all_jie: List[datetime] = []
    for year in (dt.year - 1, dt.year, dt.year + 1):
        for _, jie_dt in get_jie_dates(year):
            all_jie.append(jie_dt)
    all_jie.sort()

    prev_jie: Optional[datetime] = None
    next_jie: Optional[datetime] = None
    for jie_dt in all_jie:
        if jie_dt <= dt:
            prev_jie = jie_dt
        else:
            next_jie = jie_dt
            break
    return prev_jie, next_jie


def lichun_of_year(year: int) -> Optional[datetime]:
    """Return the datetime of 立春 for the given Gregorian year."""
    return _get_solarterm_dt(year, "立春")
