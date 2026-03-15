"""
api/date_selection.py
=====================
FastAPI router for DateSelection (择日) endpoints.
"""
from fastapi import APIRouter, HTTPException
from models.common import ApiResponse
from models.fengshui import DateSelectionRequest
from core.date_selection.selector import select_dates

router = APIRouter(prefix="/date-selection", tags=["择日"])


@router.post("/select", summary="择日 — 选取吉日")
async def select_auspicious_dates(req: DateSelectionRequest):
    """
    Return auspicious days for the given purpose in a month.
    """
    try:
        result = select_dates(
            purpose=req.purpose,
            year=req.year,
            month=req.month,
            birth_year=req.birth_year,
            birth_month=req.birth_month,
            birth_day=req.birth_day,
        )
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
