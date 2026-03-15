"""
core/fengshui/flying_stars.py
===============================
玄空飞星风水 (Xuan Kong Flying Stars FengShui)

Implements:
  • Annual flying star calculation (年飞星) for any year
  • Nine star (九宫飞星) meanings and interactions
  • Auspicious / inauspicious sector identification
  • Room placement recommendations
  • Personal lucky direction (文昌/催财/桃花/健康位)
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple

# ─────────────────────────────────────────────────────────────
# 1. Nine Star (九星) Properties
# ─────────────────────────────────────────────────────────────

NINE_STARS: Dict[int, Dict[str, Any]] = {
    1: {
        "name": "一白贪狼星", "element": "水", "nature": "吉",
        "color": "#3498db", "palace": "坎",
        "meaning": "主桃花、文学、学业、贵人、口才",
        "room_use": ["书房", "主卧（单身或学生）"],
        "career": "利文学、外交、贸易、演讲",
        "health": "注意肾脏、泌尿系统",
        "annual_2026": "流年运势中等，利文学求职",
    },
    2: {
        "name": "二黑巨门星", "element": "土", "nature": "大凶",
        "color": "#e74c3c", "palace": "坤",
        "meaning": "主疾病、孕产风险、官非口舌",
        "room_use": ["厕所", "储物室（避免卧室厨房）"],
        "career": "此宫位不利工作，防官非",
        "health": "脾胃、妇科（女性）、腹部疾病",
        "annual_2026": "二黑病符，此方位放铜葫芦化煞",
        "remedy": "铜葫芦、六帝钱、铜钟化煞",
    },
    3: {
        "name": "三碧禄存星", "element": "木", "nature": "凶",
        "color": "#e67e22", "palace": "震",
        "meaning": "主口舌是非、争吵、官司",
        "room_use": ["厕所", "厨房（火克木，化解口舌）"],
        "career": "防口舌纷争，合同纠纷",
        "health": "肝胆、神经系统、肢体受伤",
        "annual_2026": "三碧蚩尤，此方位易有口角官非",
        "remedy": "红色物品化解（火克木）",
    },
    4: {
        "name": "四绿文昌星", "element": "木", "nature": "吉",
        "color": "#27ae60", "palace": "巽",
        "meaning": "主文学、考试、桃花、聪明才智",
        "room_use": ["书房", "儿童房", "办公室"],
        "career": "利文职、学术、写作、教育",
        "health": "注意肝胆，整体较平稳",
        "annual_2026": "四绿文昌，此方位学习读书大吉",
    },
    5: {
        "name": "五黄廉贞星", "element": "土", "nature": "大凶",
        "color": "#c0392b", "palace": "中",
        "meaning": "主灾祸、疾病、死亡、破财，最凶之星",
        "room_use": ["避免一切活动，尤其忌动土"],
        "career": "此方位开工动土必出大事",
        "health": "五脏皆有风险，尤其重病",
        "annual_2026": "五黄飞入XX宫（见年飞星表），此方绝对不可动土",
        "remedy": "六帝钱、铜风铃、葫芦化煞（最重要）",
    },
    6: {
        "name": "六白武曲星", "element": "金", "nature": "吉",
        "color": "#f39c12", "palace": "乾",
        "meaning": "主武职、权力、偏财、贵人",
        "room_use": ["主卧（当家者）", "书房", "客厅主位"],
        "career": "利军警、管理、投资、武职",
        "health": "头部、肺部注意",
        "annual_2026": "六白武曲当旺，利偏财求财",
    },
    7: {
        "name": "七赤破军星", "element": "金", "nature": "凶",
        "color": "#9b59b6", "palace": "兑",
        "meaning": "主口舌、血光、盗贼、破财",
        "room_use": ["厕所", "储物室"],
        "career": "防被骗、合同纠纷、口舌",
        "health": "肺部、皮肤、手术",
        "annual_2026": "七赤入中，防口舌血光",
        "remedy": "蓝色水晶球、水种植物化解",
    },
    8: {
        "name": "八白左辅星", "element": "土", "nature": "大吉",
        "color": "#f1c40f", "palace": "艮",
        "meaning": "主财帛、房产、旺丁旺财，当运最吉之星",
        "room_use": ["主卧", "客厅", "财位（放招财物品）"],
        "career": "最利置业、投资、经营",
        "health": "脾胃平稳，整体健康",
        "annual_2026": "八白正当运，旺丁旺财，此方位为财位",
    },
    9: {
        "name": "九紫右弼星", "element": "火", "nature": "吉",
        "color": "#e74c3c", "palace": "离",
        "meaning": "主喜庆、婚姻、名声、贵人",
        "room_use": ["客厅", "主卧（夫妻）"],
        "career": "利名声、喜庆、升迁、婚事",
        "health": "心脑血管、眼睛注意",
        "annual_2026": "九紫入宅，主喜庆连连，婚嫁喜事",
    },
}

# ─────────────────────────────────────────────────────────────
# 2. Annual Flying Star Chart Calculation (年飞星布局)
#    The annual center star cycles: 1→9→8→7→6→5→4→3→2→1
#    Regression: 2024=三碧(3), 2025=二黑(2), 2026=一白(1), 2027=九紫(9)
# ─────────────────────────────────────────────────────────────

# Reference: year 1984 = center star 9 (九紫)
# Each year: center star = (9 - (year - 1984)) % 9, or 9 if 0
def get_annual_center_star(year: int) -> int:
    """Return the center palace star number for the given year."""
    star = (9 - (year - 1984) % 9) % 9
    return star if star != 0 else 9

# Luoshu (洛书) natural positions for stars 1-9:
# 4 9 2
# 3 5 7
# 8 1 6
# Position order (luoshu): pos 1→S, 2→SW, 3→E, 4→SE, 5→C, 6→NW, 7→W, 8→NE, 9→N
LUOSHU_NATURAL: Dict[int, str] = {
    1: "北",   2: "西南", 3: "东",
    4: "东南", 5: "中",   6: "西北",
    7: "西",   8: "东北", 9: "南",
}

DIRECTION_TO_LUOSHU: Dict[str, int] = {v: k for k, v in LUOSHU_NATURAL.items()}

# Yang (forward) flying order for annual stars:
# Center → then fly in luoshu sequence 5→6→7→8→9→1→2→3→4
YANG_FLY_ORDER = [5, 6, 7, 8, 9, 1, 2, 3, 4]  # palace position order

def calculate_annual_flying_stars(year: int) -> Dict[str, Any]:
    """
    Calculate the nine-palace flying star chart for a year.
    Returns a dict with direction → star number mapping.
    """
    center = get_annual_center_star(year)

    # Stars fly in yang order starting from center's natural position
    # Each palace position gets a star by rotating from center
    palace_to_star: Dict[int, int] = {}
    for i, palace_pos in enumerate(YANG_FLY_ORDER):
        star = ((center - 1 + i) % 9) + 1
        palace_to_star[palace_pos] = star

    # Build direction → star mapping
    direction_stars: Dict[str, Dict[str, Any]] = {}
    for palace_pos, star_num in palace_to_star.items():
        direction = LUOSHU_NATURAL[palace_pos]
        star_info = NINE_STARS[star_num].copy()
        direction_stars[direction] = {
            "star_num": star_num,
            "direction": direction,
            **star_info,
        }

    # Identify special positions for this year
    auspicious = [d for d, s in direction_stars.items() if s["nature"] in ("吉", "大吉")]
    inauspicious = [d for d, s in direction_stars.items() if s["nature"] in ("凶", "大凶")]
    five_yellow = next((d for d, s in direction_stars.items() if s["star_num"] == 5), "")
    two_black = next((d for d, s in direction_stars.items() if s["star_num"] == 2), "")
    eight_white = next((d for d, s in direction_stars.items() if s["star_num"] == 8), "")
    four_green = next((d for d, s in direction_stars.items() if s["star_num"] == 4), "")
    one_white = next((d for d, s in direction_stars.items() if s["star_num"] == 1), "")

    return {
        "year": year,
        "center_star": center,
        "center_star_name": NINE_STARS[center]["name"],
        "direction_stars": direction_stars,
        "auspicious_directions": auspicious,
        "inauspicious_directions": inauspicious,
        "five_yellow_direction": five_yellow,
        "two_black_direction": two_black,
        "wealth_direction": eight_white,      # 八白当运为财位
        "study_direction": four_green,         # 四绿文昌为学位
        "romance_direction": one_white,        # 一白桃花
        "annual_summary": _build_annual_summary(year, center, eight_white, five_yellow, four_green),
    }

def _build_annual_summary(year: int, center: int, wealth_dir: str, danger_dir: str, study_dir: str) -> str:
    center_name = NINE_STARS[center]["name"]
    return (
        f"{year}年，{center_name}入中宫。"
        f"财位在{wealth_dir}方（八白旺财），宜在此方摆放招财物品；"
        f"文昌位在{study_dir}方（四绿文昌），宜在此方设书房；"
        f"五黄在{danger_dir}方，此方绝对禁止动土装修，宜放六帝钱化煞；"
        f"二黑病符位需摆铜葫芦化病气。"
    )

# ─────────────────────────────────────────────────────────────
# 3. Personal Lucky Directions (个人吉方)
#    Based on Ming Gua and natal year
# ─────────────────────────────────────────────────────────────

# Ming Gua → 4 lucky directions (生气/天医/延年/伏位) and 4 unlucky
MING_GUA_LUCKY: Dict[int, Dict[str, Any]] = {
    1: {
        "shengqi": "东南", "tianyi": "东", "niannian": "南", "fuwei": "北",
        "jueming": "西", "wugui": "西北", "liusha": "东北", "huohai": "西南",
        "best_bed_dir": "东南（生气）", "best_desk_dir": "东（天医）",
        "wealth_spot": "东南角", "health_spot": "东方", "romance_spot": "南方",
    },
    2: {
        "shengqi": "西北", "tianyi": "西南", "niannian": "东北", "fuwei": "西南",
        "jueming": "东", "wugui": "东南", "liusha": "南", "huohai": "北",
        "best_bed_dir": "西北（生气）", "best_desk_dir": "西南（天医）",
        "wealth_spot": "西北角", "health_spot": "西南方", "romance_spot": "东北方",
    },
    3: {
        "shengqi": "南", "tianyi": "北", "niannian": "东南", "fuwei": "东",
        "jueming": "西南", "wugui": "东北", "liusha": "西北", "huohai": "西",
        "best_bed_dir": "南（生气）", "best_desk_dir": "北（天医）",
        "wealth_spot": "南方", "health_spot": "北方", "romance_spot": "东南方",
    },
    4: {
        "shengqi": "北", "tianyi": "南", "niannian": "东", "fuwei": "东南",
        "jueming": "西北", "wugui": "西", "liusha": "西南", "huohai": "东北",
        "best_bed_dir": "北（生气）", "best_desk_dir": "南（天医）",
        "wealth_spot": "北方", "health_spot": "南方", "romance_spot": "东方",
    },
    6: {
        "shengqi": "西南", "tianyi": "东北", "niannian": "西", "fuwei": "西北",
        "jueming": "南", "wugui": "北", "liusha": "东", "huohai": "东南",
        "best_bed_dir": "西南（生气）", "best_desk_dir": "东北（天医）",
        "wealth_spot": "西南角", "health_spot": "东北方", "romance_spot": "西方",
    },
    7: {
        "shengqi": "东北", "tianyi": "西", "niannian": "西北", "fuwei": "西",
        "jueming": "东", "wugui": "南", "liusha": "东南", "huohai": "北",
        "best_bed_dir": "东北（生气）", "best_desk_dir": "西（天医）",
        "wealth_spot": "东北角", "health_spot": "西方", "romance_spot": "西北方",
    },
    8: {
        "shengqi": "西", "tianyi": "西北", "niannian": "西南", "fuwei": "东北",
        "jueming": "东南", "wugui": "东", "liusha": "南", "huohai": "北",
        "best_bed_dir": "西（生气）", "best_desk_dir": "西北（天医）",
        "wealth_spot": "西方", "health_spot": "西北方", "romance_spot": "西南方",
    },
    9: {
        "shengqi": "东", "tianyi": "东南", "niannian": "北", "fuwei": "南",
        "jueming": "西南", "wugui": "西", "liusha": "西北", "huohai": "东北",
        "best_bed_dir": "东（生气）", "best_desk_dir": "东南（天医）",
        "wealth_spot": "东方", "health_spot": "东南方", "romance_spot": "北方",
    },
}

def get_personal_directions(ming_gua: int) -> Dict[str, Any]:
    """Return personal lucky and unlucky directions for a Ming Gua."""
    info = MING_GUA_LUCKY.get(ming_gua, MING_GUA_LUCKY[1])
    return {
        "ming_gua": ming_gua,
        "shengqi": {"direction": info["shengqi"], "meaning": "生气位（最旺财丁，宜主卧门向）"},
        "tianyi": {"direction": info["tianyi"], "meaning": "天医位（利健康求医，宜卧室）"},
        "niannian": {"direction": info["niannian"], "meaning": "延年位（利婚姻家庭，宜客厅）"},
        "fuwei": {"direction": info["fuwei"], "meaning": "伏位（稳定守成，宜储藏）"},
        "jueming": {"direction": info["jueming"], "meaning": "绝命位（最凶，忌卧室厨房）"},
        "wugui": {"direction": info["wugui"], "meaning": "五鬼位（官非灾祸，忌主要房间）"},
        "liusha": {"direction": info["liusha"], "meaning": "六煞位（破财损丁，忌财位）"},
        "huohai": {"direction": info["huohai"], "meaning": "祸害位（口舌疾病，忌卧室）"},
        "best_bed_dir": info.get("best_bed_dir", ""),
        "best_desk_dir": info.get("best_desk_dir", ""),
        "wealth_spot": info.get("wealth_spot", ""),
        "health_spot": info.get("health_spot", ""),
        "romance_spot": info.get("romance_spot", ""),
        "room_advice": [
            f"主卧建议朝向{info.get('best_bed_dir','')}，最有利于休息和健康",
            f"书桌/工作台面朝{info.get('best_desk_dir','')}，有助提升专注力和贵人运",
            f"财位在{info.get('wealth_spot','')}，宜摆放招财貔貅、绿植或流水盆",
            f"忌在绝命位（{info.get('jueming','')}）设置主卧或厨房",
        ],
    }

# ─────────────────────────────────────────────────────────────
# 4. Combined Analysis (合参八宅 + 飞星)
# ─────────────────────────────────────────────────────────────

def comprehensive_fengshui_analysis(
    ming_gua: int,
    house_gua: int,
    year: int,
    house_facing: str,
) -> Dict[str, Any]:
    """Combine Eight Mansion + Flying Stars + Personal Directions."""
    annual = calculate_annual_flying_stars(year)
    personal = get_personal_directions(ming_gua)

    # Cross-reference: which personal lucky directions also have good annual stars?
    lucky_dir = personal["shengqi"]["direction"]
    annual_star_at_lucky = annual["direction_stars"].get(lucky_dir, {})

    combined_wealth = personal.get("wealth_spot", "")
    annual_wealth = annual.get("wealth_direction", "")

    return {
        "annual_chart": annual,
        "personal_directions": personal,
        "year": year,
        "combined_advice": _build_combined_advice(
            ming_gua, annual, personal, annual_star_at_lucky, combined_wealth, annual_wealth
        ),
    }

def _build_combined_advice(
    ming_gua: int, annual: Dict, personal: Dict,
    annual_at_lucky: Dict, personal_wealth: str, annual_wealth: str,
) -> List[str]:
    advice = []

    # Wealth
    if personal_wealth == annual_wealth:
        advice.append(f"✦ 大利财运：个人生气位（{personal_wealth}）与年飞星财位重合，是难得的双重旺财方位！强烈建议在此方摆放招财物品或设置财位。")
    else:
        advice.append(f"◆ 个人财位在{personal_wealth}方（生气），年飞星财位在{annual_wealth}方（八白），两者兼顾最佳。")

    # Five Yellow warning
    fy_dir = annual.get("five_yellow_direction", "")
    if fy_dir:
        advice.append(f"⚠ 重要警示：{annual.get('year','')}年五黄凶星飞临{fy_dir}方，此方位绝对禁止动土装修，需放六帝钱或铜葫芦化煞。")

    # Study direction
    sd = annual.get("study_direction", "")
    pd = personal.get("tianyi", {}).get("direction", "")
    if sd:
        advice.append(f"◆ 文昌学位在{sd}方（四绿文昌星），学生建议在此方向学习，或将书桌朝向此方。")

    # Romance
    romance = personal.get("romance_spot", "")
    if romance:
        advice.append(f"◆ 桃花情缘位在{romance}方，单身者可在此方摆放粉晶、鲜花以催旺感情。")

    return advice
