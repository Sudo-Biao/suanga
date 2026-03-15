"""
models/bazi.py
==============
Pydantic request / response schemas for the BaZi (八字) API.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ──────────────────────────────────────────────
# Requests
# ──────────────────────────────────────────────

class BaziRequest(BaseModel):
    """Birth data for a BaZi reading."""
    year:   int  = Field(..., ge=1900, le=2100)
    month:  int  = Field(..., ge=1, le=12)
    day:    int  = Field(..., ge=1, le=31)
    hour:   int  = Field(..., ge=0, le=23)
    minute: int  = Field(0, ge=0, le=59)
    gender: str  = Field("male", description="male | female")
    name:   Optional[str] = None
    use_true_solar_time: bool = Field(False, description="使用真太阳时")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("male", "female", "男", "女"):
            raise ValueError("gender must be 'male' or 'female'")
        return v


class CompatibilityRequest(BaseModel):
    person_a: BaziRequest
    person_b: BaziRequest


class FortuneRequest(BaseModel):
    birth: BaziRequest
    query_year:  Optional[int] = None
    query_month: Optional[int] = None


# ──────────────────────────────────────────────
# Sub-objects in responses
# ──────────────────────────────────────────────

class PillarDetail(BaseModel):
    tiangan:     str
    dizhi:       str
    nayin:       Optional[str] = None
    canggan:     List[str] = []
    shishen_gan: Optional[str] = None   # ten-god of the stem
    shishen_zhi: Optional[str] = None   # ten-god of the branch's main hidden stem
    wuxing_gan:  Optional[str] = None
    wuxing_zhi:  Optional[str] = None


class ShishenSummary(BaseModel):
    shishen:  str
    count:    int
    stems:    List[str] = []
    strength: str = ""   # 旺/相/休/囚/死


class DayunPeriod(BaseModel):
    index:      int
    tiangan:    str
    dizhi:      str
    start_age:  float
    end_age:    float
    start_year: int
    end_year:   int
    quality:    str = ""   # 吉/凶/平


class LiunianDetail(BaseModel):
    year:     int
    tiangan:  str
    dizhi:    str
    age:      int
    shishen_gan: str = ""
    shishen_zhi: str = ""
    quality:  str = ""
    summary:  str = ""


class ShenSha(BaseModel):
    name:   str
    dizhi:  str
    pillar: str   # 年/月/日/时


# ──────────────────────────────────────────────
# Top-level responses
# ──────────────────────────────────────────────

class BaziChartResponse(BaseModel):
    year_pillar:  PillarDetail
    month_pillar: PillarDetail
    day_pillar:   PillarDetail
    hour_pillar:  PillarDetail
    day_master:   str
    day_master_wuxing: str
    shishen_list: List[ShishenSummary] = []
    pattern:      str = ""
    pattern_desc: str = ""
    shensha:      List[ShenSha] = []
    strength:     str = ""   # 身强/身弱/中和
    nayin_summary: str = ""


class FortuneResponse(BaseModel):
    dayun_list:   List[DayunPeriod] = []
    current_dayun: Optional[DayunPeriod] = None
    liunian_list: List[LiunianDetail] = []
    summary:      str = ""


class CompatibilityResponse(BaseModel):
    score:   int = Field(..., ge=0, le=100)
    summary: str = ""
    details: Dict[str, Any] = {}


class ApplicationResponse(BaseModel):
    topic:    str
    analysis: str
    advice:   List[str] = []
    lucky:    Dict[str, Any] = {}
