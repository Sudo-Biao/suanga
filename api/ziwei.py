"""
api/ziwei.py
============
FastAPI router for Zi Wei Dou Shu (紫微斗数) endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from models.common import ApiResponse
from core.ziwei.chart import build_ziwei_chart

router = APIRouter(prefix="/ziwei", tags=["紫微斗数"])

# Hour index reference (0=子时 … 11=亥时, each covers 2 hours)
HOUR_MAP = {
    "子时(23-1)": 0, "丑时(1-3)": 1, "寅时(3-5)": 2,  "卯时(5-7)": 3,
    "辰时(7-9)": 4,  "巳时(9-11)": 5, "午时(11-13)": 6, "未时(13-15)": 7,
    "申时(15-17)": 8,"酉时(17-19)": 9,"戌时(19-21)": 10,"亥时(21-23)": 11,
}


class ZiWeiRequest(BaseModel):
    year:   int  = Field(..., ge=1800, le=2100, description="出生年（公历）")
    month:  int  = Field(..., ge=1, le=12)
    day:    int  = Field(..., ge=1, le=31)
    hour:   int  = Field(..., ge=0, le=23, description="出生小时（0-23，24小时制）")
    gender: str  = Field("男", description="男 | 女")
    name:   Optional[str] = None

    def to_solar_date(self) -> str:
        return f"{self.year}-{self.month}-{self.day}"

    def to_hour_index(self) -> int:
        """Convert 24h hour to iztro time index (0=子 … 11=亥)."""
        # 子(23,0,1) 丑(1,2,3) 寅(3,4,5) 卯(5,6,7) 辰(7,8,9) 巳(9,10,11)
        # 午(11,12,13) 未(13,14,15) 申(15,16,17) 酉(17,18,19) 戌(19,20,21) 亥(21,22,23)
        h = self.hour
        if h == 23 or h in (0, 1): return 0   # 子
        if h in (1, 2, 3):         return 1   # 丑
        if h in (3, 4, 5):         return 2   # 寅
        if h in (5, 6, 7):         return 3   # 卯
        if h in (7, 8, 9):         return 4   # 辰
        if h in (9, 10, 11):       return 5   # 巳
        if h in (11, 12, 13):      return 6   # 午
        if h in (13, 14, 15):      return 7   # 未
        if h in (15, 16, 17):      return 8   # 申
        if h in (17, 18, 19):      return 9   # 酉
        if h in (19, 20, 21):      return 10  # 戌
        return 11  # 亥 (21-23)


@router.post("/chart", summary="紫微斗数排盘")
async def ziwei_chart(req: ZiWeiRequest):
    """Generate a complete Zi Wei Dou Shu astrolabe."""
    try:
        gender = req.gender if req.gender in ("男", "女") else "男"
        result = build_ziwei_chart(
            solar_date=req.to_solar_date(),
            birth_hour_index=req.to_hour_index(),
            gender=gender,
        )
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/hours", summary="时辰对照表")
async def hour_table():
    """Return the 12 Chinese hours with clock-time ranges."""
    hours = [
        {"index": 0,  "name": "子时", "range": "23:00–01:00", "clock": [23, 0]},
        {"index": 1,  "name": "丑时", "range": "01:00–03:00", "clock": [1, 2]},
        {"index": 2,  "name": "寅时", "range": "03:00–05:00", "clock": [3, 4]},
        {"index": 3,  "name": "卯时", "range": "05:00–07:00", "clock": [5, 6]},
        {"index": 4,  "name": "辰时", "range": "07:00–09:00", "clock": [7, 8]},
        {"index": 5,  "name": "巳时", "range": "09:00–11:00", "clock": [9, 10]},
        {"index": 6,  "name": "午时", "range": "11:00–13:00", "clock": [11, 12]},
        {"index": 7,  "name": "未时", "range": "13:00–15:00", "clock": [13, 14]},
        {"index": 8,  "name": "申时", "range": "15:00–17:00", "clock": [15, 16]},
        {"index": 9,  "name": "酉时", "range": "17:00–19:00", "clock": [17, 18]},
        {"index": 10, "name": "戌时", "range": "19:00–21:00", "clock": [19, 20]},
        {"index": 11, "name": "亥时", "range": "21:00–23:00", "clock": [21, 22]},
    ]
    return ApiResponse(success=True, data=hours)
