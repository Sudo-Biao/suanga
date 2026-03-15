"""
core/date_selection/twelve_officers.py
========================================
十二建除 (Twelve Day Officers) system for professional date selection.

Each day is governed by one of 12 officers based on the relationship
between the month's DiZhi and the day's DiZhi.

Also includes:
  • 二十八宿 simplified lucky/unlucky classification
  • 岁破/月破 (Year/Month Breaker) detection
  • 三煞 (Three Killings) calculation
  • Detailed suitability/avoidance for each purpose × officer
"""
from __future__ import annotations
from datetime import date, timedelta
from typing import Dict, List, Any, Optional

from core.constants import DIZHI_INDEX, TIANGAN_INDEX, TIANGAN_WUXING, DIZHI_WUXING

# ─────────────────────────────────────────────────────────────
# 1. Twelve Officers (十二建除神)
# ─────────────────────────────────────────────────────────────

TWELVE_OFFICERS = ["建", "除", "满", "平", "定", "执", "破", "危", "成", "收", "开", "闭"]

OFFICER_DATA: Dict[str, Dict[str, Any]] = {
    "建": {
        "nature": "吉凶互见",
        "color": "#f39c12",
        "general": "建日主大事开始，有领导力和开拓精神，但也有争讼之象",
        "suitable": ["祭祀", "出行（短途）", "开业（需配吉星）", "求职", "动土（不宜挖掘）"],
        "avoid": ["婚嫁", "入宅", "开仓", "手术"],
        "detail": "建日如建国奠基，主新开端。利启动新事业，但忌婚嫁入宅，有争竞之象。配吉神则诸事顺遂。",
    },
    "除": {
        "nature": "大吉",
        "color": "#27ae60",
        "general": "除日主扫除旧秽，万事更新，大利诸事",
        "suitable": ["婚嫁", "入宅", "动土", "签约", "求医", "沐浴", "修造", "开业"],
        "avoid": ["祭祀（不利鬼神）"],
        "detail": "除日如扫除污秽，主洁净更新。为十二建除中大吉之日，百事皆可为，尤利婚嫁入宅。",
    },
    "满": {
        "nature": "小吉",
        "color": "#3498db",
        "general": "满日主丰盈满足，利收获储藏，但忌轻举妄动",
        "suitable": ["收获", "入库", "储藏", "婚嫁（部分）", "开仓"],
        "avoid": ["出行（易受阻）", "官司（满而溢则破）", "动土"],
        "detail": "满日如杯满盈溢，利守成收藏。婚嫁可用，但宜静不宜动。出行、争讼皆不宜。",
    },
    "平": {
        "nature": "中平",
        "color": "#95a5a6",
        "general": "平日主平稳中庸，无大吉凶，百事平顺",
        "suitable": ["日常事务", "出行", "祭祀", "修缮（小项目）"],
        "avoid": ["大事决策", "婚嫁（平淡）", "投资"],
        "detail": "平日不偏不倚，主平稳。适合处理日常事务，但不宜谋划重大事项，吉凶都不明显。",
    },
    "定": {
        "nature": "大吉",
        "color": "#27ae60",
        "general": "定日主坚定稳固，万事有决断，大利婚嫁签约",
        "suitable": ["婚嫁", "签约", "开业", "入宅", "立约定盟", "祭祀"],
        "avoid": ["官司诉讼（定则难变）", "出行（动中有定）"],
        "detail": "定日如山岳稳固，百事皆有定局。最宜婚嫁签约，有一锤定音之效。官司忌用，因难以变动。",
    },
    "执": {
        "nature": "凶",
        "color": "#e67e22",
        "general": "执日主执行、抓捕，有强制性，利捕猎防盗，不利一般事务",
        "suitable": ["收债", "捕猎", "防盗", "执行法律事务"],
        "avoid": ["婚嫁", "开业", "入宅", "出行（易受阻）", "签约"],
        "detail": "执日有强制执行之象，主抓捕束缚。一般吉事皆忌，利执法、收债之事。商旅婚嫁皆不宜。",
    },
    "破": {
        "nature": "大凶",
        "color": "#e74c3c",
        "general": "破日诸事皆凶，万事破败，为十二建除中最凶之日",
        "suitable": ["拆除旧屋（破而后立）", "治病（破除病气）"],
        "avoid": ["婚嫁", "开业", "入宅", "签约", "动土", "出行（重大行程）"],
        "detail": "破日为十二建除中最凶，主破败毁损。只有拆除破坏性的事情才可用，其他一切吉事皆应回避。",
    },
    "危": {
        "nature": "凶",
        "color": "#c0392b",
        "general": "危日主危险不安，登高远行皆凶",
        "suitable": ["祭祀", "沐浴祈福"],
        "avoid": ["登高（危险）", "出行（远途）", "婚嫁", "动土", "开业"],
        "detail": "危日有高处险阻之象，诸事宜低调谨慎。忌登高、远行、冒险之事。宜在家祈福养身。",
    },
    "成": {
        "nature": "大吉",
        "color": "#27ae60",
        "general": "成日主成就收获，万事皆成，为吉日",
        "suitable": ["婚嫁", "开业", "签约", "入宅", "出行", "求职", "动土", "开仓"],
        "avoid": ["官司诉讼（对方也成）"],
        "detail": "成日万事皆成，是十二建除中最利于办大事的吉日之一。百业皆宜，唯官司诉讼需慎，因双方皆有成就之象。",
    },
    "收": {
        "nature": "小吉",
        "color": "#3498db",
        "general": "收日主收纳聚集，利储蓄收藏，但忌散发外出",
        "suitable": ["收藏", "储蓄", "婚嫁（纳聘礼）", "入仓", "收账"],
        "avoid": ["出行（收而不发）", "开业（收而不展）", "求医（收煞气）"],
        "detail": "收日主聚敛收纳，利守成内敛之事。婚嫁收礼金、收藏珍品皆宜。外出开展新事业不利。",
    },
    "开": {
        "nature": "大吉",
        "color": "#27ae60",
        "general": "开日主开展通达，万事开门，大吉大利",
        "suitable": ["婚嫁", "开业", "出行", "入宅", "签约", "动土", "求财", "求职", "手术"],
        "avoid": ["埋葬（开而不藏）"],
        "detail": "开日诸事皆开，是与成日并列最吉的日子。百事皆宜，门门大开，利一切进取开拓之事。",
    },
    "闭": {
        "nature": "凶",
        "color": "#7f8c8d",
        "general": "闭日主关闭封存，不利开展新事，宜结束旧事",
        "suitable": ["埋葬", "藏物", "封存", "结束项目"],
        "avoid": ["婚嫁", "开业", "出行", "入宅", "签约", "求医（闭而不通）"],
        "detail": "闭日如关门闭户，主封闭终结。只宜做结束性的事情，一切开展性的吉事皆不宜。",
    },
}

# ─────────────────────────────────────────────────────────────
# 2. Calculate Day Officer (十二建除神 计算)
# ─────────────────────────────────────────────────────────────

def get_day_officer(day_dizhi: str, month_dizhi: str) -> str:
    """
    Calculate the twelve officer for a day.
    Month DiZhi = 建, day DiZhi offset from that gives the officer.
    Month sequence: 寅卯辰巳午未申酉戌亥子丑
    """
    month_order = ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"]
    if month_dizhi not in month_order:
        month_idx = DIZHI_INDEX.get(month_dizhi, 0)
        day_idx = DIZHI_INDEX.get(day_dizhi, 0)
    else:
        month_idx = month_order.index(month_dizhi)
        try:
            day_month_idx = month_order.index(day_dizhi)
        except ValueError:
            day_month_idx = DIZHI_INDEX.get(day_dizhi, 0)
            month_idx = month_order.index(month_dizhi) if month_dizhi in month_order else 0
            return TWELVE_OFFICERS[(day_month_idx - month_idx + 12) % 12]

        offset = (day_month_idx - month_idx + 12) % 12
        return TWELVE_OFFICERS[offset]

    offset = (day_idx - month_idx + 12) % 12
    return TWELVE_OFFICERS[offset]

# ─────────────────────────────────────────────────────────────
# 3. 岁破 / 月破 Detection
# ─────────────────────────────────────────────────────────────

from core.constants import LIUCHONG

def get_year_breaker(year: int) -> str:
    """Return the DiZhi that is the Year Breaker (岁破) for a year."""
    from core.calendar.ganzhi import ganzhi_from_index
    idx = (year - 1984) % 60
    _, year_zhi = ganzhi_from_index(idx)
    return LIUCHONG.get(year_zhi, "")

def is_year_breaker_day(day_dizhi: str, year: int) -> bool:
    """Check if a day's DiZhi is the Year Breaker."""
    return day_dizhi == get_year_breaker(year)

def is_month_breaker_day(day_dizhi: str, month_dizhi: str) -> bool:
    """Check if a day's DiZhi is the Month Breaker (月破 = 六冲 with month DiZhi)."""
    return day_dizhi == LIUCHONG.get(month_dizhi, "")

# ─────────────────────────────────────────────────────────────
# 4. 三煞 (Three Killings) Calculation
# ─────────────────────────────────────────────────────────────

# Three killings direction based on year DiZhi group:
# 申子辰年 → 三煞在南 (午方)
# 巳酉丑年 → 三煞在东 (卯方)
# 寅午戌年 → 三煞在北 (子方)
# 亥卯未年 → 三煞在西 (酉方)

THREE_KILLINGS: Dict[str, Dict[str, Any]] = {
    "申子辰": {"direction": "南", "dizhi": ["巳", "午", "未"], "desc": "南方三煞（巳午未方）"},
    "巳酉丑": {"direction": "东", "dizhi": ["寅", "卯", "辰"], "desc": "东方三煞（寅卯辰方）"},
    "寅午戌": {"direction": "北", "dizhi": ["亥", "子", "丑"], "desc": "北方三煞（亥子丑方）"},
    "亥卯未": {"direction": "西", "dizhi": ["申", "酉", "戌"], "desc": "西方三煞（申酉戌方）"},
}

def get_three_killings(year: int) -> Dict[str, Any]:
    """Return Three Killings direction for the year."""
    from core.calendar.ganzhi import ganzhi_from_index
    idx = (year - 1984) % 60
    _, year_zhi = ganzhi_from_index(idx)
    for group, info in THREE_KILLINGS.items():
        if year_zhi in group:
            return {"year_zhi": year_zhi, **info}
    return {"year_zhi": year_zhi, "direction": "未知", "desc": ""}

# ─────────────────────────────────────────────────────────────
# 5. 二十八宿 Simplified (Lucky/Unlucky Classification)
# ─────────────────────────────────────────────────────────────

# 28 lunar mansions cycle with days; simplified lucky/unlucky/neutral
TWENTY_EIGHT_XIUS = [
    "角", "亢", "氐", "房", "心", "尾", "箕",   # 东方青龙
    "斗", "牛", "女", "虚", "危", "室", "壁",   # 北方玄武
    "奎", "娄", "胃", "昴", "毕", "觜", "参",   # 西方白虎
    "井", "鬼", "柳", "星", "张", "翼", "轸",   # 南方朱雀
]

XIU_NATURE: Dict[str, str] = {
    "角": "吉", "亢": "凶", "氐": "凶", "房": "吉", "心": "凶", "尾": "吉", "箕": "吉",
    "斗": "吉", "牛": "凶", "女": "凶", "虚": "凶", "危": "凶", "室": "吉", "壁": "吉",
    "奎": "凶", "娄": "吉", "胃": "吉", "昴": "凶", "毕": "吉", "觜": "凶", "参": "吉",
    "井": "吉", "鬼": "凶", "柳": "凶", "星": "凶", "张": "吉", "翼": "凶", "轸": "吉",
}

def get_day_xiu(target_date: date) -> str:
    """Return the lunar mansion (宿) for a given date (approximate)."""
    # Reference: 2000-01-07 = 虚 (index 10)
    ref = date(2000, 1, 7)
    delta = (target_date - ref).days
    idx = (10 + delta) % 28
    return TWENTY_EIGHT_XIUS[idx]

# ─────────────────────────────────────────────────────────────
# 6. Purpose × Officer Suitability Matrix
# ─────────────────────────────────────────────────────────────

PURPOSE_OFFICER_SUITABILITY: Dict[str, List[str]] = {
    "婚嫁": ["除", "定", "成", "开"],
    "开业": ["除", "定", "成", "开"],
    "动土": ["除", "成", "开", "定"],
    "搬家": ["除", "成", "开"],
    "出行": ["除", "定", "成", "开"],
    "求医": ["除", "开", "成"],
    "祭祀": ["建", "除", "平", "定", "危"],
    "签约": ["定", "成", "开"],
}

PURPOSE_OFFICER_AVOID: Dict[str, List[str]] = {
    "婚嫁": ["破", "执", "危", "闭"],
    "开业": ["破", "执", "闭", "建"],
    "动土": ["破", "闭"],
    "搬家": ["破", "闭", "建"],
    "出行": ["破", "危", "建", "收", "闭"],
    "求医": ["破", "死", "闭"],
    "祭祀": ["执", "破"],
    "签约": ["破", "闭", "执"],
}

def get_officer_suitability(officer: str, purpose: str) -> str:
    """Return '宜用', '可用', '忌用' for officer × purpose."""
    if purpose in PURPOSE_OFFICER_SUITABILITY:
        if officer in PURPOSE_OFFICER_SUITABILITY[purpose]:
            return "宜用"
    if purpose in PURPOSE_OFFICER_AVOID:
        if officer in PURPOSE_OFFICER_AVOID[purpose]:
            return "忌用"
    return "可用"

# ─────────────────────────────────────────────────────────────
# 7. Annotate a Day with Full Officer Analysis
# ─────────────────────────────────────────────────────────────

def annotate_day(
    d: date,
    day_gan: str,
    day_zhi: str,
    month_zhi: str,
    year: int,
    purpose: str,
) -> Dict[str, Any]:
    """Return full day annotation including officer, xiu, breakers."""
    officer = get_day_officer(day_zhi, month_zhi)
    officer_data = OFFICER_DATA.get(officer, {})
    officer_suit = get_officer_suitability(officer, purpose)

    xiu = get_day_xiu(d)
    xiu_nature = XIU_NATURE.get(xiu, "平")

    is_yb = is_year_breaker_day(day_zhi, year)
    is_mb = is_month_breaker_day(day_zhi, month_zhi)

    # Compute day score adjustments from officer
    score_adj = 0
    if officer in ["除", "成", "开", "定"]:
        score_adj = 2
    elif officer in ["破", "执"]:
        score_adj = -2
    elif officer in ["危", "闭"]:
        score_adj = -1
    elif officer in ["满", "收"]:
        score_adj = 0

    # Breakers are always bad
    if is_yb:
        score_adj -= 2
    if is_mb:
        score_adj -= 2

    if xiu_nature == "吉":
        score_adj += 1
    elif xiu_nature == "凶":
        score_adj -= 1

    # Officer suitability adjustment
    if officer_suit == "宜用":
        score_adj += 1
    elif officer_suit == "忌用":
        score_adj -= 1

    return {
        "officer": officer,
        "officer_nature": officer_data.get("nature", "中"),
        "officer_suitable": officer_data.get("suitable", []),
        "officer_avoid": officer_data.get("avoid", []),
        "officer_detail": officer_data.get("detail", ""),
        "officer_suitability_for_purpose": officer_suit,
        "xiu": xiu,
        "xiu_nature": xiu_nature,
        "is_year_breaker": is_yb,
        "is_month_breaker": is_mb,
        "score_adjustment": score_adj,
        "breaker_warning": (
            f"⚠ {'岁破日（冲太岁）' if is_yb else ''}{'月破日' if is_mb else ''}"
            if (is_yb or is_mb) else ""
        ),
    }
