"""
models/liuyao.py
================
Pydantic schemas for the LiuYao (六爻) API.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from core.constants import YaoType, LineType


class TrigramModel(BaseModel):
    name:      str
    symbol:    str
    wuxing:    str
    direction: str
    nature:    str
    number:    int
    lines:     List[str]   # ["阳","阳","阳"] etc.


class HexagramModel(BaseModel):
    number:       int
    name:         str
    upper:        TrigramModel
    lower:        TrigramModel
    judgment:     str
    image:        str = ""
    lines:        List[str] = []   # line texts [1..6]


class DivinationRequest(BaseModel):
    method:    str   = Field("coin", description="coin | yarrow | time | manual")
    question:  str   = Field("", description="占卜问题")
    # For manual method: provide 6 yao values (6/7/8/9 from bottom to top)
    yao_values: Optional[List[int]] = Field(None, description="手动输入六爻值 [6/7/8/9] ×6")
    # For time method
    query_time: Optional[str] = Field(None, description="ISO datetime string")


class YaoDetail(BaseModel):
    position:    int     # 1=初爻 … 6=上爻
    yao_type:    YaoType
    line:        LineType
    is_changing: bool
    description: str = ""


class DivinationResponse(BaseModel):
    method:         str
    question:       str
    original:       HexagramModel
    changed:        Optional[HexagramModel] = None
    changing_lines: List[int] = []
    yaos:           List[YaoDetail] = []
    interpretation: str = ""
    advice:         str = ""
