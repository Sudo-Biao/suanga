"""
api/qimen.py
============
FastAPI router for QiMen DunJia (奇门遁甲) endpoints.
"""
from fastapi import APIRouter, HTTPException
from models.common import ApiResponse
from models.qimen import QimenRequest
from core.qimen.algorithm import calculate_qimen
from core.qimen.analyzer import analyze_qimen
from core.qimen.purpose_analysis import enrich_qimen_analysis

router = APIRouter(prefix="/qimen", tags=["奇门遁甲"])


@router.post("/layout", summary="排盘 — 奇门遁甲布局")
async def get_layout(req: QimenRequest):
    """Calculate a full QiMen DunJia layout with interpretation."""
    try:
        layout = calculate_qimen(
            req.year, req.month, req.day, req.hour, req.minute,
            yang_dun_override=req.use_yang_dun,
        )
        result = analyze_qimen(layout)
        result = enrich_qimen_analysis(result)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/now", summary="即时排盘 — 以当前时间起局")
async def get_now_layout():
    """Calculate QiMen layout for the current moment."""
    from datetime import datetime
    now = datetime.now()
    try:
        layout = calculate_qimen(now.year, now.month, now.day, now.hour, now.minute)
        result = analyze_qimen(layout)
        result = enrich_qimen_analysis(result)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
