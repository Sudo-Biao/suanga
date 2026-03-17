"""
core/date_selection/selector.py  — v3 powered by lunar-python (6tail)
=======================================================================
Uses the authoritative lunar-python library for ALL day calculations:
  * 每日宜忌  (getDayYi / getDayJi)
  * 吉神/凶煞 (getDayJiShen / getDayXiongSha)
  * 黄道黑道  (getDayTianShen / getDayTianShenType)
  * 彭祖百忌  (getPengZuGan / getPengZuZhi)
  * 二十八宿  (getXiu / getXiuLuck)
  * 胎神方位  (getDayPositionTai)
  * 吉神方位  (喜/财/福/阳贵/阴贵)
  * 空亡      (getDayXunKong)
  * 节气      (getJieQi)

Frontend data contract (unchanged):
  day (int), officer, star, score (int), reasons (list[str]),
  ganzhi, weekday, huangdao, tiande, yuede,
  is_year_breaker, is_month_breaker, breaker_warning
"""
from __future__ import annotations
from datetime import date, timedelta
from typing import Dict, List, Any, Optional

from lunar_python import Solar, LunarYear
from core.date_selection.twelve_officers import (
    get_three_killings, OFFICER_DATA,
    PURPOSE_OFFICER_SUITABILITY, PURPOSE_OFFICER_AVOID,
)

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# ─────────────────────────────────────────────────────────────
# 1. Purpose × Yi/Ji mapping
#    We check if the purpose keyword appears in getDayYi/getDayJi
# ─────────────────────────────────────────────────────────────

PURPOSE_YI_KEYWORDS: Dict[str, List[str]] = {
    "婚嫁":  ["嫁娶", "婚嫁", "纳采", "问名"],
    "开业":  ["开市", "开业", "立券", "交易"],
    "动土":  ["动土", "修造", "破土", "竖柱"],
    "搬家":  ["入宅", "移徙", "安床"],
    "出行":  ["出行", "远行"],
    "求医":  ["求医", "治病"],
    "祭祀":  ["祭祀", "祈福"],
    "签约":  ["立券", "交易", "签约"],
    "安床":  ["安床"],
    "剃胎发": ["剃头", "沐浴"],
}

PURPOSE_JI_KEYWORDS: Dict[str, List[str]] = {
    "婚嫁":  ["嫁娶"],
    "开业":  ["开市"],
    "动土":  ["动土", "破土"],
    "搬家":  ["入宅"],
    "出行":  ["出行"],
    "求医":  ["求医"],
    "祭祀":  ["祭祀"],
    "签约":  ["立券", "交易"],
    "安床":  ["安床"],
    "剃胎发": ["剃头"],
}

# ─────────────────────────────────────────────────────────────
# 2. Officer calculation via month branch
# ─────────────────────────────────────────────────────────────

_MONTH_TO_DIZHI = ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"]
_TWELVE_OFFICERS = ["建","除","满","平","定","执","破","危","成","收","开","闭"]
_DIZHI_IDX = {z: i for i, z in enumerate(
    ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
)}

def _get_officer(day_zhi: str, month_zhi: str) -> str:
    mz_list = ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"]
    try:
        m_idx = mz_list.index(month_zhi)
        d_idx = mz_list.index(day_zhi)
    except ValueError:
        return "平"
    return _TWELVE_OFFICERS[(d_idx - m_idx + 12) % 12]

def _get_year_zhi(year: int) -> str:
    from core.calendar.ganzhi import ganzhi_from_index
    _, y_zhi = ganzhi_from_index((year - 1984) % 60)
    return y_zhi

# ─────────────────────────────────────────────────────────────
# 3. Build a single day record
# ─────────────────────────────────────────────────────────────

def _build_day(
    d: date,
    purpose: str,
    month: int,
    month_zhi: str,
    year: int,
    year_zhi: str,
    birth_zhi: Optional[str],
) -> Dict[str, Any]:
    from lunar_python import Solar as LSolar
    from core.constants import LIUCHONG, LIUHE

    sol = LSolar.fromYmd(d.year, d.month, d.day)
    lun = sol.getLunar()

    # ── GanZhi ─────────────────────────────────────────────
    ganzhi  = lun.getDayInGanZhi()
    day_gan = lun.getDayGan()
    day_zhi = lun.getDayZhi()

    # ── 天神 黄道/黑道 ─────────────────────────────────────
    tian_shen      = lun.getDayTianShen()
    tian_shen_type = lun.getDayTianShenType()   # "黄道" | "黑道"
    tian_shen_luck = lun.getDayTianShenLuck()   # "吉" | "凶"
    is_huangdao    = (tian_shen_type == "黄道")

    # ── 宜忌 ───────────────────────────────────────────────
    yi_list  = lun.getDayYi()    # list[str]
    ji_list  = lun.getDayJi()    # list[str]
    ji_shen  = lun.getDayJiShen()   # 吉神 list
    xiong_sha = lun.getDayXiongSha()  # 凶煞 list

    # ── 彭祖百忌 ───────────────────────────────────────────
    peng_zu_gan = lun.getPengZuGan()
    peng_zu_zhi = lun.getPengZuZhi()

    # ── 二十八宿 ───────────────────────────────────────────
    xiu        = lun.getXiu()
    xiu_luck   = lun.getXiuLuck()   # "吉" | "凶" | "平"

    # ── 胎神/吉神方位 ──────────────────────────────────────
    tai_shen    = lun.getDayPositionTai()
    xi_shen     = lun.getDayPositionXiDesc()
    cai_shen    = lun.getDayPositionCaiDesc()
    fu_shen     = lun.getDayPositionFuDesc()
    yang_gui    = lun.getDayPositionYangGuiDesc()

    # ── 空亡 冲 ────────────────────────────────────────────
    xun_kong    = lun.getDayXunKong()
    chong_desc  = lun.getDayChongDesc()
    jie_qi      = lun.getJieQi()

    # ── 纳音 ────────────────────────────────────────────────
    nayin = lun.getDayNaYin()

    # ── 建除十二神 ─────────────────────────────────────────
    officer = _get_officer(day_zhi, month_zhi)
    officer_data = OFFICER_DATA.get(officer, {})
    officer_nature = officer_data.get("nature", "中")
    officer_detail = officer_data.get("detail", "")

    # Purpose × officer suitability
    if purpose in PURPOSE_OFFICER_SUITABILITY and officer in PURPOSE_OFFICER_SUITABILITY[purpose]:
        officer_suit = "宜用"
    elif purpose in PURPOSE_OFFICER_AVOID and officer in PURPOSE_OFFICER_AVOID[purpose]:
        officer_suit = "忌用"
    else:
        officer_suit = "可用"

    # ── 岁破/月破 ──────────────────────────────────────────
    year_break_zhi  = LIUCHONG.get(year_zhi, "")
    month_break_zhi = LIUCHONG.get(month_zhi, "")
    is_yb = (day_zhi == year_break_zhi)
    is_mb = (day_zhi == month_break_zhi)

    # ── 天德/月德 (check if 天德 or 月德 appears in ji_shen) ─
    has_tiande = any("天德" in s for s in ji_shen)
    has_yuede  = any("月德" in s for s in ji_shen)

    # ── 生辰相冲/六合 ──────────────────────────────────────
    birth_clash = bool(birth_zhi and LIUCHONG.get(day_zhi) == birth_zhi)
    birth_he    = bool(birth_zhi and LIUHE.get(day_zhi)    == birth_zhi)

    # ── Purpose宜忌 from lunar-python data ─────────────────
    purpose_yi_kws = PURPOSE_YI_KEYWORDS.get(purpose, [])
    purpose_ji_kws = PURPOSE_JI_KEYWORDS.get(purpose, [])
    in_yi = any(kw in yi_list for kw in purpose_yi_kws)
    in_ji = any(kw in ji_list for kw in purpose_ji_kws)

    # ── Scoring ────────────────────────────────────────────
    score = 0

    # 建除神 (most important)
    if officer_suit == "宜用":   score += 3
    elif officer_suit == "忌用": score -= 3
    else:                        score += 0

    # 黄道黑道
    if is_huangdao:  score += 2
    else:            score -= 1

    # 天德/月德
    if has_tiande: score += 2
    if has_yuede:  score += 1

    # 老黄历宜忌
    if in_yi: score += 2
    if in_ji: score -= 2

    # 二十八宿
    if xiu_luck == "吉":   score += 1
    elif xiu_luck == "凶": score -= 1

    # 岁破/月破 (hard penalties)
    if is_yb: score -= 4
    if is_mb: score -= 3

    # 生辰
    if birth_clash: score -= 2
    if birth_he:    score += 1

    # ── Reasons ────────────────────────────────────────────
    reasons: List[str] = []

    # 1. 建除神
    if officer_suit == "宜用":
        reasons.append(f"宜用{officer}日 — {officer_detail[:35] if officer_detail else officer_nature}")
    elif officer_suit == "忌用":
        reasons.append(f"忌用{officer}日 — {officer_detail[:35] if officer_detail else officer_nature}")
    else:
        reasons.append(f"{officer}日（{officer_nature}）")

    # 2. 黄道/黑道
    if is_huangdao:
        reasons.append(f"黄道吉日「{tian_shen}」临，{', '.join(ji_shen[:3]) if ji_shen else '诸事皆宜'}")
    else:
        reasons.append(f"黑道凶日「{tian_shen}」，凶煞：{', '.join(xiong_sha[:3]) if xiong_sha else '宜低调'}")

    # 3. 老黄历宜忌
    if yi_list:
        reasons.append(f"老黄历宜：{'、'.join(yi_list[:5])}")
    if ji_list:
        reasons.append(f"老黄历忌：{'、'.join(ji_list[:4])}")

    # 4. 彭祖百忌
    reasons.append(f"彭祖百忌 — {peng_zu_gan}；{peng_zu_zhi}")

    # 5. 天德/月德
    if has_tiande and has_yuede:
        reasons.append("天德月德双贵临日，百煞皆化")
    elif has_tiande:
        reasons.append("天德贵神临日，可化诸煞")
    elif has_yuede:
        reasons.append("月德贵神临日")

    # 6. 岁破/月破
    if is_yb:
        reasons.append(f"⚠ 岁破日（冲太岁{year_zhi}），百事大忌")
    if is_mb:
        reasons.append(f"⚠ 月破日（冲月建{month_zhi}），诸事受损")

    # 7. 二十八宿
    reasons.append(f"{xiu_luck}宿「{xiu}」值日，冲{chong_desc}，空亡{xun_kong}")

    # 8. 节气提示
    if jie_qi:
        reasons.append(f"今日节气：{jie_qi}")

    # 9. 胎神 + 吉神方位
    reasons.append(f"喜神{xi_shen}，财神{cai_shen}，福神{fu_shen}，阳贵{yang_gui}")
    if tai_shen:
        reasons.append(f"胎神占{tai_shen}，孕妇忌动此处")

    # 10. 生辰
    if birth_clash:
        reasons.append(f"⚠ 日支{day_zhi}冲本命{birth_zhi}，个人不宜")
    elif birth_he:
        reasons.append(f"日支{day_zhi}与本命{birth_zhi}六合，个人加持")

    breaker_warning = ""
    if is_yb or is_mb:
        parts = []
        if is_yb: parts.append("岁破，冲太岁")
        if is_mb: parts.append("月破，诸事忌")
        breaker_warning = "⚠ " + "；".join(parts)

    return {
        "day":             d.day,
        "date":            d.isoformat(),
        "weekday":         WEEKDAYS[d.weekday()],
        "ganzhi":          ganzhi,
        "nayin":           nayin,
        "officer":         officer,
        "officer_nature":  officer_nature,
        "officer_detail":  officer_detail,
        "star":            xiu,
        "star_nature":     xiu_luck,
        "score":           score,
        "reasons":         reasons,
        "huangdao":        is_huangdao,
        "day_god":         tian_shen,
        "day_god_type":    tian_shen_type,
        "ji_shen":         ji_shen,
        "xiong_sha":       xiong_sha,
        "yi":              yi_list,
        "ji":              ji_list,
        "peng_zu_gan":     peng_zu_gan,
        "peng_zu_zhi":     peng_zu_zhi,
        "tai_shen":        tai_shen,
        "xi_shen":         xi_shen,
        "cai_shen":        cai_shen,
        "fu_shen":         fu_shen,
        "yang_gui":        yang_gui,
        "xun_kong":        xun_kong,
        "chong":           chong_desc,
        "jie_qi":          jie_qi,
        "tiande":          has_tiande,
        "yuede":           has_yuede,
        "is_year_breaker": is_yb,
        "is_month_breaker": is_mb,
        "breaker_warning": breaker_warning,
        "notes": (
            f"{ganzhi}日{tian_shen_type}"
            f"{'【天德】' if has_tiande else ''}"
            f"{'【月德】' if has_yuede else ''}"
            f"{'【岁破】' if is_yb else ''}"
            f"{'【月破】' if is_mb else ''}"
            f"{'（节气：'+jie_qi+'）' if jie_qi else ''}"
        ),
    }

# ─────────────────────────────────────────────────────────────
# 4. Public API
# ─────────────────────────────────────────────────────────────

def select_dates(
    purpose: str,
    year: int,
    month: int,
    birth_year: Optional[int] = None,
    birth_month: Optional[int] = None,
    birth_day: Optional[int] = None,
) -> Dict[str, Any]:
    month_zhi = _MONTH_TO_DIZHI[(month - 1) % 12]
    year_zhi  = _get_year_zhi(year)

    birth_zhi: Optional[str] = None
    if birth_year and birth_month and birth_day:
        try:
            from core.calendar.ganzhi import ganzhi_from_index, _REF_DATE, _REF_DAY_IDX
            from datetime import date as _date
            bd = _date(birth_year, birth_month, birth_day)
            bd_delta = (bd - _REF_DATE).days
            _, birth_zhi = ganzhi_from_index((_REF_DAY_IDX + bd_delta) % 60)
        except Exception:
            pass

    start = date(year, month, 1)
    end   = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)

    all_days: List[Dict[str, Any]] = []
    d = start
    while d < end:
        rec = _build_day(d, purpose, month, month_zhi, year, year_zhi, birth_zhi)
        all_days.append(rec)
        d += timedelta(days=1)

    auspicious   = [x for x in all_days if x["score"] >= 3]
    inauspicious = [x for x in all_days if x["score"] <= -2]
    best_days    = sorted(auspicious, key=lambda x: x["score"], reverse=True)[:3]

    tk = get_three_killings(year)
    three_killings_str = f"{tk.get('direction','未知')}方（{tk.get('desc','')}）"

    # Get solar terms this month via lunar-python
    try:
        ly = LunarYear.fromYear(year)
        jq_jd = ly.getJieQiJulianDays()
        from lunar_python import Solar as LSolar
        JIE_QI_NAMES = [
            "小寒","大寒","立春","雨水","惊蛰","春分","清明","谷雨",
            "立夏","小满","芒种","夏至","小暑","大暑","立秋","处暑",
            "白露","秋分","寒露","霜降","立冬","小雪","大雪","冬至",
        ]
        month_jieqi = []
        for i, jd in enumerate(jq_jd):
            if i >= len(JIE_QI_NAMES): break
            s = LSolar.fromJulianDay(jd)
            if s.getYear() == year and s.getMonth() == month:
                month_jieqi.append(f"{JIE_QI_NAMES[i]} {s.toYmd()}")
    except Exception:
        month_jieqi = []

    return {
        "purpose":           purpose,
        "month_summary":     f"{year}年{month}月 · {purpose}择日（老黄历 lunar-python 驱动）",
        "auspicious_days":   auspicious,
        "best_days":         best_days,
        "inauspicious_days": inauspicious,
        "all_days":          all_days,
        "three_killings":    three_killings_str,
        "month_jieqi":       month_jieqi,
        "year_zhi":          year_zhi,
        "month_zhi":         month_zhi,
    }
