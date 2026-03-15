"""
api/knowledge.py
================
FastAPI router for the knowledge base API.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from models.common import ApiResponse
from knowledge.manager import knowledge_manager

router = APIRouter(prefix="/knowledge", tags=["知识库"])


class SearchRequest(BaseModel):
    keyword: str
    category: Optional[str] = None


@router.get("/search", summary="搜索知识库")
async def search(
    keyword: str = Query(..., description="关键词"),
    category: Optional[str] = Query(None, description="类别"),
):
    try:
        results = knowledge_manager.search(keyword, category)
        return ApiResponse(success=True, data=results, message=f"找到 {len(results)} 条")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", summary="POST搜索知识库")
async def search_post(req: SearchRequest):
    try:
        results = knowledge_manager.search(req.keyword, req.category)
        return ApiResponse(success=True, data=results, message=f"找到 {len(results)} 条")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", summary="获取知识类别列表")
async def get_categories():
    return ApiResponse(success=True, data=knowledge_manager.get_categories())


@router.post("/smart-search", summary="智能搜索")
async def smart_search(req: SearchRequest):
    try:
        result = knowledge_manager.smart_search(req.keyword)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Classical Knowledge endpoints ──────────────────────────

@router.get("/classical/shishen", summary="十神完整解析")
async def classical_shishen():
    try:
        from knowledge.classical_knowledge import SHISHEN_FULL
        return ApiResponse(success=True, data=SHISHEN_FULL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/shishen/{name}", summary="单一十神详解")
async def classical_shishen_detail(name: str):
    try:
        from knowledge.classical_knowledge import SHISHEN_FULL
        data = SHISHEN_FULL.get(name)
        if not data:
            return ApiResponse(success=False, data=None, message=f"未找到: {name}")
        return ApiResponse(success=True, data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/pillars", summary="四柱宫位深解")
async def classical_pillars():
    try:
        from knowledge.classical_knowledge import PILLAR_PALACE_MEANINGS
        return ApiResponse(success=True, data=PILLAR_PALACE_MEANINGS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/dizhi", summary="地支关系全解")
async def classical_dizhi():
    try:
        from knowledge.classical_knowledge import DIZHI_RELATIONS_DETAIL
        return ApiResponse(success=True, data=DIZHI_RELATIONS_DETAIL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-topics", summary="六爻占问用神规则（12类）")
async def classical_liuyao_topics():
    try:
        from knowledge.liuyao_classical import LIUYAO_TOPIC_RULES
        return ApiResponse(success=True, data=LIUYAO_TOPIC_RULES)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-rules", summary="六爻经典决断口诀（16条）")
async def classical_liuyao_rules():
    try:
        from knowledge.liuyao_classical import LIUYAO_CLASSICAL_RULES
        return ApiResponse(success=True, data=LIUYAO_CLASSICAL_RULES)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-system", summary="六爻纳甲体系（浑天纳甲+世应+六亲）")
async def classical_liuyao_system():
    try:
        from knowledge.liuyao_classical import LIUYAO_NAJIA_SYSTEM
        return ApiResponse(success=True, data=LIUYAO_NAJIA_SYSTEM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-gods", summary="六神断事精要")
async def classical_liuyao_gods():
    try:
        from knowledge.liuyao_classical import LIUYAO_SIX_GODS
        return ApiResponse(success=True, data=LIUYAO_SIX_GODS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-relatives", summary="六亲详解（用神取法）")
async def classical_liuyao_relatives():
    try:
        from knowledge.liuyao_classical import LIUYAO_SIX_RELATIVES
        return ApiResponse(success=True, data=LIUYAO_SIX_RELATIVES)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-timing", summary="应期推算总法（病药原则）")
async def classical_liuyao_timing():
    try:
        from knowledge.liuyao_classical import LIUYAO_TIMING
        return ApiResponse(success=True, data=LIUYAO_TIMING)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-flying", summary="飞神伏神详法")
async def classical_liuyao_flying():
    try:
        from knowledge.liuyao_classical import LIUYAO_FLYING_HIDDEN
        return ApiResponse(success=True, data=LIUYAO_FLYING_HIDDEN)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/liuyao-history", summary="六爻纳甲体系源流")
async def classical_liuyao_history():
    try:
        from knowledge.liuyao_classical import LIUYAO_HISTORY
        return ApiResponse(success=True, data=LIUYAO_HISTORY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/qimen-matrix", summary="奇门星门组合矩阵")
async def classical_qimen_matrix():
    try:
        from knowledge.classical_knowledge import QIMEN_STAR_DOOR_MATRIX
        return ApiResponse(success=True, data=QIMEN_STAR_DOOR_MATRIX)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/formulas", summary="经典口诀")
async def classical_formulas():
    try:
        from knowledge.classical_knowledge import CLASSIC_FORMULAS
        return ApiResponse(success=True, data=CLASSIC_FORMULAS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/24mountains", summary="二十四山")
async def classical_24mountains():
    try:
        from knowledge.classical_knowledge import TWENTY_FOUR_MOUNTAINS
        return ApiResponse(success=True, data=TWENTY_FOUR_MOUNTAINS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# 八字经典知识库
# ═══════════════════════════════════════════════════════════

@router.get("/classical/bazi-tiao-hou", summary="《穷通宝鉴》调候用神表")
async def classical_bazi_tiao_hou():
    try:
        from knowledge.bazi_classical import TIAO_HOU_TABLE
        return ApiResponse(success=True, data=TIAO_HOU_TABLE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/bazi-shigan", summary="《滴天髓》十天干论命口诀")
async def classical_bazi_shigan():
    try:
        from knowledge.bazi_classical import SHIGAN_JIJUE
        return ApiResponse(success=True, data=SHIGAN_JIJUE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/bazi-gejv", summary="《子平真诠》格局体系")
async def classical_bazi_gejv():
    try:
        from knowledge.bazi_classical import BAZIGE_SYSTEM
        return ApiResponse(success=True, data=BAZIGE_SYSTEM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/bazi-rizhupan", summary="日主强弱判断规则")
async def classical_bazi_rizhupan():
    try:
        from knowledge.bazi_classical import RIZHUPAN_RULES, YUNIAN_RULES
        return ApiResponse(success=True, data={"strength": RIZHUPAN_RULES, "yun": YUNIAN_RULES})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/bazi-zhuwei", summary="四柱宫位六亲体系")
async def classical_bazi_zhuwei():
    try:
        from knowledge.bazi_classical import ZHUWEI_LIUQIN, LIUQIN_BAZI
        return ApiResponse(success=True, data={"pillars": ZHUWEI_LIUQIN, "liuqin": LIUQIN_BAZI})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# 奇门遁甲经典知识库
# ═══════════════════════════════════════════════════════════

@router.get("/classical/qimen-sanqi", summary="三奇六仪详解")
async def classical_qimen_sanqi():
    try:
        from knowledge.qimen_classical import SAN_QI_LIU_YI
        return ApiResponse(success=True, data=SAN_QI_LIU_YI)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/qimen-bamen", summary="八门详解（《烟波钓叟赋》）")
async def classical_qimen_bamen():
    try:
        from knowledge.qimen_classical import BA_MEN_DETAIL
        return ApiResponse(success=True, data=BA_MEN_DETAIL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/qimen-jiuxing", summary="九星详解")
async def classical_qimen_jiuxing():
    try:
        from knowledge.qimen_classical import JIU_XING_DETAIL
        return ApiResponse(success=True, data=JIU_XING_DETAIL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/qimen-yanbo", summary="《烟波钓叟赋》核心口诀")
async def classical_qimen_yanbo():
    try:
        from knowledge.qimen_classical import YANBO_JIJUE
        return ApiResponse(success=True, data=YANBO_JIJUE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/qimen-gejv", summary="奇门格局（吉凶格局）")
async def classical_qimen_gejv():
    try:
        from knowledge.qimen_classical import QIMEN_GEJV
        return ApiResponse(success=True, data=QIMEN_GEJV)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# 风水经典知识库
# ═══════════════════════════════════════════════════════════

@router.get("/classical/fengshui-yangzhai", summary="《阳宅三要》门主灶")
async def classical_fengshui_yangzhai():
    try:
        from knowledge.fengshui_classical import YANGZHAI_THREE
        return ApiResponse(success=True, data=YANGZHAI_THREE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/fengshui-bayuan", summary="《八宅明镜》游年九星")
async def classical_fengshui_bayuan():
    try:
        from knowledge.fengshui_classical import BAYUAN_JIUXING, DONGXI_SANZHAI
        return ApiResponse(success=True, data={"jiuxing": BAYUAN_JIUXING, "dongxi": DONGXI_SANZHAI})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/fengshui-xuankong", summary="《沈氏玄空学》飞星九运")
async def classical_fengshui_xuankong():
    try:
        from knowledge.fengshui_classical import XUANKONG_THEORY, SHAQT_HUAJIE
        return ApiResponse(success=True, data={"xuankong": XUANKONG_THEORY, "sha": SHAQT_HUAJIE})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/fengshui-longxue", summary="《地理五诀》龙穴砂水向")
async def classical_fengshui_longxue():
    try:
        from knowledge.fengshui_classical import LONGXUE_THEORY
        return ApiResponse(success=True, data=LONGXUE_THEORY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# 择日经典知识库
# ═══════════════════════════════════════════════════════════

@router.get("/classical/date-jianshen", summary="建除十二神择日")
async def classical_date_jianshen():
    try:
        from knowledge.date_classical import JIANSHEN_TWELVE
        return ApiResponse(success=True, data=JIANSHEN_TWELVE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/date-huangdao", summary="黄道十二神")
async def classical_date_huangdao():
    try:
        from knowledge.date_classical import HUANGDAO_TWELVE
        return ApiResponse(success=True, data=HUANGDAO_TWELVE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/date-shensha", summary="《协纪辨方书》重要神煞")
async def classical_date_shensha():
    try:
        from knowledge.date_classical import ZERI_SHENSHA
        return ApiResponse(success=True, data=ZERI_SHENSHA)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classical/date-events", summary="各类事务择日要诀")
async def classical_date_events():
    try:
        from knowledge.date_classical import ZERI_EVENTS
        return ApiResponse(success=True, data=ZERI_EVENTS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# 基础知识库
# ═══════════════════════════════════════════════════════════

@router.get("/foundations/yinyang", summary="阴阳理论完整体系")
async def foundations_yinyang():
    from knowledge.foundations import YINYANG
    return ApiResponse(success=True, data=YINYANG)

@router.get("/foundations/wuxing", summary="五行完整体系（含旺相休囚死）")
async def foundations_wuxing():
    from knowledge.foundations import WUXING, WUXING_RELATIONS
    return ApiResponse(success=True, data={"wuxing": WUXING, "relations": WUXING_RELATIONS})

@router.get("/foundations/tiangan", summary="十天干完整体系（含《滴天髓》口诀）")
async def foundations_tiangan():
    from knowledge.foundations import TIANGAN, TIANGAN_LIUHE, TIANGAN_WANGSHUAI
    return ApiResponse(success=True, data={"tiangan": TIANGAN, "liuhe": TIANGAN_LIUHE, "wangshuai": TIANGAN_WANGSHUAI})

@router.get("/foundations/dizhi", summary="十二地支完整体系（含藏干·六冲·三合）")
async def foundations_dizhi():
    from knowledge.foundations import DIZHI, DIZHI_RELATIONS
    return ApiResponse(success=True, data={"dizhi": DIZHI, "relations": DIZHI_RELATIONS})

@router.get("/foundations/nayin", summary="六十甲子纳音五行")
async def foundations_nayin():
    from knowledge.foundations import JIAZI_NAYIN
    return ApiResponse(success=True, data=JIAZI_NAYIN)

@router.get("/foundations/canggan", summary="十二地支藏干表")
async def foundations_canggan():
    from knowledge.foundations import DIZHI
    data = {zhi: info["藏干"] for zhi, info in DIZHI.items()}
    return ApiResponse(success=True, data=data)

# ═══════════════════════════════════════════════════════════
# 十神·神煞·六亲知识库
# ═══════════════════════════════════════════════════════════

@router.get("/shishen/all", summary="十神完整体系（含断法）")
async def shishen_all():
    from knowledge.shishen_shensha import SHISHEN
    return ApiResponse(success=True, data=SHISHEN)

@router.get("/shishen/shensha", summary="重要神煞完整体系")
async def shishen_shensha():
    from knowledge.shishen_shensha import SHENSHA
    return ApiResponse(success=True, data=SHENSHA)

@router.get("/shishen/liuqin", summary="六亲宫位论断")
async def shishen_liuqin():
    from knowledge.shishen_shensha import LIUQIN_GONGWEI
    return ApiResponse(success=True, data=LIUQIN_GONGWEI)

@router.get("/shishen/changsheng", summary="十二长生详解")
async def shishen_changsheng():
    from knowledge.shishen_shensha import SHIER_CHANGSHENG
    return ApiResponse(success=True, data=SHIER_CHANGSHENG)

@router.get("/shishen/dayun", summary="大运流年断法")
async def shishen_dayun():
    from knowledge.shishen_shensha import DAYUN_LIUNIAN
    return ApiResponse(success=True, data=DAYUN_LIUNIAN)

# ═══════════════════════════════════════════════════════════
# 高级体系知识库
# ═══════════════════════════════════════════════════════════

@router.get("/advanced/ziwei", summary="紫微斗数体系概要")
async def advanced_ziwei():
    from knowledge.advanced_systems import ZIWEI
    return ApiResponse(success=True, data=ZIWEI)

@router.get("/advanced/meihua", summary="梅花易数体系")
async def advanced_meihua():
    from knowledge.advanced_systems import MEIHUA
    return ApiResponse(success=True, data=MEIHUA)

@router.get("/advanced/daliuren", summary="大六壬体系概要")
async def advanced_daliuren():
    from knowledge.advanced_systems import DA_LIUREN
    return ApiResponse(success=True, data=DA_LIUREN)

@router.get("/advanced/bazi-deep", summary="八字高级论命体系")
async def advanced_bazi_deep():
    from knowledge.advanced_systems import BAZI_ADVANCED
    return ApiResponse(success=True, data=BAZI_ADVANCED)

@router.get("/advanced/liuyao-deep", summary="六爻高级断法")
async def advanced_liuyao_deep():
    from knowledge.advanced_systems import LIUYAO_ADVANCED
    return ApiResponse(success=True, data=LIUYAO_ADVANCED)

@router.get("/advanced/qimen-deep", summary="奇门遁甲高级体系")
async def advanced_qimen_deep():
    from knowledge.advanced_systems import QIMEN_ADVANCED
    return ApiResponse(success=True, data=QIMEN_ADVANCED)

@router.get("/advanced/xuankong-deep", summary="玄空飞星高级体系")
async def advanced_xuankong_deep():
    from knowledge.advanced_systems import XUANKONG_ADVANCED
    return ApiResponse(success=True, data=XUANKONG_ADVANCED)

@router.get("/advanced/xingshi", summary="形家风水高级体系")
async def advanced_xingshi():
    from knowledge.advanced_systems import XINGSHI_FENGSHUI
    return ApiResponse(success=True, data=XINGSHI_FENGSHUI)

@router.get("/advanced/philosophy", summary="命理哲学与宇宙观")
async def advanced_philosophy():
    from knowledge.advanced_systems import MINGLI_ZHEXUE
    return ApiResponse(success=True, data=MINGLI_ZHEXUE)

# ═══════════════════════════════════════════════════════════
# 实战断法知识库
# ═══════════════════════════════════════════════════════════

@router.get("/practical/steps", summary="命理断命实战步骤")
async def practical_steps():
    from knowledge.practical_divination import DUANMING_STEPS
    return ApiResponse(success=True, data=DUANMING_STEPS)

@router.get("/practical/caiyun", summary="财运断法大全")
async def practical_caiyun():
    from knowledge.practical_divination import CAIYUN_DUANFA
    return ApiResponse(success=True, data=CAIYUN_DUANFA)

@router.get("/practical/ganqing", summary="感情婚姻断法")
async def practical_ganqing():
    from knowledge.practical_divination import GANQING_DUANFA
    return ApiResponse(success=True, data=GANQING_DUANFA)

@router.get("/practical/shiye", summary="事业官运断法")
async def practical_shiye():
    from knowledge.practical_divination import SHIYE_DUANFA
    return ApiResponse(success=True, data=SHIYE_DUANFA)

@router.get("/practical/jibing", summary="疾病健康断法")
async def practical_jibing():
    from knowledge.practical_divination import JIBING_DUANFA
    return ApiResponse(success=True, data=JIBING_DUANFA)

@router.get("/practical/yingqi", summary="应期推算综合体系")
async def practical_yingqi():
    from knowledge.practical_divination import YINGQI_ZONGHE
    return ApiResponse(success=True, data=YINGQI_ZONGHE)

@router.get("/practical/zeri", summary="择日选时精要")
async def practical_zeri():
    from knowledge.practical_divination import ZERI_JINGZAO
    return ApiResponse(success=True, data=ZERI_JINGZAO)

@router.get("/practical/koujue", summary="古今断命口诀汇总")
async def practical_koujue():
    from knowledge.practical_divination import DUANMING_KOUJUE
    return ApiResponse(success=True, data=DUANMING_KOUJUE)

@router.get("/practical/mingjia", summary="名家论断精华")
async def practical_mingjia():
    from knowledge.practical_divination import MINGJIA_JINGHUA
    return ApiResponse(success=True, data=MINGJIA_JINGHUA)


# ═══════════════════════════════════════════════════════════
# 八卦体系
# ═══════════════════════════════════════════════════════════

@router.get("/bagua/taiji", summary="太极两仪四象八卦生成体系")
async def bagua_taiji():
    from knowledge.bagua_system import TAIJI_SHENGCHENG
    return ApiResponse(success=True, data=TAIJI_SHENGCHENG)

@router.get("/bagua/xiantian", summary="先天八卦（伏羲八卦）完整体系")
async def bagua_xiantian():
    from knowledge.bagua_system import XIANTIAN_BAGUA
    return ApiResponse(success=True, data=XIANTIAN_BAGUA)

@router.get("/bagua/houtian", summary="后天八卦（文王八卦）完整体系")
async def bagua_houtian():
    from knowledge.bagua_system import HOUTIAN_BAGUA
    return ApiResponse(success=True, data=HOUTIAN_BAGUA)

@router.get("/bagua/xiangyi", summary="八卦完整象意（含《说卦传》原文）")
async def bagua_xiangyi():
    from knowledge.bagua_system import BAGUA_XIANGYI, BAGUA_JIATING
    return ApiResponse(success=True, data={"xiangyi": BAGUA_XIANGYI, "jiating": BAGUA_JIATING})

@router.get("/bagua/yingyong", summary="八卦与奇门·命理·风水对应")
async def bagua_yingyong():
    from knowledge.bagua_system import BAGUA_YINGYONG
    return ApiResponse(success=True, data=BAGUA_YINGYONG)

@router.get("/bagua/64gua", summary="六十四卦完整列表（卦辞·吉凶·核心）")
async def bagua_64gua():
    from knowledge.bagua_system import LIUSHISI_GUA, LIUSHISI_GUA_KOUJUE
    return ApiResponse(success=True, data={"gua_list": LIUSHISI_GUA, "koujue": LIUSHISI_GUA_KOUJUE})

@router.get("/bagua/jingfang", summary="京房八宫卦体系")
async def bagua_jingfang():
    from knowledge.bagua_system import JINGFANG_BAGONG
    return ApiResponse(success=True, data=JINGFANG_BAGONG)

@router.get("/bagua/yizhuan", summary="易经十翼《易传》核心内容")
async def bagua_yizhuan():
    from knowledge.bagua_system import SHICHI_JINGHUA
    return ApiResponse(success=True, data=SHICHI_JINGHUA)

# ═══════════════════════════════════════════════════════════
# 星宿体系
# ═══════════════════════════════════════════════════════════

@router.get("/xingxiu/sixiang", summary="四象（青龙·朱雀·白虎·玄武）体系")
async def xingxiu_sixiang():
    from knowledge.xingxiu_system import SIXIANG
    return ApiResponse(success=True, data=SIXIANG)

@router.get("/xingxiu/28xiu", summary="二十八宿完整体系（禽星·吉凶·歌诀·宜忌·天文）")
async def xingxiu_28xiu():
    from knowledge.xingxiu_system import ERSHIBA_XIU
    return ApiResponse(success=True, data=ERSHIBA_XIU)

@router.get("/xingxiu/jixiong", summary="二十八宿吉凶速查表")
async def xingxiu_jixiong():
    from knowledge.xingxiu_system import XIU_JIXIONG, XIU_DIZHI
    return ApiResponse(success=True, data={"jixiong": XIU_JIXIONG, "dizhi": XIU_DIZHI})

@router.get("/xingxiu/qinxing", summary="禽星体系（二十八宿配七曜动物）")
async def xingxiu_qinxing():
    from knowledge.xingxiu_system import QINXING
    return ApiResponse(success=True, data=QINXING)

@router.get("/xingxiu/sanvuan", summary="三垣（紫微·太微·天市）体系")
async def xingxiu_sanvuan():
    from knowledge.xingxiu_system import SANVUAN
    return ApiResponse(success=True, data=SANVUAN)

@router.get("/xingxiu/qizheng", summary="七政（日月五星）命理应用")
async def xingxiu_qizheng():
    from knowledge.xingxiu_system import QIZHENG
    return ApiResponse(success=True, data=QIZHENG)

@router.get("/xingxiu/fenye", summary="二十八宿分野（星宿与地域对应）")
async def xingxiu_fenye():
    from knowledge.xingxiu_system import FENYE
    return ApiResponse(success=True, data=FENYE)

@router.get("/xingxiu/zeri", summary="二十八宿择日应用（宜忌·四季用法）")
async def xingxiu_zeri():
    from knowledge.xingxiu_system import XIU_择日, XIU_JIEQI
    return ApiResponse(success=True, data={"zeri": XIU_择日, "jieqi": XIU_JIEQI})

# ═══════════════════════════════════════════════════════════
# 丰富的基础知识补充
# ═══════════════════════════════════════════════════════════

@router.get("/foundations/hetu", summary="河图洛书完整体系")
async def foundations_hetu():
    from knowledge.foundations import HETU_LUOSHU
    return ApiResponse(success=True, data=HETU_LUOSHU)

@router.get("/foundations/ganzhi-calendar", summary="干支纪年法完整体系")
async def foundations_ganzhi_calendar():
    from knowledge.foundations import GANZHI_JINIAN
    return ApiResponse(success=True, data=GANZHI_JINIAN)

@router.get("/classical/bazi-gejv", summary="八字格局完整体系（《子平真诠》）")
async def classical_bazi_gejv():
    from knowledge.bazi_classical import BAZI_GEJV_COMPLETE, QIONGTONG_TIAHOU
    return ApiResponse(success=True, data={"gejv": BAZI_GEJV_COMPLETE, "tiahou": QIONGTONG_TIAHOU})

@router.get("/classical/fengshui-extended", summary="风水扩展知识（紫白飞星·八宅·煞气）")
async def classical_fengshui_extended():
    from knowledge.fengshui_classical import ZIBAIFEIXING_RULES, BAZHAI_COMPLETE, SHAJIAO_HUAJIE
    return ApiResponse(success=True, data={
        "zibaifeixing": ZIBAIFEIXING_RULES,
        "bazhai": BAZHAI_COMPLETE,
        "shajie": SHAJIAO_HUAJIE,
    })


# ═══ Missing endpoints for new Knowledge page ═══

@router.get("/classical/bazi-tiahou", summary="《穷通宝鉴》调候用神月令表")
async def classical_bazi_tiahou():
    from knowledge.bazi_classical import TIAO_HOU_TABLE, QIONGTONG_TIAHOU
    return ApiResponse(success=True, data={"tiahou_table": TIAO_HOU_TABLE, "theory": QIONGTONG_TIAHOU})

@router.get("/classical/rizhupan", summary="日主强弱分析体系")
async def classical_rizhupan():
    from knowledge.bazi_classical import RIZHUPAN_RULES, SHIGAN_JIJUE
    return ApiResponse(success=True, data={"rizhupan": RIZHUPAN_RULES, "shigan": SHIGAN_JIJUE})

@router.get("/classical/bayuan", summary="八宅派风水（八宅明镜）")
async def classical_bayuan():
    from knowledge.fengshui_classical import BAYUAN_JIUXING, BAZHAI_COMPLETE
    return ApiResponse(success=True, data={"jiuxing": BAYUAN_JIUXING, "bazhai": BAZHAI_COMPLETE})


# ═══ Enriched data endpoints ═══

@router.get("/classical/liuyao-gods-full", summary="六神完整象意与断法（含六神配六亲）")
async def classical_liuyao_gods_full():
    from knowledge.liuyao_classical import LIUYAO_LIUSHEN_COMPLETE, LIUSHEN_JIEGUA
    return ApiResponse(success=True, data={"六神详解": LIUYAO_LIUSHEN_COMPLETE, "结合断法": LIUSHEN_JIEGUA})

@router.get("/classical/liuyao-yingqi-deep", summary="六爻应期深度（《黄金策》精华）")
async def classical_liuyao_yingqi_deep():
    from knowledge.liuyao_classical import LIUYAO_YINGQI_DEEP
    return ApiResponse(success=True, data=LIUYAO_YINGQI_DEEP)

@router.get("/classical/qimen-yanbo-full", summary="《烟波钓叟赋》完整原文逐句解析")
async def classical_qimen_yanbo_full():
    from knowledge.qimen_classical import YANBO_QUANWEN
    return ApiResponse(success=True, data=YANBO_QUANWEN)

@router.get("/classical/qimen-zhaiji", summary="奇门择吉实战案例体系")
async def classical_qimen_zhaiji():
    from knowledge.qimen_classical import QIMEN_ZHAIJI_SHIZHAN
    return ApiResponse(success=True, data=QIMEN_ZHAIJI_SHIZHAN)

@router.get("/advanced/ziwei-deep", summary="紫微斗数深度（命宫主星·四化深论·三方四正·大限）")
async def advanced_ziwei_deep():
    from knowledge.advanced_systems import ZIWEI_DEEP
    return ApiResponse(success=True, data=ZIWEI_DEEP)

@router.get("/advanced/meihua-deep", summary="梅花易数深度（起卦详法·体用精义·邵雍案例）")
async def advanced_meihua_deep():
    from knowledge.advanced_systems import MEIHUA_DEEP
    return ApiResponse(success=True, data=MEIHUA_DEEP)


# ═══ Deep specialty endpoints ═══

@router.get("/classical/ziwei-zhuxing", summary="紫微斗数十四主星详论")
async def classical_ziwei_zhuxing():
    from knowledge.classical_knowledge import ZIWEI_ZHUXING
    return ApiResponse(success=True, data=ZIWEI_ZHUXING)

@router.get("/classical/meihua-qigua", summary="梅花易数七种起卦法")
async def classical_meihua_qigua():
    from knowledge.classical_knowledge import MEIHUA_QIGUA
    return ApiResponse(success=True, data=MEIHUA_QIGUA)

@router.get("/classical/liuyao-yingqi-full", summary="六爻应期速查全论")
async def classical_liuyao_yingqi_full():
    from knowledge.classical_knowledge import LIUYAO_YINGQI_FULL
    return ApiResponse(success=True, data=LIUYAO_YINGQI_FULL)
