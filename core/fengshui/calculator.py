"""
core/fengshui/calculator.py
============================
FengShui core calculations:
  • Ming Gua (命卦) — personal trigram number
  • House Gua (宅卦) — house trigram
  • Eight Mansion (八宅) sector analysis
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple


# ─────────────────────────────────────────────────────────────
# 1. Ming Gua (命卦)
# ─────────────────────────────────────────────────────────────

# 东四命 (East Four Life)
EAST_FOUR_LIFE = {1, 3, 4, 9}
# 西四命 (West Four Life)
WEST_FOUR_LIFE = {2, 5, 6, 7, 8}

def calculate_ming_gua(birth_year: int, gender: str) -> int:
    """
    Calculate the Ming Gua (命卦) number for a person.
    Uses the traditional formula:
      Male:   (10 - (year digit sum % 9)) % 9, or 9 if result = 0
      Female: (year digit sum + 5) % 9, or 9 if result = 0
      After 2000: male subtract from 9 instead of 10.
    """
    # Sum year digits until single digit
    y = birth_year % 100  # last 2 digits
    while y >= 10:
        y = sum(int(d) for d in str(y))
    if y == 0:
        y = 9

    male = gender in ("male", "男")

    if birth_year < 2000:
        gua = (10 - y) % 9 if male else (y + 5) % 9
    else:
        gua = (9 - y) % 9 if male else (y + 6) % 9

    if gua == 0:
        gua = 9
    if gua == 5:
        gua = 2 if male else 8   # 5 is converted to 2(male) or 8(female)

    return gua


def get_ming_gua_group(gua: int) -> str:
    return "东四命" if gua in EAST_FOUR_LIFE else "西四命"


# ─────────────────────────────────────────────────────────────
# 2. House Gua (宅卦)
# ─────────────────────────────────────────────────────────────

# Direction → Gua number mapping (facing direction determines house gua)
DIRECTION_GUA: Dict[str, int] = {
    "南":  9,  "北":  1,  "东":  3,  "西":  7,
    "东南": 4, "西北": 6, "东北": 8, "西南": 2,
}

EAST_FOUR_HOUSE = {1, 3, 4, 9}
WEST_FOUR_HOUSE = {2, 6, 7, 8}

def get_house_gua(facing_direction: str) -> int:
    return DIRECTION_GUA.get(facing_direction, 9)


def get_house_group(gua: int) -> str:
    return "东四宅" if gua in EAST_FOUR_HOUSE else "西四宅"


def check_compatibility(ming_gua: int, house_gua: int) -> str:
    """
    Check compatibility between person's Ming Gua and house Gua.
    Now includes 《八宅明镜》详细判断 and 《阳宅三要》建议.
    """
    ming_group  = get_ming_gua_group(ming_gua)
    house_group = get_house_group(house_gua)

    _MING_NAME = {1:"坎（水）",2:"坤（土）",3:"震（木）",4:"巽（木）",
                  6:"乾（金）",7:"兑（金）",8:"艮（土）",9:"离（火）"}
    _HOUSE_NAME = {1:"坎宅（北向）",2:"坤宅（西南）",3:"震宅（东向）",4:"巽宅（东南）",
                   6:"乾宅（西北）",7:"兑宅（西向）",8:"艮宅（东北）",9:"离宅（南向）"}

    mn = _MING_NAME.get(ming_gua, str(ming_gua))
    hn = _HOUSE_NAME.get(house_gua, str(house_gua))

    if ming_group[0] == house_group[0]:
        level = "相配"
        detail = (f"命卦{mn}（{ming_group}）与{hn}（{house_group}）同属{ming_group[:1]}四宅，"
                  f"《八宅明镜》云：东四命住东四宅，西四命住西四宅，同类相得则吉。")
    else:
        level = "不相配"
        detail = (f"命卦{mn}（{ming_group}）与{hn}（{house_group}）不同类，"
                  f"《八宅明镜》云：东命住西宅，或西命住东宅，命宅相克则凶，"
                  f"建议重点布局生气位（{get_sector_direction(ming_gua, '生气')}）弥补。")

    return f"{level}｜{detail}"


def get_sector_direction(ming_gua: int, sector: str) -> str:
    """Return the compass direction of a specific sector for a given ming_gua."""
    sectors = EIGHT_MANSION.get(ming_gua, {})
    for direction, name in sectors.items():
        if name == sector:
            return direction
    return "未知"


def get_sector_analysis(house_gua: int) -> List[Dict[str, str]]:
    """
    Return sector analysis for a house based on its Gua.
    Now enriched with 《八宅明镜》《阳宅三要》classical guidance.
    """
    sectors = EIGHT_MANSION.get(house_gua, EIGHT_MANSION[1])

    # Load classical enrichment
    _CLASSICAL_DETAIL = {}
    try:
        from knowledge.fengshui_classical import BAYUAN_JIUXING
        _CLASSICAL_DETAIL = BAYUAN_JIUXING
    except Exception:
        pass

    result = []
    for direction, sector_name in sectors.items():
        sq = SECTOR_QUALITY.get(sector_name, {})
        classical = _CLASSICAL_DETAIL.get(sector_name, {})

        # Use classical main symbol if available
        main_symbol = classical.get("主象", sq.get("desc", ""))
        classical_use = classical.get("适宜", "")

        # Build usage advice
        base_advice = sq.get("advice", "")
        if classical_use:
            if isinstance(classical_use, list):
                advice_ext = "宜：" + "、".join(classical_use[:3])
            else:
                advice_ext = str(classical_use)
            full_advice = f"{base_advice}；{advice_ext}"
        else:
            full_advice = base_advice

        result.append({
            "direction": direction,
            "star":      sector_name,
            "quality":   sq.get("quality", "中"),
            "meaning":   main_symbol,
            "advice":    full_advice,
            "classical_name": classical.get("星名", ""),
        })
    return result



# ─────────────────────────────────────────────────────────────
# 3. Eight Mansion (八宅) sectors
# ─────────────────────────────────────────────────────────────

# For each house Gua, the 8 compass sectors have different qualities.
# Keys: Gua 1–9 (excl 5), values: dict of direction→quality
# Qualities: 生气, 天医, 延年, 伏位, 绝命, 五鬼, 六煞, 祸害

# 八宅游年法 layout (simplified standard table)
EIGHT_MANSION: Dict[int, Dict[str, str]] = {
    1: {  # 坎宅 (北)
        "北": "伏位", "南": "延年", "东": "生气", "西": "绝命",
        "东南": "天医", "西北": "五鬼", "东北": "六煞", "西南": "祸害",
    },
    2: {  # 坤宅 (西南)
        "北": "绝命", "南": "祸害", "东": "六煞", "西": "生气",
        "东南": "五鬼", "西北": "天医", "东北": "五鬼", "西南": "伏位",
    },
    3: {  # 震宅 (东)
        "北": "天医", "南": "六煞", "东": "伏位", "西": "五鬼",
        "东南": "生气", "西北": "绝命", "东北": "祸害", "西南": "延年",
    },
    4: {  # 巽宅 (东南)
        "北": "六煞", "南": "天医", "东": "生气", "西": "祸害",
        "东南": "伏位", "西北": "五鬼", "东北": "延年", "西南": "绝命",
    },
    6: {  # 乾宅 (西北)
        "北": "五鬼", "南": "绝命", "东": "六煞", "西": "延年",
        "东南": "祸害", "西北": "伏位", "东北": "天医", "西南": "生气",
    },
    7: {  # 兑宅 (西)
        "北": "祸害", "南": "五鬼", "东": "绝命", "西": "伏位",
        "东南": "六煞", "西北": "延年", "东北": "生气", "西南": "天医",
    },
    8: {  # 艮宅 (东北)
        "北": "六煞", "南": "五鬼", "东": "祸害", "西": "生气",
        "东南": "延年", "西北": "天医", "东北": "伏位", "西南": "绝命",
    },
    9: {  # 离宅 (南)
        "北": "延年", "南": "伏位", "东": "天医", "西": "六煞",
        "东南": "六煞", "西北": "绝命", "东北": "五鬼", "西南": "祸害",
    },
}

SECTOR_QUALITY: Dict[str, Dict[str, str]] = {
    "生气": {"quality": "吉", "desc": "最吉，利发展、求财、婚姻", "advice": "宜置卧室、书房"},
    "天医": {"quality": "吉", "desc": "利健康、求医、贵人", "advice": "宜置卧室、厨房"},
    "延年": {"quality": "吉", "desc": "利长寿、家庭和睦", "advice": "宜置主卧、客厅"},
    "伏位": {"quality": "中", "desc": "稳定守成，无大吉凶", "advice": "宜置储藏室、卫生间"},
    "祸害": {"quality": "凶", "desc": "有口舌、疾病之忧", "advice": "宜置厕所、储藏室"},
    "六煞": {"quality": "凶", "desc": "六煞损丁，主破财", "advice": "宜置厕所、车库"},
    "五鬼": {"quality": "凶", "desc": "五鬼作祟，主官非灾祸", "advice": "宜置厕所"},
    "绝命": {"quality": "大凶", "desc": "最凶，主重病、绝嗣", "advice": "宜置厕所、车库，切忌卧室"},
}
