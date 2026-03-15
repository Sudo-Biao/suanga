"""
api/liuyao.py
=============
FastAPI router for LiuYao (六爻) divination endpoints.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional, List

from models.common import ApiResponse
from models.liuyao import DivinationRequest
from core.liuyao.divination import (
    coin_divination, yarrow_divination, time_divination, manual_divination,
)
from core.liuyao.interpreter import interpret
from core.liuyao.najia import annotate_with_najia, HEXAGRAM_PALACE

router = APIRouter(prefix="/liuyao", tags=["六爻"])


@router.post("/divine", summary="占卜 — 起卦")
async def divine(req: DivinationRequest):
    """
    Perform a LiuYao divination using the specified method.
    Methods: coin | yarrow | time | manual
    """
    try:
        method = req.method.lower()

        if method == "coin":
            result = coin_divination(req.yao_values)
        elif method == "yarrow":
            result = yarrow_divination()
        elif method == "time":
            dt = datetime.fromisoformat(req.query_time) if req.query_time else None
            result = time_divination(dt)
        elif method == "manual":
            if not req.yao_values or len(req.yao_values) != 6:
                raise ValueError("manual方法需要提供6个爻值 (6/7/8/9)")
            result = manual_divination(req.yao_values)
        else:
            raise ValueError(f"不支持的占卜方法: {method}")

        # Step 1: annotate with Najia (sets is_world, is_application, liu_qin, liu_shen, etc.)
        from datetime import datetime
        from core.calendar.ganzhi import ganzhi_from_index, _REF_DATE, _REF_DAY_IDX
        from core.constants import TIANGAN_WUXING, hour_to_dizhi
        now = datetime.now()
        day_delta = (now.date() - _REF_DATE).days
        day_idx   = (_REF_DAY_IDX + day_delta) % 60
        day_gan, day_zhi = ganzhi_from_index(day_idx)
        month_zhi = hour_to_dizhi(now.month * 2 + 1)
        hex_num    = result["original"]["number"]
        lower_name = result["original"]["lower"]["name"]
        upper_name = result["original"]["upper"]["name"]
        try:
            annotate_with_najia(
                result, hex_num, lower_name, upper_name,
                day_gan, day_idx, day_zhi,
            )
        except Exception:
            pass  # Najia is enhancement; don't fail the whole request

        # Step 2: apply classical interpretation (now has is_world, liu_qin, etc.)
        interpreted = interpret(result, req.question)

        return ApiResponse(success=True, data=interpreted)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/hexagram/{number}", summary="查卦 — 查询指定卦象")
async def get_hexagram(number: int):
    """Get full data for a specific hexagram by King-Wen number (1-64)."""
    try:
        from core.liuyao.hexagram_data import HEXAGRAM_DATA, HEXAGRAM_TRIGRAM_MAPPING
        from core.constants import TRIGRAMS
        if number < 1 or number > 64:
            raise ValueError("卦序必须在1-64之间")
        data    = HEXAGRAM_DATA[number]
        lower_n, upper_n = HEXAGRAM_TRIGRAM_MAPPING[number]
        return ApiResponse(success=True, data={
            "number":   number,
            "name":     data["name"],
            "upper":    {**TRIGRAMS[upper_n], "name": upper_n},
            "lower":    {**TRIGRAMS[lower_n], "name": lower_n},
            "judgment": data["judgment"],
            "image":    data.get("image", ""),
            "lines":    data.get("lines", {}),
            "interpretation": data.get("interpretation", ""),
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/hexagrams", summary="列卦 — 获取所有64卦列表")
async def list_hexagrams():
    """Return a compact list of all 64 hexagrams."""
    from core.liuyao.hexagram_data import HEXAGRAM_DATA
    items = [
        {"number": n, "name": d["name"], "element": d.get("element", "")}
        for n, d in sorted(HEXAGRAM_DATA.items())
    ]
    return ApiResponse(success=True, data=items)
