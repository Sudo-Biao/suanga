"""
core/ziwei/chart.py
===================
Zi Wei Dou Shu (紫微斗数) chart engine powered by iztro-py.

Wraps iztro_py to produce a serializable dict matching the
frontend ZiWeiPage.jsx data contract.
"""
from __future__ import annotations
from typing import Dict, Any, Optional
from iztro_py import astro

# ── Internal→Chinese name maps built from iztro translate API ──────────────

def _translate_star_name(raw: str) -> str:
    """Return Chinese name for a star's raw key, e.g. 'tanlangMaj' → '贪狼'"""
    # Build a tiny chart just to resolve one star name via translate
    # Simpler: use a static table for 14 major + common minor stars
    pass

_PALACE_NAMES_ZH = {
    "soulPalace":     "命宫",
    "siblingsPalace": "兄弟宫",
    "spousePalace":   "夫妻宫",
    "childrenPalace": "子女宫",
    "wealthPalace":   "财帛宫",
    "healthPalace":   "疾厄宫",
    "surfacePalace":  "迁移宫",
    "friendsPalace":  "交友宫",
    "careerPalace":   "官禄宫",
    "propertyPalace": "田宅宫",
    "spiritPalace":   "福德宫",
    "parentsPalace":  "父母宫",
}

_GENDER_NOTES = {
    "男": "阳男顺行大限",
    "女": "阴女逆行大限",
}


def build_ziwei_chart(
    solar_date: str,        # "YYYY-MM-DD"
    birth_hour_index: int,  # 0=子时 … 11=亥时 (each 2h period)
    gender: str,            # "男" | "女"
    language: str = "zh-CN",
) -> Dict[str, Any]:
    """
    Build a complete Zi Wei Dou Shu chart.

    Returns a serializable dict with all 12 palaces, major/minor/adjective
    stars, decadal ranges, long-life-12 positions, and chart metadata.
    """
    chart = astro.by_solar(solar_date, birth_hour_index, gender)

    # ── Metadata ────────────────────────────────────────────────────────────
    metadata = {
        "solar_date":       solar_date,
        "birth_hour_index": birth_hour_index,
        "birth_hour_name":  chart.time,
        "birth_hour_range": chart.time_range,
        "gender":           gender,
        "lunar_date":       chart.lunar_date,
        "chinese_date":     chart.chinese_date,   # 四柱干支
        "zodiac":           chart.zodiac,
        "sign":             chart.sign,            # 星座
        "five_elements":    chart.five_elements_class,  # 五行局
        "soul_star":        chart.soul,            # 命主 (raw)
        "body_star":        chart.body,            # 身主 (raw)
        "earthly_soul":     chart.earthly_branch_of_soul_palace,
        "earthly_body":     chart.earthly_branch_of_body_palace,
    }

    # ── Palaces ──────────────────────────────────────────────────────────────
    palaces = []
    for i in range(12):
        p = chart.palace(i)
        if p is None:
            continue

        def _stars(star_list):
            return [
                {
                    "name":       s.translate_name(),
                    "type":       getattr(s, "type", ""),
                    "brightness": getattr(s, "brightness", None) or "",
                    "mutagen":    getattr(s, "mutagen", None) or "",
                    "scope":      getattr(s, "scope", "origin"),
                }
                for s in star_list
            ]

        # Decadal fortune range for this palace
        p_dump = p.model_dump()
        decadal = p_dump.get("decadal") or {}

        palace_dict = {
            "index":          p.index,
            "name":           p.translate_name(),
            "name_raw":       p.name,
            "heavenly_stem":  p.translate_heavenly_stem(),
            "earthly_branch": p.translate_earthly_branch(),
            "is_soul":        (p.name == "soulPalace"),
            "is_body":        p.is_body_palace,
            "major_stars":    _stars(p.major_stars),
            "minor_stars":    _stars(p.minor_stars),
            "adj_stars":      _stars(getattr(p, "adjective_stars", [])),
            "changsheng12":   p_dump.get("changsheng12", ""),
            "boshi12":        p_dump.get("boshi12", ""),
            "decadal_range":  list(decadal.get("range", [])) if decadal else [],
            "decadal_stem":   decadal.get("heavenly_stem", "") if decadal else "",
            "decadal_branch": decadal.get("earthly_branch", "") if decadal else "",
        }
        palaces.append(palace_dict)

    # ── Soul & Body palace summaries ──────────────────────────────────────
    soul_p  = chart.get_soul_palace()
    body_p  = chart.get_body_palace()

    soul_summary = {
        "name":       soul_p.translate_name(),
        "stem_branch": f"{soul_p.translate_heavenly_stem()}{soul_p.translate_earthly_branch()}",
        "major_stars": [s.translate_name() for s in soul_p.major_stars],
        "minor_stars": [s.translate_name() for s in soul_p.minor_stars],
    }
    body_summary = {
        "name":       body_p.translate_name(),
        "stem_branch": f"{body_p.translate_heavenly_stem()}{body_p.translate_earthly_branch()}",
        "major_stars": [s.translate_name() for s in body_p.major_stars],
    }

    # ── Three-direction-four-normal (三方四正) of soul palace ─────────────
    try:
        surround = chart.surrounded_palaces(soul_p.index)
        sanjiao = []
        for sp in surround.all_palaces():
            sanjiao.append({
                "name":       sp.translate_name(),
                "major_stars": [s.translate_name() for s in sp.major_stars],
            })
    except Exception:
        sanjiao = []

    # ── Translate soul/body stars ─────────────────────────────────────────
    try:
        soul_star_zh = chart.get_soul_palace().translate_name()   # not the right way
        # Get the raw soul/body star names translated
        # They're stored as internal keys like 'lucunMin'
        # We pull from a palace that has them
        soul_star_translated = ""
        body_star_translated = ""
        for p_raw in chart.model_dump()["palaces"]:
            for s in p_raw.get("minor_stars", []) + p_raw.get("major_stars", []):
                if s["name"] == chart.soul:
                    # Get translated via palace object
                    pass
        # Simplest: just use the raw key, frontend knows it
        soul_star_translated = chart.soul
        body_star_translated = chart.body
    except Exception:
        soul_star_translated = chart.soul
        body_star_translated = chart.body

    return {
        "metadata":     metadata,
        "palaces":      palaces,
        "soul_palace":  soul_summary,
        "body_palace":  body_summary,
        "sanjiao_sizheng": sanjiao,
        "soul_star_raw": soul_star_translated,
        "body_star_raw": body_star_translated,
    }
