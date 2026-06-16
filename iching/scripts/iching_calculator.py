#!/usr/bin/env python3
"""
易經卜卦計算機 (I Ching Hexagram Calculator)
=============================================
硬幣法：6 次擲硬幣，每次結果：
  3 正（老陽/動爻）→ 7（陽爻，動）
  2 正 1 反（少陽）→ 9（陽爻，靜）
  1 正 2 反（少陰）→ 8（陰爻，靜）
  3 反（老陰/動爻）→ 6（陰爻，動）

Convention: 6=少陰(動), 7=少陽(動), 8=陰, 9=陽 (King Wen numbering)
"""

import random
from dataclasses import dataclass
from typing import Optional

# ═══════════════════════════════════════════════════════════════
#  六十四卦資料庫
# ═══════════════════════════════════════════════════════════════

HEXAGRAMS = {
    1:  {"name": "乾", "trigram": "☰☰", "fu_xi": 63, "judgment": "元亨利貞", "judgment_text": "大吉大利，諸事亨通。", "nuclear": 2},
    2:  {"name": "坤", "trigram": "☷☷", "fu_xi": 0, "judgment": "元亨利牝馬之貞", "judgment_text": "柔順大地，安泰吉祥。", "nuclear": 1},
    3:  {"name": "屯", "trigram": "☵☳", "fu_xi": 7, "judgment": "元亨利貞，勿用有攸往", "judgment_text": "萬事起頭難，囤積力量。", "nuclear": 24},
    4:  {"name": "蒙", "trigram": "☶☴", "fu_xi": 15, "judgment": "亨，匪我求童蒙，童蒙求我", "judgment_text": "蒙昧初期，需虛心求教。", "nuclear": 23},
    5:  {"name": "需", "trigram": "☵☰", "fu_xi": 55, "judgment": "亨，出險在穴上", "judgment_text": "耐心等待，時機未到。", "nuclear": 10},
    6:  {"name": "讼", "trigram": "☰☵", "fu_xi": 62, "judgment": "有孚窒，中吉，終凶", "judgment_text": "爭訴訟說，宜和解。", "nuclear": 11},
    7:  {"name": "師", "trigram": "☷☵", "fu_xi": 14, "judgment": "丈人吉，無咎", "judgment_text": "領導統馭，仗義行事。", "nuclear": 16},
    8:  {"name": "比", "trigram": "☵☷", "fu_xi": 49, "judgment": "吉，原筮元永貞，無咎", "judgment_text": "親近輔助，團結和睦。", "nuclear": 15},
    9:  {"name": "小畜", "trigram": "☰☴", "fu_xi": 61, "judgment": "亨，密雲不雨，自我西郊", "judgment_text": "小有積蓄，蓄勢待發。", "nuclear": 20},
    10: {"name": "履", "trigram": "☴☰", "fu_xi": 46, "judgment": "履虎尾，不咥人，亨", "judgment_text": "謹慎行事，踩線不咬。", "nuclear": 5},
    11: {"name": "泰", "trigram": "☷☰", "fu_xi": 52, "judgment": "小往大來，吉亨", "judgment_text": "天地交泰，萬事通達。", "nuclear": 6},
    12: {"name": "否", "trigram": "☰☷", "fu_xi": 59, "judgment": "否之匪人，不利君子貞，大往小來", "judgment_text": "陰陽不通，諸事不順。", "nuclear": 5},
    13: {"name": "同人", "trigram": "☰☲", "fu_xi": 30, "judgment": "同人於野，亨，利涉大川", "judgment_text": "與人同心，合作順利。", "nuclear": 44},
    14: {"name": "大有", "trigram": "☲☰", "fu_xi": 38, "judgment": "元亨", "judgment_text": "大豐收，諸事大吉。", "nuclear": 43},
    15: {"name": "謙", "trigram": "☶☷", "fu_xi": 34, "judgment": "亨，君子有終", "judgment_text": "謙虛待人，諸事亨通。", "nuclear": 8},
    16: {"name": "豫", "trigram": "☷☳", "fu_xi": 41, "judgment": "利建侯行師", "judgment_text": "預備充足，師出有名。", "nuclear": 7},
    17: {"name": "隨", "trigram": "☳☰", "fu_xi": 25, "judgment": "元亨利貞，無咎", "judgment_text": "隨緣而動，順勢而為。", "nuclear": 45},
    18: {"name": "蠱", "trigram": "☴☶", "fu_xi": 22, "judgment": "元亨，利涉大川，先甲三日，後甲三日", "judgment_text": "整頓積弊，革新轉機。", "nuclear": 46},
    19: {"name": "臨", "trigram": "☷☳", "fu_xi": 54, "judgment": "元亨利貞，至於八月有凶", "judgment_text": "領導來臨，警惕轉折。", "nuclear": 32},
    20: {"name": "觀", "trigram": "☴☷", "fu_xi": 20, "judgment": "盥而不薦，有孚顒若", "judgment_text": "觀望局勢，誠心待時。", "nuclear": 9},
    21: {"name": "噬嗑", "trigram": "☲☶", "fu_xi": 5, "judgment": "亨，利用獄", "judgment_text": "明斷是非，執行力強。", "nuclear": 42},
    22: {"name": "賁", "trigram": "☶☲", "fu_xi": 17, "judgment": "亨，小利有攸往", "judgment_text": "修飾包裝，外表重要。", "nuclear": 53},
    23: {"name": "剝", "trigram": "☷☶", "fu_xi": 2, "judgment": "不利有攸往", "judgment_text": "剝落衰退，保守為宜。", "nuclear": 4},
    24: {"name": "復", "trigram": "☶☷", "fu_xi": 35, "judgment": "亨，出入無疾，朋來無咎，反復其道", "judgment_text": "恢復生機，陰衰陽長。", "nuclear": 3},
    25: {"name": "無妄", "trigram": "☳☰", "fu_xi": 13, "judgment": "元亨利貞，其匪正有眚，不利有攸往", "judgment_text": "循正道行，勿投机取巧。", "nuclear": 36},
    26: {"name": "大畜", "trigram": "☰☶", "fu_xi": 58, "judgment": "利貞，不家食吉，利涉大川", "judgment_text": "大有積蓄，厚積薄發。", "nuclear": 41},
    27: {"name": "頤", "trigram": "☶☳", "fu_xi": 26, "judgment": "貞吉，觀頤，自求口實", "judgment_text": "養生待時，蓄德養性。", "nuclear": 29},
    28: {"name": "大過", "trigram": "☴☲", "fu_xi": 47, "judgment": "棟橈，利有攸往，亨", "judgment_text": "太過剛強，預防危險。", "nuclear": 28},
    29: {"name": "坎", "trigram": "☵☵", "fu_xi": 7, "judgment": "習坎，有孚，維心亨，行有尚", "judgment_text": "重重險難，心誠可通。", "nuclear": 27},
    30: {"name": "離", "trigram": "☲☲", "fu_xi": 56, "judgment": "利貞，亨，畜牝牛吉", "judgment_text": "光明美善，依附正道。", "nuclear": 29},
    31: {"name": "咸", "trigram": "☱☶", "fu_xi": 44, "judgment": "亨利貞，取女吉", "judgment_text": "感應交流，情緣來臨。", "nuclear": 53},
    32: {"name": "恆", "trigram": "☶☱", "fu_xi": 57, "judgment": "亨，無咎，利貞，利有攸往", "judgment_text": "持之以恆，長久穩定。", "nuclear": 19},
    33: {"name": "遯", "trigram": "☱☰", "fu_xi": 40, "judgment": "亨，小利貞", "judgment_text": "退隱山林，保存實力。", "nuclear": 38},
    34: {"name": "大壯", "trigram": "☰☱", "fu_xi": 53, "judgment": "利貞", "judgment_text": "勢力壯大，但需守正。", "nuclear": 31},
    35: {"name": "晉", "trigram": "☷☲", "fu_xi": 37, "judgment": "康侯用錫馬蕃庶，晝日三接", "judgment_text": "晉升高升，名利雙收。", "nuclear": 52},
    36: {"name": "明夷", "trigram": "☲☷", "fu_xi": 45, "judgment": "利艱貞", "judgment_text": "小人當道，韜光養晦。", "nuclear": 33},
    37: {"name": "家人", "trigram": "☲☴", "fu_xi": 50, "judgment": "利女貞", "judgment_text": "家庭和樂，女性有利。", "nuclear": 62},
    38: {"name": "睽", "trigram": "☴☲", "fu_xi": 51, "judgment": "小事吉", "judgment_text": "乖離對立，小事可成。", "nuclear": 39},
    39: {"name": "蹇", "trigram": "☶☵", "fu_xi": 21, "judgment": "利西南，不利東北，利見大人", "judgment_text": "前路艱難，貴人相助。", "nuclear": 48},
    40: {"name": "解", "trigram": "☵☶", "fu_xi": 42, "judgment": "利西南，無所往，其來復吉，有攸往，夙吉", "judgment_text": "解除困難，遲早皆吉。", "nuclear": 47},
    41: {"name": "損", "trigram": "☶☴", "fu_xi": 32, "judgment": "有攸往，得臣無家", "judgment_text": "減損自身，反而得益。", "nuclear": 26},
    42: {"name": "益", "trigram": "☴☶", "fu_xi": 29, "judgment": "利有攸往，利涉大川", "judgment_text": "增益助益，行動有利。", "nuclear": 21},
    43: {"name": "夬", "trigram": "☱☰", "fu_xi": 60, "judgment": "揚於王庭，孚號有厲，告自邑，不利即戎", "judgment_text": "果斷決策，預防小人。", "nuclear": 57},
    44: {"name": "姤", "trigram": "☰☱", "fu_xi": 59, "judgment": "女壯，勿用取女", "judgment_text": "邂逅相遇，警惕女色。", "nuclear": 36},
    45: {"name": "萃", "trigram": "☷☱", "fu_xi": 36, "judgment": "亨，王假有廟，利見大人，亨利貞", "judgment_text": "相聚一堂，人多好辦事。", "nuclear": 50},
    46: {"name": "升", "trigram": "☱☷", "fu_xi": 43, "judgment": "南征吉", "judgment_text": "步步高升，方向南方。", "nuclear": 49},
    47: {"name": "困", "trigram": "☱☵", "fu_xi": 8, "judgment": "亨，貞大人吉，無咎，有言不信", "judgment_text": "困厄之時，心誠口慎。", "nuclear": 40},
    48: {"name": "井", "trigram": "☵☴", "fu_xi": 39, "judgment": "改邑不改井，無喪無得，往來井井", "judgment_text": "源源不絕，修養自身。", "nuclear": 39},
    49: {"name": "革", "trigram": "☲☱", "fu_xi": 54, "judgment": "己日乃孚，元亨利貞，悔亡", "judgment_text": "改革創新，時機成熟。", "nuclear": 32},
    50: {"name": "鼎", "trigram": "☴☲", "fu_xi": 48, "judgment": "元吉，亨", "judgment_text": "重心穩定，嶄新開始。", "nuclear": 38},
    51: {"name": "震", "trigram": "☳☳", "fu_xi": 4, "judgment": "亨，震來虩虩，笑言啞啞", "judgment_text": "震動來臨，驚而不慌。", "nuclear": 24},
    52: {"name": "艮", "trigram": "☶☶", "fu_xi": 31, "judgment": "艮其背，不獲其身，行其庭，不見其人", "judgment_text": "靜止不動，適可而止。", "nuclear": 51},
    53: {"name": "漸", "trigram": "☱☲", "fu_xi": 23, "judgment": "女歸吉，利貞", "judgment_text": "漸進發展，女歸大吉。", "nuclear": 44},
    54: {"name": "歸妹", "trigram": "☲☱", "fu_xi": 33, "judgment": "征凶，無攸利", "judgment_text": "嫁娶之事，不宜輕舉。", "nuclear": 34},
    55: {"name": "豐", "trigram": "☲☳", "fu_xi": 62, "judgment": "亨，王假之，勿憂，宜日中", "judgment_text": "豐盛繁榮，如日當空。", "nuclear": 60},
    56: {"name": "旅", "trigram": "☳☲", "fu_xi": 9, "judgment": "小亨，旅貞吉", "judgment_text": "旅行在外，謹慎小亨。", "nuclear": 63},
    57: {"name": "巽", "trigram": "☴☴", "fu_xi": 28, "judgment": "小亨，利有攸往，利見大人", "judgment_text": "順風行事，柔中帶剛。", "nuclear": 43},
    58: {"name": "兌", "trigram": "☱☱", "fu_xi": 27, "judgment": "亨利貞", "judgment_text": "喜悅和諧，人際和睦。", "nuclear": 58},
    59: {"name": "渙", "trigram": "☵☴", "fu_xi": 10, "judgment": "亨，王假有廟，利涉大川，利貞", "judgment_text": "渙散重聚，團結有利。", "nuclear": 61},
    60: {"name": "節", "trigram": "☴☵", "fu_xi": 18, "judgment": "亨，苦節不可貞", "judgment_text": "節制節約，過度則凶。", "nuclear": 59},
    61: {"name": "中孚", "trigram": "☴☱", "fu_xi": 11, "judgment": "豚魚吉，利涉大川，利貞", "judgment_text": "心中誠信，小物也能吉。", "nuclear": 55},
    62: {"name": "小過", "trigram": "☳☶", "fu_xi": 16, "judgment": "亨，利貞，可小事，不可大事", "judgment_text": "小過難免，大事不宜。", "nuclear": 37},
    63: {"name": "既濟", "trigram": "☵☲", "fu_xi": 3, "judgment": "亨，小利貞，初吉終亂", "judgment_text": "功成圓滿，慎終如始。", "nuclear": 64},
    64: {"name": "未濟", "trigram": "☲☵", "fu_xi": 60, "judgment": "亨，小狐汔濟，濡其尾，無攸利", "judgment_text": "未竟之功，需慎行事。", "nuclear": 63},
}

# ═══════════════════════════════════════════════════════════════
#  核心計算
# ═══════════════════════════════════════════════════════════════

def toss_six_coins() -> list[int]:
    """擲六次硬幣，回傳六個爻值（7=少陽動, 9=老陽動, 6=老陰動, 8=少陰靜）
    
    Convention:
      3正面=7（少陽，動爻）→ 9陽爻（不動）
      2正1反=9（老陽，動爻）→ 7陽爻（動）
      1正2反=8（老陰，動爻）→ 8陰爻（不動）
      3反=6（老陰，動爻）→ 6陰爻（動）
    
    實際上我們的 convention：
    - 奇數(7,9) = 陽，偶數(6,8) = 陰
    - 7,6 = 動爻，8,9 = 靜爻
    """
    return [random.choice([6, 7, 8, 9]) for _ in range(6)]


def coins_to_line(coin: int) -> dict:
    """將硬幣值轉為爻描述"""
    if coin == 7:
        return {"raw": 7, "yang": True, "moving": False, "symbol": "⚊", "name": "九", "desc": "老陽（不動）"}
    elif coin == 9:
        return {"raw": 9, "yang": True, "moving": False, "symbol": "⚊", "name": "九", "desc": "少陽（不動）"}
    elif coin == 6:
        return {"raw": 6, "yang": False, "moving": True, "symbol": "⚋", "name": "六", "desc": "老陰（動）"}
    elif coin == 8:
        return {"raw": 8, "yang": False, "moving": False, "symbol": "⚋", "name": "六", "desc": "少陰（不動）"}


def coins_to_fuxi(lines: list[int]) -> int:
    """將六爻轉為伏羲序列（binary: 陽=1, 陰=0，最下方為最低位）"""
    binary = 0
    for i, coin in enumerate(lines):
        bit = 1 if coin in (7, 9) else 0
        binary |= bit << i  # 第1爻在最右邊
    return binary


def fuxi_to_kingwen(fuxi: int) -> int:
    """伏羲序列 → 文王序列（King Wen ordering）"""
    # 這是簡化版：建立完整映射表
    FK_MAP = {hex["fu_xi"]: kw for kw, hex in HEXAGRAMS.items()}
    return FK_MAP.get(fuxi, 1)


def generate_nuclear(fuxi: int) -> int:
    """取得互卦（Nuclear Hexagram）"""
    nuclear_fuxi = 63 - fuxi
    return fuxi_to_kingwen(nuclear_fuxi)


def get_changing_lines(lines: list[int]) -> list[int]:
    """取得所有動爻位置（1=初爻, 6=上爻）"""
    return [i+1 for i, c in enumerate(lines) if c in (6, 7)]


@dataclass
class HexagramResult:
    question: str
    lines: list[int]  # [6..9] x 6
    king_wen: int
    name: str
    trigram: str
    judgment: str
    judgment_text: str
    changing_lines: list[int]
    changing_texts: list[str]
    nuclear: Optional[int]
    nuclear_name: str
    nuclear_judgment: str

    def format_hexagram_display(self) -> str:
        """產出上下疊的卦象（Unicode 線條）"""
        trigrams = self.trigram  # 上☰下☳
        lines_display = []
        for i in range(5, -1, -1):
            coin = self.lines[i]
            if coin in (7, 9):
                lines_display.append("⚊")  # 陽
            else:
                lines_display.append("⚋")  # 陰
        top = "".join(lines_display[:3])
        bot = "".join(lines_display[3:])
        return f"{top}\n{bot}"

    def format_simple(self) -> str:
        """產出簡單卦象文字"""
        symbols = []
        for coin in reversed(self.lines):
            if coin == 7:
                symbols.append("⚊（九·動）")
            elif coin == 9:
                symbols.append("⚊（九）")
            elif coin == 6:
                symbols.append("⚋（六·動）")
            elif coin == 8:
                symbols.append("⚋（六）")
        return "\n".join(symbols)


# 標準爻辭（取前十卦作為示範）
YAO_TEXTS = {
    1: {  # 乾
        1: "潛龍勿用", 2: "見龍在田，利見大人", 3: "君子終日乾乾，夕惕若厲，無咎",
        4: "或躍在淵，無咎", 5: "飛龍在天，利見大人", 6: "亢龍有悔",
    },
    2: {  # 坤
        1: "履霜，堅冰至", 2: "直方大，不習無不利", 3: "含章可貞，或從王事，無成有終",
        4: "括囊，無咎無譽", 5: "黃裳元吉", 6: "龍戰于野，其血玄黃",
    },
    11: {  # 泰
        1: "拔茅茹，以其彚，征吉", 2: "包荒，用馮河，不遐遺，朋亡，得尚于中行",
        3: "無平不陂，無往不復，艱貞無咎，勿恤其孚，于食有福",
        4: "翩翩，不富以其鄰，不戒以孚", 5: "帝乙歸妹，以祉元吉", 6: "城復于隍，勿用師，自邑告命，貞吝",
    },
    14: {  # 大有
        1: "無交害，匪咎，艱則無咎", 2: "大車以載，有攸往，無咎",
        3: "公用亨于天子，小人弗克", 4: "匪其彭，無咎", 5: "厥孚交如，威如，吉", 6: "吉，自天祐之",
    },
    5: {  # 需
        1: "需于郊，利用恆，無咎", 2: "需于沙，小有言，終吉",
        3: "需于泥，致寇至", 4: "需于血，出自穴", 5: "需于酒食，貞吉", 6: "有不速之客三人來，敬之終吉",
    },
}

# 通用爻辭（當沒有特定卦時使用）
GENERIC_YAO = {
    1: "初爻：萬事起頭，靜待時機。",
    2: "二爻：柔順待時，積累力量。",
    3: "三爻：小心行事，不宜冒進。",
    4: "四爻：謹慎觀望，伺機而動。",
    5: "五爻：居中守正，吉祥如意。",
    6: "上爻：物極必反，謹慎收尾。",
}


def consult(question: str) -> HexagramResult:
    """對任意問題進行一次卜卦"""
    lines = toss_six_coins()
    fuxi = coins_to_fuxi(lines)
    kw = fuxi_to_kingwen(fuxi)
    hex_data = HEXAGRAMS[kw]
    nuclear_fuxi = 63 - fuxi
    nuclear_kw = fuxi_to_kingwen(nuclear_fuxi)
    nuclear_data = HEXAGRAMS.get(nuclear_kw, {})

    changing = get_changing_lines(lines)

    # 爻辭
    yao_texts = []
    yao_data = YAO_TEXTS.get(kw, {})
    for pos in changing:
        yao_texts.append(f"第{pos}爻：「{yao_data.get(pos, GENERIC_YAO.get(pos, '靜待時機'))}」")

    return HexagramResult(
        question=question,
        lines=lines,
        king_wen=kw,
        name=hex_data["name"],
        trigram=hex_data["trigram"],
        judgment=hex_data["judgment"],
        judgment_text=hex_data["judgment_text"],
        changing_lines=changing,
        changing_texts=yao_texts,
        nuclear=nuclear_kw if nuclear_kw != kw else None,
        nuclear_name=nuclear_data.get("name", ""),
        nuclear_judgment=nuclear_data.get("judgment", ""),
    )


def format_iching(result: HexagramResult) -> str:
    """格式化輸出完整卜卦結果"""
    lines_out = []
    lines_out.append("═" * 44)
    lines_out.append("        🔮  易經卜卦  🔮")
    lines_out.append("═" * 44)

    lines_out.append(f"\n【請示事宜】")
    lines_out.append(f"  {result.question}")

    lines_out.append(f"\n【卦象】")
    # 上下卦象（Unicode line-by-line）
    symbols = []
    for coin in reversed(result.lines):
        if coin in (7, 9):
            symbols.append("  ⚊")  # 陽
        else:
            symbols.append("  ⚋")  # 陰
    lines_out.append(f"  上卦：{''.join(symbols[:3])}")
    lines_out.append(f"  下卦：{''.join(symbols[3:])}")

    # 爻值（從下往上）
    yao_vals = [str(c) for c in result.lines]
    lines_out.append(f"  爻值（初→上）：{', '.join(yao_vals)}")
    if result.changing_lines:
        lines_out.append(f"  動爻：第{'、'.join(map(str, result.changing_lines))}爻")

    lines_out.append(f"\n【本卦】第{result.king_wen}卦「{result.name}」{result.trigram}")
    lines_out.append(f"  卦辭：{result.judgment}")
    lines_out.append(f"  概解：{result.judgment_text}")

    # 動爻爻辭
    if result.changing_texts:
        lines_out.append(f"\n【動爻詮釋】")
        for t in result.changing_texts:
            lines_out.append(f"  {t}")

    # 互卦
    if result.nuclear and result.nuclear != result.king_wen:
        lines_out.append(f"\n【互卦】（過渡卦）")
        lines_out.append(f"  第{result.nuclear}卦「{result.nuclear_name}」")
        lines_out.append(f"  卦辭：{result.nuclear_judgment}")
        lines_out.append(f"  （事物正從本卦過渡到互卦的狀態）")

    # 簡單生活建議
    advice = _generate_simple_advice(result)
    lines_out.append(f"\n【小荷的話】")
    lines_out.append(f"  {advice}")

    lines_out.append(f"\n{'─' * 44}")
    lines_out.append("  占卜僅供參考，自己的判斷才是關鍵 💪")
    lines_out.append("═" * 44)
    return "\n".join(lines_out)


def _generate_simple_advice(result: HexagramResult) -> str:
    """根據卦象產生簡單生活建議"""
    kw = result.king_wen
    nuclear = result.nuclear
    changing_count = len(result.changing_lines)
    name = result.name

    if changing_count == 0:
        return (f"本卦「{name}」無動爻，局勢穩定。卦辭「{result.judgment}」"
                f"，表示{final_judgment_text(kw)}。")

    nuclear_name = HEXAGRAMS.get(nuclear, {}).get("name", "") if nuclear else ""

    if changing_count == 1:
        yao_pos = result.changing_lines[0]
        yao_text = result.changing_texts[0].split("：")[1] if "：" in result.changing_texts[0] else ""
        return (f"一爻變動，局勢微調。第{yao_pos}爻「{yao_text}」，"
                f"暗示此事在這個階段需要特別留意。")

    elif changing_count == 2:
        return (f"二爻變動，局勢正在重組。本卦「{name}」指引當前處境，"
                f"互卦「{nuclear_name}」預示未來方向——事物正在過渡中。")

    elif changing_count == 3:
        return (f"三爻同變，來到關鍵轉折！本卦「{name}」顯示當前狀態，"
                f"但局勢即將大幅改變，仔細觀察再行動。")

    elif changing_count == 6:
        return "⚠️ 六爻皆動，這是極強的轉變信號！局勢將完全翻轉。"

    elif changing_count in (4, 5):
        return (f"{changing_count}爻同變，本卦「{name}」顯示局勢複雜多變。"
                f"建議暫緩行動，多觀察一段時間再決定。")

    return f"本卦「{name}」，{final_judgment_text(kw)}。"




def final_judgment_text(kw: int) -> str:
    """根據卦象類型給出簡單的判斷傾向（輔助建議用）"""
    judgments = {
        1: "萬事亨通，可大膽前進", 2: "柔中求進，穩步發展",
        3: "起初艱難，但蘊含機遇", 4: "蒙昧不明，需虛心求教",
        5: "耐心等待，時機將至", 6: "爭訴訟說，宜謀和解",
        7: "領導得當，仗義行事", 8: "親近輔助，團結得力",
        9: "小有積蓄，蓄勢待發", 10: "謹慎行事，危機潛藏",
        11: "諸事通達，大吉之兆", 12: "陰陽不交，保守為宜",
        13: "與人同心，合作有利", 14: "大豐收，大吉之象",
        15: "謙虛待人，必有善終", 16: "預備充足，師出有名",
        17: "隨緣而動，順勢而為", 18: "整頓革新，轉機將至",
        19: "領導來臨，警惕八月", 20: "靜觀其變，誠心待時",
        21: "明斷是非，執行力強", 22: "修飾外表，小事先進",
        23: "剝落衰退，保守為宜", 24: "恢復生機，陽氣漸長",
        25: "循正道行，不投機取巧", 26: "厚積薄發，大有可為",
        27: "養生待時，蓄德修性", 28: "太過剛強，預防危險",
        29: "重重險難，心誠可通", 30: "光明依附，美善繁盛",
        31: "感應交流，情緣來臨", 32: "持之以恆，長久穩定",
        33: "退隱保存，伺機而動", 34: "勢力壯大，守正為宜",
        35: "晉升高升，名利雙收", 36: "小人當道，韜光養晦",
        37: "家庭和樂，各安其位", 38: "乖離對立，小事可成",
        39: "前路艱難，貴人相助", 40: "解除困難，遲早皆吉",
        41: "減損自身，反而得益", 42: "增益助益，行動有利",
        43: "果斷決策，預防小人", 44: "邂逅相遇，警惕女色",
        45: "相聚一堂，團結有利", 46: "步步高升，南方更佳",
        47: "困厄之時，心誠口慎", 48: "源源不絕，修養自身",
        49: "改革創新，時機成熟", 50: "重心穩定，嶄新開始",
        51: "震動來臨，驚而不慌", 52: "靜止不動，適可而止",
        53: "漸進發展，女歸大吉", 54: "嫁娶之事，不宜輕舉",
        55: "豐盛繁榮，如日當空", 56: "旅行在外，謹慎小亨",
        57: "順風行事，柔中帶剛", 58: "喜悅和諧，人際和睦",
        59: "渙散重聚，團結有利", 60: "節制節約，過度則凶",
        61: "心中誠信，小物也吉", 62: "小過難免，大事不宜",
        63: "功成圓滿，慎終如始", 64: "未竟之功，需慎行事",
    }
    return judgments.get(kw, "依卦象行事")


def consult(question: str) -> HexagramResult:
    """對任意問題進行一次卜卦（使用亂數硬幣）"""
    lines = toss_six_coins()
    fuxi = coins_to_fuxi(lines)
    kw = fuxi_to_kingwen(fuxi)
    hex_data = HEXAGRAMS[kw]
    nuclear_fuxi = 63 - fuxi
    nuclear_kw = fuxi_to_kingwen(nuclear_fuxi)
    nuclear_data = HEXAGRAMS.get(nuclear_kw, {})

    changing = get_changing_lines(lines)

    # 爻辭
    yao_texts = []
    yao_data = YAO_TEXTS.get(kw, {})
    for pos in changing:
        yao_texts.append(f"第{pos}爻：「{yao_data.get(pos, GENERIC_YAO.get(pos, '靜待時機'))}」")

    return HexagramResult(
        question=question,
        lines=lines,
        king_wen=kw,
        name=hex_data["name"],
        trigram=hex_data["trigram"],
        judgment=hex_data["judgment"],
        judgment_text=hex_data["judgment_text"],
        changing_lines=changing,
        changing_texts=yao_texts,
        nuclear=nuclear_kw if nuclear_kw != kw else None,
        nuclear_name=nuclear_data.get("name", ""),
        nuclear_judgment=nuclear_data.get("judgment", ""),
    )


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if not args:
        print("用法：")
        print("  python iching_calculator.py <問題>")
        print("範例：")
        print("  python iching_calculator.py 最近工作會順利嗎")
        sys.exit(1)

    question = " ".join(args)
    result = consult(question)
    print(format_iching(result))