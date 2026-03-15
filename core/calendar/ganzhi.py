"""
core/calendar/ganzhi.py
=======================
Utilities for working with the 60-cycle GanZhi (干支) system.
Pure functions — no side effects, no I/O.
"""
from typing import Tuple
from datetime import date as _date
from core.constants import TIANGAN, DIZHI, TIANGAN_INDEX, DIZHI_INDEX

# Reference constants also exported for other modules
_REF_DATE    = _date(1900, 1, 1)
_REF_DAY_IDX = 10   # 1900-01-01 = 甲戌 = index 10


def ganzhi_index(tiangan: str, dizhi: str) -> int:
    """
    Return the 0-based position (0–59) in the 60-cycle for a
    given TianGan + DiZhi pair.
    """
    g = TIANGAN_INDEX[tiangan]
    z = DIZHI_INDEX[dizhi]
    # The 60-cycle starts at 甲子(0). Both sequences advance by 1 each step.
    # A given pair exists iff (g % 2 == z % 2).
    # Index = the unique n in [0,59] where n%10==g and n%12==z.
    for n in range(60):
        if n % 10 == g and n % 12 == z:
            return n
    raise ValueError(f"Invalid GanZhi pair: {tiangan}{dizhi}")


def ganzhi_from_index(idx: int) -> Tuple[str, str]:
    """Return (TianGan, DiZhi) for 0-based index 0–59."""
    idx = idx % 60
    return TIANGAN[idx % 10], DIZHI[idx % 12]


def ganzhi_name(tiangan: str, dizhi: str) -> str:
    """Return the combined name, e.g. '甲子'."""
    return tiangan + dizhi


def next_ganzhi(tiangan: str, dizhi: str, steps: int = 1) -> Tuple[str, str]:
    """Advance a GanZhi pair by *steps* in the 60-cycle."""
    idx = ganzhi_index(tiangan, dizhi)
    return ganzhi_from_index(idx + steps)


def ganzhi_cycle_distance(from_gz: Tuple[str, str], to_gz: Tuple[str, str]) -> int:
    """
    Positive distance (0–59) from one GanZhi to another in the 60-cycle.
    """
    a = ganzhi_index(*from_gz)
    b = ganzhi_index(*to_gz)
    return (b - a) % 60
