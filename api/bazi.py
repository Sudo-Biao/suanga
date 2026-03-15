"""
api/bazi.py
===========
FastAPI router for all BaZi (八字) endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from models.common import ApiResponse
from models.bazi import (
    BaziRequest, FortuneRequest, CompatibilityRequest,
    BaziChartResponse, FortuneResponse, CompatibilityResponse, ApplicationResponse,
)
from core.bazi.chart import build_chart
from core.bazi.analyzer import analyze_chart
from core.bazi.forecaster import calculate_dayun, calculate_liunian, calculate_liuyue
from core.bazi.applications import (
    career_analysis, marriage_analysis, health_analysis, wealth_analysis,
)
from core.bazi.day_master_profiles import get_day_master_profile, analyze_yong_shen

router = APIRouter(prefix="/bazi", tags=["八字"])


def _build_and_analyze(req: BaziRequest) -> dict:
    """Build chart + run full static analysis. Shared by multiple endpoints."""
    chart = build_chart(req.year, req.month, req.day, req.hour, req.minute)
    analyze_chart(chart)
    chart["_gender"] = req.gender
    return chart


@router.post("/chart", summary="排盘 — 生成四柱八字命盘")
async def get_chart(req: BaziRequest):
    """
    Build the Four Pillars chart with Ten Gods, pattern, strength,
    and Shensha analysis.
    """
    try:
        chart = _build_and_analyze(req)
        chart["day_master_profile"] = get_day_master_profile(chart["day_master"])
        chart["yong_shen"] = analyze_yong_shen(chart)
        return ApiResponse(success=True, data=chart)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fortune", summary="运势 — 大运流年流月预测")
async def get_fortune(req: FortuneRequest):
    """
    Calculate DaYun (10-year cycles), LiuNian (yearly), and
    optionally LiuYue (monthly) fortune.
    """
    try:
        birth = req.birth
        chart = _build_and_analyze(birth)

        dayun = calculate_dayun(chart, birth.gender, birth.year)

        from_yr = req.query_year or birth.year
        to_yr   = (req.query_year or birth.year) + 20
        liunian = calculate_liunian(chart, birth.gender, birth.year,
                                    from_yr, to_yr)

        liuyue = None
        if req.query_year and req.query_month:
            # Find LiuNian TianGan for the query year
            from core.calendar.ganzhi import ganzhi_from_index
            ly_idx = (req.query_year - 1984) % 60
            ly_gan, _ = ganzhi_from_index(ly_idx)
            liuyue = calculate_liuyue(chart, req.query_year, ly_gan)

        data = {
            "dayun":   dayun,
            "liunian": liunian,
            "liuyue":  liuyue,
        }
        return ApiResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/career", summary="事业 — 职业方向分析")
async def get_career(req: BaziRequest):
    try:
        chart = _build_and_analyze(req)
        result = career_analysis(chart)
        profile = get_day_master_profile(chart["day_master"])
        result["profile_career"] = profile.get("career", {})
        result["personality_traits"] = profile.get("strengths", [])
        result["weaknesses"] = profile.get("weaknesses", [])
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/marriage", summary="婚姻 — 感情婚姻分析")
async def get_marriage(req: BaziRequest):
    try:
        chart = _build_and_analyze(req)
        result = marriage_analysis(chart, req.gender)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/health", summary="健康 — 身体健康分析")
async def get_health(req: BaziRequest):
    try:
        chart = _build_and_analyze(req)
        result = health_analysis(chart)
        profile = get_day_master_profile(chart["day_master"])
        result["profile_health"] = profile.get("health", {})
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wealth", summary="财运 — 财富潜力分析")
async def get_wealth(req: BaziRequest):
    try:
        chart = _build_and_analyze(req)
        result = wealth_analysis(chart)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compatibility", summary="合婚 — 八字合婚分析")
async def get_compatibility(req: CompatibilityRequest):
    """Compare two BaZi charts for relationship compatibility."""
    try:
        chart_a = _build_and_analyze(req.person_a)
        chart_b = _build_and_analyze(req.person_b)

        # Simple compatibility: compare wuxing balance
        from core.constants import WUXING_SHENG, WUXING_KE, TIANGAN_WUXING
        wx_a = TIANGAN_WUXING[chart_a["day_master"]]
        wx_b = TIANGAN_WUXING[chart_b["day_master"]]

        if WUXING_SHENG.get(wx_a) == wx_b or WUXING_SHENG.get(wx_b) == wx_a:
            score, summary = 85, f"五行相生（{wx_a}生{wx_b}），婚配和谐，相互扶持"
        elif wx_a == wx_b:
            score, summary = 70, "五行同类，志同道合，需注意各自独立空间"
        elif WUXING_KE.get(wx_a) == wx_b or WUXING_KE.get(wx_b) == wx_a:
            score, summary = 55, "五行相克，性格差异较大，需多磨合包容"
        else:
            score, summary = 75, "五行平衡，婚配较好，相互补充"

        return ApiResponse(success=True, data={
            "score": score,
            "summary": summary,
            "person_a": {"day_master": chart_a["day_master"],
                         "pattern":    chart_a.get("pattern", "")},
            "person_b": {"day_master": chart_b["day_master"],
                         "pattern":    chart_b.get("pattern", "")},
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
