"""
core/liuyao/interpreter.py
==========================
Applies classical LiuYao rules from the knowledge library to enriched
yao data and produces structured professional analysis.

Sources applied:
  《增删卜易》《卜筮正宗》《易隐》《火珠林》《黄金策》
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional

from core.liuyao.hexagram_data import HEXAGRAM_DATA
from core.constants import TRIGRAMS, DIZHI_INDEX, DIZHI_WUXING, WUXING_KE, WUXING_SHENG


# ─────────────────────────────────────────────────────────────
# 1. Topic matching — map question keywords → liuyao topic rules
# ─────────────────────────────────────────────────────────────

_TOPIC_MAP: Dict[str, str] = {
    "官司诉讼": ["官司","诉讼","打官司","法院","起诉","律师","纠纷","判决","赔偿","仲裁","胜诉","败诉"],
    "求医疾病": ["病","医","健康","手术","治疗","痊愈","身体","检查","诊断","康复","药","住院"],
    "考试功名": ["考试","功名","学历","文凭","录取","入学","高考","考研","成绩","分数","金榜"],
    "婚姻感情": ["婚","恋","感情","对象","结婚","爱","姻缘","追","分手","离婚","桃花","缘分","伴侣"],
    "求官仕途": ["升职","升迁","晋升","职位","公务","录用","考核","考编","考公","职场","仕途","官职"],
    "求子嗣":  ["孩子","生育","怀孕","子嗣","要孩子","生孩子","备孕","求子"],
    "找人行人": ["找人","行人","失踪","下落","联系","寻找","归来","消息","人回","何时归"],
    "失物寻物": ["失物","丢失","找东西","寻物","遗失","丢了","寻回","失窃"],
    "家宅风水": ["家宅","住宅","搬家","装修","风水","家庭","房子","居家","买房"],
    "出行远行": ["出行","旅行","出差","远行","旅游","出门","路途","行程","航班","能否成行"],
    "求财":    ["财","钱","生意","投资","收入","赚","金融","股","贷款","利润","薪","借","求财","财运"],
    "天气占候": ["天气","下雨","晴天","气候","风","雨","明天","后天"],
}

def _match_topic(question: str) -> str:
    for topic, keywords in _TOPIC_MAP.items():
        if any(k in question for k in keywords):
            return topic
    return "综合"


def _get_topic_rules(topic: str) -> Optional[Dict]:
    try:
        from knowledge.liuyao_classical import LIUYAO_TOPIC_RULES
        return LIUYAO_TOPIC_RULES.get(topic)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# 2. Core yong-shen determination
# ─────────────────────────────────────────────────────────────

_TOPIC_YONG_SHEN: Dict[str, List[str]] = {
    "求财":    ["妻财"],
    "求官仕途": ["官鬼", "父母"],
    "考试功名": ["父母", "官鬼"],
    "婚姻感情": ["妻财", "官鬼"],   # male: 妻财, female: 官鬼
    "求医疾病": ["世爻", "子孙"],
    "出行远行": ["世爻", "妻财"],
    "官司诉讼": ["世爻", "应爻"],
    "求子嗣":  ["子孙"],
    "找人行人": ["应爻"],
    "失物寻物": ["妻财"],
    "家宅风水": ["父母", "世爻"],
    "综合":    ["世爻"],
}


def _find_yao_by_liuqin(yaos: List[Dict], liuqin: str) -> Optional[Dict]:
    return next((y for y in yaos if y.get("liu_qin") == liuqin), None)


# ─────────────────────────────────────────────────────────────
# 3. Classical rule application
# ─────────────────────────────────────────────────────────────

def _get_six_combine_class(hex_type: str) -> str:
    if hex_type == "六合":
        return "六合卦：诸事聚合，婚姻易成，谋事可就，感情融洽"
    if hex_type == "六冲":
        return "六冲卦：诸事散乱，出行不宜，感情有分，事情反复"
    return ""


def _apply_classical_rules(yaos: List[Dict], world_yao: Optional[Dict],
                            app_yao: Optional[Dict], kong_wang: List[str],
                            changing: List[Dict], topic: str) -> List[str]:
    """
    Apply classical rules to produce analysis points.
    Returns list of analysis strings.
    """
    points = []

    # ── 世爻分析 ──
    if world_yao:
        wq = world_yao.get("liu_qin", "")
        ws = world_yao.get("strength", {}).get("label", "")
        wb = world_yao.get("branch", "")
        wk = world_yao.get("kong_wang", False)
        wg = world_yao.get("liu_shen", "")
        is_changing_world = world_yao.get("is_changing", False)

        # 世爻旺衰
        if ws in ("旺", "相"):
            points.append(f"世爻{wq}爻（{wb}）{ws}，身强有力，"
                          f"《卜筮正宗》云：世爻旺相最为强，作事亨通大吉昌")
        elif ws in ("休", "囚", "死"):
            points.append(f"世爻{wq}爻（{wb}）{ws}，身弱力衰，"
                          f"谋事宜守不宜攻，须得生扶方可奋进")

        # 世爻空亡
        if wk:
            points.append(f"世爻（{wb}）落旬空，《黄金策》云：心退悔兮世空，"
                          f"问卦者心意不定、做事乏力，须待出空后再图")

        # 世爻动
        if is_changing_world:
            points.append(f"世爻发动，《增删卜易》云：世应不宜动，"
                          f"世爻动主本人三心二意、左顾右盼，事情反复")

        # 六神临世
        if wg == "白虎":
            points.append(f"白虎临世爻，主凶险血光，诸事宜防意外")
        elif wg == "玄武":
            points.append(f"玄武临世爻，主有暗谋、心思不正，防欺骗")
        elif wg == "青龙":
            points.append(f"青龙临世爻，贵人扶助，诸事顺遂")
        elif wg == "腾蛇":
            points.append(f"腾蛇临世爻，主虚惊烦恼，事多反复")

    # ── 应爻分析 ──
    if app_yao:
        aq = app_yao.get("liu_qin", "")
        ab = app_yao.get("branch", "")
        ak = app_yao.get("kong_wang", False)
        if ak:
            points.append(f"应爻（{ab}）空亡，对方无诚意或有障碍，"
                          f"所求之人或事暂时无法落实")

        # 世应生克关系
        if world_yao and app_yao:
            w_wx = DIZHI_WUXING.get(world_yao.get("branch", ""), "")
            a_wx = DIZHI_WUXING.get(app_yao.get("branch", ""), "")
            if w_wx and a_wx:
                if WUXING_KE.get(w_wx) == a_wx:
                    points.append(f"世克应：己方强势主动，对方处于被动，"
                                  f"《卜筮正宗》云：世旺克应，我胜")
                elif WUXING_KE.get(a_wx) == w_wx:
                    points.append(f"应克世：对方强势，己方处于被动，"
                                  f"《卜筮正宗》云：应旺克世，彼胜")
                elif WUXING_SHENG.get(a_wx) == w_wx:
                    points.append(f"应生世：对方助力，双方有情，事情可就")
                elif WUXING_SHENG.get(w_wx) == a_wx:
                    points.append(f"世生应：己方资助对方，损己利人，"
                                  f"《卜筮正宗》谓之反德扶人，所求不易")

    # ── 动爻分析 ──
    if len(changing) == 1:
        y = changing[0]
        yq = y.get("liu_qin", "")
        yb = y.get("branch", "")
        yg = y.get("liu_shen", "")
        points.append(f"独发一爻（第{y.get('line','')}爻 {yq}爻 {yb}）动，"
                      f"《增删卜易》云：独发易取——此爻为本卦断事之关键，"
                      f"《火珠林》云：动爻急如火")
        if yg == "白虎":
            points.append(f"独发爻逢白虎，主凶险速发，尤防血光意外")
        elif yg == "青龙":
            points.append(f"独发爻逢青龙，贵人主动相助，事情可期")

    elif len(changing) == 0:
        points.append("六爻皆静，《增删卜易》云：六爻安静，以本卦卦辞论断，"
                      "事情稳定少变，以世爻所在六亲论吉凶")
    elif len(changing) >= 5:
        points.append("爻动过多（五、六爻皆动），《增删卜易》云：乱动难寻，"
                      "吉凶交错，须以之卦为准，重新论断")

    # ── 用神空亡检查 ──
    yong_shen_names = _TOPIC_YONG_SHEN.get(topic, ["世爻"])
    for ys_name in yong_shen_names:
        if ys_name == "世爻":
            continue
        ys_yao = _find_yao_by_liuqin(yaos, ys_name)
        if ys_yao:
            if ys_yao.get("kong_wang"):
                points.append(f"用神{ys_name}爻（{ys_yao.get('branch','')}）旬空，"
                               f"《黄金策》云：伏神空亡，凡事不利，"
                               f"须待出空之期，方有希望")
            ys_s = ys_yao.get("strength", {}).get("label", "")
            if ys_s in ("旺", "相"):
                points.append(f"用神{ys_name}爻旺相有力，所问之事有望成就")
            elif ys_s in ("死",):
                points.append(f"用神{ys_name}爻死绝无气，所问之事难以成就，"
                               f"须待其旺相之月日再图")

    # ── 兄弟动（克财）——特别警示 ──
    if topic == "求财":
        for y in changing:
            if y.get("liu_qin") == "兄弟":
                points.append(f"兄弟爻（{y.get('branch','')}）发动，"
                               f"《火珠林》云：兄动，事不实，难成，且财被克截，"
                               f"防他人争财或合伙破散")

    # ── 子孙动（化官）——求官警示 ──
    if topic in ("求官仕途", "考试功名"):
        for y in changing:
            if y.get("liu_qin") == "子孙":
                points.append(f"子孙爻（{y.get('branch','')}）发动克官鬼，"
                               f"《火珠林》云：忌子孙持世，不中，"
                               f"官职功名受阻，需化解")

    return points


# ─────────────────────────────────────────────────────────────
# 4. Timing analysis (应期推算) using classical rules
# ─────────────────────────────────────────────────────────────

def _calc_timing(yaos: List[Dict], topic: str, changing: List[Dict],
                 kong_wang: List[str]) -> Dict[str, Any]:
    """
    Generate timing guidance using classical rules.
    Based on: 病药原则, 进退神, 月建日辰, 飞伏, 空亡出空
    """
    timing = {}

    # Determine main yong shen
    ys_names = _TOPIC_YONG_SHEN.get(topic, ["世爻"])
    ys_name = ys_names[0] if ys_names else "世爻"

    timing["yong_shen_name"] = ys_name
    timing["rules_applied"] = []

    # Apply timing rules from classical knowledge
    for y in changing:
        yb = y.get("branch", "")
        yq = y.get("liu_qin", "")
        # Check for 进退神
        jin_shen = _check_jin_tui_shen(yb)
        if jin_shen == "进":
            timing["rules_applied"].append(
                f"{yq}爻（{yb}）化进神，事情好转发展，应期在进神地支值日时"
            )
        elif jin_shen == "退":
            timing["rules_applied"].append(
                f"{yq}爻（{yb}）化退神，{'+'.join(['凶中有消退'])}，应期在退神地支冲日时"
            )

    # Kong wang timing
    if kong_wang:
        timing["kong_wang_timing"] = (
            f"旬空地支{'/'.join(kong_wang)}，待出旬（{kong_wang[0]}）之后方可应验；"
            f"或有日辰冲空（{_get_chong(kong_wang[0])}日），亦为应期"
        )

    # General principle
    timing["general"] = (
        "《黄金策》病药原则：卦中空破墓合为【病】（阻碍），"
        "出空填实冲墓冲合为【药】（解除阻碍），药至则事验。"
        "急事应日时，中事应月，大事应年。"
    )

    return timing


# 进退神表
_JIN_SHEN = {"子":"丑","寅":"卯","卯":"辰","巳":"午","午":"未","申":"酉","酉":"戌","亥":"子"}
_TUI_SHEN = {v:k for k,v in _JIN_SHEN.items()}

def _check_jin_tui_shen(zhi: str) -> str:
    if zhi in _JIN_SHEN:  return "进"
    if zhi in _TUI_SHEN:  return "退"
    return ""

# 六冲表
_CHONG = {"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
          "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}

def _get_chong(zhi: str) -> str:
    return _CHONG.get(zhi, "")


# ─────────────────────────────────────────────────────────────
# 5. Build topic-specific analysis using classical rules
# ─────────────────────────────────────────────────────────────

def _build_topic_analysis(yaos: List[Dict], topic: str,
                          changing: List[Dict], kong_wang: List[str],
                          hex_type: str) -> Dict[str, Any]:
    """
    Apply topic-specific classical rules and return structured analysis.
    """
    analysis = {
        "topic":      topic,
        "verdict":    "",
        "key_points": [],
        "timing":     {},
        "classical_ref": "",
    }

    topic_rules = _get_topic_rules(topic)
    if not topic_rules:
        return analysis

    # Determine yong shen
    ys_names_raw = _TOPIC_YONG_SHEN.get(topic, ["世爻"])
    key_points = []

    # Get primary yong shen yao
    primary_ys = None
    for ys_name in ys_names_raw:
        if ys_name in ("世爻", "应爻"):
            continue
        y = _find_yao_by_liuqin(yaos, ys_name)
        if y:
            primary_ys = y
            break

    # Apply the first 4 topic rules
    rules = topic_rules.get("规则") or topic_rules.get("rules", [])
    for r in rules[:4]:
        key_points.append(r)

    # Verdict based on primary yong shen
    if primary_ys:
        ys_strength = primary_ys.get("strength", {}).get("label", "")
        ys_kong = primary_ys.get("kong_wang", False)
        ys_q = primary_ys.get("liu_qin", "")
        ys_b = primary_ys.get("branch", "")

        if ys_kong:
            analysis["verdict"] = f"用神{ys_q}爻旬空，所谋之事落空或难以实现，待出空后再图"
        elif ys_strength in ("旺", "相"):
            analysis["verdict"] = f"用神{ys_q}爻（{ys_b}）旺相有力，{topic_rules.get('summary','所谋可成')}"
        elif ys_strength in ("死",):
            analysis["verdict"] = f"用神{ys_q}爻（{ys_b}）死绝，{topic}之谋难以成就，须待旺相之时"
        else:
            analysis["verdict"] = topic_rules.get("summary", "需结合全卦参断")
    else:
        analysis["verdict"] = topic_rules.get("summary", "")

    # 六合/六冲 overlay
    combine_note = _get_six_combine_class(hex_type)
    if combine_note:
        key_points.insert(0, combine_note)

    analysis["key_points"] = key_points
    analysis["timing"] = _calc_timing(yaos, topic, changing, kong_wang)
    analysis["classical_ref"] = (
        topic_rules.get("卜筮正宗") or
        topic_rules.get("增删卜易") or
        topic_rules.get("火珠林") or
        topic_rules.get("黄金策") or ""
    )

    return analysis


# ─────────────────────────────────────────────────────────────
# 6. Main interpret function
# ─────────────────────────────────────────────────────────────

def interpret(result: Dict[str, Any], question: str = "") -> Dict[str, Any]:
    """
    Enrich a divination result with professional classical analysis.
    Uses the najia-annotated yao data + liuyao_classical knowledge library.
    """
    orig    = result["original"]
    changed = result.get("changed")
    yaos    = result.get("yaos", [])
    kong    = result.get("kong_wang_branches", [])
    hex_type = result.get("hex_type", "")   # 六合/六冲 etc.

    orig_num  = orig["number"]
    orig_data = HEXAGRAM_DATA.get(orig_num, {})

    # ── Basic hexagram info ──
    upper_nature = TRIGRAMS.get(orig["upper"]["name"], {}).get("nature", "")
    lower_nature = TRIGRAMS.get(orig["lower"]["name"], {}).get("nature", "")

    # ── Find world / application yaos ──
    world_pos = result.get("world_line", 0)
    app_pos   = result.get("application_line", 0)
    world_yao = next((y for y in yaos if y.get("is_world")),    None)
    app_yao   = next((y for y in yaos if y.get("is_application")), None)
    changing  = [y for y in yaos if y.get("is_changing")]

    # ── Topic matching ──
    topic = _match_topic(question)

    # ── Classical rule analysis ──
    classical_points = _apply_classical_rules(
        yaos, world_yao, app_yao, kong, changing, topic
    )

    # ── Topic-specific analysis ──
    topic_analysis = _build_topic_analysis(
        yaos, topic, changing, kong, hex_type
    )

    # ── Hexagram introduction ──
    intro = (
        f"本卦第{orig_num}卦【{orig_data.get('name','')}卦】，"
        f"上{orig['upper']['name']}（{upper_nature}）下{orig['lower']['name']}（{lower_nature}）。"
    )
    body  = orig_data.get("interpretation", orig_data.get("judgment", ""))

    # ── Changing lines ──
    if changing:
        line_texts = []
        for y in changing:
            pos  = y.get("line", "")
            text = orig_data.get("lines", {}).get(pos, "")
            qin  = y.get("liu_qin", "")
            shen = y.get("liu_shen", "")
            # Apply flying/hidden god rule
            jin = _check_jin_tui_shen(y.get("branch", ""))
            jin_note = f"，化{'进' if jin=='进' else '退'}神" if jin else ""
            line_texts.append(f"第{pos}爻{qin}爻（{shen}）动{jin_note}：{text}")
        change_section = "【动爻详析】" + "；".join(line_texts)

        if changed:
            ch_data = HEXAGRAM_DATA.get(changed["number"], {})
            change_section += (
                f"\n【之卦】第{changed['number']}卦【{ch_data.get('name','')}卦】，"
                f"{ch_data.get('interpretation', '')[:80]}。"
            )
    else:
        change_section = "【六爻皆静】以本卦卦辞论断，事情平稳少变。"

    # ── World / Application summary ──
    world_summary = ""
    if world_yao:
        wq = world_yao.get("liu_qin", "")
        wb = world_yao.get("branch", "")
        ws = world_yao.get("strength", {}).get("label", "")
        wg = world_yao.get("liu_shen", "")
        wk = "（旬空！）" if world_yao.get("kong_wang") else ""
        world_summary = f"世爻：{wq}爻 {wb} {ws}{wk}，{wg}临爻"
    if app_yao:
        aq = app_yao.get("liu_qin", "")
        ab = app_yao.get("branch", "")
        ak = "（旬空！）" if app_yao.get("kong_wang") else ""
        world_summary += f" ‖ 应爻：{aq}爻 {ab}{ak}"

    # ── Six Gods analysis ──
    try:
        from knowledge.liuyao_classical import LIUYAO_SIX_GODS
        gods_active = []
        for y in changing:
            g = y.get("liu_shen", "")
            q = y.get("liu_qin", "")
            b = y.get("branch", "")
            if g and g in LIUYAO_SIX_GODS:
                god_info = LIUYAO_SIX_GODS[g]
                dynamic_key = f"临{q}"
                meaning = god_info.get(dynamic_key, god_info.get("口诀", ""))
                gods_active.append(f"{g}临{q}爻（{b}）动：{meaning}")
        gods_section = "【六神动爻】" + "；".join(gods_active) if gods_active else ""
    except Exception:
        gods_section = ""

    # ── Build full interpretation ──
    parts = [intro, body, change_section]
    if world_summary:
        parts.append(f"【世应】{world_summary}")
    if gods_section:
        parts.append(gods_section)
    if classical_points:
        parts.append("【经典断法】" + "。".join(classical_points[:5]))
    interpretation = "\n\n".join(p for p in parts if p)

    # ── Advice ──
    advice_lines = []
    if topic_analysis.get("verdict"):
        advice_lines.append(topic_analysis["verdict"])
    if topic_analysis.get("timing", {}).get("general"):
        advice_lines.append(topic_analysis["timing"]["general"])
    if topic_analysis.get("timing", {}).get("kong_wang_timing"):
        advice_lines.append(topic_analysis["timing"]["kong_wang_timing"])
    advice = "；".join(advice_lines) or "宜审时度势，以诚信处世。"

    # ── Attach all to result ──
    result["question"]       = question
    result["topic"]          = topic
    result["interpretation"] = interpretation
    result["advice"]         = advice
    result["topic_analysis"] = topic_analysis
    result["classical_points"] = classical_points
    result["world_summary"]  = world_summary
    result["changing_analysis"] = [
        {
            "line":     y.get("line", ""),
            "liu_qin":  y.get("liu_qin", ""),
            "liu_shen": y.get("liu_shen", ""),
            "branch":   y.get("branch", ""),
            "jin_tui":  _check_jin_tui_shen(y.get("branch", "")),
            "kong_wang": y.get("kong_wang", False),
        }
        for y in changing
    ]

    return result
