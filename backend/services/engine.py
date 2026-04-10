# -*- coding: utf-8 -*-
"""
命理核心引擎
100% 确定性规则，无 LLM 依赖
"""
import math
import datetime
from typing import Dict, List, Tuple, Any

# ─────────────────────────────────────────────
# 常量表
# ─────────────────────────────────────────────
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

WUXING_GAN = {"甲": "木", "乙": "木", "丙": "火", "丁": "火",
              "戊": "土", "己": "土", "庚": "金", "辛": "金",
              "壬": "水", "癸": "水"}
WUXING_ZHI = {"子": "水", "丑": "土", "寅": "木", "卯": "木",
              "辰": "土", "巳": "火", "午": "火", "未": "土",
              "申": "金", "酉": "金", "戌": "土", "亥": "水"}

YINYANG_GAN = {"甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴",
               "戊": "阳", "己": "阴", "庚": "阳", "辛": "阴",
               "壬": "阳", "癸": "阴"}

JIAZI = [g + d for g in TIANGAN for d in DIZHI]  # 60甲子循环

# 地支藏干（简化）
ZANGAN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}

# 六爻卦名表（64卦，上卦+下卦→名称映射）
GUA_64_MAP = {
    ("乾", "乾"): "乾", ("乾", "兑"): "大有", ("乾", "离"): "大壮",
    ("乾", "震"): "小畜", ("乾", "巽"): "需", ("乾", "坎"): "大畜",
    ("乾", "艮"): "泰", ("乾", "坤"): "履",
    ("兑", "乾"): "兑", ("兑", "兑"): "睽", ("兑", "离"): "归妹",
    ("兑", "震"): "中孚", ("兑", "巽"): "节", ("兑", "坎"): "损",
    ("兑", "艮"): "临", ("兑", "坤"): "萃",
    ("离", "乾"): "离", ("离", "兑"): "同人", ("离", "离"): "革",
    ("离", "震"): "丰", ("离", "巽"): "家人", ("离", "坎"): "既济",
    ("离", "艮"): "贲", ("离", "坤"): "明夷",
    ("震", "乾"): "震", ("震", "兑"): "豫", ("震", "离"): "解",
    ("震", "震"): "恒", ("震", "巽"): "升", ("震", "坎"): "井",
    ("震", "艮"): "大过", ("震", "坤"): "随",
    ("巽", "乾"): "巽", ("巽", "兑"): "小过", ("巽", "离"): "旅",
    ("巽", "震"): "咸", ("巽", "巽"): "渐", ("巽", "坎"): "蹇",
    ("巽", "艮"): "涣", ("巽", "坤"): "讼",
    ("坎", "乾"): "坎", ("坎", "兑"): "师", ("坎", "离"): "解",
    ("坎", "震"): "困", ("坎", "巽"): "未济", ("坎", "坎"): "蒙",
    ("坎", "艮"): "涣", ("坎", "坤"): "讼",
    ("艮", "乾"): "艮", ("艮", "兑"): "贲", ("艮", "离"): "大蓄",
    ("艮", "震"): "损", ("艮", "巽"): "睽", ("艮", "坎"): "履",
    ("艮", "艮"): "中孚", ("艮", "坤"): "渐",
    ("坤", "乾"): "坤", ("坤", "兑"): "比", ("坤", "离"): "剥",
    ("坤", "震"): "观", ("坤", "巽"): "豫", ("坤", "坎"): "晋",
    ("坤", "艮"): "萃", ("坤", "坤"): "否",
}

# 八卦符号映射
GUA_SYMBOL = {
    "乾": "☰", "兑": "☱", "离": "☲", "震": "☳",
    "巽": "☴", "坎": "☵", "艮": "☶", "坤": "☷"
}

# 八卦五行
GUA_WUXING = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土"
}

# 梅花卦象分析
GUA_ANALYSIS = {
    "乾": "刚健进取，天道循环。", "坤": "柔顺包容，大地承载。",
    "屯": "始生艰难，利于根基。", "蒙": "蒙昧初始，尊师则吉。",
    "需": "需待时机，有信则通。", "讼": "争论诉讼，宜和解。",
    "师": "众兵兴师，宜慎用兵。", "比": "亲比依附，选贤与能。",
    "小畜": "小有畜积，宜守待机。", "履": "踩虎尾，需谨慎。",
    "泰": "天地交泰，万物通达。", "否": "天地不交，闭塞不通。",
    "同人": "与人同心，利于大事。", "大有": "大有所获，宜守成。",
    "谦": "谦受益，满招损。", "豫": "喜逸豫乐，需戒备。",
    "随": "随从顺势，宜从吉。", "蛊": "事有弊端，拨乱反正。",
    "临": "临近督导，择善而从。", "观": "观察审视，择主而事。",
    "噬嗑": "刑罚明断，除奸去恶。", "贲": "文饰外表，返朴归真。",
    "剥": "剥落衰败，宜守不宜进。", "复": "复归本原，宜积蓄。",
    "无妄": "无妄为，顺势而行。", "大畜": "大有所蓄，待时而发。",
    "颐": "颐养饮食，宜自养德。", "大过": "大有过越，需谨慎。",
    "坎": "坎陷险难，宜守正道。", "咸": "感应交心，宜婚嫁。",
    "恒": "恒久不变，宜守常。", "遁": "退隐待机，宜蛰伏。",
    "大壮": "壮而有力，宜守正。", "晋": "晋升进步，宜进取。",
    "明夷": "明入地中，宜韬光养晦。", "家人": "家人相亲，宜齐家。",
    "睽": "睽违离散，宜和同。", "蹇": "蹇难阻碍，宜待时。",
    "解": "解除困难，宜行动。", "损": "损己益人，宜布施。",
    "益": "增益利益，宜进取。", "夬": "决断果决，宜速行。",
    "姤": "邂逅相遇，宜慎始。", "萃": "聚集荟萃，宜用人。",
    "升": "上升进步，宜进取。", "困": "困境艰难，宜守正。",
    "井": "井养无穷，宜守成。", "革": "变革革新，宜顺势。",
    "鼎": "鼎新立业，宜创建。", "震": "震动惊雷，宜警觉。",
    "艮": "艮止静止，宜止行。", "渐": "渐进有序，宜积累。",
    "归妹": "归妹婚配，宜守礼。", "丰": "丰盛广大，宜守成。",
    "旅": "旅行在外，宜小心。", "巽": "巽顺入心，宜谦逊。",
    "兑": "兑悦和洽，宜和众。", "涣": "涣散离散，宜凝聚。",
    "节": "节制节约，宜守度。", "中孚": "心中诚信，宜守信。",
    "小过": "小有过越，宜谨慎。", "既济": "事已成功，宜守成。",
    "未济": "事未成功，宜待时。",
}


# ─────────────────────────────────────────────
# 核心算法
# ─────────────────────────────────────────────

def solar_to_jd(year: int, month: int, day: int, hour: int = 12) -> float:
    """公历转儒略日"""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    return (int(365.25 * (year + 4716)) +
            int(30.6001 * (month + 1)) +
            day + hour / 24.0 + B - 1524.5)


def jd_to_solar(jd: float) -> Tuple[int, int, int]:
    """儒略日转公历"""
    jd += 0.5
    Z = int(jd)
    F = jd - Z
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E)
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715
    return year, month, day


def solar_to_lunar(year: int, month: int, day: int) -> Tuple[int, int, int, int]:
    """
    简化公历转农历
    返回 (闰月, 月, 日, 干支年序号)
    """
    # 以2000年1月6日为甲子日（第0天）推算
    base_jd = 2451550.0  # 2000/1/6 00:00 的 JD
    target_jd = solar_to_jd(year, month, day)
    days_diff = int(target_jd - base_jd)

    # 干支年：每60年一循环
    ganzhi_year_idx = days_diff // 360  # 粗略估算
    # 精确：用已知春节干支反推
    # 简化：用春节分界
    spring_month = 2  # 农历新年大致在公历2月
    spring_day = 4
    # 以春节为界调整
    if month < spring_month or (month == spring_month and day < spring_day):
        ganzhi_year_idx -= 1

    # 干支年序号（0-59）
    gz_idx = ganzhi_year_idx % 60
    # 农历月（简化）
    lunar_month = month  # 实际需要查农历表，此处用近似
    # 干支日
    ganzhi_day_idx = days_diff % 60
    return 0, month, day, gz_idx


def get_year_zhu(year: int) -> str:
    """年柱干支（简化：以春节为分界）"""
    base_year = 1984  # 甲子年
    offset = year - base_year
    idx = offset % 60
    if idx < 0:
        idx += 60
    return JIAZI[idx]


def get_month_zhu(year_gan: str, month: int) -> str:
    """月柱干支"""
    # 五虎遁：年起月表
    month_gan_table = {
        "甲": 2, "乙": 3, "丙": 4, "丁": 5, "戊": 6,
        "己": 7, "庚": 8, "辛": 9, "壬": 10, "癸": 0
    }
    gan_idx = month_gan_table.get(year_gan, 0)
    idx = (gan_idx + month - 1) % 10
    month_zhi_idx = (month + 1) % 12  # 以寅月为正月
    if month_zhi_idx == 0:
        month_zhi_idx = 12
    # 月干
    month_gan = TIANGAN[idx]
    # 月支
    month_zhi = DIZHI[(month + 1) % 12]
    return month_gan + month_zhi


def get_day_zhu(year: int, month: int, day: int) -> str:
    """日柱干支"""
    base_jd = 2451550.0  # 2000/1/6 = 甲子日
    target_jd = solar_to_jd(year, month, day)
    days_diff = int(target_jd - base_jd)
    idx = days_diff % 60
    if idx < 0:
        idx += 60
    return JIAZI[idx]


def get_time_zhu(hour: int) -> str:
    """时柱干支（五鼠遁：日起时）"""
    # 以子时0点为起点
    time_zhi_idx = (hour + 1) // 2 % 12  # 每2小时一个时辰
    time_gan_table = {
        0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0,
        6: 2, 7: 4, 8: 6, 9: 8, 10: 0, 11: 2,
        12: 4, 13: 6, 14: 8, 15: 0, 16: 2, 17: 4,
        18: 6, 19: 8, 20: 0, 21: 2, 22: 4, 23: 6
    }
    # 更精确的算法
    time_zhi_idx = hour // 2 % 12
    gan_idx = (time_zhi_idx * 2 + 2) % 10  # 以甲日子时为0
    return TIANGAN[gan_idx] + DIZHI[time_zhi_idx]


def calc_wuxing_score(year_zhu: str, month_zhu: str, day_zhu: str, time_zhu: str) -> Dict[str, float]:
    """五行得分"""
    score = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}
    pillars = [year_zhu, month_zhu, day_zhu, time_zhu]
    for p in pillars:
        if len(p) >= 2:
            g = p[0]
            z = p[1]
            wg = WUXING_GAN.get(g, "")
            wz = WUXING_ZHI.get(z, "")
            if wg:
                score[wg] = score.get(wg, 0.0) + 2.0
            if wz:
                score[wz] = score.get(wz, 0.0) + 1.0
    return score


def judge_strong_weak(wuxing_scores: Dict[str, float], month_zhi: str) -> str:
    """判断日主旺衰"""
    day_wuxing = WUXING_ZHI.get(month_zhi, "土")
    total = sum(wuxing_scores.values())
    if total == 0:
        return "弱"
    day_score = wuxing_scores.get(day_wuxing, 0)
    ratio = day_score / total if total > 0 else 0
    month_wuxing = WUXING_ZHI.get(month_zhi, "土")
    # 月令加权
    yueling = wuxing_scores.get(month_wuxing, 0)
    if yueling >= 3 and ratio >= 0.4:
        return "强"
    elif yueling <= 1 and ratio <= 0.2:
        return "弱"
    elif ratio >= 0.35:
        return "偏强"
    elif ratio <= 0.15:
        return "偏弱"
    return "中和"


def calc_shishen(day_gan: str, year_zhu: str, month_zhu: str, time_zhu: str) -> List[Dict]:
    """计算十神"""
    result = []
    positions = [("年柱", year_zhu), ("月柱", month_zhu), ("时柱", time_zhu)]
    day_element = WUXING_GAN.get(day_gan, "")
    shishen_map = {
        "木": {"木": "比肩", "火": "食神", "土": "伤官", "金": "偏财", "水": "正财"},
        "火": {"木": "正印", "火": "比肩", "土": "食神", "金": "伤官", "水": "偏财"},
        "土": {"木": "偏印", "火": "正印", "土": "比肩", "金": "食神", "水": "伤官"},
        "金": {"木": "正官", "火": "偏官", "土": "正印", "金": "比肩", "水": "食神"},
        "水": {"木": "偏官", "火": "正官", "土": "偏印", "金": "正印", "水": "比肩"},
    }
    for pos, zhu in positions:
        if len(zhu) < 2:
            continue
        g, z = zhu[0], zhu[1]
        wx = WUXING_GAN.get(g, "")
        # 十神关系：同我者比劫，我生者食伤，我克者财，克我者官杀，生我者印枭
        sx_map = shishen_map.get(day_element, {})
        sx = sx_map.get(wx, "")
        result.append({
            "position": pos,
            "gan": g,
            "shishen": sx,
            "wuxing": wx
        })
    return result


def judge_geju(day_gan: str, shishen_list: List[Dict], strong_weak: str) -> Dict:
    """判断格局"""
    month_shishen = next((s for s in shishen_list if s["position"] == "月柱"), None)
    if not month_shishen:
        return {"name": "正格", "level": "中"}
    ss = month_shishen["shishen"]
    # 官杀格
    if ss in ["正官", "七杀"]:
        if strong_weak in ["强", "偏强"]:
            return {"name": "官杀格", "level": "高"}
        else:
            return {"name": "官杀格", "level": "中"}
    # 财格
    elif ss in ["正财", "偏财"]:
        return {"name": "财格", "level": "高" if strong_weak in ["弱", "偏弱"] else "中"}
    # 印格
    elif ss in ["正印", "偏印"]:
        return {"name": "印格", "level": "高" if strong_weak in ["强", "偏强"] else "中"}
    # 食伤格
    elif ss in ["食神", "伤官"]:
        return {"name": "食伤格", "level": "中"}
    # 比劫格
    elif ss in ["比肩", "劫财"]:
        return {"name": "比劫格", "level": "低"}
    return {"name": "正格", "level": "中"}


def calc_xiyongshen(wuxing_scores: Dict, strong_weak: str) -> Tuple[List[str], List[str]]:
    """用神忌神"""
    wx_elements = ["木", "火", "土", "金", "水"]
    # 找最弱和最强的
    sorted_wx = sorted(wuxing_scores.items(), key=lambda x: x[1])
    if strong_weak in ["弱", "偏弱"]:
        # 扶抑：生身者为用，克身为忌
        xiyong = [sorted_wx[0][0], sorted_wx[1][0]] if len(sorted_wx) >= 2 else [sorted_wx[0][0]]
        jishen = [sorted_wx[-1][0]]
    else:
        # 调候：旺者泄之
        xiyong = [sorted_wx[-1][0]]
        jishen = [sorted_wx[0][0]]
    return xiyong[:2], jishen[:2]


def calc_dayun(day_zhu: str, birth_year: int, gender: str, count: int = 10) -> List[Dict]:
    """计算大运"""
    result = []
    day_idx = JIAZI.index(day_zhu) if day_zhu in JIAZI else 0
    for i in range(count):
        idx = (day_idx + i + 1) % 60
        gz = JIAZI[idx]
        age = birth_year + (i * 10) + 5
        result.append({
            "step": i + 1,
            "ganzhi": gz,
            "wuxing": WUXING_GAN.get(gz[0], ""),
            "age_start": age
        })
    return result


def calc_liuniian(birth_year: int, birth_month: int, day_zhu: str, count: int = 20) -> List[Dict]:
    """计算流年"""
    result = []
    day_idx = JIAZI.index(day_zhu) if day_zhu in day_zhu else 0
    current_year = datetime.datetime.now().year
    for i in range(count):
        year = current_year - 10 + i
        offset = year - birth_year
        idx = (day_idx + offset) % 60
        gz = JIAZI[idx]
        result.append({
            "year": year,
            "ganzhi": gz,
            "wuxing": WUXING_GAN.get(gz[0], ""),
            "score": 50 + hash(gz) % 40
        })
    return result


def time_gua(year: int, month: int, day: int, hour: int, gender: str = "男") -> Dict:
    """梅花易数时间起卦"""
    # 上卦
    upper_num = (year % 100 + month + day) % 8
    if upper_num == 0:
        upper_num = 8
    upper_gua = ["乾", "坤", "震", "坎", "艮", "乾", "兑", "离", "巽"][upper_num - 1] if upper_num <= 8 else "乾"

    # 下卦
    lower_num = (year % 100 + month + day + hour) % 8
    if lower_num == 0:
        lower_num = 8
    lower_gua = ["乾", "坤", "震", "坎", "艮", "乾", "兑", "离", "巽"][lower_num - 1] if lower_num <= 8 else "坤"

    # 卦名
    gua_name = GUA_64_MAP.get((upper_gua, lower_gua), upper_gua + lower_gua)

    # 动爻（上下之和 mod 6，为0则用6）
    dong_yao = (year % 100 + month + day + hour) % 6
    if dong_yao == 0:
        dong_yao = 6

    # 变卦
    upper_idx = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"].index(upper_gua) if upper_gua in ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"] else 0
    lower_idx = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"].index(lower_gua) if lower_gua in ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"] else 0
    change_upper_idx = upper_idx
    change_lower_idx = lower_idx
    # 动爻位（从下往上数：1=初，6=上）
    # dong_yao = 1 means bottom line moves
    yao_positions = ["初", "二", "三", "四", "五", "上"]
    dong_pos = yao_positions[dong_yao - 1] if dong_yao <= 6 else "上"

    # 简化：动哪一爻，该爻阴阳互换即为变卦
    # 这里用动爻+1的位置确定变卦名（简化处理）
    change_idx = dong_yao % 8
    change_lower_gua = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"][change_idx]
    change_upper_gua = upper_gua
    change_gua_name = GUA_64_MAP.get((change_upper_gua, change_lower_gua), gua_name + "之" + change_lower_gua)

    # 五行
    element = GUA_WUXING.get(lower_gua, "土")

    # 卦象分析
    analysis = GUA_ANALYSIS.get(gua_name, "卦象分析待定。")

    return {
        "original_gua": gua_name,
        "upper_gua": upper_gua,
        "lower_gua": lower_gua,
        "change_gua": change_gua_name,
        "element": element,
        "dong_yao": dong_yao,
        "dong_pos": dong_pos,
        "yaoci": f"第{dong_yao}爻动",
        "analysis": analysis,
        "symbol": GUA_SYMBOL.get(upper_gua, "☰") + GUA_SYMBOL.get(lower_gua, "☷")
    }


# ─────────────────────────────────────────────
# 主排盘函数
# ─────────────────────────────────────────────

def bazi_pan(year: int, month: int, day: int, hour: int,
             gender: str = "男", location: str = "北京") -> Dict[str, Any]:
    """八字排盘主函数"""
    year_zhu = get_year_zhu(year)
    month_zhu = get_month_zhu(year_zhu[0], month)
    day_zhu = get_day_zhu(year, month, day)
    time_zhu = get_time_zhu(hour)

    pillar = {
        "year": year_zhu,
        "month": month_zhu,
        "day": day_zhu,
        "time": time_zhu,
    }

    # 五行
    wuxing_scores = calc_wuxing_score(year_zhu, month_zhu, day_zhu, time_zhu)
    strong_weak = judge_strong_weak(wuxing_scores, month_zhu[1])
    # wuxing_scores 只含数值，strong_weak 单独存
    _score_copy = dict(wuxing_scores)

    # 十神
    shishen_list = calc_shishen(day_zhu[0], year_zhu, month_zhu, time_zhu)

    # 格局
    geju = judge_geju(day_zhu[0], shishen_list, strong_weak)

    # 用神忌神（用数值副本）
    xiyongshen, jishen = calc_xiyongshen(_score_copy, strong_weak)

    # 大运
    dayun = calc_dayun(day_zhu, year, gender)

    # 流年
    liunian = calc_liuniian(year, month, day_zhu)

    # 六爻
    gua_result = time_gua(year, month, day, hour, gender)

    return {
        "pillar": pillar,
        "wuxing": {
            "score": wuxing_scores,
            "strong_weak": strong_weak,
            "xiyongshen": xiyongshen,
            "jishen": jishen
        },
        "shishen": {
            "day_master": day_zhu[0],
            "positions": shishen_list
        },
        "geju": geju,
        "dayun": dayun,
        "liunian": liunian,
        "gua": gua_result,
        "birth_info": {
            "year": year, "month": month, "day": day, "hour": hour,
            "gender": gender, "location": location
        }
    }


def build_llm_prompt(pillar_result: Dict, ask: str = "", style: str = "professional") -> Tuple[str, str]:
    """构建 LLM 解读 Prompt"""
    pillar = pillar_result["pillar"]
    wuxing = pillar_result["wuxing"]
    shishen = pillar_result["shishen"]
    geju = pillar_result["geju"]
    dayun = pillar_result["dayun"]
    gua = pillar_result.get("gua", {})

    dayun_str = "、".join([f"{d['step']}步{d['ganzhi']}" for d in dayun[:5]])

    style_desc = {
        "professional": "严谨、文明、理性、人文向，200-400字，专业命理术语",
        "simple": "简洁明了，100字以内，通俗易懂",
        "plain": "通俗语言，200字，有温度的解读"
    }
    style_text = style_desc.get(style, style_desc["professional"])

    system_prompt = f"""你是专业传统命理分析师。
请根据以下结构化八字数据，进行严谨、文明、理性、人文向的解读。
不恐吓、不封建迷信、不绝对化。
只基于五行、格局、十神、喜用神逻辑推演。
输出应通顺、专业、可阅读。
风格：{style_text}"""

    user_prompt = f"""八字结构：
年柱{pillar['year']}、月柱{pillar['month']}、日柱{pillar['day']}、时柱{pillar['time']}

五行分布：木：{wuxing['score'].get('木',0)}分、火：{wuxing['score'].get('火',0)}分、土：{wuxing['score'].get('土',0)}分、金：{wuxing['score'].get('金',0)}分、水：{wuxing['score'].get('水',0)}分，日主{wuxing['strong_weak']}

格局：{geju['name']}（{geju['level']}级）

用神喜神：用神：{'、'.join(wuxing['xiyongshen'])}；忌神：{'、'.join(wuxing['jishen'])}

大运：{dayun_str}

{'六爻卦：' + gua.get('original_gua','') + '，' + gua.get('yaoci','') + '，' + gua.get('analysis','') if gua else ''}

{'用户提问：' + ask if ask else '请给出整体性格、事业方向与建议性解读。'}"""

    return system_prompt, user_prompt

# -*- coding: utf-8 -*-
# This file is appended to backend/services/engine.py
# DO NOT import this file directly

# ═══════════════════════════════════════════════════════════════════
# 紫微斗数引擎
# ═══════════════════════════════════════════════════════════════════

# 紫微斗数14颗主星
ZIWEI_MAIN_STARS = [
    "紫微", "天机", "太阳", "武曲", "天同",
    "廉贞", "天府", "太阴", "贪狼", "巨门",
    "天相", "天梁", "七杀", "破军"
]

# 紫微斗数12宫位顺序
ZIWEI_PALACES = [
    "命宫", "兄弟", "夫妻", "子女",
    "财帛", "疾厄", "迁移", "仆役",
    "官禄", "田宅", "福德", "父母"
]

# 十二地支对应紫微斗数宫位
ZIWEI_GAN_ZHI_PALACE = {
    "子": 0, "丑": 1, "寅": 2, "卯": 3,
    "辰": 4, "巳": 5, "午": 6, "未": 7,
    "申": 8, "酉": 9, "戌": 10, "亥": 11
}

# 五行局（水二、木三、金四、土五、火六）
WUXING_JU_MAP = {
    "甲": "木三局", "乙": "木三局",
    "丙": "火六局", "丁": "火六局",
    "戊": "土五局", "己": "土五局",
    "庚": "金四局", "辛": "金四局",
    "壬": "水二局", "癸": "水二局"
}


def _place_stars(life_palace_idx: int) -> dict:
    """安14主星到12宫位，返回 {星名: 宫位索引}"""
    result = {}
    # 按固定顺序从命宫逆时针安星（紫微在命宫起逆数）
    star_order = [
        ("紫微", 0), ("天机", 1), ("太阳", 2), ("武曲", 3), ("天同", 4),
        ("廉贞", 5), ("天府", 6), ("太阴", 7), ("贪狼", 8), ("巨门", 9),
        ("天相", 10), ("天梁", 11), ("七杀", 12), ("破军", 13),
    ]
    for star, offset in star_order:
        palace_idx = (life_palace_idx - offset) % 12
        result[star] = palace_idx
    return result


def ziwei_pan(year: int, month: int, day: int, hour: int, gender: str) -> dict:
    """
    紫微斗数排盘
    参数：出生年月日时分，性别
    返回：14主星位置、12宫位、安命身宫、五行局
    """
    year_zhu = get_year_zhu(year)
    month_zhu = get_month_zhu(year_zhu[0], month)
    day_zhu = get_day_zhu(year, month, day)
    time_zhu = get_time_zhu(hour)

    # 年干定五行局
    day_gan = day_zhu[0]
    geju = WUXING_JU_MAP.get(day_gan, "土五局")

    # 命宫起法：月支起正月，顺时针排12宫，命宫在生月地支位
    month_zhi = month_zhu[1]
    month_zhi_idx = DIZHI.index(month_zhi)

    # 以月支为命宫基数
    life_palace_idx = month_zhi_idx

    # 身宫：时支起正月顺排，身宫在生时地支位
    time_zhi = time_zhu[1]
    time_zhi_idx = DIZHI.index(time_zhi)
    body_palace_idx = time_zhi_idx

    # 安14主星（从命宫逆时针）
    star_positions = _place_stars(life_palace_idx)

    # 安12宫位（以命宫为月支，顺时针排列）
    palaces = {}
    palace_order = ZIWEI_PALACES
    for i, name in enumerate(palace_order):
        palace_zhi_idx = (life_palace_idx + i) % 12
        palace_stars = [star for star, pos in star_positions.items() if pos == palace_zhi_idx]
        palaces[name] = {
            "zhi": DIZHI[palace_zhi_idx],
            "stars": palace_stars
        }

    # 命宫和身宫特殊处理
    for pname in ["命宫", "身宫"]:
        if pname not in palaces:
            palaces[pname] = {"zhi": "", "stars": []}

    # 星曜组合分析
    star_combos = _analyze_star_combinations(star_positions, palaces)

    # 流年星曜
    liunian_stars = _calc_ziwei_liunian(year_zhu, year)

    return {
        "geju": geju,
        "life_palace": life_palace_idx,
        "body_palace": body_palace_idx,
        "stars": {star: int(idx) for star, idx in star_positions.items()},
        "palaces": palaces,
        "star_combinations": star_combos,
        "liunian_stars": liunian_stars,
        "birth_pillar": {
            "year": year_zhu, "month": month_zhu,
            "day": day_zhu, "time": time_zhu
        },
        "gender": gender,
        "analysis": {
            "personality": _ziwei_personality_analysis(star_positions, life_palace_idx),
            "career": _ziwei_career_analysis(star_positions),
            "wealth": _ziwei_wealth_analysis(star_positions),
            "marriage": _ziwei_marriage_analysis(star_positions),
        }
    }


def _analyze_star_combinations(star_positions: dict, palaces: dict) -> dict:
    """分析主要星曜组合"""
    results = {}
    life_idx = palaces.get("命宫", {}).get("zhi", "")
    life_stars = [s for s, p in star_positions.items() if s in palaces.get("命宫", {}).get("stars", [])]
    life_stars = palaces.get("命宫", {}).get("stars", [])

    if "紫微" in star_positions:
        results["紫微星"] = "紫微坐命，主人尊崇端庄，有领导统御之才。"
    if "天府" in star_positions:
        results["天府星"] = "天府守命，主人稳重保守，理财有方。"
    if "廉贞" in star_positions:
        results["廉贞星"] = "廉贞星曜，性刚硬朗，利于武职。"
    if "贪狼" in star_positions:
        results["贪狼星"] = "贪狼星入命，主人多才多艺，欲望心重。"
    if "紫微" in star_positions and "天府" in star_positions:
        if star_positions["紫微"] == star_positions["天府"]:
            results["双星组合"] = "紫微天府同宫，极为吉美，富贵双全。"
    return results


def _ziwei_personality_analysis(star_positions: dict, life_idx: int) -> str:
    """紫微性格分析"""
    life_stars = [s for s, p in star_positions.items() if p == life_idx]
    if "紫微" in life_stars:
        return "命带紫微星，主人具有领袖气质，志向高远，做事有条理，重权威。"
    elif "天机" in life_stars:
        return "命带天机星，主人聪明机敏，思维灵活，善于策划和思考。"
    elif "太阳" in life_stars:
        return "命带太阳星，主人热情开朗，光明磊落，乐于助人。"
    elif "武曲" in life_stars:
        return "命带武曲星，主人刚毅果断，善于理财，适合从事实业。"
    else:
        return "命宫星曜组合平和，主人性格稳重，适应力强。"


def _ziwei_career_analysis(star_positions: dict) -> str:
    """紫微事业分析"""
    # 官禄宫在palace_order中是第8位（索引8）
    career_idx = 8
    career_stars = [s for s, p in star_positions.items() if p == career_idx]
    if "紫微" in career_stars:
        return "官禄宫紫微星临照，宜从政、管理、领导类工作，有晋升发展之运。"
    elif "武曲" in career_stars:
        return "官禄宫武曲星坐守，宜从事实业、金融、工程等技术性工作。"
    elif "太阳" in career_stars:
        return "官禄宫太阳星明亮，宜从事教育、传播、文化、公益事业。"
    elif "天机" in career_stars:
        return "官禄宫天机星临照，宜从事策划、智库、学术研究类工作。"
    return "官禄宫星曜配置中等，事业平稳发展，需把握时机。"


def _ziwei_wealth_analysis(star_positions: dict) -> str:
    """紫微财运分析"""
    # 财帛宫在palace_order中是第4位（索引4）
    wealth_idx = 4
    wealth_stars = [s for s, p in star_positions.items() if p == wealth_idx]
    if "武曲" in wealth_stars:
        return "财帛宫武曲星守，财运旺盛，善于理财，适合创业投资。"
    elif "天府" in wealth_stars:
        return "财帛宫天府星临照，财库充盈，善于积蓄，理财有方。"
    elif "贪狼" in wealth_stars:
        return "财帛宫贪狼星入，财来财去，欲望心强，适合商业贸易。"
    return "财帛宫星曜配置平稳，财运稳定，需努力积累。"


def _ziwei_marriage_analysis(star_positions: dict) -> str:
    """紫微婚姻分析"""
    # 夫妻宫在palace_order中是第2位（索引2）
    marriage_idx = 2
    marriage_stars = [s for s, p in star_positions.items() if p == marriage_idx]
    if "紫微" in marriage_stars:
        return "夫妻宫紫微星坐守，配偶地位较高，婚姻稳重，需尊重对方。"
    elif "天府" in marriage_stars:
        return "夫妻宫天府星临照，配偶稳重可靠，婚姻和谐。"
    elif "贪狼" in marriage_stars:
        return "夫妻宫贪狼星入，配偶热情浪漫，感情丰富，需防范桃花。"
    elif "天同" in marriage_stars:
        return "夫妻宫天同星坐守，配偶温和体贴，婚姻幸福美满。"
    return "夫妻宫星曜配置一般，婚姻平稳发展。"


def _calc_ziwei_liunian(year_zhu: str, target_year: int) -> dict:
    """计算流年星曜（小限）"""
    gan = year_zhu[0]
    year_offset = (target_year - 2024) % 12
    star_list = [
        "太阴", "巨门", "贪狼", "禄存", "文昌", "擎羊",
        "陀罗", "火星", "天机", "天梁", "文曲", "七杀"
    ]
    current_star = star_list[year_offset % len(star_list)]
    return {
        "year": target_year,
        "zhi_year": DIZHI[year_offset % 12],
        "limiting_star": current_star,
        "note": f"流年小限星：{current_star}星值年"
    }


# ═══════════════════════════════════════════════════════════════════
# 奇门遁甲引擎
# ═══════════════════════════════════════════════════════════════════

# 九宫格布局（洛书数字对应宫位）
QIMEN_GONG_WEI = {
    1: {"name": "坎一宫", "zhi": "子", "wx": "水"},
    2: {"name": "坤二宫", "zhi": "未申", "wx": "土"},
    3: {"name": "震三宫", "zhi": "卯", "wx": "木"},
    4: {"name": "巽四宫", "zhi": "辰巳", "wx": "木"},
    5: {"name": "中五宫", "zhi": "", "wx": "土"},
    6: {"name": "乾六宫", "zhi": "戌亥", "wx": "金"},
    7: {"name": "兑七宫", "zhi": "酉", "wx": "金"},
    8: {"name": "艮八宫", "zhi": "丑寅", "wx": "土"},
    9: {"name": "离九宫", "zhi": "午", "wx": "火"},
}

# 八门
QIMEN_MEN = ["休", "生", "伤", "杜", "景", "死", "惊", "开"]

# 八神（顺时针排列）
QIMEN_SHEN = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

# 九星
QIMEN_XING = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]


def _get_xunkong(day_zhu: str) -> list:
    """计算旬空宫位名"""
    gan = day_zhu[0]
    zhi = day_zhu[1]
    gan_idx = TIANGAN.index(gan)
    zhi_idx = DIZHI.index(zhi)
    xk1 = (gan_idx - zhi_idx) % 12
    xk2 = (xk1 + 1) % 12
    result = []
    zhi_names = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    for i in [xk1, xk2]:
        for gong_num, info in QIMEN_GONG_WEI.items():
            if info["zhi"] and zhi_names[i] in info["zhi"]:
                result.append(info["name"])
                break
    return result[:2]


def _get_horse_star(month_zhi: str) -> str:
    """计算驿马星"""
    ma_map = {"寅": "申", "申": "寅", "巳": "亥", "亥": "巳", "亥": "巳"}
    return ma_map.get(month_zhi, "")


def qimen_pan(year: int, month: int, day: int, hour: int) -> dict:
    """
    奇门遁甲排盘
    参数：年月日时分
    返回：九宫格布局、八门、八神、九星、旬空、马星
    """
    year_zhu = get_year_zhu(year)
    month_zhu = get_month_zhu(year_zhu[0], month)
    day_zhu = get_day_zhu(year, month, day)
    time_zhu = get_time_zhu(hour)

    # 阴遁/阳遁判断（冬半年阴遁，夏半年阳遁）
    yn_dun = "阳遁" if month in [5, 6, 7, 8, 9, 10] else "阴遁"

    # 时干起九星
    time_gan = time_zhu[0]
    time_gan_idx = TIANGAN.index(time_gan)
    star_base = time_gan_idx % 9

    # 时支起八门
    time_zhi = time_zhu[1]
    time_zhi_idx = DIZHI.index(time_zhi)
    men_base = (time_zhi_idx + 1) % 8

    # 九宫布局
    # 洛书：1坎9离3震7兑4巽6乾2坤8艮
    luoshu_grid = {
        1: (0, 0), 2: (1, 1), 3: (2, 0),
        4: (2, 1), 5: (1, 0), 6: (0, 2),
        7: (1, 2), 8: (2, 2), 9: (0, 1),
    }

    palace_data = {}
    for gong_num, info in QIMEN_GONG_WEI.items():
        pos = luoshu_grid.get(gong_num, (0, 0))
        # 九星（阳遁顺排，阴遁逆排）
        if yn_dun == "阳遁":
            xing = QIMEN_XING[(star_base + gong_num - 1) % 9]
        else:
            xing = QIMEN_XING[(star_base - gong_num + 1) % 9]
        # 八门（时支起，顺排）
        men = QIMEN_MEN[(men_base + gong_num - 1) % 8]
        # 八神（值符随星）
        shen = QIMEN_SHEN[(star_base + gong_num - 1) % 8]
        palace_data[gong_num] = {
            "宫名": info["name"],
            "地支": info["zhi"],
            "五行": info["wx"],
            "九星": xing,
            "八门": men,
            "八神": shen,
        }

    # 九宫格矩阵
    grid = [[None for _ in range(3)] for _ in range(3)]
    for gong_num, pos in luoshu_grid.items():
        grid[pos[0]][pos[1]] = gong_num

    # 旬空
    xunkong = _get_xunkong(day_zhu)

    # 马星
    ma_star = _get_horse_star(month_zhu[1])

    # 整体解读
    overall = _qimen_interpret(palace_data, yn_dun)

    return {
        "yn_dun": yn_dun,
        "grid": grid,
        "palace_data": palace_data,
        "xunkong": xunkong,
        "horse_star": ma_star,
        "day_pillar": day_zhu,
        "time_pillar": time_zhu,
        "analysis": overall,
        "birth_pillar": {
            "year": year_zhu, "month": month_zhu,
            "day": day_zhu, "time": time_zhu
        },
    }


def _qimen_interpret(palace_data: dict, yn_dun: str) -> dict:
    """奇门整体解读"""
    men_meanings = {
        "休": "休门吉：利于休养、谈判、聚会。",
        "生": "生门吉：利于求财、创业、生产。",
        "伤": "伤门凶：伤灾、争执，谨慎行动。",
        "杜": "杜门中平：保密、防泄露，不利公开。",
        "景": "景门中平：利于信息、文化、宴请。",
        "死": "死门凶：诸事不利，大忌动土。",
        "惊": "惊门凶：惊恐、口舌是非，谨慎言行。",
        "开": "开门吉：诸事大吉，利开业、求官。",
    }
    xing_meanings = {
        "天蓬": "天蓬星大凶：破财、盗难，需谨慎。",
        "天芮": "天芮星凶：疾病、问题，宜学习。",
        "天冲": "天冲星中平：主动出击，有冲劲。",
        "天辅": "天辅星大吉：学业、考试、求职。",
        "天禽": "天禽星大吉：正中宫，诸事皆吉。",
        "天心": "天心星吉：求医、修行、管理。",
        "天柱": "天柱星凶：破败、灾祸，不宜妄动。",
        "天任": "天任星吉：求财、谈判，守成为上。",
        "天英": "天英星中平：文事、名誉，利求名。",
    }

    # 坎一宫为值符宫
    first = palace_data.get(1, {})
    first_men = first.get("八门", "")
    first_xing = first.get("九星", "")
    good_men = ["休", "生", "开", "景"]
    good_xing = ["天辅", "天禽", "天心", "天任"]

    judgment = "吉利" if first_men in good_men and first_xing in good_xing else \
        "中等" if first_men in good_men or first_xing in good_xing else "需谨慎"

    return {
        "type": f"{yn_dun}遁局",
        "key_palace": first.get("宫名", ""),
        "key_star": first_xing,
        "key_men": first_men,
        "star_meaning": xing_meanings.get(first_xing, ""),
        "men_meaning": men_meanings.get(first_men, ""),
        "judgment": judgment,
        "overall": f"值符宫{first.get('宫名', '')}，{first_xing}星、{first_men}门临宫，整体格局{judgment}。"
    }


# ═══════════════════════════════════════════════════════════════════
# 婚姻姻缘分析
# ═══════════════════════════════════════════════════════════════════

def marriage_analysis(pillar_result: dict) -> dict:
    """
    婚姻姻缘分析
    参数：八字排盘结果
    返回：配偶星、婚姻宫、婚恋建议
    """
    pillar = pillar_result["pillar"]
    wuxing = pillar_result["wuxing"]
    shishen = pillar_result["shishen"]

    day_gan = pillar["day"][0]
    month_zhu = pillar["month"]
    year_zhu = pillar["year"]
    gender = pillar_result.get("birth_info", {}).get("gender", "男")

    # 配偶星判断
    if gender == "男":
        cai_stars = [s for s in shishen.get("positions", []) if "财" in s.get("shishen", "")]
        spouse_detail = "; ".join([
            f"{s['position']}柱{s['gan']}为{s['shishen']}"
            for s in cai_stars[:2]
        ]) or "命局财星不明显，需待运势引动。"
        spouse_analysis = f"男命以财星为妻星。{spouse_detail}"
        direction = "东方、北方"
    else:
        guan_stars = [s for s in shishen.get("positions", []) if "官" in s.get("shishen", "")]
        spouse_detail = "; ".join([
            f"{s['position']}柱{s['gan']}为{s['shishen']}"
            for s in guan_stars[:2]
        ]) or "命局官杀星不明显，需待运势引动。"
        spouse_analysis = f"女命以官杀星为夫星。正官为正缘，七杀为偏缘。{spouse_detail}"
        direction = "西方、南方"

    # 婚姻宫分析
    month_zhi = month_zhu[1]
    wx_scores = wuxing.get("score", {})
    month_wx = WUXING_ZHI.get(month_zhi, "")
    month_score = wx_scores.get(month_wx, 0)
    if month_score >= 4:
        marriage_palace = "婚姻宫旺相，缘分较深。"
    elif month_score >= 2:
        marriage_palace = "婚姻宫平稳，缘分中等。"
    else:
        marriage_palace = "婚姻宫偏弱，早年感情易波折，中年后渐稳。"

    # 晚婚/早婚判断
    strong_weak = wuxing.get("strong_weak", "")
    xiyong = wuxing.get("xiyongshen", [])
    jishen = wuxing.get("jishen", [])

    if "官" in spouse_analysis or "财" in spouse_analysis:
        marriage_timing = "早婚倾向较强，28岁前遇到正缘可能性大。"
    elif strong_weak in ["强", "偏强"]:
        marriage_timing = "命局身强，晚婚倾向（30岁后）更有利于婚姻稳定。"
    else:
        marriage_timing = "婚姻时机中等，28-32岁结婚较适宜。"

    # 配偶年龄差
    year_gan = year_zhu[0]
    year_idx = TIANGAN.index(year_gan)
    month_idx = TIANGAN.index(month_zhu[0])
    age_diff_val = (month_idx - year_idx) % 10
    if age_diff_val <= 2:
        age_diff = "年龄相近（差1-3岁）"
    elif age_diff_val <= 5:
        age_diff = "配偶可能年长（差3-5岁）"
    else:
        age_diff = "配偶可能年幼（差3-5岁）"

    return {
        "gender": gender,
        "spouse_star_analysis": spouse_analysis,
        "marriage_palace": marriage_palace,
        "marriage_timing": marriage_timing,
        "age_difference": age_diff,
        "spouse_fangwei": f"姻缘方位：{direction}，缘分多在出生地或工作地附近。",
        "advice": _marriage_advice(shishen, wuxing, gender),
    }


def _marriage_advice(shishen: dict, wuxing: dict, gender: str) -> str:
    """婚恋建议"""
    xiyong = wuxing.get("xiyongshen", [])
    advice_list = []
    wx_dir = {"木": "东方或木旺之地", "火": "南方或火旺之地",
              "土": "本地或土旺之地", "金": "西方或金旺之地", "水": "北方或水旺之地"}
    for wx in xiyong[:2]:
        advice_list.append(f"宜在{wx_dir.get(wx, '适宜地区')}寻求姻缘。")
    if not advice_list:
        advice_list.append("保持开放心态，顺其自然，把握时机。")
    advice_list.append("注意性格磨合期，以包容理解维系婚姻关系。")
    return " ".join(advice_list)


# ═══════════════════════════════════════════════════════════════════
# 健康分析
# ═══════════════════════════════════════════════════════════════════

WUXING_ORGANS = {
    "木": {"yin": "肝", "yang": "胆", "note": "肝胆代谢"},
    "火": {"yin": "心", "yang": "小肠", "note": "心脑血管"},
    "土": {"yin": "脾", "yang": "胃", "note": "消化系统"},
    "金": {"yin": "肺", "yang": "大肠", "note": "呼吸系统"},
    "水": {"yin": "肾", "yang": "膀胱", "note": "泌尿生殖"},
}

WUXING_DEFICIENCY_HEALTH = {
    "木": "肝胆功能偏弱，易出现情绪抑郁、眼睛干涩、指甲干裂、手脚麻木。",
    "火": "心脑血管功能偏弱，易出现心悸失眠、血压不稳、血液循环不佳。",
    "土": "脾胃消化功能偏弱，易出现食欲不振、腹胀、便溏、体倦乏力。",
    "金": "肺呼吸系统偏弱，易出现咳嗽气喘、皮肤干燥、便秘、感冒频发。",
    "水": "肾泌尿系统偏弱，易出现腰膝酸软、耳鸣、记忆力减退、水肿。",
}

SEASONAL_CARE = {
    "春": "木旺之季，养肝护胆，多食绿色蔬菜，避免生气发怒。",
    "夏": "火旺之季，养心护脑，多食红色食物，避免过度劳累。",
    "秋": "金旺之季，养肺护肠，多食白色食物，注意润燥防燥。",
    "冬": "水旺之季，养肾护膀胱，多食黑色食物，早睡晚起养精。",
    "长夏": "土旺之季，养脾护胃，多食黄色食物，注意饮食规律。",
}


def health_analysis(pillar_result: dict) -> dict:
    """
    健康分析
    参数：八字排盘结果
    返回：五行缺失、脏腑强弱、养生建议
    """
    wuxing = pillar_result["wuxing"]
    birth_info = pillar_result.get("birth_info", {})
    wx_scores = wuxing.get("score", {})
    total = sum(wx_scores.values()) or 1

    # 五行缺失
    missing = [wx for wx in ["木", "火", "土", "金", "水"] if wx_scores.get(wx, 0) / total < 0.12]

    # 脏腑强弱
    organ_strength = {}
    for wx, info in WUXING_ORGANS.items():
        score = wx_scores.get(wx, 0)
        if score >= 4:
            level, desc = "强", f"{info['yin']}（{info['note']}）功能旺盛，注意调养不要过亢。"
        elif score >= 2:
            level, desc = "中", f"{info['yin']}（{info['note']}）功能平稳。"
        else:
            level, desc = "弱", f"{info['yin']}（{info['note']}）功能偏弱，需要养护。"
        organ_strength[info["yin"]] = {"level": level, "description": desc, "score": int(score)}

    # 健康隐患
    health_risks = []
    for wx in missing:
        risk = WUXING_DEFICIENCY_HEALTH.get(wx, "")
        if risk:
            health_risks.append(f"【{wx}行缺失】{risk}")

    # 当前季节
    current_month = birth_info.get("month", 6)
    if current_month in [3, 4, 5]:
        season = "春"
    elif current_month in [6, 7, 8]:
        season = "夏"
    elif current_month in [9, 10, 11]:
        season = "秋"
    else:
        season = "冬"

    seasonal_care = SEASONAL_CARE.get(season, "")

    # 饮食建议
    diet_advice = _health_diet_advice(missing, season)

    # 情志建议
    emotion_advice = _health_emotion_advice(missing)

    missing_yin = ", ".join([WUXING_ORGANS.get(w, {}).get("yin", "") for w in missing]) if missing else "整体"
    return {
        "missing_wuxing": missing,
        "organ_strength": organ_strength,
        "health_risks": health_risks,
        "season": season,
        "seasonal_care": seasonal_care,
        "diet_advice": diet_advice,
        "emotion_advice": emotion_advice,
        "overall": f"命局{len(missing)}行偏弱（{','.join(missing) if missing else '五行均衡'}），重点养护{missing_yin}。"
    }


def _health_diet_advice(missing: list, season: str) -> str:
    """饮食建议"""
    diet_map = {
        "木": "多食绿色蔬菜（菠菜、芹菜）、酸味食物（醋、柠檬）、豆制品。",
        "火": "多食红色食物（红枣、枸杞）、苦味食物（苦瓜、莲子）、鱼类。",
        "土": "多食黄色食物（小米、南瓜）、甘味食物（山药、红糖）、粥类养脾。",
        "金": "多食白色食物（百合、银耳、梨）、辛味食物（葱、姜、蒜）、润肺食物。",
        "水": "多食黑色食物（黑豆、黑芝麻、核桃）、咸味食物（海带）、补肾食品。",
    }
    advice = [diet_map.get(wx, "") for wx in missing[:2] if diet_map.get(wx, "")]
    if not advice:
        advice.append(f"{season}季宜清淡饮食，顺应时节养护脏腑。")
    return advice[0] if advice else ""


def _health_emotion_advice(missing: list) -> str:
    """情志养护建议"""
    emotion_map = {
        "木": "戒怒：怒伤肝，保持心情舒畅，多户外舒展运动。",
        "火": "戒躁：躁伤心，避免情绪激动，多静心冥想。",
        "土": "戒思：思伤脾，避免过度思虑，规律饮食定时运动。",
        "金": "戒悲：悲伤肺，保持积极乐观，多做深呼吸。",
        "水": "戒恐：恐伤肾，避免恐惧心理，早睡养肾适度运动。",
    }
    advice = [emotion_map.get(wx, "") for wx in missing if wx in emotion_map]
    if not advice:
        advice.append("保持心态平和，情绪稳定是健康根本。")
    return advice[0] if advice else ""


# ═══════════════════════════════════════════════════════════════════
# 流年精批
# ═══════════════════════════════════════════════════════════════════

def liunian_detail(birth_year: int, day_zhu: str, target_year: int) -> dict:
    """
    流年精批
    参数：出生年、日柱干支、目标年份
    返回：逐年详细分析（事业/财运/健康/感情四维度）
    """
    # 计算目标年干支
    day_idx = JIAZI.index(day_zhu)
    year_offset = target_year - birth_year
    target_gz_idx = (day_idx + year_offset) % 60
    target_gz = JIAZI[target_gz_idx]

    # 逐年分析（近3年）
    yearly_details = []
    for offset in range(-1, 3):
        yr = target_year + offset
        yr_offset = yr - birth_year
        yr_idx = (day_idx + yr_offset) % 60
        yr_gz = JIAZI[yr_idx]
        analysis = _year_analysis(yr_gz, yr, target_year)
        yearly_details.append({
            "year": yr,
            "ganzhi": yr_gz,
            "is_current": yr == target_year,
            "analysis": analysis,
        })

    # 重点提示
    highlights = _year_highlights(target_gz, target_year)
    summary = _liunian_summary(target_gz)

    return {
        "target_year": target_year,
        "target_ganzhi": target_gz,
        "yearly_details": yearly_details,
        "highlights": highlights,
        "summary": summary,
    }


def _year_analysis(yr_gz: str, yr: int, current_year: int) -> dict:
    """单一年份分析"""
    gan = yr_gz[0]
    zhi = yr_gz[1]
    gan_wx = WUXING_GAN.get(gan, "")
    zhi_wx = WUXING_ZHI.get(zhi, "")

    # 流年星
    zhi_idx = DIZHI.index(zhi)
    liunian_xing_map = {
        0: "太岁", 1: "青龙", 2: "丧门", 3: "六合", 4: "官符",
        5: "白虎", 6: "天德", 7: "吊客", 8: "病符", 9: "天狗",
        10: "紫微", 11: "小耗",
    }
    liunian_xing = liunian_xing_map.get(zhi_idx, "普通")

    # 四维度基础分
    career = _score_dim(gan_wx, ["木", "火"], 50)
    wealth = _score_dim(gan_wx, ["土", "金"], 50)
    health = _score_dim(gan_wx, ["水", "木"], 50)
    love = _score_dim(gan_wx, ["火", "土"], 50)

    # 调整
    if "太岁" in liunian_xing:
        career = min(100, career + 15)
    if zhi_idx in [3, 4, 8]:
        wealth = min(100, wealth + 10)
    if zhi_idx in [1, 5]:
        wealth = max(0, wealth - 5)
    if zhi_idx in [8, 9]:
        health = max(0, health - 10)
    if zhi_idx in [2, 7]:
        love = min(100, love + 10)

    return {
        "liunian_star": liunian_xing,
        "career": {"score": career, "desc": _dim_desc(career, "事业")},
        "wealth": {"score": wealth, "desc": _dim_desc(wealth, "财运")},
        "health": {"score": health, "desc": _dim_desc(health, "健康")},
        "love": {"score": love, "desc": _dim_desc(love, "感情")},
    }


def _score_dim(gan_wx: str, favorable: list, base: int) -> int:
    """计算维度分数"""
    return min(100, base + (10 if gan_wx in favorable else 0))


def _dim_desc(score: int, dim: str) -> str:
    """维度描述"""
    if score >= 80:
        return f"{dim}大旺，诸事顺遂。"
    elif score >= 65:
        return f"{dim}运势良好，稳步发展。"
    elif score >= 50:
        return f"{dim}运势平稳，需稳扎稳打。"
    elif score >= 35:
        return f"{dim}运势一般，注意调整。"
    else:
        return f"{dim}运势低迷，谨慎行动，蓄势待发。"


def _year_highlights(target_gz: str, target_year: int) -> list:
    """年度重点提示"""
    highlights = []
    zhi_idx = DIZHI.index(target_gz[1])

    if target_year % 12 == 0:
        highlights.append("本命年：变化较大，需低调行事，注意健康和安全。")
    if zhi_idx == 3:  # 卯
        highlights.append("值年太岁冲克卯宫：注意变动，人际关系波动。")
    if zhi_idx == 9:  # 酉
        highlights.append("值年太岁冲克酉宫：注意变动，口舌是非。")
    if zhi_idx == 6:  # 午
        highlights.append("岁破：变动较大，不宜冒险，守成为上。")
    if target_year % 6 in [1, 4]:
        highlights.append("天喜/红鸾星照命：姻缘、人际关系有好事。")
    if not highlights:
        highlights.append(f"{target_gz}年整体格局平和，顺势而为，积极进取。")
    return highlights


def _liunian_summary(target_gz: str) -> str:
    """流年总结"""
    wx = WUXING_GAN.get(target_gz[0], "")
    wx_summary = {
        "木": "木年：生发、创新、变动，多有新的开始和机会。",
        "火": "火年：热情、上升、活跃，多有展示才华的机遇。",
        "土": "土年：积累、沉淀、稳定，多有收获和积蓄的年份。",
        "金": "金年：决断、肃杀、收获，多有决定性结果和成果。",
        "水": "水年：流动、智慧、转折，多有深思和方向调整的年份。",
    }
    return wx_summary.get(wx, f"{target_gz}年：顺势而行，把握机遇，稳健发展。")
