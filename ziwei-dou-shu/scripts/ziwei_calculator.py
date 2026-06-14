#!/usr/bin/env python3
"""
紫微斗數 命盤計算機 (Zi Wei Dou Shu Chart Calculator)
=====================================================
擴充版：本命命盤 + 每日運勢 + 每月運勢 + 卜事算法

算法依據：傳統紫微斗數掌上诀法 + 流日流月四化慣例
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
import calendar

# ── 12 宮位名稱 (順時針排列) ──────────────────────────────────────────
PALACE_NAMES = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮",
    "財帛宮", "疾厄宮", "遷移宮", "僕役宮",
    "官祿宮", "田宅宮", "福德宮", "父母宮"
]

# ── 14 主星基本屬性 ────────────────────────────────────────────────────
MAIN_STARS = {
    "紫微星": {"trait": "帝王之星，尊貴、領導、自主", "desc": "領導欲強，重面子，愛好掌控"},
    "天機星": {"trait": "智慧之星，機敏、善變、策略", "desc": "頭腦靈活，擅思考，好奇心重"},
    "太陽星": {"trait": "光明之星，熱情、正義、外向", "desc": "講義氣，愛表現，追求光彩"},
    "武曲星": {"trait": "財富之星，剛毅、固執、務實", "desc": "個性直爽，理財力強，固執己見"},
    "天同星": {"trait": "福氣之星，溫和、享樂、人緣佳", "desc": "人緣好，追求舒適，有藝術氣息"},
    "廉貞星": {"trait": "感情之星，熱情、敢愛敢恨、複雜", "desc": "感情豐富，善嫉，情緒波動大"},
    "天府星": {"trait": "保守之星，穩重、誠實、理財高手", "desc": "理財高手，為人保守，不冒險"},
    "太陰星": {"trait": "柔情之星，柔順、細膩、藝術", "desc": "心思細膩，追求完美，適合藝術"},
    "貪狼星": {"trait": "欲望之星，現實、圓滑、桃花旺", "desc": "慾望強，擅交際，桃花旺"},
    "巨門星": {"trait": "是非之星，口才佳、善分析、多疑", "desc": "口才佳，善分析，多疑心"},
    "天相星": {"trait": "印星，穩重、服務、依賴", "desc": "重穿著，依賴性強，服務導向"},
    "天梁星": {"trait": "庇護之星，穩重、照顧人、保守", "desc": "擅長照顧人，穩重，保守派"},
    "七殺星": {"trait": "威嚴之星，剛烈、果斷、孤獨", "desc": "脾氣暴燥果斷，適合創業"},
    "破軍星": {"trait": "耗費之星，破壞創新、不穩定、耗費", "desc": "開創性強，但理財不佳，花費大"},
}

# ── 天干 / 地支 ────────────────────────────────────────────────────────
GAN_NAMES = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZHI_TO_INDEX = {z: i for i, z in enumerate(ZHI_NAMES)}

# ── 六十甲子（年干支快速查表）───────────────────────────────────────────
CYCLE_BASE_YEAR = 1984  # 甲子年

# ── 四化星（流日、流月、卜事共用）────────────────────────────────────────
# 傳統四化：貪白、巨陽、機陰、天梁、禄權科、紫破
SIHUA_BY_GAN = {
    "甲": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "乙": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "丙": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "丁": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "戊": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "己": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "庚": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "辛": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "壬": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
    "癸": {"化祿": "祿", "化權": "權", "化科": "科", "化忌": "忌"},
}

# 流日四化表（按日干，流日干支以當天日干為準）
SIHUA_DAY = {
    "甲": {"化祿": "貪狼", "化權": "巨門", "化科": "天機", "化忌": "太陰"},
    "乙": {"化祿": "天機", "化權": "太陰", "化科": "紫微", "化忌": "天梁"},
    "丙": {"化祿": "天同", "化權": "天梁", "化科": "天機", "化忌": "太陰"},
    "丁": {"化祿": "太陰", "化權": "巨門", "化科": "天同", "化忌": "天梁"},
    "戊": {"化祿": "貪狼", "化權": "天梁", "化科": "天機", "化忌": "天同"},
    "己": {"化祿": "武曲", "化權": "貪狼", "化科": "天梁", "化忌": "天同"},
    "庚": {"化祿": "天同", "化權": "天機", "化科": "天梁", "化忌": "太陰"},
    "辛": {"化祿": "天機", "化權": "天梁", "化科": "巨門", "化忌": "貪狼"},
    "壬": {"化祿": "天同", "化權": "天梁", "化科": "天府", "化忌": "天機"},
    "癸": {"化祿": "天梁", "化權": "天府", "化科": "天同", "化忌": "巨門"},
}

# 流月四化表（按月干，流月干以當月節氣月起點）
SIHUA_MONTH = {
    "甲": {"化祿": "貪狼", "化權": "巨門", "化科": "天機", "化忌": "太陰"},
    "乙": {"化祿": "天機", "化權": "太陰", "化科": "紫微", "化忌": "天梁"},
    "丙": {"化祿": "天同", "化權": "天梁", "化科": "天機", "化忌": "太陰"},
    "丁": {"化祿": "太陰", "化權": "巨門", "化科": "天同", "化忌": "天梁"},
    "戊": {"化祿": "貪狼", "化權": "天梁", "化科": "天機", "化忌": "天同"},
    "己": {"化祿": "武曲", "化權": "貪狼", "化科": "天梁", "化忌": "天同"},
    "庚": {"化祿": "天同", "化權": "天機", "化科": "天梁", "化忌": "太陰"},
    "辛": {"化祿": "天機", "化權": "天梁", "化科": "巨門", "化忌": "貪狼"},
    "壬": {"化祿": "天同", "化權": "天梁", "化科": "天府", "化忌": "天機"},
    "癸": {"化祿": "天梁", "化權": "天府", "化科": "天同", "化忌": "巨門"},
}

# 卜事四化表（按時干）
SIHUA_HOUR = {
    "甲": {"化祿": "貪狼", "化權": "巨門", "化科": "天機", "化忌": "太陰"},
    "乙": {"化祿": "天機", "化權": "太陰", "化科": "紫微", "化忌": "天梁"},
    "丙": {"化祿": "天同", "化權": "天梁", "化科": "天機", "化忌": "太陰"},
    "丁": {"化祿": "太陰", "化權": "巨門", "化科": "天同", "化忌": "天梁"},
    "戊": {"化祿": "貪狼", "化權": "天梁", "化科": "天機", "化忌": "天同"},
    "己": {"化祿": "武曲", "化權": "貪狼", "化科": "天梁", "化忌": "天同"},
    "庚": {"化祿": "天同", "化權": "天機", "化科": "天梁", "化忌": "太陰"},
    "辛": {"化祿": "天機", "化權": "天梁", "化科": "巨門", "化忌": "貪狼"},
    "壬": {"化祿": "天同", "化權": "天梁", "化科": "天府", "化忌": "天機"},
    "癸": {"化祿": "天梁", "化權": "天府", "化科": "天同", "化忌": "巨門"},
}

# 流日宮位速算表：{日干: 起宮 index}
LIURI_START = {
    "甲": 0, "乙": 1, "丙": 2, "丁": 3, "戊": 4,
    "己": 5, "庚": 6, "辛": 7, "壬": 8, "癸": 9
}

# 流月宮位速算表：{月干: 起宮 index}
LIUYUE_START = {
    "甲": 0, "乙": 1, "丙": 2, "丁": 3, "戊": 4,
    "己": 5, "庚": 6, "辛": 7, "壬": 8, "癸": 9
}


# ══════════════════════════════════════════════════════════════════════
#  核心工具函式
# ══════════════════════════════════════════════════════════════════════

def get_gan_index(gan: str) -> int:
    return GAN_NAMES.index(gan)


def get_year_gz(year: int) -> tuple[str, str]:
    """取得年份的干支"""
    offset = (year - CYCLE_BASE_YEAR) % 60
    return GAN_NAMES[offset % 10], ZHI_NAMES[offset % 12]


def get_day_gz(year: int, month: int, day: int) -> tuple[str, str]:
    """取得任意日期的日干支（Zeller公式近似）"""
    # 調整月份
    if month < 3:
        month += 12
        year -= 1
    # 使用蔡勒公式計算星期
    Y, M, D = year, month, day
    K = Y % 100
    J = Y // 100
    # 蔡勒公式：0=週六
    h = (D + (13 * (M + 1)) // 5 + K + K // 4 + J // 4 - 2 * J) % 7
    # 轉為我們的週期：0=週日
    weekday = (h + 6) % 7
    # 以 1984-01-01 (甲子日, 週日) 為基準
    base = date(1984, 1, 1)
    target = date(year, month if month >= 3 else month + 12, day)
    days_diff = (target - base).days
    offset = days_diff % 60
    return GAN_NAMES[offset % 10], ZHI_NAMES[offset % 12]


def calculate_life_palace(birth_month: int, birth_hour: int) -> int:
    """掌上诀法：計算命宮 index（0~11）"""
    month_coeff = birth_month
    hour_index = ((birth_hour + 1) // 2) % 12 + 1
    life_idx = (month_coeff * 2 + hour_index + 2) % 12
    return life_idx % 12


def build_palaces(birth_month: int, birth_hour: int) -> list[int]:
    """建立 12 宮排列（以命宮為起點順時針）"""
    life = calculate_life_palace(birth_month, birth_hour)
    return [(life + i) % 12 for i in range(12)]


# ══════════════════════════════════════════════════════════════════════
#  本命命盤
# ══════════════════════════════════════════════════════════════════════

def place_main_stars(
    birth_year: int, birth_month: int, birth_day: int, birth_hour: int
) -> dict[int, list[str]]:
    """將 14 主星分配到 12 宮"""
    palace_stars: dict[int, list[str]] = {i: [] for i in range(12)}
    year_gan, _ = get_year_gz(birth_year)
    year_offset = get_gan_index(year_gan)
    _, day_zhi = get_day_gz(birth_year, birth_month, birth_day)
    day_zhi_index = ZHI_TO_INDEX[day_zhi]
    life_palace = calculate_life_palace(birth_month, birth_hour)

    STAR_BASE = {
        "紫微星": 0, "天機星": 2, "太陽星": 3, "武曲星": 4,
        "天同星": 5, "廉貞星": 6, "天府星": 8, "太陰星": 9,
        "貪狼星": 10, "巨門星": 11, "天相星": 1, "天梁星": 7,
        "七殺星": 8, "破軍星": 9,
    }

    # 北斗七星（年干系數）
    palace_stars[(life_palace + (STAR_BASE["紫微星"] + year_offset) % 12) % 12].append("紫微星")
    palace_stars[(life_palace + (STAR_BASE["天機星"] + year_offset) % 12) % 12].append("天機星")
    taiyang_palace = (life_palace + (day_zhi_index + birth_hour // 2) % 12) % 12
    palace_stars[taiyang_palace].append("太陽星")
    palace_stars[(life_palace + (year_offset + 4) % 12) % 12].append("武曲星")
    palace_stars[(life_palace + (year_offset + 5) % 12) % 12].append("天同星")
    palace_stars[(life_palace + (year_offset + 6) % 12) % 12].append("廉貞星")

    # 南斗六星（月令）
    palace_stars[(life_palace + (birth_month - 1 + year_offset) % 12) % 12].append("天府星")
    palace_stars[(life_palace + (birth_month + year_offset + 3) % 12) % 12].append("太陰星")
    palace_stars[(life_palace + (year_offset * 2 + birth_month) % 12) % 12].append("貪狼星")
    palace_stars[(life_palace + (year_offset * 3 + birth_month + 1) % 12) % 12].append("巨門星")
    palace_stars[(life_palace + (year_offset + birth_month + 5) % 12) % 12].append("天相星")
    palace_stars[(life_palace + (year_offset + birth_month + 7) % 12) % 12].append("天梁星")
    palace_stars[(life_palace + (year_offset * 2 + birth_month * 2) % 12) % 12].append("七殺星")
    palace_stars[(life_palace + (year_offset + birth_day + birth_hour) % 12) % 12].append("破軍星")

    return palace_stars


def interpret_palace(palace_idx: int, stars: list[str], year_gan: str) -> str:
    """單一宮位解讀"""
    pname = PALACE_NAMES[palace_idx]
    base = PALACE_INTERPRETATIONS.get(pname, "")
    star_descriptions = [f"{s}（{MAIN_STARS.get(s, {}).get('desc', '')}）" for s in stars if s in MAIN_STARS]
    star_text = "、".join(star_descriptions) if star_descriptions else "（無主星）"
    return f"【{pname}】\n  主星：{star_text}\n  概要：{base}"


PALACE_INTERPRETATIONS = {
    "命宮": "代表先天個性與外表形象，是整張命盤的核心。命宮強者自主性強；命宮弱則依賴性重。",
    "兄弟宮": "反映兄弟姐妹緣分與人際支持力道。強旺者得兄弟朋友相助；薄弱者較孤單。",
    "夫妻宮": "掌管感情婚姻與伴侶互動。星曜聚集者感情豐富；空宮者較晚婚或需異地姻緣。",
    "子女宮": "象徵子女緣分、創造力與晚年運勢。強旺者子女有成；空宮者子女緣較淡。",
    "財帛宮": "理財態度與財運型態。星曜聚集善理財；空宮者財運來去都快，宜開源節流。",
    "疾厄宮": "身心健康與疾病傾向。注意此宮可提前調整生活作息，維持健康運勢。",
    "遷移宮": "外出發展、旅遊、國外運勢。強旺者適合外出闖蕩；薄弱者宜守本地發展。",
    "僕役宮": "社交圈子與下屬關係。顯示貴人運多寡，助你了解人脈經營方向。",
    "官祿宮": "事業發展與職場表現。星曜聚集者事業心強，適合創業或管理階層。",
    "田宅宮": "房產、不動產與家庭氛圍。影響置產運與居住環境滿意度。",
    "福德宮": "福氣、道德修養與精神生活。影響人生整體滿足感與休閒品質。",
    "父母宮": "與父母的緣分、學歷與文書印章運。顯示早年助力與學術表現。",
}


def analyze_combinations(all_stars: list[str]) -> list[str]:
    """分析重要星曜組合"""
    results = []
    combos = []
    if "紫微星" in all_stars and "天機星" in all_stars:
        combos.append("紫機相會：智謀兼備，適合策劃與分析")
    if "太陽星" in all_stars and "太陰星" in all_stars:
        combos.append("日月照命：內外交輝，人緣佳")
    if "武曲星" in all_stars and "天府星" in all_stars:
        combos.append("武府同宮：理財能力極強，適合財務管理")
    if "貪狼星" in all_stars and "廉貞星" in all_stars:
        combos.append("貪廉同宮：感情豐富，桃花與理智交織，需節制")
    if "天梁星" in all_stars and "天機星" in all_stars:
        combos.append("梁機會合：擅長照顧後輩，適合教育或醫護")
    if "七殺星" in all_stars and "破軍星" in all_stars:
        combos.append("殺破會照：開創力強，適合創業或打破現狀")
    if "巨門星" in all_stars and "太陽星" in all_stars:
        combos.append("門太陽照：口才極佳，適合法界、教育或銷售")
    if "天同星" in all_stars and "太陰星" in all_stars:
        combos.append("同陰會命：溫柔敏感，適合藝術創作或服務業")
    if "天府星" in all_stars and "天梁星" in all_stars:
        combos.append("府梁並照：理財穩健，晚年有福，宜長線投資")
    if "紫微星" in all_stars and "貪狼星" in all_stars:
        combos.append("紫貪照命：慾望與理想並存，需自制方能成大事")
    if not combos:
        results.append("命盤中星曜以獨立運行為主，無明顯富貴組合，需靠個人努力發揮")
    else:
        results.extend(combos)
    return results


def generate_chart(birth_year: int, birth_month: int, birth_day: int,
                   birth_hour: int, gender: str = "male") -> dict:
    """生成完整本命命盤"""
    year_gan, year_zhi = get_year_gz(birth_year)
    life_palace = calculate_life_palace(birth_month, birth_hour)
    life_palace_name = PALACE_NAMES[life_palace]
    palace_stars = place_main_stars(birth_year, birth_month, birth_day, birth_hour)
    chart_order = build_palaces(birth_month, birth_hour)

    all_stars = []
    for stars in palace_stars.values():
        all_stars.extend(stars)

    combos = analyze_combinations(all_stars)

    palace_readings = []
    for i, palace_global_idx in enumerate(chart_order):
        pname = PALACE_NAMES[i]
        stars = palace_stars[palace_global_idx]
        palace_readings.append({
            "palace": pname,
            "stars": stars,
            "reading": interpret_palace(palace_global_idx, stars, year_gan)
        })

    life_stars = palace_stars[life_palace]
    life_trait = [MAIN_STARS[s]["trait"] for s in life_stars if s in MAIN_STARS]
    life_trait_text = "、".join(life_trait) if life_trait else "穩重低調，適應力強"

    return {
        "birth_info": {
            "year": birth_year, "month": birth_month, "day": birth_day,
            "hour": birth_hour, "gender": gender,
            "year_stem_branch": f"{year_gan}{year_zhi}",
        },
        "summary": {
            "life_palace": life_palace_name,
            "life_palace_index": life_palace,
            "personality_trait": life_trait_text,
            "zodiac_sign": f"{year_gan}{year_zhi}",
        },
        "combinations": combos,
        "palace_readings": palace_readings,
        "all_stars": all_stars,
        "palace_stars": {PALACE_NAMES[k]: v for k, v in palace_stars.items()},
        "chart_order": chart_order,  # 每個位置對應的實際宮位
    }


# ══════════════════════════════════════════════════════════════════════
#  每日運勢（流日）
# ══════════════════════════════════════════════════════════════════════

def calculate_liuri(target_date: date, life_palace: int, chart: dict) -> dict:
    """
    計算流日宮位與四化
    公式：流日宮 = (起宮 + 距天數) % 12
    起宮按日干：甲日起命宮，乙日兄弟宮...
    """
    day_gan, day_zhi = get_day_gz(target_date.year, target_date.month, target_date.day)
    day_gan_idx = get_gan_index(day_gan)

    # 起宮：甲=0(命宮), 乙=1(兄弟宮)...
    start_palace = day_gan_idx % 12  # 甲→0,乙→1,...癸→9
    # 距今天數（相對於月首）
    days_in_month = calendar.monthrange(target_date.year, target_date.month)[1]
    day_of_month = target_date.day
    liuri_palace_idx = (start_palace + day_of_month - 1) % 12

    # 流日四化
    sihua = SIHUA_DAY.get(day_gan, {})
    sihua_stars = {k: v for k, v in sihua.items()}

    # 流日宮內之星（本日增強的星）
    # 在實際命盤中，該宮原有的星曜今日能量增强
    chart_order = chart["chart_order"]
    # 流日宮在命盤中對應哪個宮位
    liuri_global_palace = chart_order[liuri_palace_idx]
    liuri_stars = chart["palace_stars"].get(PALACE_NAMES[liuri_global_palace], [])

    return {
        "date": str(target_date),
        "day_gan_zhi": f"{day_gan}{day_zhi}",
        "liuri_palace": PALACE_NAMES[liuri_palace_idx],
        "liuri_palace_index": liuri_palace_idx,
        "liuri_global_palace": PALACE_NAMES[liuri_global_palace],
        "liuri_stars": liuri_stars,
        "sihua": sihua_stars,
        "strength": _judge_palace_strength(liuri_global_palace, liuri_stars, sihua_stars),
    }


# ══════════════════════════════════════════════════════════════════════
#  每月運勢（流月）
# ══════════════════════════════════════════════════════════════════════

def calculate_liuyue(target_year: int, target_month: int,
                     life_palace: int, chart: dict) -> dict:
    """
    計算流月宮位與四化
    公式：流月宮 = (起宮 + 月數) % 12
    起宮按月干（甲己年起命宮，乙庚年起兄弟宮...）
    """
    # 月干：粗略以月建計算（初一就換月）
    month_gan = GAN_NAMES[(target_month - 1 + 6) % 10]  # 粗簡對照
    day_gan = GAN_NAMES[(target_year % 10)]  # 用年干代替月干（實務簡化）
    month_gan = GAN_NAMES[(target_month * 2 - 2) % 10]  # 傳統月干

    start_palace = get_gan_index(month_gan) % 12
    liuyue_palace_idx = (start_palace + target_month - 1) % 12

    # 流月四化
    sihua = SIHUA_MONTH.get(month_gan, {})
    sihua_stars = {k: v for k, v in sihua.items()}

    chart_order = chart["chart_order"]
    liuyue_global_palace = chart_order[liuyue_palace_idx]
    liuyue_stars = chart["palace_stars"].get(PALACE_NAMES[liuyue_global_palace], [])

    return {
        "year_month": f"{target_year}/{target_month:02d}",
        "month_gan": month_gan,
        "liuyue_palace": PALACE_NAMES[liuyue_palace_idx],
        "liuyue_palace_index": liuyue_palace_idx,
        "liuyue_global_palace": PALACE_NAMES[liuyue_global_palace],
        "liuyue_stars": liuyue_stars,
        "sihua": sihua_stars,
        "strength": _judge_palace_strength(liuyue_global_palace, liuyue_stars, sihua_stars),
    }


# ══════════════════════════════════════════════════════════════════════
#  卜事（針對特定事件）
# ══════════════════════════════════════════════════════════════════════

def calculate_bushi(event_time: datetime, chart: dict, question: str = "") -> dict:
    """
    卜事算法：取發問時辰
    - 時干起宮（發問時的時辰干支）
    - 飛化：時干四化映照在命盤上的影響
    - 重點宮：時宮（焦點宮）、對宮（感應宮）
    """
    year, month, day = event_time.year, event_time.month, event_time.day
    hour = event_time.hour

    # 五鼠遁：根據日干求出時干
    # 甲己日子時起甲，乙庚起丙，丙辛起戊，丁壬起癸，戊癸起甲
    day_gan, _ = get_day_gz(year, month, day)
    hour_zhi_idx = ((hour + 1) // 2) % 12  # 子時=0, 丑=1, ...
    wushudun_start = {
        "甲": 0, "己": 0,
        "乙": 1, "庚": 1,
        "丙": 2, "辛": 2,
        "丁": 3, "壬": 3,
        "戊": 4, "癸": 4,
    }
    actual_hour_gan = GAN_NAMES[(wushudun_start.get(day_gan, 0) + hour_zhi_idx) % 10]
    actual_hour_zhi = ZHI_NAMES[hour_zhi_idx]

    # 時干起宮
    start_palace = get_gan_index(actual_hour_gan) % 12
    bushi_palace_idx = start_palace

    # 時干四化
    sihua = SIHUA_HOUR.get(actual_hour_gan, {})
    sihua_stars = dict(sihua)

    chart_order = chart["chart_order"]
    bushi_global_palace = chart_order[bushi_palace_idx]
    bushi_stars = chart["palace_stars"].get(PALACE_NAMES[bushi_global_palace], [])
    opposite_idx = (bushi_palace_idx + 6) % 12
    opposite_global_palace = chart_order[opposite_idx]
    opposite_stars = chart["palace_stars"].get(PALACE_NAMES[opposite_global_palace], [])

    return {
        "event_time": event_time.isoformat(),
        "hour_gan_zhi": f"{actual_hour_gan}{actual_hour_zhi}",
        "question": question,
        "bushi_palace": PALACE_NAMES[bushi_palace_idx],
        "bushi_palace_index": bushi_palace_idx,
        "bushi_global_palace": PALACE_NAMES[bushi_global_palace],
        "bushi_stars": bushi_stars,
        "opposite_palace": PALACE_NAMES[opposite_idx],
        "opposite_global_palace": PALACE_NAMES[opposite_global_palace],
        "opposite_stars": opposite_stars,
        "sihua": sihua_stars,
        "strength": _judge_bushi(
            PALACE_NAMES[bushi_global_palace], bushi_stars,
            PALACE_NAMES[opposite_global_palace], opposite_stars, sihua_stars
        ),
    }


# ══════════════════════════════════════════════════════════════════════
#  強度判斷
# ══════════════════════════════════════════════════════════════════════

def _judge_palace_strength(global_palace_name: str, palace_stars: list[str],
                           sihua: dict) -> dict:
    """判斷宮位強弱（供流日/流月使用）"""
    score = 0
    notes = []

    # 星曜加分
    good_stars = ["紫微星", "天府星", "天梁星", "天機星", "太陽星", "天同星", "太陰星"]
    bad_stars = ["七殺星", "破軍星", "貪狼星", "廉貞星"]
    for s in palace_stars:
        if s in good_stars:
            score += 1
            notes.append(f"{s}增強")
        elif s in bad_stars:
            score -= 1
            notes.append(f"{s}波動")

    # 四化影響
    for transform, star in sihua.items():
        if star in good_stars and transform in ("化祿", "化權"):
            score += 1
            notes.append(f"{transform}{star}")
        elif transform == "化忌":
            score -= 1
            notes.append(f"{transform}{star}")

    # 宮位特性（強宮加分）
    strong_palaces = ["命宮", "官祿宮", "財帛宮", "遷移宮"]
    if global_palace_name in strong_palaces:
        score += 1
        notes.append(f"{global_palace_name}為強宮")

    if score >= 2:
        level = "大旺"
    elif score == 1:
        level = "小旺"
    elif score == 0:
        level = "平穩"
    elif score == -1:
        level = "小起伏"
    else:
        level = "動盪"

    return {"score": score, "level": level, "notes": notes}


def _judge_bushi(bushi_palace: str, bushi_stars: list[str],
                 opposite_palace: str, opposite_stars: list[str],
                 sihua: dict) -> dict:
    """判斷卜事結果"""
    notes = []
    score = 0

    for transform, star in sihua.items():
        if transform == "化祿":
            notes.append(f"{transform}{star}：如願以償")
            score += 1
        elif transform == "化權":
            notes.append(f"{transform}{star}：全力以赴")
            score += 1
        elif transform == "化科":
            notes.append(f"{transform}{star}：有貴人指點")
            score += 0
        elif transform == "化忌":
            notes.append(f"{transform}{star}：有阻礙，需謹慎")
            score -= 1

    bushi_star_names = [s for s in bushi_stars if s in MAIN_STARS]
    if bushi_star_names:
        notes.append(f"焦點宮位{bushi_palace}有：{'、'.join(bushi_star_names)}")
        score += len([s for s in bushi_star_names if s in ["紫微星", "天府星", "天梁星"]])

    if score >= 2:
        level = "大吉"
    elif score == 1:
        level = "小吉"
    elif score == 0:
        level = "平穩"
    elif score == -1:
        level = "小凶"
    else:
        level = "大凶"

    return {"score": score, "level": level, "notes": notes}


# ══════════════════════════════════════════════════════════════════════
#  格式化輸出
# ══════════════════════════════════════════════════════════════════════

def format_fortune(chart: dict, liuri: dict = None, liuyue: dict = None,
                   bushi: dict = None) -> str:
    """產生帶運勢的完整命盤報告"""
    lines = []
    lines.append("═" * 50)
    lines.append("     🌸 紫微斗數 命盤分析報告 🌸")
    lines.append("═" * 50)

    b = chart["birth_info"]
    lines.append(f"\n【本命資料】")
    lines.append(f"  出生：{b['year']}年{b['month']}月{b['day']}日 {b['hour']}時")
    lines.append(f"  年柱：{b['year_stem_branch']}  性別：{b['gender']}")

    s = chart["summary"]
    lines.append(f"\n【命宮特質】")
    lines.append(f"  命宮：{s['life_palace']}  性格：{s['personality_trait']}")

    if chart["combinations"]:
        lines.append(f"\n【命盤格局】")
        for c in chart["combinations"]:
            lines.append(f"  ✦ {c}")

    # 每日
    if liuri:
        lines.append(f"\n{'─' * 50}")
        lines.append(f"【每日運勢】{liuri['date']} ({liuri['day_gan_zhi']}日)")
        lines.append(f"  流日宮：{liuri['liuri_palace']}（{liuri['liuri_global_palace']}）")
        if liuri['liuri_stars']:
            lines.append(f"  宮內星曜：{'、'.join(liuri['liuri_stars'])}")
        lines.append(f"  流日四化：{', '.join(f'{k}{v}' for k,v in liuri['sihua'].items())}")
        st = liuri['strength']
        lines.append(f"  今日強度：{st['level']}（{st['score']:+d}）")
        if st['notes']:
            lines.append(f"  動力摘要：{'；'.join(st['notes'])}")

    # 每月
    if liuyue:
        lines.append(f"\n{'─' * 50}")
        lines.append(f"【每月運勢】{liuyue['year_month']}（月干：{liuyue['month_gan']}）")
        lines.append(f"  流月宮：{liuyue['liuyue_palace']}（{liuyue['liuyue_global_palace']}）")
        if liuyue['liuyue_stars']:
            lines.append(f"  宮內星曜：{'、'.join(liuyue['liuyue_stars'])}")
        lines.append(f"  流月四化：{', '.join(f'{k}{v}' for k,v in liuyue['sihua'].items())}")
        st = liuyue['strength']
        lines.append(f"  本月強度：{st['level']}（{st['score']:+d}）")
        if st['notes']:
            lines.append(f"  動力摘要：{'；'.join(st['notes'])}")

    # 卜事
    if bushi:
        lines.append(f"\n{'─' * 50}")
        lines.append(f"【卜事指引】")
        if bushi.get('question'):
            lines.append(f"  問題：{bushi['question']}")
        lines.append(f"  起卦時辰：{bushi['hour_gan_zhi']}時")
        lines.append(f"  焦點宮位：{bushi['bushi_palace']}（{bushi['bushi_global_palace']}）")
        lines.append(f"  感應對宮：{bushi['opposite_palace']}（{bushi['opposite_global_palace']}）")
        if bushi.get('bushi_stars'):
            lines.append(f"  宮內星曜：{'、'.join(bushi['bushi_stars'])}")
        if bushi.get('opposite_stars'):
            lines.append(f"  對宮星曜：{'、'.join(bushi['opposite_stars'])}")
        lines.append(f"  時辰四化：{', '.join(f'{k}{v}' for k,v in bushi['sihua'].items())}")
        st = bushi['strength']
        lines.append(f"  判斷：{st['level']}（{st['score']:+d}）")
        if st['notes']:
            lines.append(f"  指引：{'；'.join(st['notes'])}")

    lines.append(f"\n{'─' * 50}")
    lines.append("  命理僅供參考，自己的努力才是決定命運的關鍵 💪")
    lines.append("═" * 50)
    return "\n".join(lines)


def format_ascii_chart(chart: dict) -> str:
    """ASCII 命盤圖"""
    life_idx = chart["summary"]["life_palace_index"]
    ps = chart["palace_stars"]

    def fmt(idx):
        stars = ps.get(PALACE_NAMES[idx], [])
        star_str = "、".join(stars[:3]) if stars else "—"
        return f"{PALACE_NAMES[idx]}[{star_str}]"

    lines = [
        "╔════════════════════════════════════════╗",
        "║       紫微斗數 命盤（簡圖）             ║",
        "╠════════════════════════════════════════╣",
        f"║  {fmt(11):21s} {fmt(0):20s} {fmt(1):19s}  ║",
        "║                                            ║",
        f"║  {fmt(10):21s} {fmt(2):20s}  ║",
        "║                                            ║",
        f"║  {fmt(9):21s} {fmt(6):20s} {fmt(7):19s}  ║",
        "║                                            ║",
        f"║  {fmt(4):21s} {fmt(5):20s} {fmt(3):19s}  ║",
        "╚════════════════════════════════════════╝",
    ]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json, sys
    from datetime import datetime as dt

    args = sys.argv[1:]
    if not args:
        print("用法：")
        print("  本命盤：  python ziwei_calculator.py chart <年份> <月份> <日期> <時辰> [性別]")
        print("  全功能：  python ziwei_calculator.py <年份> <月份> <日期> <時辰> [性別]")
        print("  卜事：    python ziwei_calculator.py bushi <年份> <月份> <日期> <時辰> [性別] [問題]")
        print()
        print("範例：")
        print("  python ziwei_calculator.py 1990 5 15 14 female")
        print("  python ziwei_calculator.py chart 1990 5 15 14 female")
        print("  python ziwei_calculator.py bushi 1990 5 15 14 female 我最近換工作好不好")
        sys.exit(1)

    # 卜事模式
    if args[0] == "bushi":
        parts = args[1:]
        if len(parts) < 4:
            print("卜事模式需要：年份 月份 日期 時辰 [性別] [問題]")
            sys.exit(1)
        year, month, day, hour = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        gender = parts[4] if len(parts) > 4 and parts[4] in ("male", "female") else "male"
        question = " ".join(parts[5:]) if len(parts) > 5 else ""
        chart = generate_chart(year, month, day, hour, gender)
        now = dt.now()
        bushi = calculate_bushi(now, chart, question)
        print(format_ascii_chart(chart))
        print()
        print(format_fortune(chart, bushi=bushi))
        sys.exit(0)

    # 本命盤模式
    if args[0] == "chart":
        _, year, month, day, hour, *rest = args
        gender = rest[0] if rest and rest[0] in ("male", "female") else "male"
        chart = generate_chart(int(year), int(month), int(day), int(hour), gender)
        print(format_ascii_chart(chart))
        print()
        print(format_fortune(chart))
        sys.exit(0)

    # 全功能模式：本命盤 + 每日 + 每月
    if len(args) >= 4:
        year, month, day, hour, *rest = args
        gender = rest[0] if rest and rest[0] in ("male", "female") else "male"
        chart = generate_chart(int(year), int(month), int(day), int(hour), gender)
        today = date.today()
        liuri = calculate_liuri(today, chart["summary"]["life_palace_index"], chart)
        liuyue = calculate_liuyue(today.year, today.month, chart["summary"]["life_palace_index"], chart)
        print(format_ascii_chart(chart))
        print()
        print(format_fortune(chart, liuri=liuri, liuyue=liuyue))
        sys.exit(0)