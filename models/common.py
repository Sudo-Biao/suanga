"""
models/common.py
================
Shared Pydantic models used across multiple disciplines.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class WuXing(str, Enum):
    MU  = "木"
    HUO = "火"
    TU  = "土"
    JIN = "金"
    SHUI = "水"


class YinYang(str, Enum):
    YIN  = "阴"
    YANG = "阳"


class GanZhi(BaseModel):
    """A single Heavenly Stem + Earthly Branch pair."""
    tiangan: str = Field(..., description="天干")
    dizhi:   str = Field(..., description="地支")
    nayin:   Optional[str] = Field(None, description="纳音五行")

    @property
    def name(self) -> str:
        return self.tiangan + self.dizhi


class Pillar(BaseModel):
    """One of the four BaZi pillars (年/月/日/时柱)."""
    label:    str          = Field(..., description="柱名 e.g. 年柱")
    tiangan:  str          = Field(..., description="天干")
    dizhi:    str          = Field(..., description="地支")
    nayin:    Optional[str] = None
    canggan:  List[str]    = Field(default_factory=list, description="藏干")
    wuxing_gan: Optional[str] = None
    wuxing_zhi: Optional[str] = None

    @property
    def ganzhi(self) -> str:
        return self.tiangan + self.dizhi


class ApiResponse(BaseModel):
    """Standard envelope for all API responses."""
    success: bool = True
    data:    Any  = None
    message: str  = ""
    errors:  List[str] = Field(default_factory=list)
