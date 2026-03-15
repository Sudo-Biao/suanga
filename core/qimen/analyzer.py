"""
core/qimen/analyzer.py
======================
奇门遁甲断事核心引擎 — 完整经典理论实现
整合四盘体系：天（九星）× 地（九宫）× 人（八门）× 神（八神）
核心断法：值符值使体系、用神取法、格局检测、应期推算
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Tuple

from core.constants import BAMEN_AUSPICIOUS

# ─────────────────────────────────────────────────────────────
# 五行生克常量
# ─────────────────────────────────────────────────────────────
_WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
_WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

_GONG_WX = {
    "坎一宫": "水", "坤二宫": "土", "震三宫": "木", "巽四宫": "木",
    "中五宫": "土", "乾六宫": "金", "兑七宫": "金", "艮八宫": "土", "离九宫": "火",
}

_TIANGAN_WX = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

_MEN_WX = {
    "开门": "金", "惊门": "金",
    "休门": "水",
    "生门": "土", "死门": "土",
    "伤门": "木", "杜门": "木",
    "景门": "火",
}

_XING_WX = {
    "天蓬": "水", "天芮": "土", "天冲": "木", "天辅": "木", "天禽": "土",
    "天心": "金", "天柱": "金", "天任": "土", "天英": "火",
}

_SHEN_WX = {
    "值符": "土", "腾蛇": "火", "太阴": "金", "六合": "木",
    "白虎": "金", "玄武": "水", "九地": "土", "九天": "金",
}

def _wx_rel(a: str, b: str) -> str:
    """Return relationship: 生/克/同/无"""
    if not a or not b: return "无"
    if a == b: return "同"
    if _WX_SHENG.get(a) == b: return "生"
    if _WX_KE.get(a) == b: return "克"
    if _WX_SHENG.get(b) == a: return "被生"
    if _WX_KE.get(b) == a: return "被克"
    return "无"


# ─────────────────────────────────────────────────────────────
# Load classical knowledge (lazy, with fallback)
# ─────────────────────────────────────────────────────────────
def _load_classical():
    try:
        from knowledge.qimen_classical import (
            BA_MEN_DETAIL, JIU_XING_DETAIL, BA_SHEN, QIMEN_GEJV,
            SAN_QI_LIU_YI, YANBO_JIJUE, ZHIFU_ZHISHI, YONG_SHEN_QIFA,
            YINGQI_TUISUAN, JIU_GONG_DETAIL, SIBAO_XITONG,
        )
        return {
            "bamen": BA_MEN_DETAIL, "jiuxing": JIU_XING_DETAIL,
            "bashen": BA_SHEN,       "gejv": QIMEN_GEJV,
            "sanqi": SAN_QI_LIU_YI, "yanbo": YANBO_JIJUE,
            "zhifushi": ZHIFU_ZHISHI, "yongshen": YONG_SHEN_QIFA,
            "yingqi": YINGQI_TUISUAN, "jiugong": JIU_GONG_DETAIL,
            "sibao": SIBAO_XITONG,
        }, True
    except Exception:
        return {k: {} for k in ["bamen","jiuxing","bashen","gejv","sanqi",
                                 "yanbo","zhifushi","yongshen","yingqi","jiugong","sibao"]}, False


# ─────────────────────────────────────────────────────────────
# Palace quality scoring (四维综合评分)
# ─────────────────────────────────────────────────────────────
def _score_palace(star_nature: str, door_nature: str, deity_nature: str,
                  stem: str, gong_wx: str) -> Tuple[str, int]:
    """
    Score palace on 5-point scale using classical 四盘 logic.
    Returns (quality_label, score_0_to_10)
    """
    # Base score from three layers
    scores = {
        "大吉": 3, "吉": 2, "次吉": 1, "小吉": 1,
        "中平": 0, "平": 0,
        "小凶": -1, "凶": -2, "大凶": -3,
    }
    total = (scores.get(star_nature, 0)
           + scores.get(door_nature, 0)
           + scores.get(deity_nature, 0))

    # Stem modifier: 三奇 big boost, 庚/己 penalty
    if stem in ("乙", "丙", "丁"):
        total += 2
    elif stem == "庚":
        total -= 2
    elif stem == "己":
        total -= 1
    elif stem in ("戊", "壬"):
        total += 1

    # Map to label
    if total >= 5:   quality = "大吉"
    elif total >= 3: quality = "吉"
    elif total >= 1: quality = "小吉"
    elif total == 0: quality = "平"
    elif total >= -2: quality = "凶"
    else:            quality = "大凶"

    return quality, max(0, total + 5)


# ─────────────────────────────────────────────────────────────
# Detect special patterns (格局检测)
# ─────────────────────────────────────────────────────────────
def _detect_patterns(layout: Dict, palaces: List[Dict], ck: Dict) -> List[Dict]:
    """Detect classical QiMen patterns from layout data."""
    gejv_db = ck.get("gejv", {})
    patterns = []

    # Fuyin / Fanyin from layout flags
    if layout.get("fuyin"):
        g = gejv_db.get("伏吟", {})
        patterns.append({
            "name": "伏吟",
            "level": "大凶",
            "desc": g.get("应事", "万事停滞，原地踏步，宜静守待时"),
            "kou": g.get("口诀", "伏吟之局最难行，万事停滞莫强动"),
        })
    if layout.get("fanyin"):
        g = gejv_db.get("反吟", {})
        patterns.append({
            "name": "反吟",
            "level": "大凶",
            "desc": g.get("应事", "反覆动荡，进退两难，事与愿违"),
            "kou": g.get("口诀", "反吟之局事颠倒，进退两难莫轻动"),
        })

    # Check star/door relationship (星克门吉，门克星凶)
    for p in palaces:
        star_wx = _XING_WX.get(p.get("star", ""), "")
        door_wx = _MEN_WX.get(p.get("door", ""), "")
        if star_wx and door_wx:
            if _WX_KE.get(star_wx) == door_wx:
                patterns.append({
                    "name": f"星克门·{p['palace_name']}",
                    "level": "吉",
                    "desc": f"{p['palace_name']}宫：{p['star']}（{star_wx}）克{p['door']}（{door_wx}），星克门主吉，天时助人和",
                    "kou": "星克门吉天助人，谋事顺遂吉自来",
                })
            elif _WX_KE.get(door_wx) == star_wx:
                patterns.append({
                    "name": f"门克星·{p['palace_name']}",
                    "level": "凶",
                    "desc": f"{p['palace_name']}宫：{p['door']}（{door_wx}）克{p['star']}（{star_wx}），门克星主凶，人和逆天时有阻",
                    "kou": "门克星凶人胜天，虽成有损要防险",
                })

    # San qi de shi (三奇得使)
    zhishi_palace = next((p for p in palaces if p.get("is_zhishi")), None)
    if zhishi_palace:
        stem = zhishi_palace.get("stem", "")
        if stem in ("乙", "丙", "丁"):
            qi_names = {"乙": "天奇", "丙": "地奇", "丁": "人奇"}
            patterns.append({
                "name": "三奇得使",
                "level": "大吉",
                "desc": f"值使门宫有{stem}（{qi_names.get(stem, '')}）临之，三奇得使大吉，贵人主动相助，谋事必成",
                "kou": "三奇得使诸事吉，贵人相助无阻隔",
            })

    return patterns[:6]  # Return top 6 most significant


# ─────────────────────────────────────────────────────────────
# Zhifu/Zhishi analysis (值符值使核心断法)
# ─────────────────────────────────────────────────────────────
def _analyze_zhifu_zhishi(palaces: List[Dict], ck: Dict) -> Dict[str, Any]:
    """
    Core analysis: 值符（全局领袖）× 值使门（执行关键）
    This is the heart of QiMen divination.
    """
    zhifu  = next((p for p in palaces if p.get("is_zhifu")), None)
    zhishi = next((p for p in palaces if p.get("is_zhishi")), None)
    if not zhifu or not zhishi:
        return {}

    fu_star_wx  = _XING_WX.get(zhifu.get("star", ""), "")
    shi_door_wx = _MEN_WX.get(zhishi.get("door", ""), "")
    fu_gong_wx  = _GONG_WX.get(zhifu.get("palace_name", ""), "")
    shi_gong_wx = _GONG_WX.get(zhishi.get("palace_name", ""), "")

    # Relationship between 值符 and 值使
    rel = _wx_rel(fu_star_wx, shi_door_wx)
    rel_desc_map = {
        "生":   ("符生使", "大吉", "值符星生值使门，贵人全力支持执行，事情顺遂"),
        "被生": ("使生符", "次吉", "值使门生值符星，费力可成，需耗费更多精力"),
        "克":   ("符克使", "吉",   "值符克值使，虽有阻力但正常前进，可成"),
        "被克": ("使克符", "大凶", "值使克值符，执行阻碍长远，事情极难成功"),
        "同":   ("符使同气", "吉",  "符使五行相同，方向一致，事情稳定可成"),
    }
    rel_info = rel_desc_map.get(rel, ("无明显关系", "平", "符使关系平和，需结合用神判断"))
    rel_name, rel_level, rel_detail = rel_info

    # 值符 strength (旺衰)
    fu_wangshuai = _wx_rel(fu_gong_wx, fu_star_wx)
    fu_strong = fu_wangshuai in ("生", "同")

    # 值使 strength
    shi_door = zhishi.get("door", "")
    shi_door_auspicious = shi_door in ("开门", "休门", "生门")

    return {
        "zhifu": {
            "star":      zhifu.get("star", ""),
            "palace":    zhifu.get("palace_name", ""),
            "stem":      zhifu.get("stem", ""),
            "deity":     zhifu.get("deity", ""),
            "wangshuai": "旺" if fu_strong else "衰",
            "role":      "全局领袖，代表长远前景",
            "desc":      ck.get("jiuxing", {}).get(zhifu.get("star", ""), {}).get("断法", ""),
        },
        "zhishi": {
            "door":      shi_door,
            "palace":    zhishi.get("palace_name", ""),
            "stem":      zhishi.get("stem", ""),
            "star":      zhishi.get("star", ""),
            "auspicious": shi_door_auspicious,
            "role":      "当下执行，代表近期事务结果",
            "yanbo":     ck.get("bamen", {}).get(shi_door, {}).get("烟波", ""),
            "desc":      ck.get("bamen", {}).get(shi_door, {}).get("详解", ""),
        },
        "relationship": {
            "name":   rel_name,
            "level":  rel_level,
            "detail": rel_detail,
        },
        "verdict":      _build_verdict(zhifu, zhishi, rel_name, rel_level, fu_strong, shi_door_auspicious),
        "priority":     "值使为第一要素（近期），值符为第二要素（长远）。先看值使，再参值符。",
        "classical_ref": "《奇门统宗》：静则只查值符、值使、时干，看其生克衰旺如何",
    }


def _build_verdict(zhifu: Dict, zhishi: Dict, rel: str, level: str,
                   fu_strong: bool, shi_auspicious: bool) -> str:
    """Build human-readable verdict from zhifu/zhishi analysis."""
    shi_door = zhishi.get("door", "")
    fu_star  = zhifu.get("star", "")

    if level == "大凶":
        return f"值使门（{shi_door}）克制值符星（{fu_star}），执行力逆转长远方向，事情极难成功，慎重行事。"
    elif level in ("大吉", "吉"):
        return (f"值符（{fu_star}）{'旺相有力' if fu_strong else '虽偏弱'}，"
                f"{'值使门（' + shi_door + '）为吉门，' if shi_auspicious else ''}"
                f"二者关系为{rel}，长远前景{'乐观' if fu_strong else '一般'}，"
                f"{'当下执行顺利' if shi_auspicious else '执行有所阻力'}。")
    else:
        return f"值符（{fu_star}）与值使门（{shi_door}）关系平和，需结合用神与宫位综合判断。"


# ─────────────────────────────────────────────────────────────
# Purpose-based yong shen analysis (用神取法)
# ─────────────────────────────────────────────────────────────
def _analyze_yong_shen(palaces: List[Dict], question: str, ck: Dict) -> Dict[str, Any]:
    """Determine 用神 and its palace for the given purpose."""
    yong_db = ck.get("yongshen", {})
    question = question or ""

    # Topic detection
    _TOPIC_MAP = [
        (["求财", "财运", "投资", "经商", "生意", "赚钱"],  "求财"),
        (["感情", "婚姻", "恋爱", "婚嫁", "桃花"],        "婚嫁感情"),
        (["事业", "升职", "求官", "职位", "工作"],        "求官仕途"),
        (["出行", "旅游", "出国", "远行", "行程"],        "出行远足"),
        (["健康", "疾病", "看病", "求医", "手术"],        "疾病求医"),
        (["考试", "学习", "求学", "考研"],               "求学考试"),
        (["谈判", "合作", "签约", "协议"],               "经商谈判"),
        (["官司", "诉讼", "打官司"],                     "官司诉讼"),
    ]
    topic = "求财"  # default
    for keywords, t in _TOPIC_MAP:
        if any(k in question for k in keywords):
            topic = t
            break

    yong_info = yong_db.get(topic, {})
    yong_shen_name = yong_info.get("用神", "生门（默认求财用神）")

    # Find yong shen palace
    yong_palace = None
    if "生门" in yong_shen_name:
        yong_palace = next((p for p in palaces if "生门" in p.get("door", "")), None)
    elif "开门" in yong_shen_name:
        yong_palace = next((p for p in palaces if "开门" in p.get("door", "")), None)
    elif "天心" in yong_shen_name:
        yong_palace = next((p for p in palaces if "天心" in p.get("star", "")), None)

    yong_quality = "平"
    if yong_palace:
        yong_quality = yong_palace.get("quality", "平")

    return {
        "topic":   topic,
        "name":    yong_shen_name,
        "palace":  yong_palace.get("palace_name", "未知") if yong_palace else "未定",
        "quality": yong_quality,
        "rules":   yong_info.get("断法", ""),
        "best":    yong_info.get("最吉", ""),
    }


# ─────────────────────────────────────────────────────────────
# Timing analysis (应期推算)
# ─────────────────────────────────────────────────────────────
def _analyze_timing(zhifu_palace: Optional[Dict], zhishi_palace: Optional[Dict],
                    ck: Dict) -> Dict[str, str]:
    """Apply 《奇门法穷》 timing rules."""
    yq = ck.get("yingqi", {})

    # Determine speed from zhishi door quality
    shi_door = zhishi_palace.get("door", "") if zhishi_palace else ""
    zhifu_stem = zhifu_palace.get("stem", "") if zhifu_palace else ""

    if shi_door in ("死门", "惊门") or zhifu_stem == "庚":
        speed = "应月甚至应年（值使凶门或庚阻，事情迟缓）"
        speed_reason = "值使逢凶门或庚金阻格"
    elif shi_door in ("开门", "生门", "休门"):
        speed = "应日或应时辰（值使吉门，事情快速应验）"
        speed_reason = "值使临三吉门，力量旺盛"
    else:
        speed = "应日至应月（中性，视用神旺衰而定）"
        speed_reason = "格局中等平稳"

    # Key timing method from 《奇门法穷》
    fu_stem_info = ""
    if zhifu_palace:
        palace = zhifu_palace.get("palace_name", "")
        stem   = zhifu_palace.get("stem", "")
        fu_stem_info = f"值符（{stem}）临{palace}，按值符相冲法推算：该宫地支相冲之日月为应期"

    return {
        "speed":       speed,
        "speed_reason": speed_reason,
        "fu_method":   fu_stem_info or "值符落宫参照《奇门法穷》值符相冲法",
        "shi_method":  f"值使门（{shi_door}）旺衰决定应期快慢，" + (
            "吉门旺相则快，死惊凶门则慢" if shi_door else "综合判断"),
        "general":     yq.get("总则", "先定地支，后配天干。先以值符落宫定应期，后以值使门落宫定应期。"),
        "three_methods": yq.get("三法", {}),
        "fu_shi_order": yq.get("符使先后", "符应主先，使应主后"),
    }


# ─────────────────────────────────────────────────────────────
# Main analyze function
# ─────────────────────────────────────────────────────────────
def analyze_qimen(layout: Dict[str, Any]) -> Dict[str, Any]:
    """
    奇门遁甲完整断事分析
    四盘体系 × 值符值使断法 × 用神取法 × 格局检测 × 应期推算
    """
    palaces = layout["palaces"]
    question = layout.get("question", "")
    ck, has_classical = _load_classical()

    bamen_db  = ck["bamen"]
    jiuxing_db = ck["jiuxing"]
    bashen_db  = ck["bashen"]
    yanbo_db   = ck["yanbo"]

    enriched = []

    for p in palaces:
        star   = p.get("star", "")
        door   = p.get("door", "")
        deity  = p.get("deity", "")
        stem   = p.get("stem", "")
        palace_name = p.get("palace_name", "")
        gong_wx = _GONG_WX.get(palace_name, "")

        # Get classical data
        c_door  = bamen_db.get(door, {})
        c_star  = jiuxing_db.get(star, {})
        c_deity = bashen_db.get(deity, {})

        star_nature  = c_star.get("吉凶")  or ("吉" if star in ("天心","天辅","天任","天禽") else
                                                "次吉" if star == "天冲" else
                                                "凶" if star in ("天蓬","天芮","天柱") else "中")
        door_nature  = c_door.get("吉凶")  or ("大吉" if door in ("开门","休门","生门") else
                                                "大凶" if door == "死门" else
                                                "小凶" if door in ("伤门","惊门","杜门") else "中")
        deity_nature = c_deity.get("属性") or ("吉" if deity in ("值符","太阴","六合","九天","九地") else "凶")

        quality, score = _score_palace(star_nature, door_nature, deity_nature, stem, gong_wx)

        # Detailed classical notes (四盘三才合参)
        star_desc  = c_star.get("主象", star + "星")
        door_desc  = c_door.get("主象", door)
        deity_desc = c_deity.get("主象", deity + "神")
        star_kou   = c_star.get("临宫口诀", "")
        door_yanbo = c_door.get("烟波", "")

        # Star-door WX relationship (星克门/门克星)
        star_wx  = _XING_WX.get(star, "")
        door_wx  = _MEN_WX.get(door, "")
        sd_rel   = _wx_rel(star_wx, door_wx)
        sd_note  = ""
        if sd_rel == "克":
            sd_note = f"★星克门（{star_wx}克{door_wx}），天时助人和，主吉"
        elif sd_rel == "被克":
            sd_note = f"▲门克星（{door_wx}克{star_wx}），逆天时，主有阻"

        # Stem (奇仪) info
        stem_info = ""
        if stem in ("乙", "丙", "丁"):
            qi_name = {"乙": "天奇（大吉）", "丙": "地奇（大吉）", "丁": "人奇（吉）"}
            stem_info = f"三奇 {stem}·{qi_name.get(stem, '')} — 贵人相助"
        elif stem == "庚":
            stem_info = "庚·太白（大凶）— 阻格损伤"
        elif stem == "戊":
            stem_info = "戊·值符本气（吉）— 稳健中正"

        # Gong-door WX relationship
        gong_door_rel = _wx_rel(gong_wx, door_wx)

        # Full classical notes
        notes = f"【{star}】{star_desc} | 【{door}】{door_desc} | 【{deity}】{deity_desc}"
        if stem_info: notes += f" | {stem_info}"
        if sd_note:   notes += f"\n{sd_note}"
        if door_yanbo: notes += f"\n《烟波》：{door_yanbo}"
        if star_kou:   notes += f"\n口诀：{star_kou}"

        enriched.append({
            **p,
            "quality":       quality,
            "score":         score,
            "star_nature":   star_nature,
            "door_nature":   door_nature,
            "deity_nature":  deity_nature,
            "star_meaning":  star_desc,
            "door_meaning":  door_desc,
            "deity_meaning": deity_desc,
            "door_yanbo":    door_yanbo,
            "star_kou":      star_kou,
            "stem_info":     stem_info,
            "sd_rel":        sd_note,
            "gong_wx":       gong_wx,
            "notes":         notes,
            "is_auspicious": quality in ("大吉", "吉", "小吉"),
            # Classical detail fields
            "star_detail":   c_star.get("断法", ""),
            "door_detail":   c_door.get("详解", ""),
            "door_yi":       c_door.get("宜", []),
            "door_ji":       c_door.get("忌", []),
            "deity_detail":  c_deity.get("断法", ""),
            "deity_renwu":   c_deity.get("人事", ""),
        })

    best  = [p for p in enriched if p["quality"] in ("大吉", "吉", "小吉")]
    worst = [p for p in enriched if p["quality"] in ("大凶", "凶")]

    # 格局检测
    patterns = _detect_patterns(layout, enriched, ck)

    # 值符值使断法 (mark zhifu/zhishi)
    zhifu_palace  = next((p for p in enriched if p.get("is_zhifu")), None)
    zhishi_palace = next((p for p in enriched if p.get("is_zhishi")), None)
    zhifu_analysis = _analyze_zhifu_zhishi(enriched, ck)

    # 用神分析
    yong_shen = _analyze_yong_shen(enriched, question, ck)

    # 应期推算
    timing = _analyze_timing(zhifu_palace, zhishi_palace, ck)

    # Summary and advice
    summary = _build_summary_full(layout, best, worst, zhifu_analysis, patterns)
    advice  = _build_advice_full(layout, best, worst, patterns, zhifu_analysis, yong_shen)

    # Top 3 yanbo quotes relevant to current layout
    yanbo_notes = [x["口诀"] for x in ck.get("yanbo", [{}])[:3]] if ck.get("yanbo") else []

    return {
        **layout,
        "palaces":      enriched,
        "summary":      summary,
        "advice":       advice,
        "best_palaces": [p["palace_name"] for p in best],
        "worst_palaces":[p["palace_name"] for p in worst],
        "patterns":     patterns,
        "zhifu_analysis": zhifu_analysis,
        "yong_shen":    yong_shen,
        "timing":       timing,
        "yanbo_notes":  yanbo_notes,
        "has_classical": has_classical,
        "sibao_desc":   "天盘九星（天时）× 人盘八门（人和）× 地盘九宫（地利）× 神盘八神（神助）",
    }


def _build_summary_full(layout: Dict, best: List, worst: List,
                        zf: Dict, patterns: List) -> str:
    ju_type   = layout.get("ju_type", "")
    ju_number = layout.get("ju_number", "")
    yuan      = layout.get("yuan", "")
    best_str  = "、".join(p["palace_name"] for p in best[:3]) or "无"
    worst_str = "、".join(p["palace_name"] for p in worst[:2]) or "无"
    verdict   = zf.get("relationship", {}).get("detail", "") if zf else ""

    base = (f"当前为{ju_type}第{ju_number}局（{yuan}），"
            f"吉方：{best_str}，凶方：{worst_str}。")
    if verdict:
        base += f" 值符值使：{verdict}"
    if patterns:
        pats = "、".join(f"【{p['name']}】{p['level']}" for p in patterns[:2])
        base += f" 特殊格局：{pats}。"
    return base


def _build_advice_full(layout: Dict, best: List, worst: List, patterns: List,
                        zf: Dict, ys: Dict) -> str:
    # Pattern override for major bad patterns
    for pat in patterns:
        if pat.get("level") == "大凶" and pat["name"] in ("伏吟", "反吟"):
            return (f"【{pat['name']}格】{pat['desc']}。"
                    f"{pat.get('kou', '')}。当前宜静守待时，万事不宜轻动。")

    if not best:
        return "当前格局偏弱，宜静守。《烟波》：时不至者不可强行。"

    top = best[0]
    door = top.get("door", "")
    yanbo = top.get("door_yanbo", "")
    door_yi = top.get("door_yi", [])

    # Main direction advice
    shi_verdict = zf.get("verdict", "") if zf else ""
    yi_str = "、".join(door_yi[:3]) if door_yi else door

    advice = (f"最佳宫位：{top['palace_name']}（{door} × {top.get('star','')} × {top.get('deity','')}）。"
              f"此宫宜：{yi_str}。")

    if shi_verdict:
        advice += f" {shi_verdict}"
    if yanbo:
        advice += f" 《烟波》：{yanbo}"

    # Yong shen note
    if ys.get("topic") and ys.get("palace"):
        advice += (f" 就{ys['topic']}而言，用神（{ys['name'][:4]}）"
                   f"在{ys['palace']}，格局{'有利' if ys.get('quality') in ('大吉','吉') else '需谨慎'}。")

    return advice
