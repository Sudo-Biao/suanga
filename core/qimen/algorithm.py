"""
core/qimen/algorithm.py
=======================
QiMen DunJia (奇门遁甲) Sanyuan Jiuju (三元九局) engine.

Determines:
  • Yang-dun or Yin-dun (阳遁/阴遁)
  • Ju number (局数 1–9)
  • Yuan (元: 上/中/下)
  • Palace layout: star (九星), door (八门), deity (八神), stem (天干)
"""
from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

from core.constants import (
    JIUGONG_POSITIONS, JIUXING, BAMEN, BASHEN, BAMEN_AUSPICIOUS,
    TIANGAN, DIZHI, TIANGAN_INDEX, DIZHI_INDEX,
    hour_to_dizhi,
)
from core.calendar.solar_terms import get_jie_dates


# ─────────────────────────────────────────────────────────────
# 1. Yang/Yin and Ju determination
# ─────────────────────────────────────────────────────────────

# Solar terms that mark boundary of each of the 9 Ju periods
# Within each half-year (冬至→夏至 = Yang, 夏至→冬至 = Yin),
# there are 9 × 5-day periods (候) cycling through Ju 1–9.

# Simplified: determine yang/yin from season (冬至–夏至 = 阳遁, 夏至–冬至 = 阴遁)
# Then estimate Ju number from position within the season.

def _is_yang_dun(dt: datetime) -> bool:
    """
    冬至 to 夏至 = 阳遁 (Yang Dun)
    夏至 to 冬至 = 阴遁 (Yin Dun)
    Approximated using month: Nov-Apr ≈ Yang, May-Oct ≈ Yin.
    """
    # More accurate: use actual solar term dates if available
    from core.calendar.solar_terms import _get_solarterm_dt
    dongzhi = _get_solarterm_dt(dt.year, "冬至") or _get_solarterm_dt(dt.year - 1, "冬至")
    xiazhi  = _get_solarterm_dt(dt.year, "夏至")

    if dongzhi and xiazhi:
        if dongzhi <= dt < xiazhi:
            return True      # 冬至 → 夏至 = 阳遁
        return False         # 夏至 → 冬至 = 阴遁

    # Fallback: month-based
    return dt.month in (11, 12, 1, 2, 3, 4)


def _estimate_ju_number(dt: datetime, yang_dun: bool) -> int:
    """
    Estimate the Ju number (1–9) for the given datetime.
    Each Jie-qi (节气) starts a new cycle; within a Jie-qi the day
    advances through sub-cycles. We use a simplified table.
    """
    # For each Jie solar term, the starting Ju is defined by classical tables.
    # 阳遁: 冬至1 小寒7 大寒4 立春8 雨水5 惊蛰2 春分9 清明6 谷雨3
    #        立夏7 小满4 芒种1
    # 阴遁: 夏至9 小暑3 大暑6 立秋2 处暑5 白露8 秋分1 寒露4 霜降7
    #        立冬3 小雪6 大雪9

    YANG_JU: Dict[str, int] = {
        "冬至": 1, "小寒": 7, "大寒": 4, "立春": 8, "雨水": 5,
        "惊蛰": 2, "春分": 9, "清明": 6, "谷雨": 3,
        "立夏": 7, "小满": 4, "芒种": 1,
    }
    YIN_JU: Dict[str, int] = {
        "夏至": 9, "小暑": 3, "大暑": 6, "立秋": 2, "处暑": 5,
        "白露": 8, "秋分": 1, "寒露": 4, "霜降": 7,
        "立冬": 3, "小雪": 6, "大雪": 9,
    }

    table = YANG_JU if yang_dun else YIN_JU

    from core.calendar.solar_terms import SOLAR_TERM_NAMES, _get_solarterm_dt

    # Find the most recent solar term
    best_dt: Optional[datetime] = None
    best_ju: int = 1

    for yr in (dt.year - 1, dt.year):
        for name in SOLAR_TERM_NAMES:
            if name not in table:
                continue
            st_dt = _get_solarterm_dt(yr, name)
            if st_dt and st_dt <= dt:
                if best_dt is None or st_dt > best_dt:
                    best_dt = st_dt
                    best_ju = table[name]

    if best_dt is None:
        return 1

    # Within a 5-day 候, advance by (day_offset // 5) % 9
    day_offset = (dt.date() - best_dt.date()).days
    direction = 1 if yang_dun else -1
    ju = ((best_ju - 1) + direction * (day_offset // 5)) % 9 + 1
    return ju


# ─────────────────────────────────────────────────────────────
# 2. Palace layout (布局)
# ─────────────────────────────────────────────────────────────

# Luoshu (洛书) positions and their natural order index:
# 4 9 2
# 3 5 7
# 8 1 6
# Reading order: 1(N/坎) 2(SW/坤) 3(E/震) 4(SE/巽) 5(C/中)
#                6(NW/乾) 7(W/兑) 8(NE/艮) 9(S/离)

# Palace position in the 3x3 grid (row, col, 0-based) for display
PALACE_GRID: Dict[int, Tuple[int, int]] = {
    4: (0,0), 9: (0,1), 2: (0,2),
    3: (1,0), 5: (1,1), 7: (1,2),
    8: (2,0), 1: (2,1), 6: (2,2),
}

# Yang-dun: stars rotate clockwise (顺飞) starting from position of Ju
# Yin-dun:  stars rotate counter-clockwise (逆飞)
# Sequence of Luoshu positions for clockwise vs counter-clockwise:
YANG_SEQUENCE = [1, 2, 3, 4, 5, 6, 7, 8, 9]   # clockwise Luoshu order
YIN_SEQUENCE  = [9, 8, 7, 6, 5, 4, 3, 2, 1]

# 九星 natural positions (坎1宫 = 天蓬, etc.)
STAR_HOME: Dict[int, str] = {
    1: "天蓬", 2: "天芮", 3: "天冲", 4: "天辅",
    5: "天禽", 6: "天心", 7: "天柱", 8: "天任", 9: "天英",
}

# 八门 natural positions
DOOR_HOME: Dict[int, str] = {
    1: "休门", 2: "死门", 3: "伤门", 4: "杜门",
    5: "——",   6: "开门", 7: "惊门", 8: "生门", 9: "景门",
}

# 八神 rotate with hour stem cycle (simplified: fixed for now)
DEITY_ORDER = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]


def _fly_layout(ju: int, yang_dun: bool) -> Dict[int, Dict[str, str]]:
    """
    Calculate the positions of all 九星 and 八门 for a given Ju.

    Returns dict keyed by Luoshu position (1–9):
        {pos: {"star": str, "door": str, "deity": str}}
    """
    sequence = YANG_SEQUENCE if yang_dun else YIN_SEQUENCE
    # The 值符/天禽 star starts at position 5 (中宫), its Ju is the base.
    # For Ju N (阳遁): 天蓬 is at position N; all stars shift relative.
    # Stars: in yang dun, position 1 gets STAR_HOME[Ju], position 2 gets next, etc.

    result: Dict[int, Dict[str, str]] = {}
    for i, pos in enumerate(sequence):
        # Star: offset by (Ju-1) from YANG_SEQUENCE starting index
        star_idx = (i + ju - 1) % 9
        star_name = JIUXING[star_idx]

        # Door: same offset but from natural door positions
        door_name = BAMEN[star_idx]  # doors fly with stars

        # Deity: simplified rotation based on Ju
        deity_idx = (i + ju - 1) % 8
        deity_name = DEITY_ORDER[deity_idx]

        result[pos] = {
            "star":   star_name,
            "door":   door_name,
            "deity":  deity_name,
        }

    return result


def _get_palace_stem(pos: int, ju: int, yang_dun: bool) -> str:
    """
    Assign a TianGan to each palace based on Ju and Yang/Yin.
    Simplified: uses fixed assignment from classical table.
    """
    # The 值符宫 (Duty Palace) holds the hour TianGan.
    # Other palaces hold stems in sequence. Simplified static assignment:
    YANG_STEMS = {1:"壬", 2:"乙", 3:"甲", 4:"辛", 5:"戊", 6:"庚", 7:"丁", 8:"丙", 9:"己"}
    YIN_STEMS  = {1:"戊", 2:"辛", 3:"庚", 4:"丁", 5:"己", 6:"丙", 7:"乙", 8:"壬", 9:"甲"}
    base = YANG_STEMS if yang_dun else YIN_STEMS
    # Rotate stems by (ju - 1) positions
    positions = [1,2,3,4,5,6,7,8,9]
    offset = (ju - 1) % 9
    rotated = positions[offset:] + positions[:offset]
    stem_map = {rotated[i]: base[positions[i]] for i in range(9)}
    return stem_map.get(pos, "戊")


# ─────────────────────────────────────────────────────────────
# 3. Public API
# ─────────────────────────────────────────────────────────────

def calculate_qimen(
    year: int, month: int, day: int, hour: int, minute: int = 0,
    yang_dun_override: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Calculate a full QiMen DunJia layout for the given datetime.
    """
    dt = datetime(year, month, day, hour, minute)

    yang_dun = yang_dun_override if yang_dun_override is not None else _is_yang_dun(dt)
    ju       = _estimate_ju_number(dt, yang_dun)

    layout   = _fly_layout(ju, yang_dun)

    # Determine 值符宫 (旬首天干所在宫) and 值使门 (时干所在宫)
    # Simplified: 值符 = palace with deity "值符"; 值使 = palace with hour stem
    _hour_stem = _get_palace_stem(1, ju, yang_dun)  # will be refined per palace
    _HOUR_STEMS = {1:"子",2:"丑",3:"寅",4:"卯",5:"辰",6:"巳",7:"午",8:"未",9:"申"}

    # 值使门: the palace whose stem matches the hour tiangan
    # Simplified heuristic: first palace containing 戊/壬 is zhishi (hour-related)
    # More precisely: zhishi is always at the position of the current hour branch
    hour = dt.hour
    _HOUR_POS_MAP = {
        23:1, 0:1, 1:1, 2:3, 3:3, 4:3, 5:3, 6:4, 7:4,
        8:9,  9:9, 10:9, 11:2, 12:2, 13:2, 14:8, 15:8,
        16:8, 17:7, 18:7, 19:6, 20:6, 21:1, 22:1,
    }
    zhishi_pos = _HOUR_POS_MAP.get(hour, 1)

    # 值符宫: palace with deity "值符"
    zhifu_pos = 1  # default

    # First pass to find 值符 palace
    for pos in range(1, 10):
        cell = layout[pos]
        if cell.get("deity") == "值符":
            zhifu_pos = pos
            break

    palaces: List[Dict[str, Any]] = []
    for pos in range(1, 10):
        cell = layout[pos]
        stem = _get_palace_stem(pos, ju, yang_dun)
        door = cell["door"]
        auspicious = door in BAMEN_AUSPICIOUS

        palaces.append({
            "position":     pos,
            "palace_name":  JIUGONG_POSITIONS[pos],
            "star":         cell["star"],
            "door":         door,
            "deity":        cell["deity"],
            "stem":         stem,
            "is_auspicious": auspicious,
            "grid":         PALACE_GRID[pos],
            "is_zhifu":     pos == zhifu_pos,
            "is_zhishi":    pos == zhishi_pos,
        })

    auspicious_dirs   = [p["palace_name"] for p in palaces if p["is_auspicious"]]
    inauspicious_dirs = [p["palace_name"] for p in palaces
                         if not p["is_auspicious"] and p["door"] not in ("——",)]

    hour_dz = hour_to_dizhi(hour)

    return {
        "datetime":   dt.isoformat(),
        "ju_type":    "阳遁" if yang_dun else "阴遁",
        "ju_number":  ju,
        "yuan":       _get_yuan(ju),
        "hour_dizhi": hour_dz,
        "palaces":    palaces,
        "auspicious_directions":   auspicious_dirs,
        "inauspicious_directions": inauspicious_dirs,
    }


def _get_yuan(ju: int) -> str:
    if ju in (1, 2, 3):
        return "上元"
    if ju in (4, 5, 6):
        return "中元"
    return "下元"
