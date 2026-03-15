"""
api/fengshui.py
===============
FastAPI router for FengShui (风水) endpoints.
"""
from fastapi import APIRouter, HTTPException
from models.common import ApiResponse
from models.fengshui import FengShuiRequest
from core.fengshui.calculator import (
    calculate_ming_gua, get_ming_gua_group,
    get_house_gua, get_house_group,
    check_compatibility, get_sector_analysis,
)
from core.fengshui.flying_stars import (
    calculate_annual_flying_stars, get_personal_directions, comprehensive_fengshui_analysis,
)

router = APIRouter(prefix="/fengshui", tags=["风水"])


@router.post("/analysis", summary="风水分析 — 命卦与宅卦")
async def feng_shui_analysis(req: FengShuiRequest):
    """
    Calculate Ming Gua, House Gua, compatibility, and Eight-Mansion
    sector analysis.
    """
    try:
        ming_gua    = calculate_ming_gua(req.birth_year, req.gender)
        ming_group  = get_ming_gua_group(ming_gua)
        house_gua   = get_house_gua(req.house_facing)
        house_group = get_house_group(house_gua)
        compat      = check_compatibility(ming_gua, house_gua)
        sectors     = get_sector_analysis(house_gua)

        auspicious   = [s for s in sectors if s["quality"] == "吉"]
        inauspicious = [s for s in sectors if s["quality"] in ("凶", "大凶")]

        from datetime import datetime
        year = datetime.now().year
        flying = comprehensive_fengshui_analysis(ming_gua, house_gua, year, req.house_facing)

        return ApiResponse(success=True, data={
            "ming_gua":           ming_gua,
            "ming_gua_group":     ming_group,
            "house_gua":          house_gua,
            "house_group":        house_group,
            "compatibility":      compat,
            "auspicious_sectors": auspicious,
            "inauspicious_sectors": inauspicious,
            "overall_advice": (
                f"命卦{ming_gua}({ming_group})，宅卦{house_gua}({house_group})，"
                f"{'命宅相配，居住有利' if compat == '相配' else '命宅不相配，建议以吉方弥补'}。"
            ),
            "annual_flying_stars": flying["annual_chart"],
            "personal_directions": flying["personal_directions"],
            "combined_advice":     flying["combined_advice"],
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
