"""
api/knowledge_api.py
====================
FastAPI router for the classical knowledge base.
Exposes lookup endpoints for all five systems.
"""
from fastapi import APIRouter
from models.common import ApiResponse

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/shishen/{name}", summary="十神详解")
async def get_shishen_detail(name: str):
    from knowledge.classical_knowledge import SHISHEN_FULL
    data = SHISHEN_FULL.get(name)
    if not data:
        return ApiResponse(success=False, data=None, message=f"未知十神: {name}")
    return ApiResponse(success=True, data=data)


@router.get("/shishen", summary="全部十神")
async def list_shishen():
    from knowledge.classical_knowledge import SHISHEN_FULL
    return ApiResponse(success=True, data={
        k: {"symbol": v["symbol"], "nature": v["nature"]}
        for k, v in SHISHEN_FULL.items()
    })


@router.get("/pillars", summary="四柱宫位解析")
async def get_pillar_meanings():
    from knowledge.classical_knowledge import PILLAR_PALACE_MEANINGS
    return ApiResponse(success=True, data=PILLAR_PALACE_MEANINGS)


@router.get("/dizhi-relations", summary="地支关系解析")
async def get_dizhi_relations():
    from knowledge.classical_knowledge import DIZHI_RELATIONS_DETAIL
    return ApiResponse(success=True, data=DIZHI_RELATIONS_DETAIL)


@router.get("/liuyao-topics", summary="六爻占问用神")
async def get_liuyao_topics():
    from knowledge.classical_knowledge import LIUYAO_TOPIC_RULES
    return ApiResponse(success=True, data=LIUYAO_TOPIC_RULES)


@router.get("/liuyao-rules", summary="六爻经典口诀")
async def get_liuyao_rules():
    from knowledge.classical_knowledge import LIUYAO_CLASSICAL_RULES
    return ApiResponse(success=True, data=LIUYAO_CLASSICAL_RULES)


@router.get("/qimen-matrix", summary="奇门星门组合")
async def get_qimen_matrix():
    from knowledge.classical_knowledge import QIMEN_STAR_DOOR_MATRIX
    return ApiResponse(success=True, data=QIMEN_STAR_DOOR_MATRIX)


@router.get("/24mountains", summary="二十四山")
async def get_24mountains():
    from knowledge.classical_knowledge import TWENTY_FOUR_MOUNTAINS
    return ApiResponse(success=True, data=TWENTY_FOUR_MOUNTAINS)


@router.get("/formulas", summary="经典口诀")
async def get_formulas():
    from knowledge.classical_knowledge import CLASSIC_FORMULAS
    return ApiResponse(success=True, data=CLASSIC_FORMULAS)


@router.get("/season-guide/{day_master}", summary="日主月令用神指南")
async def get_season_guide(day_master: str):
    from knowledge.classical_knowledge import DAY_MASTER_SEASON_GUIDE
    result = {k: v for k, v in DAY_MASTER_SEASON_GUIDE.items() if k.startswith(day_master + "_")}
    return ApiResponse(success=True, data=result)
