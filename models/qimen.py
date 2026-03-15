"""
models/qimen.py
===============
Pydantic schemas for the QiMen DunJia (奇门遁甲) API.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class QimenRequest(BaseModel):
    year:   int
    month:  int
    day:    int
    hour:   int
    minute: int = 0
    question: str = ""
    use_yang_dun: Optional[bool] = None   # None = auto-detect


class PalaceCell(BaseModel):
    position:    int          # 1–9 (洛书方位)
    palace_name: str          # 坎宫 etc.
    star:        str          # 天蓬 etc.
    door:        str          # 休门 etc.
    deity:       str          # 值符 etc.
    stem:        str          # 天干
    is_auspicious: bool = False
    notes:       str = ""


class QimenResponse(BaseModel):
    ju_type:     str           # 阳遁/阴遁
    ju_number:   int           # 1–9
    yuan:        str           # 上元/中元/下元
    palaces:     List[PalaceCell] = []
    auspicious_directions: List[str] = []
    inauspicious_directions: List[str] = []
    summary:     str = ""
    advice:      str = ""
