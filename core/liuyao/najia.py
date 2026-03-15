"""
core/liuyao/najia.py
=====================
Complete Najia (纳甲) system for professional LiuYao divination.

Implements:
  • Branch assignment (纳甲地支) for each line of each hexagram
  • Six Relatives (六亲): 父母/兄弟/妻财/子孙/官鬼
  • Six Spirits (六神/六兽): 青龙/朱雀/勾陈/腾蛇/白虎/玄武
  • World Line (世爻) and Application Line (应爻) positions
  • Void / Emptiness (空亡) calculation
  • Seasonal strength (旺相休囚死) for each line
"""
from __future__ import annotations
from datetime import date
from typing import Dict, List, Tuple, Optional, Any

from core.constants import (
    TIANGAN, DIZHI, TIANGAN_INDEX, DIZHI_INDEX,
    TIANGAN_WUXING, DIZHI_WUXING, WUXING_SHENG, WUXING_KE,
)

# ─────────────────────────────────────────────────────────────
# 1. Najia Branch Assignments (纳甲地支)
#    Each trigram has 3 lines; inner vs outer palace gets different stems.
#    Format: { trigram_name: {"inner": [zhi0, zhi1, zhi2], "outer": [zhi3, zhi4, zhi5]} }
#    Index 0 = 初爻(bottom), Index 2 = 上爻(top for each trigram half)
# ─────────────────────────────────────────────────────────────

NAJIA_BRANCHES: Dict[str, Dict[str, List[str]]] = {
    "乾": {"inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},   # 甲/壬
    "坤": {"inner": ["未", "巳", "卯"], "outer": ["丑", "亥", "酉"]},   # 乙/癸
    "震": {"inner": ["子", "寅", "辰"], "outer": ["午", "申", "戌"]},   # 庚
    "巽": {"inner": ["丑", "亥", "酉"], "outer": ["未", "巳", "卯"]},   # 辛
    "坎": {"inner": ["寅", "子", "戌"], "outer": ["申", "午", "辰"]},   # 戊
    "离": {"inner": ["卯", "巳", "未"], "outer": ["酉", "亥", "丑"]},   # 己
    "艮": {"inner": ["辰", "寅", "子"], "outer": ["戌", "申", "午"]},   # 丙
    "兑": {"inner": ["巳", "未", "酉"], "outer": ["亥", "丑", "卯"]},   # 丁
}

# Palace (宫) element for six-relative calculation
PALACE_ELEMENT: Dict[str, str] = {
    "乾": "金", "兑": "金",
    "震": "木", "巽": "木",
    "坎": "水",
    "离": "火",
    "艮": "土", "坤": "土",
}

# ─────────────────────────────────────────────────────────────
# 2. Eight-Palace Hexagram Classification
#    Maps King-Wen number → (palace, palace_position 1-8)
#    Position determines 世爻: 1→世6, 2→世1, 3→世2, 4→世3, 5→世4, 6→世5, 7→世4, 8→世3
# ─────────────────────────────────────────────────────────────

# {hex_num: (palace_trigram, palace_position_1_to_8)}
HEXAGRAM_PALACE: Dict[int, Tuple[str, int]] = {
    # 乾宫
    1: ("乾",1), 44:("乾",2), 33:("乾",3), 12:("乾",4),
    20:("乾",5), 23:("乾",6), 35:("乾",7), 14:("乾",8),
    # 坤宫
    2: ("坤",1), 24:("坤",2), 19:("坤",3), 11:("坤",4),
    34:("坤",5), 43:("坤",6),  5:("坤",7),  8:("坤",8),
    # 震宫
    51:("震",1), 16:("震",2), 40:("震",3), 32:("震",4),
    46:("震",5), 48:("震",6), 28:("震",7), 17:("震",8),
    # 巽宫
    57:("巽",1),  9:("巽",2), 37:("巽",3), 42:("巽",4),
    25:("巽",5), 21:("巽",6), 27:("巽",7), 18:("巽",8),
    # 坎宫
    29:("坎",1), 60:("坎",2),  3:("坎",3), 63:("坎",4),
    49:("坎",5), 55:("坎",6), 36:("坎",7),  7:("坎",8),
    # 离宫
    30:("离",1), 56:("离",2), 50:("离",3), 64:("离",4),
     4:("离",5), 59:("离",6),  6:("离",7), 13:("离",8),
    # 艮宫
    52:("艮",1), 22:("艮",2), 26:("艮",3), 41:("艮",4),
    38:("艮",5), 10:("艮",6), 61:("艮",7), 53:("艮",8),
    # 兑宫
    58:("兑",1), 47:("兑",2), 45:("兑",3), 31:("兑",4),
    39:("兑",5), 15:("兑",6), 62:("兑",7), 54:("兑",8),
}

# Palace position → 世爻 position (1-indexed, 1=初爻, 6=上爻)
PALACE_POS_TO_WORLD: Dict[int, int] = {
    1: 6,  # 本宫卦：世在上爻
    2: 1,  # 一爻变：世在初爻
    3: 2,  # 二爻变：世在二爻
    4: 3,  # 三爻变：世在三爻
    5: 4,  # 四爻变：世在四爻
    6: 5,  # 五爻变：世在五爻
    7: 4,  # 游魂：世在四爻
    8: 3,  # 归魂：世在三爻
}

def _get_world_line(hex_num: int) -> Tuple[int, int]:
    """Return (world_line_pos, application_line_pos) for a hexagram. 1-indexed."""
    palace, pos = HEXAGRAM_PALACE.get(hex_num, ("乾", 1))
    world = PALACE_POS_TO_WORLD.get(pos, 6)
    application = ((world - 1 + 3) % 6) + 1  # always 3 positions ahead
    return world, application

# ─────────────────────────────────────────────────────────────
# 3. Six Spirits (六神) Assignment
#    Starting spirit for 初爻 depends on the day stem.
#    Order: 青龙→朱雀→勾陈→腾蛇→白虎→玄武 (repeating)
# ─────────────────────────────────────────────────────────────

LIU_SHEN = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]

LIU_SHEN_START: Dict[str, int] = {
    "甲": 0, "乙": 0,   # 青龙起
    "丙": 1, "丁": 1,   # 朱雀起
    "戊": 2,             # 勾陈起
    "己": 3,             # 腾蛇起
    "庚": 4, "辛": 4,   # 白虎起
    "壬": 5, "癸": 5,   # 玄武起
}

LIU_SHEN_MEANINGS: Dict[str, Dict[str, str]] = {
    "青龙": {"nature": "吉", "color": "#27ae60", "desc": "青龙主吉，利贵人、喜庆、财帛"},
    "朱雀": {"nature": "凶", "color": "#e74c3c", "desc": "朱雀主口舌、文书、争讼"},
    "勾陈": {"nature": "凶", "color": "#f39c12", "desc": "勾陈主拖延、田土、官非"},
    "腾蛇": {"nature": "凶", "color": "#9b59b6", "desc": "腾蛇主惊恐、虚惊、怪异之事"},
    "白虎": {"nature": "凶", "color": "#e74c3c", "desc": "白虎主凶险、疾病、血光、丧事"},
    "玄武": {"nature": "凶", "color": "#34495e", "desc": "玄武主盗贼、暗昧、色情、欺诈"},
}

def assign_liu_shen(day_stem: str) -> List[str]:
    """Return list of 6 spirits from 初爻(index 0) to 上爻(index 5)."""
    start = LIU_SHEN_START.get(day_stem, 0)
    return [LIU_SHEN[(start + i) % 6] for i in range(6)]

# ─────────────────────────────────────────────────────────────
# 4. Six Relatives (六亲)
#    Compare each line's element with the palace element.
# ─────────────────────────────────────────────────────────────

LIU_QIN_NAMES = {
    "same":     "兄弟",   # same element as palace
    "generates":"子孙",   # palace generates this line's element
    "generated":"父母",   # this line's element generates palace
    "controls": "妻财",   # palace controls this line's element
    "controlled":"官鬼",  # this line's element controls palace
}

LIU_QIN_MEANINGS: Dict[str, Dict[str, str]] = {
    "父母": {
        "nature": "中", "color": "#8e44ad",
        "meaning": "主文书、父母、屋宅、官方文件、知识",
        "favorable_for": "求学、考试、签合同、官方审批",
        "unfavorable_for": "求子（克子孙爻）、婚姻（有耗泄）",
    },
    "兄弟": {
        "nature": "凶", "color": "#e67e22",
        "meaning": "主竞争、兄弟、朋友、阻碍财路",
        "favorable_for": "求助朋友、合作共事",
        "unfavorable_for": "求财（克妻财爻）、婚姻（兄弟争财）",
    },
    "子孙": {
        "nature": "吉", "color": "#27ae60",
        "meaning": "主福德、子女、医药、享乐、化解凶象",
        "favorable_for": "求医问药、生育、官司中（克官鬼）",
        "unfavorable_for": "功名（克官鬼）、官职",
    },
    "妻财": {
        "nature": "吉", "color": "#f1c40f",
        "meaning": "主财帛、妻妾（男性）、食物、日常所需",
        "favorable_for": "求财、经商、饮食",
        "unfavorable_for": "考功名（财克印）、父母病（财克父母）",
    },
    "官鬼": {
        "nature": "中", "color": "#c0392b",
        "meaning": "主官职、功名、丈夫（女性）、疾病、灾祸",
        "favorable_for": "求官职、女性求婚配、诉讼中有力",
        "unfavorable_for": "求健康（为疾病爻）、求财（官鬼克兄弟不直接助财）",
    },
}

def _wx_relation(palace_wx: str, line_wx: str) -> str:
    """Return relation type: same/generates/generated/controls/controlled."""
    if palace_wx == line_wx:
        return "same"
    if WUXING_SHENG.get(palace_wx) == line_wx:
        return "generates"  # palace generates line → 子孙
    if WUXING_SHENG.get(line_wx) == palace_wx:
        return "generated"  # line generates palace → 父母
    if WUXING_KE.get(palace_wx) == line_wx:
        return "controls"   # palace controls line → 妻财
    if WUXING_KE.get(line_wx) == palace_wx:
        return "controlled" # line controls palace → 官鬼
    return "same"

def get_liu_qin(palace_trigram: str, line_zhi: str) -> str:
    """Get the Six Relative name for a line."""
    palace_wx = PALACE_ELEMENT.get(palace_trigram, "金")
    line_wx = DIZHI_WUXING.get(line_zhi, "金")
    relation = _wx_relation(palace_wx, line_wx)
    return LIU_QIN_NAMES[relation]

# ─────────────────────────────────────────────────────────────
# 5. Void / Emptiness (空亡) Calculation
#    Based on the day's GanZhi: each 10-day cycle has 2 void branches.
# ─────────────────────────────────────────────────────────────

# The 60-cycle is divided into 6 groups of 10; each group has 2 void branches.
# Cycle index 0-9: 子亥 (甲子旬), 10-19: 戌酉 (甲戌旬), 20-29: 申未,
# 30-39: 午巳, 40-49: 辰卯, 50-59: 寅丑
KONG_WANG_TABLE: Dict[int, List[str]] = {
    0: ["戌", "亥"],   # 甲子旬空戌亥
    1: ["申", "酉"],   # 甲戌旬空申酉
    2: ["午", "未"],   # 甲申旬空午未
    3: ["辰", "巳"],   # 甲午旬空辰巳
    4: ["寅", "卯"],   # 甲辰旬空寅卯
    5: ["子", "丑"],   # 甲寅旬空子丑
}

def get_kong_wang(day_ganzhi_index: int) -> List[str]:
    """
    Return the 2 void DiZhi for a given day GanZhi cycle index (0-59).
    The 旬空 is based on which 10-day group the day falls in.
    """
    group = (day_ganzhi_index // 10) % 6
    return KONG_WANG_TABLE[group]

# ─────────────────────────────────────────────────────────────
# 6. Seasonal Strength (旺相休囚死)
#    Already in constants; expose convenience function here.
# ─────────────────────────────────────────────────────────────

from core.constants import get_wuxing_strength as _get_wx_strength

STRENGTH_LABELS = {
    "旺": {"label": "旺", "color": "#e74c3c", "desc": "当令最旺，力量最强"},
    "相": {"label": "相", "color": "#e67e22", "desc": "相气有力，力量较强"},
    "休": {"label": "休", "color": "#95a5a6", "desc": "退气休歇，力量一般"},
    "囚": {"label": "囚", "color": "#7f8c8d", "desc": "受制被囚，力量较弱"},
    "死": {"label": "死", "color": "#bdc3c7", "desc": "死绝无气，力量最弱"},
}

def get_line_strength(line_zhi: str, month_zhi: str) -> Dict[str, str]:
    """Return strength info for a line in the current month."""
    wx = DIZHI_WUXING.get(line_zhi, "土")
    s = _get_wx_strength(wx, month_zhi)
    return STRENGTH_LABELS.get(s, {"label": s, "color": "#95a5a6", "desc": ""})

# ─────────────────────────────────────────────────────────────
# 7. Master annotate function
#    Takes a divination result + query date and adds Najia data.
# ─────────────────────────────────────────────────────────────

def annotate_with_najia(
    result: Dict[str, Any],
    hex_num: int,
    lower_trigram: str,
    upper_trigram: str,
    day_stem: str,
    day_ganzhi_index: int,
    month_zhi: str,
) -> Dict[str, Any]:
    """
    Enrich each yao in result['yaos'] with:
      - branch (纳甲地支)
      - element (五行)
      - liu_qin (六亲)
      - liu_shen (六神)
      - kong_wang (是否空亡)
      - strength (旺相休囚死)
      - world/application marker
    """
    palace_trig, _ = HEXAGRAM_PALACE.get(hex_num, (lower_trigram, 1))
    world_pos, app_pos = _get_world_line(hex_num)
    kong_wang_branches = get_kong_wang(day_ganzhi_index)
    liu_shen_list = assign_liu_shen(day_stem)

    yaos = result.get("yaos", [])
    enriched_yaos = []

    for i, yao in enumerate(yaos):
        pos = i + 1  # 1-indexed
        # Which trigram half?
        if pos <= 3:
            trigram = lower_trigram
            branch = NAJIA_BRANCHES.get(trigram, {}).get("inner", ["子","寅","辰"])[i]
        else:
            trigram = upper_trigram
            branch = NAJIA_BRANCHES.get(trigram, {}).get("outer", ["午","申","戌"])[i - 3]

        wx = DIZHI_WUXING.get(branch, "土")
        liu_qin = get_liu_qin(palace_trig, branch)
        liu_shen = liu_shen_list[i]
        is_kong_wang = branch in kong_wang_branches
        strength = get_line_strength(branch, month_zhi)
        is_world = (pos == world_pos)
        is_application = (pos == app_pos)

        enriched_yaos.append({
            **yao,
            "branch": branch,
            "element": wx,
            "liu_qin": liu_qin,
            "liu_shen": liu_shen,
            "liu_shen_meaning": LIU_SHEN_MEANINGS.get(liu_shen, {}),
            "liu_qin_meaning": LIU_QIN_MEANINGS.get(liu_qin, {}),
            "kong_wang": is_kong_wang,
            "strength": strength,
            "is_world": is_world,
            "is_application": is_application,
        })

    result["yaos"] = enriched_yaos
    result["world_line"] = world_pos
    result["application_line"] = app_pos
    result["kong_wang_branches"] = kong_wang_branches
    result["palace_trigram"] = palace_trig
    result["palace_element"] = PALACE_ELEMENT.get(palace_trig, "金")
    result["najia_summary"] = _build_najia_summary(enriched_yaos, world_pos, app_pos, kong_wang_branches)
    return result


def _build_najia_summary(yaos: List[Dict], world: int, application: int, kong: List[str]) -> Dict[str, Any]:
    """Build a professional summary of the Najia analysis."""
    world_yao = next((y for y in yaos if y.get("is_world")), None)
    app_yao = next((y for y in yaos if y.get("is_application")), None)

    changing = [y for y in yaos if y.get("is_changing")]
    active_liu_qin = {}
    for y in changing:
        qin = y.get("liu_qin", "")
        if qin:
            active_liu_qin.setdefault(qin, []).append(y.get("branch", ""))

    world_desc = ""
    if world_yao:
        wq = world_yao.get("liu_qin", "")
        ws = world_yao.get("strength", {}).get("label", "")
        wk = "（空亡！）" if world_yao.get("kong_wang") else ""
        world_desc = f"世爻为{wq}爻（{world_yao.get('branch','')}），{ws}{wk}"

    app_desc = ""
    if app_yao:
        aq = app_yao.get("liu_qin", "")
        ak = "（空亡！）" if app_yao.get("kong_wang") else ""
        app_desc = f"应爻为{aq}爻（{app_yao.get('branch','')}）{ak}"

    kong_desc = f"旬空地支：{'、'.join(kong)}" if kong else ""

    return {
        "world_desc": world_desc,
        "app_desc": app_desc,
        "kong_desc": kong_desc,
        "active_liu_qin": active_liu_qin,
        "changing_count": len(changing),
    }
