"""
api/agent.py
============
AI Agent endpoints — streaming LLM-powered consultations.

Supports multiple providers via request headers:
  X-LLM-Key:       API key
  X-LLM-Provider:  anthropic | deepseek | openai | moonshot  (default: anthropic)
  X-LLM-Base-Url:  optional override base URL
  X-LLM-Model:     optional override model name

All endpoints stream Server-Sent Events (SSE).
"""
from __future__ import annotations
import json
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from models.common import ApiResponse

router = APIRouter(prefix="/agent", tags=["AI命理顾问"])

# ─────────────────────────────────────────────────────────────
# Provider configuration
# ─────────────────────────────────────────────────────────────

PROVIDER_DEFAULTS = {
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1/messages",
        "model":    "claude-sonnet-4-6",
        "style":    "anthropic",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1/chat/completions",
        "model":    "deepseek-chat",
        "style":    "openai",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "model":    "gpt-4o",
        "style":    "openai",
    },
    "moonshot": {
        "base_url": "https://api.moonshot.cn/v1/chat/completions",
        "model":    "moonshot-v1-8k",
        "style":    "openai",
    },
}


def _get_llm_config(request: Request) -> dict:
    """Read LLM config from request headers."""
    provider = (request.headers.get("X-LLM-Provider") or "anthropic").lower().strip()
    key      = (request.headers.get("X-LLM-Key") or "").strip()
    base_url = (request.headers.get("X-LLM-Base-Url") or "").strip()
    model    = (request.headers.get("X-LLM-Model") or "").strip()

    if provider not in PROVIDER_DEFAULTS:
        provider = "anthropic"

    defaults = PROVIDER_DEFAULTS[provider]
    return {
        "provider": provider,
        "key":      key,
        "base_url": base_url or defaults["base_url"],
        "model":    model    or defaults["model"],
        "style":    defaults["style"],
    }


# ─────────────────────────────────────────────────────────────
# Streaming helpers — one per API style
# ─────────────────────────────────────────────────────────────

async def _stream_anthropic(cfg: dict, system: str, messages: list, max_tokens: int = 2000):
    """Stream from Anthropic-style API."""
    headers = {
        "Content-Type":    "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key":       cfg["key"],
    }
    payload = {
        "model":      cfg["model"],
        "max_tokens": max_tokens,
        "stream":     True,
        "system":     system,
        "messages":   messages,
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            async with client.stream("POST", cfg["base_url"], headers=headers, json=payload) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    err  = body.decode(errors="replace")
                    msg  = f"⚠️ API错误({resp.status_code}) — 请求地址: {cfg['base_url']}\n详情: {err[:300]}"
                    yield "data: " + json.dumps({"text": msg}, ensure_ascii=False) + "\n\n"
                    yield "data: [DONE]\n\n"
                    return
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        ev = json.loads(data)
                        if ev.get("type") == "content_block_delta":
                            text = ev.get("delta", {}).get("text", "")
                            if text:
                                yield "data: " + json.dumps({"text": text}, ensure_ascii=False) + "\n\n"
                    except Exception:
                        pass
    except Exception as e:
        msg = f"⚠️ 网络错误: {type(e).__name__}: {str(e)[:200]}"
        yield "data: " + json.dumps({"text": msg}, ensure_ascii=False) + "\n\n"
    yield "data: [DONE]\n\n"


async def _stream_openai(cfg: dict, system: str, messages: list, max_tokens: int = 2000):
    """Stream from OpenAI-compatible API (DeepSeek, Moonshot, OpenAI)."""
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {cfg['key']}",
    }
    full_messages = [{"role": "system", "content": system}] + messages
    payload = {
        "model":      cfg["model"],
        "max_tokens": max_tokens,
        "stream":     True,
        "messages":   full_messages,
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            async with client.stream("POST", cfg["base_url"], headers=headers, json=payload) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    err  = body.decode(errors="replace")
                    msg  = f"⚠️ API错误({resp.status_code}) — 请求地址: {cfg['base_url']}\n详情: {err[:300]}"
                    yield "data: " + json.dumps({"text": msg}, ensure_ascii=False) + "\n\n"
                    yield "data: [DONE]\n\n"
                    return
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        ev = json.loads(data)
                        text = ev.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if text:
                            yield "data: " + json.dumps({"text": text}, ensure_ascii=False) + "\n\n"
                    except Exception:
                        pass
    except Exception as e:
        msg = f"⚠️ 网络错误: {type(e).__name__}: {str(e)[:200]}"
        yield "data: " + json.dumps({"text": msg}, ensure_ascii=False) + "\n\n"
    yield "data: [DONE]\n\n"


async def _stream_llm(cfg: dict, system: str, messages: list, max_tokens: int = 2000):
    """Dispatch to the right streaming function based on provider style."""
    if not cfg["key"]:
        yield f'data: {json.dumps({"text": "⚠️ 未配置 API Key，请在设置页面填写。"})}\n\n'
        yield "data: [DONE]\n\n"
        return

    if cfg["style"] == "anthropic":
        async for chunk in _stream_anthropic(cfg, system, messages, max_tokens):
            yield chunk
    else:
        async for chunk in _stream_openai(cfg, system, messages, max_tokens):
            yield chunk


# ─────────────────────────────────────────────────────────────
# Request models
# ─────────────────────────────────────────────────────────────

class ConsultRequest(BaseModel):
    question: str
    context:  Optional[Dict[str, Any]] = None
    session_history: Optional[List[Dict]] = None


class BaziAgentRequest(BaseModel):
    year: int; month: int; day: int; hour: int; minute: int = 0
    gender: str = "male"
    question: Optional[str] = None
    focus:    Optional[str] = None


class LiuyaoAgentRequest(BaseModel):
    method:     str = "time"
    yao_values: Optional[List[int]] = None
    question:   str = ""
    query_time: Optional[str] = None


class QimenAgentRequest(BaseModel):
    year: Optional[int] = None; month: Optional[int] = None
    day:  Optional[int] = None; hour:  Optional[int] = None
    minute: int = 0
    question: str = ""


class FengShuiAgentRequest(BaseModel):
    birth_year:    int
    gender:        str = "male"
    house_facing:  str
    question:      Optional[str] = None


# ─────────────────────────────────────────────────────────────
# System prompts
# ─────────────────────────────────────────────────────────────

MASTER_SYSTEM = """你是一位精通中国传统命理的AI命理顾问，深研：
《穷通宝鉴》《滴天髓》《三命通会》《子平真诠》《神峰通考》《奇门遁甲》《六爻纳甲》《八宅风水》。

职责：用专业而通俗的语言解答命理问题，引用经典典籍支撑论断，给出实用建议。
格式：先给核心论断 → 引用典籍 → 给出建议，使用小标题分隔。
语言：中文，专业而不失亲切。"""

BAZI_SYSTEM = """你是专精八字命理的AI命理师，精通《穷通宝鉴》《滴天髓》《子平真诠》《三命通会》。
分析步骤：①日主强弱（月令旺衰）→ ②用神喜忌（调候+格局）→ ③格局判断 → ④十神六亲 → ⑤运程论断
引经据典，如"《穷通宝鉴》云：…"，语言专业含人情味，用中文回答。"""

LIUYAO_SYSTEM = """你是精通六爻纳甲的AI占卜师，深研《增删卜易》《卜筮正宗》。
分析框架：①本卦卦义 → ②世应关系 → ③用神取定 → ④旺衰动静 → ⑤六亲六神 → ⑥吉凶应期
结合问题具体分析，给出时间应期判断，用中文回答。"""

QIMEN_SYSTEM = """你是精通奇门遁甲的AI战略顾问，深研《奇门遁甲统宗》《烟波钓叟赋》。
分析框架：①局势判断 → ②宫位解读 → ③星门神综合 → ④格局识别 → ⑤行动建议
从全局到细节，给出具体可操作的方向建议，用中文回答。"""

FENGSHUI_SYSTEM = """你是精通八宅风水的AI风水顾问，深研《阳宅三要》《八宅明镜》。
分析框架：①命卦 → ②宅卦 → ③命宅配合 → ④四吉四凶 → ⑤布局建议（化煞方法）
给出具体家居布局建议，化解方案切实可行，用中文回答。"""


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────

def _sse_response(generator, cfg: dict):
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no",
                 "X-LLM-Provider": cfg["provider"], "X-LLM-Model": cfg["model"]},
    )


@router.post("/consult")
async def consult(req: ConsultRequest, request: Request):
    cfg = _get_llm_config(request)
    messages = list(req.session_history or [])
    content  = req.question
    if req.context:
        content = f"【已知数据】\n{json.dumps(req.context, ensure_ascii=False, indent=2)}\n\n【问题】\n{req.question}"
    messages.append({"role": "user", "content": content})
    return _sse_response(_stream_llm(cfg, MASTER_SYSTEM, messages, 2000), cfg)


@router.post("/bazi")
async def bazi_agent(req: BaziAgentRequest, request: Request):
    cfg = _get_llm_config(request)

    from core.bazi.chart import build_chart
    from core.bazi.analyzer import analyze_chart
    from core.bazi.forecaster import calculate_dayun

    chart = build_chart(req.year, req.month, req.day, req.hour, req.minute)
    analyze_chart(chart)
    dayun = calculate_dayun(chart, req.gender, req.year, num_periods=5)

    dm = chart["day_master"]
    summary = {
        "年柱": f"{chart['year_pillar']['tiangan']}{chart['year_pillar']['dizhi']} [{chart['year_pillar']['nayin']}]",
        "月柱": f"{chart['month_pillar']['tiangan']}{chart['month_pillar']['dizhi']} [{chart['month_pillar']['nayin']}]",
        "日柱": f"{chart['day_pillar']['tiangan']}{chart['day_pillar']['dizhi']} [{chart['day_pillar']['nayin']}]",
        "时柱": f"{chart['hour_pillar']['tiangan']}{chart['hour_pillar']['dizhi']} [{chart['hour_pillar']['nayin']}]",
        "日主": dm, "五行": chart["day_master_wuxing"],
        "身强弱": chart.get("strength", ""), "格局": chart.get("pattern", ""),
        "格局描述": chart.get("pattern_desc", ""),
        "大运": [f"{d['tiangan']}{d['dizhi']}（{int(d['start_age'])}~{int(d['end_age'])}岁，{d['quality']}）" for d in dayun],
        "神煞": [s["name"] for s in chart.get("shensha", [])],
    }

    focus_str = f"重点分析{req.focus}方面" if req.focus else "综合分析"

    # Load classical rules for this day master + birth month
    classical_ctx = ""
    try:
        from knowledge.bazi_classical import TIAO_HOU_TABLE, SHIGAN_JIJUE, RIZHUPAN_RULES, BAZIGE_SYSTEM
        month_dz = chart["month_pillar"]["dizhi"]
        tiao_hou = TIAO_HOU_TABLE.get(dm, {}).get(month_dz, "")
        shigan   = SHIGAN_JIJUE.get(dm, {})
        pattern  = chart.get("pattern", "")
        gejv     = BAZIGE_SYSTEM.get(pattern, {})
        classical_ctx = (
            f"\n\n【《穷通宝鉴》调候用神】{dm}日干{month_dz}月：{tiao_hou}"
            f"\n\n【《滴天髓》{dm}干论命】\n"
            f"口诀：{shigan.get('口诀','')}\n"
            f"解析：{shigan.get('解析','')}\n"
            f"喜忌：{shigan.get('喜忌','')}"
        )
        if gejv:
            classical_ctx += (
                f"\n\n【《子平真诠》{pattern}格局】\n"
                f"取格：{gejv.get('取格','')}\n"
                f"喜：{'、'.join(gejv.get('喜',[]))}\n"
                f"忌：{'、'.join(gejv.get('忌',[]))}"
            )
        classical_ctx += f"\n\n【日主强弱总纲】{RIZHUPAN_RULES.get('中和论','')}"
    except Exception:
        pass

    user_msg = (
        f"{req.year}年{req.month}月{req.day}日{req.hour}时，{req.gender}命\n\n"
        f"{json.dumps(summary, ensure_ascii=False, indent=2)}"
        f"{classical_ctx}\n\n"
        f"请按以下步骤深度分析：①日主强弱（月令旺衰得令）→②调候用神（《穷通宝鉴》）→"
        f"③格局判断（《子平真诠》）→④十神六亲吉凶→⑤大运流年趋势。"
        f"引经据典，具体到位。{req.question or focus_str}"
    )
    return _sse_response(_stream_llm(cfg, BAZI_SYSTEM, [{"role":"user","content":user_msg}], 2800), cfg)


@router.post("/liuyao")
async def liuyao_agent(req: LiuyaoAgentRequest, request: Request):
    cfg = _get_llm_config(request)

    from core.liuyao.divination import coin_divination, yarrow_divination, time_divination, manual_divination
    from core.liuyao.interpreter import interpret

    method = req.method.lower()
    if method == "coin":      result = coin_divination(req.yao_values)
    elif method == "yarrow":  result = yarrow_divination()
    elif method == "time":
        dt = datetime.fromisoformat(req.query_time) if req.query_time else None
        result = time_divination(dt)
    elif method == "manual":
        if not req.yao_values or len(req.yao_values) != 6:
            raise HTTPException(400, "manual方法需提供6个爻值(6/7/8/9)")
        result = manual_divination(req.yao_values)
    else:
        raise HTTPException(400, f"不支持: {method}")

    # Apply full classical analysis (now uses liuyao_classical.py rules)
    interp  = interpret(result, req.question)
    orig    = interp["original"]
    changed = interp.get("changed")
    yaos    = interp.get("yaos", [])
    topic   = interp.get("topic", "综合")

    # Build enriched yao detail for AI context
    yao_detail = []
    for y in yaos:
        yd = {
            "位": f"第{y.get('line','')}爻",
            "六亲": y.get("liu_qin", ""),
            "六神": y.get("liu_shen", ""),
            "地支": y.get("branch", ""),
            "旺衰": y.get("strength", {}).get("label", ""),
            "世应": "世" if y.get("is_world") else ("应" if y.get("is_application") else ""),
            "空亡": "是" if y.get("kong_wang") else "否",
            "动": "动" if y.get("is_changing") else "静",
        }
        if y.get("is_changing"):
            from core.liuyao.interpreter import _check_jin_tui_shen
            jt = _check_jin_tui_shen(y.get("branch",""))
            if jt:
                yd["进退"] = f"化{jt}神"
        yao_detail.append(yd)

    # Classical analysis already computed by interpreter
    classical_pts = interp.get("classical_points", [])
    topic_analysis = interp.get("topic_analysis", {})

    # Load relevant classical rules for this topic
    classical_context = ""
    try:
        from knowledge.liuyao_classical import LIUYAO_TOPIC_RULES, LIUYAO_CLASSICAL_RULES
        topic_rule = LIUYAO_TOPIC_RULES.get(topic, {})
        key_rules = topic_rule.get("规则") or topic_rule.get("rules", [])
        classical_context = (
            f"\n【{topic}用神规则（经典）】\n" +
            "\n".join(f"• {r}" for r in key_rules[:5]) +
            f"\n【{topic}总结】{topic_rule.get('summary','')}"
        )
    except Exception:
        pass

    summary = {
        "占问": req.question or "综合运势",
        "占事类型": topic,
        "本卦": f"第{orig['number']}卦 {orig['name']}（上{orig['upper']['name']} 下{orig['lower']['name']}）",
        "卦辞": orig.get("judgment", "")[:80],
        "之卦": f"第{changed['number']}卦 {changed['name']}" if changed else "无",
        "旬空": interp.get("kong_wang_branches", []),
        "世应": interp.get("world_summary", ""),
        "六爻纳甲详情": yao_detail,
        "系统初步断法": classical_pts[:5],
        "动爻分析": interp.get("changing_analysis", []),
        "初判": topic_analysis.get("verdict", ""),
    }

    user_msg = (
        f"{json.dumps(summary, ensure_ascii=False, indent=2)}"
        f"\n\n{classical_context}"
        f"\n\n请基于以上纳甲数据和经典规则，进行深度六爻分析：\n"
        f"①本卦卦义与整体态势  ②世应爻旺衰关系  ③动爻六亲六神影响  "
        f"④用神吉凶判断  ⑤应期推算（病药原则）  ⑥综合建议"
    )
    return _sse_response(_stream_llm(cfg, LIUYAO_SYSTEM, [{"role":"user","content":user_msg}], 2500), cfg)


@router.post("/qimen")
async def qimen_agent(req: QimenAgentRequest, request: Request):
    cfg = _get_llm_config(request)

    from core.qimen.algorithm import calculate_qimen
    from core.qimen.analyzer import analyze_qimen

    now = datetime.now()
    layout   = calculate_qimen(req.year or now.year, req.month or now.month,
                               req.day or now.day, req.hour if req.hour is not None else now.hour, req.minute)
    analysis = analyze_qimen(layout)

    summary = {
        "时间": f"{req.year or now.year}年{req.month or now.month}月{req.day or now.day}日{req.hour if req.hour is not None else now.hour}时",
        "局":   f"{layout.get('ju_type','')} {layout.get('ju_number','')}局 {layout.get('yuan','')}",
        "吉方": layout.get("auspicious_directions", []),
        "凶方": layout.get("inauspicious_directions", []),
        "综合": analysis.get("summary",""),
        "建议": analysis.get("advice",""),
        "宫位": [{"宫":p["palace_name"],"星":p["star"],"门":p["door"],"神":p["deity"],"吉":p.get("is_auspicious")}
                 for p in layout.get("palaces",[])[:9]],
    }
    # Load classical qimen context
    classical_ctx = ""
    try:
        from knowledge.qimen_classical import BA_MEN_DETAIL, JIU_XING_DETAIL, YANBO_JIJUE, QIMEN_GEJV
        # Find most relevant palace (highest auspicious)
        palaces = layout.get("palaces", [])
        auspicious = [p for p in palaces if p.get("is_auspicious")]
        inauspicious = [p for p in palaces if not p.get("is_auspicious")]
        # Build door/star context
        door_ctx = []
        for p in palaces[:3]:
            door = p.get("door", "")
            star = p.get("star", "")
            if door in BA_MEN_DETAIL:
                d_info = BA_MEN_DETAIL[door]
                door_ctx.append(f"{p.get('palace_name','')}宫 {door}+{star}：{d_info.get('吉凶','')}，{d_info.get('主象','')}")
        yanbo_key = "\n".join(f"「{x['口诀']}」" for x in YANBO_JIJUE[:3])
        classical_ctx = (
            f"\n\n【《烟波钓叟赋》要诀】\n{yanbo_key}"
            f"\n\n【关键宫位门星解读】\n" + "\n".join(door_ctx)
        )
    except Exception:
        pass

    user_msg = (
        f"{json.dumps(summary, ensure_ascii=False, indent=2)}"
        f"{classical_ctx}"
        f"\n\n请分析：①局势总纲（阴阳局、元运）→②关键宫位门星神组合→③格局识别（吉凶格）→"
        f"④最佳行动方向→⑤具体时机建议。引用《烟波钓叟赋》《奇门遁甲统宗》。"
        f"\n\n问题：{req.question or '请分析当前局势，给出行动建议。'}"
    )
    return _sse_response(_stream_llm(cfg, QIMEN_SYSTEM, [{"role":"user","content":user_msg}], 2200), cfg)


@router.post("/fengshui")
async def fengshui_agent(req: FengShuiAgentRequest, request: Request):
    cfg = _get_llm_config(request)

    from core.fengshui.calculator import (
        calculate_ming_gua, get_ming_gua_group,
        get_house_gua, get_house_group,
        check_compatibility, get_sector_analysis,
    )

    ming_gua    = calculate_ming_gua(req.birth_year, req.gender)
    house_gua   = get_house_gua(req.house_facing)
    compat      = check_compatibility(ming_gua, house_gua)
    sectors     = get_sector_analysis(house_gua)

    summary = {
        "命卦": f"{ming_gua}（{get_ming_gua_group(ming_gua)}）",
        "宅卦": f"{house_gua}（{get_house_group(house_gua)}）",
        "命宅相配": compat,
        "八方": [{"方":s["direction"],"星":s["star"],"吉凶":s["quality"],"含义":s["meaning"]} for s in sectors],
    }
    # Load classical fengshui context
    classical_ctx = ""
    try:
        from knowledge.fengshui_classical import YANGZHAI_THREE, BAYUAN_JIUXING, XUANKONG_THEORY
        # Get relevant sector info
        inauspicious_sectors = [s for s in sectors if "凶" in s.get("quality", "")]
        auspicious_sectors   = [s for s in sectors if "吉" in s.get("quality", "")]
        current_yun = XUANKONG_THEORY["三元九运"]["当前"]
        classical_ctx = (
            f"\n\n【《阳宅三要》核心原则】\n"
            f"门：{YANGZHAI_THREE['大门']['经典']}\n"
            f"主：{YANGZHAI_THREE['主房']['经典']}\n"
            f"灶：{YANGZHAI_THREE['灶台']['经典']}"
            f"\n\n【当前九运】{current_yun}"
            f"\n\n【绝命位须知】{BAYUAN_JIUXING['绝命']['主象']}，化解：{BAYUAN_JIUXING['绝命']['化解']}"
            f"\n\n【五鬼位须知】{BAYUAN_JIUXING['五鬼']['主象']}，化解：{BAYUAN_JIUXING['五鬼']['化解']}"
        )
    except Exception:
        pass

    user_msg = (
        f"{req.birth_year}年生，{req.gender}命，房屋朝向{req.house_facing}\n\n"
        f"{json.dumps(summary, ensure_ascii=False, indent=2)}"
        f"{classical_ctx}"
        f"\n\n请深度分析：①命宅相配评估（东西四宅配合）→②四吉方位利用（生气/天乙/延年/伏位）→"
        f"③四凶方化解（祸害/六煞/五鬼/绝命，引《阳宅三要》）→④主卧书房灶台具体方位建议→⑤玄空九运影响。"
        f"\n\n{req.question or '请给出详细家居布局建议，包括主卧、书房、灶口方向，以及吉方利用和凶方化解方法。'}"
    )
    return _sse_response(_stream_llm(cfg, FENGSHUI_SYSTEM, [{"role":"user","content":user_msg}], 2200), cfg)


@router.get("/health")
async def agent_health():
    return ApiResponse(success=True, data={"status": "ok", "providers": list(PROVIDER_DEFAULTS.keys())})


# ─────────────────────────────────────────────────────────────
# Universal interpret endpoint — feeds any module's data to LLM
# ─────────────────────────────────────────────────────────────

class InterpretRequest(BaseModel):
    module: str                      # bazi | liuyao | qimen | fengshui | date | knowledge
    data:   Dict[str, Any]           # the computed result from the module
    question: Optional[str] = None   # optional user question
    extra_context: Optional[str] = ""  # tab name, purpose, etc.


INTERPRET_SYSTEMS = {
    "bazi": """你是专精八字命理的AI命理师，精通《穷通宝鉴》《滴天髓》《子平真诠》《三命通会》《神峰通考》。

分析步骤：
1. **日主与格局**：明确日主五行、身强身弱、格局高低
2. **用神喜忌**：调候用神（穷通宝鉴）+ 格局用神双管齐下
3. **十神六亲**：各柱十神的人生象意
4. **运程节点**：大运流年的吉凶走势
5. **具体建议**：职业方向、感情、健康、财富的实操建议

引用典籍，语言专业而亲切，用中文回答。""",

    "liuyao": """你是精通六爻纳甲的AI占卜师，深研《增删卜易》《卜筮正宗》《断易天机》。

分析框架：
1. **本卦卦义**：卦名象意，上下卦组合的整体含义
2. **世应关系**：世爻（问卦者）与应爻（对方/结果）的生克关系
3. **用神旺衰**：用神爻的月建日辰旺衰，有无动变
4. **六亲六神**：各爻六亲含义，六神（青龙/白虎等）临爻的影响
5. **动爻变爻**：变爻的回头生克，之卦的最终指向
6. **应期判断**：给出事情应验的具体时间节点

结论要明确吉凶，给出可操作的建议，用中文回答。""",

    "qimen": """你是精通奇门遁甲的AI战略顾问，深研《奇门遁甲统宗》《烟波钓叟赋》《奇门旨归》。

分析框架：
1. **局势总判**：阴阳遁、局数、时间背景对整体运势的影响
2. **吉方选取**：哪些方位的星门神组合最有利于此次问事
3. **星门神详析**：重点宫位的九星×八门×八神三维解读
4. **格局识别**：是否存在奇仪格、三奇格等特殊格局
5. **行动方案**：具体的方向选择、时机把握、注意事项

提供战略性的、可落地的建议，用中文回答。""",

    "fengshui": """你是精通八宅风水和玄空飞星的AI风水顾问，深研《阳宅三要》《八宅明镜》《玄空飞星》《沈氏玄空学》。

分析框架：
1. **命宅匹配**：命卦与宅卦的东西四命/四宅配合关系
2. **八宅方位**：四吉方（生气/天医/延年/伏位）和四凶方的具体含义
3. **飞星叠加**：年度飞星与八宅方位的叠加效应
4. **个人吉方**：根据命卦给出主卧、书房、灶口的最优方位
5. **化煞布局**：凶方的具体化解方法和物品摆放建议

建议要具体可操作，避免泛泛而谈，用中文回答。""",

    "date": """你是精通择日选时的AI命理师，深研《协纪辨方书》《象吉通书》《万年历择日》。

分析框架：
1. **建除论断**：当月十二建除的整体走势，哪些日子最宜此事
2. **最佳吉日**：重点解读最佳吉日的建除、二十八宿、神煞组合
3. **三煞警示**：本年三煞方位对择日的影响
4. **岁破月破**：需要回避的破日说明
5. **时辰选择**：建议配合吉日使用的吉时

给出3-5个最佳日期的具体推荐，注明理由，用中文回答。""",

    "knowledge": """你是中国传统命理学的AI学术顾问，精通八字、六爻、奇门、风水、择日五大体系。

针对用户查阅的知识点：
1. **核心要义**：用浅显语言解释该知识点的本质含义
2. **古籍出处**：引用相关典籍原文及注解
3. **实战应用**：该知识点在实际命理分析中如何运用
4. **案例举例**：给出1-2个具体的应用案例
5. **关联知识**：与该知识点相关的其他重要概念

深入浅出，兼顾学术严谨性和实用性，用中文回答。""",
}


def _build_interpret_prompt(module: str, data: dict, question: str, extra_context: str) -> str:
    """Build a compact but rich prompt from module data."""

    def j(d, keys=None, maxlen=2000):
        """Serialize selected keys of d, truncated."""
        if keys:
            d = {k: d[k] for k in keys if k in d}
        s = json.dumps(d, ensure_ascii=False, indent=2)
        return s[:maxlen] + ("…" if len(s) > maxlen else "")

    if module == "bazi":
        tab = extra_context or "综合"
        pillars = {
            "年柱": f"{data.get('year_pillar',{}).get('tiangan','')}{data.get('year_pillar',{}).get('dizhi','')}",
            "月柱": f"{data.get('month_pillar',{}).get('tiangan','')}{data.get('month_pillar',{}).get('dizhi','')}",
            "日柱": f"{data.get('day_pillar',{}).get('tiangan','')}{data.get('day_pillar',{}).get('dizhi','')}",
            "时柱": f"{data.get('hour_pillar',{}).get('tiangan','')}{data.get('hour_pillar',{}).get('dizhi','')}",
        }
        profile = data.get("day_master_profile", {})
        yong = data.get("yong_shen", {})
        ctx = {
            "四柱": pillars,
            "日主": data.get("day_master", ""),
            "五行": data.get("day_master_wuxing", ""),
            "身强弱": data.get("strength", ""),
            "格局": data.get("pattern", ""),
            "用神": yong.get("yong_shen_wx", ""),
            "喜神": yong.get("xi_shen_wx", ""),
            "忌神": yong.get("ji_shen_wx", ""),
            "日主性格": profile.get("personality_detail", "")[:100] if profile else "",
            "神煞": [s.get("name","") for s in data.get("shensha", [])[:4]],
            "格局描述": data.get("pattern_desc", ""),
            # Extra fields for non-chart tabs
            "分析": data.get("analysis", ""),
            "建议": data.get("advice", [])[:3] if isinstance(data.get("advice"), list) else "",
        }
        return f"八字命盘（{tab}）\n{j(ctx)}\n\n请针对「{tab}」方面进行深度分析。{question or ''}"

    elif module == "liuyao":
        orig     = data.get("original", {})
        yaos     = data.get("yaos", [])
        topic    = data.get("topic", question[:4] if question else "综合")
        classical_pts = data.get("classical_points", [])
        world_summary = data.get("world_summary", "")

        yao_summary = [
            f"第{i+1}爻: {y.get('line','')} {y.get('liu_qin','')} {y.get('liu_shen','')} "
            f"{'世' if y.get('is_world') else ''}{'应' if y.get('is_application') else ''}"
            f" {y.get('branch','')} {y.get('strength',{}).get('label','')}"
            f"{'(空)' if y.get('kong_wang') else ''}{'[动]' if y.get('is_changing') else ''}"
            for i, y in enumerate(yaos)
        ]

        # Include relevant classical rules
        classical_rules_text = ""
        try:
            from knowledge.liuyao_classical import LIUYAO_TOPIC_RULES, LIUYAO_CLASSICAL_RULES
            match_topic = topic if topic in LIUYAO_TOPIC_RULES else "综合"
            topic_rule = LIUYAO_TOPIC_RULES.get(match_topic, {})
            rules = topic_rule.get("规则") or topic_rule.get("rules", [])
            if rules:
                classical_rules_text = f"\n【{match_topic}经典规则】\n" + "\n".join(f"• {r}" for r in rules[:4])
                classical_rules_text += f"\n总结：{topic_rule.get('summary','')}"
        except Exception:
            pass

        ctx = {
            "占问": data.get("question", question) or "综合运势",
            "占事类型": topic,
            "本卦": f"第{orig.get('number','')}卦 {orig.get('name','')}",
            "卦辞": orig.get("judgment", "")[:60],
            "动爻": data.get("changing_lines", []),
            "之卦": f"第{data.get('changed',{}).get('number','')}卦 {data.get('changed',{}).get('name','')}" if data.get("changed") else "无",
            "旬空": data.get("kong_wang_branches", []),
            "世应": world_summary,
            "六爻纳甲": yao_summary,
            "系统断法": classical_pts[:4],
            "初判": data.get("topic_analysis", {}).get("verdict", ""),
        }
        return (
            f"六爻占问\n{j(ctx)}"
            f"{classical_rules_text}"
            f"\n\n请深度分析：①卦象总义 ②世应旺衰 ③动爻六亲六神 ④用神吉凶 ⑤应期 ⑥综合建议。{question or ''}"
        )

    elif module == "qimen":
        palaces = data.get("palaces", [])
        top_palaces = [
            {"宫": p.get("palace_name",""), "星": p.get("star",""), "门": p.get("door",""),
             "神": p.get("deity",""), "干": p.get("stem",""), "吉": p.get("is_auspicious",False)}
            for p in palaces[:9]
        ]
        ctx = {
            "时间": data.get("datetime", ""),
            "局": f"{data.get('ju_type','')} 第{data.get('ju_number','')}局 {data.get('yuan','')}",
            "吉方": data.get("auspicious_directions", []),
            "宫位": top_palaces,
            "伏吟反吟": data.get("fuyin_fanyin", {}),
            "综合": data.get("summary", ""),
        }
        purpose = extra_context or "综合"
        pa = data.get("purpose_analyses", {}).get(purpose, {})
        if pa:
            ctx["事项分析"] = {"推荐": pa.get("recommendation",""), "警示": pa.get("warning","")}
        return f"奇门遁甲起局\n{j(ctx)}\n\n请分析当前局势，针对「{purpose}」给出战略建议。{question or ''}"

    elif module == "fengshui":
        ctx = {
            "命卦": f"{data.get('ming_gua','')}（{data.get('ming_gua_group','')}）",
            "宅卦": f"{data.get('house_gua','')}（{data.get('house_group','')}）",
            "命宅相配": data.get("compatibility",""),
            "吉方": [{"方位": s.get("direction",""), "星": s.get("star",""), "意义": s.get("meaning","")[:40]}
                     for s in data.get("auspicious_sectors", [])[:4]],
            "凶方": [{"方位": s.get("direction",""), "星": s.get("star",""), "意义": s.get("meaning","")[:40]}
                     for s in data.get("inauspicious_sectors", [])[:4]],
            "年度财位": data.get("annual_flying_stars", {}).get("wealth_direction",""),
            "年度五黄": data.get("annual_flying_stars", {}).get("five_yellow_direction",""),
            "个人生气位": data.get("personal_directions", {}).get("shengqi", {}).get("direction",""),
            "个人绝命位": data.get("personal_directions", {}).get("jueming", {}).get("direction",""),
        }
        # Add classical context
        classical_ctx = ""
        try:
            from knowledge.fengshui_classical import YANGZHAI_THREE, XUANKONG_THEORY
            current_yun = XUANKONG_THEORY["三元九运"]["当前"]
            classical_ctx = (
                f"\n\n【《阳宅三要》】门：{YANGZHAI_THREE['大门']['经典']}"
                f"\n【九运当令】{current_yun}"
            )
        except Exception:
            pass
        return f"八宅风水分析\n{j(ctx)}{classical_ctx}\n\n请给出详细的家居布局建议，包括化煞方法。{question or ''}"

    elif module == "date":
        purpose = data.get("purpose", extra_context or "")
        best = data.get("best_day", {})
        top_days = [
            {"日期": d_item.get("date",""), "干支": d_item.get("ganzhi",""),
             "建除": d_item.get("officer",""), "星宿": d_item.get("xiu",""),
             "评分": d_item.get("quality",0)}
            for d_item in data.get("auspicious_days", [])[:5]
        ]
        ctx = {
            "择事目的": purpose,
            "最佳日期": best,
            "前五吉日": top_days,
            "三煞警示": data.get("three_killings", {}),
            "本月概述": data.get("month_summary",""),
        }
        # Add classical context
        classical_ctx = ""
        try:
            from knowledge.date_classical import ZERI_EVENTS, JIANSHEN_TWELVE
            event_rules = ZERI_EVENTS.get(purpose, {})
            if event_rules:
                classical_ctx = (
                    f"\n\n【《协纪辨方书》{purpose}择日要诀】"
                    f"\n最佳日：{event_rules.get('最佳日','')}"
                    f"\n忌：{event_rules.get('忌','')}"
                    f"\n注意：{event_rules.get('注意','')}"
                    f"\n口诀：{event_rules.get('口诀','')}"
                )
        except Exception:
            pass
        return f"择日分析\n{j(ctx)}{classical_ctx}\n\n请详细解读最佳择日方案，说明理由并给出时辰建议。{question or ''}"

    elif module == "knowledge":
        # data is whatever knowledge section they're viewing
        ctx_str = j(data, maxlen=1500)
        topic = extra_context or "命理知识"
        return f"命理知识主题：{topic}\n\n相关知识数据：\n{ctx_str}\n\n请深度解读此知识点的含义、古籍出处和实战应用。{question or ''}"

    else:
        return f"数据：{j(data)}\n\n{question or '请分析以上数据。'}"


@router.post("/interpret", summary="通用AI解读 — 任意模块结果流式解读")
async def interpret(req: InterpretRequest, request: Request):
    """
    Universal LLM interpretation endpoint.
    Accepts any module's computed result and streams AI analysis.
    """
    cfg = _get_llm_config(request)

    system = INTERPRET_SYSTEMS.get(req.module, MASTER_SYSTEM)
    user_msg = _build_interpret_prompt(
        req.module, req.data, req.question or "", req.extra_context or ""
    )

    return _sse_response(
        _stream_llm(cfg, system, [{"role": "user", "content": user_msg}], 2500),
        cfg
    )
