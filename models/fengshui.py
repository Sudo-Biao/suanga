"""
models/fengshui.py
==================
Pydantic schemas for FengShui (风水) and DateSelection (择日) APIs.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ── FengShui ─────────────────────────────────

class FengShuiRequest(BaseModel):
    birth_year:   int = Field(..., description="出生年份 (for 命卦)")
    gender:       str = Field("male", description="male | female")
    house_facing: str = Field(..., description="房屋朝向 e.g. 南, 北, 东南")
    house_sitting: Optional[str] = Field(None, description="坐向 (auto-derived if omitted)")
    floors:       Optional[int] = Field(None, description="层数")
    rooms:        Optional[List[Dict[str, str]]] = Field(None, description="房间朝向列表")


class FengShuiSector(BaseModel):
    direction:  str
    star:       str
    quality:    str   # 吉/凶/平
    meaning:    str
    advice:     str = ""


class FengShuiResponse(BaseModel):
    ming_gua:           int
    ming_gua_group:     str   # 东四命/西四命
    house_gua:          int
    house_group:        str   # 东四宅/西四宅
    compatibility:      str   # 相配/不相配
    auspicious_sectors: List[FengShuiSector] = []
    inauspicious_sectors: List[FengShuiSector] = []
    overall_advice:     str = ""


# ── DateSelection ────────────────────────────

class DateSelectionRequest(BaseModel):
    purpose:    str   = Field(..., description="择日目的 e.g. 婚嫁, 开业, 动土, 搬家")
    year:       int
    month:      int
    birth_year: Optional[int]  = None
    birth_month: Optional[int] = None
    birth_day:  Optional[int]  = None
    gender:     Optional[str]  = None


class AuspiciousDay(BaseModel):
    date:     str   # ISO date string
    weekday:  str
    ganzhi:   str
    quality:  int   # 1–5 stars
    suitable: List[str] = []
    avoid:    List[str] = []
    notes:    str = ""


class DateSelectionResponse(BaseModel):
    purpose:         str
    month_summary:   str = ""
    auspicious_days: List[AuspiciousDay] = []
    inauspicious_days: List[str] = []
    best_day:        Optional[AuspiciousDay] = None
