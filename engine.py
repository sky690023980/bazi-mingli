# -*- coding: utf-8 -*-
import math
from datetime import datetime
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)

TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
DZ_WX = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
    '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
    '戌': '土', '亥': '水'
}
TG_WX = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}
WX_XG = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
WX_XS = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
WX_SHENG = {'木生火': '火', '火生土': '土', '土生金': '金', '金生水': '水', '水生木': '木'}
WX_KESHI = {'木克土': '土', '土克水': '水', '水克火': '火', '火克金': '金', '金克木': '木'}

SHISHEN = {
    '甲': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '乙': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '丙': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '丁': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '戊': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '己': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '庚': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '辛': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '壬': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
    '癸': {'比': '比肩', '劫': '劫财', '食': '食神', '伤': '伤官', '才': '偏财', '财': '正财', '官': '正官', '杀': '七杀', '印': '正印', '枭': '偏印'},
}

def get_shishen(gan, zhiguan):
    if gan not in SHISHEN:
        return ''
    return SHISHEN[gan].get(zhiguan, '')

def get_ganzhi(index, is_gan=True):
    arr = TIANGAN if is_gan else DIZHI
    return arr[index % len(arr)]

def wuxing_score(wx_count):
    scores = {}
    total = sum(wx_count.values())
    if total == 0:
        return {k: 20 for k in ['木', '火', '土', '金', '水']}
    for k, v in wx_count.items():
        scores[k] = round(v / total * 100, 1)
    return scores

def day_master_strength(day_gan, wx_count):
    score = 0
    score += wx_count.get(TG_WX.get(day_gan, ''), 0) * 2
    score += wx_count.get(WX_SHENG.get(day_gan + '生火', ''), 0) * 0.5 if '生' not in day_gan else 0
    score += wx_count.get(WX_XS.get(day_gan, ''), 0) * 0.8
    score -= wx_count.get(WX_XG.get(day_gan, ''), 0) * 1.5
    return score

def get_yongshen(wx_score):
    if not wx_score:
        return '用神待定', '忌神待定'
    sorted_wx = sorted(wx_score.items(), key=lambda x: x[1])
    weak = [x[0] for x in sorted_wx[:2]]
    strong = [x[0] for x in sorted_wx[-2:]]
    return '、'.join(weak), '、'.join(strong)

def calculate_dayun(year, day_gan):
    cycle_year = (year - 4) % 60
    start_gan = TIANGAN[cycle_year % 10]
    result = []
    for i in range(8):
        offset = (cycle_year + i * 10) % 60
        g = TIANGAN[offset % 10]
        z = DIZHI[offset % 12]
        start_year = year + i * 10
        result.append({'ganzhi': g + z, 'start_year': start_year, 'shichen': DIZHI.index(z) * 2 % 12})
    return result

def liunian_detail(birth_year, day_zhu, target_year):
    gan = day_zhu[0]
    zhi = day_zhu[1] if len(day_zhu) > 1 else ''
    current_idx = (target_year - birth_year) % 60
    g = TIANGAN[current_idx % 10]
    z = DIZHI[current_idx % 12]
    wx_g = TG_WX.get(gan, '')
    wx_z = DZ_WX.get(z, '')
    wx_day = TG_WX.get(gan, '')
    summary = f'{g}{z}年，五行{wx_g}{wx_z}，日主{wx_day}气'
    return {'year': target_year, 'ganzhi': g + z, 'wuxing': {'天干': wx_g, '地支': wx_z}, 'summary': summary, 'tips': f'此年宜静不宜动，{wx_g}旺则吉，忌{wx_z}受冲。'}

def health_analysis(pj):
    day_gan = pj.get('day_gan', '')
    wx = pj.get('wuxing', {})
    wx_values = [v for v in wx.values() if isinstance(v, (int, float))]
    wx_dict = dict(wx)
    weak = [k for k, v in wx_dict.items() if isinstance(v, (int, float)) and v < 1]
    organ_map = {'木': '肝胆', '火': '心脑血管', '土': '脾胃', '金': '肺大肠', '水': '肾膀胱'}
    organ_body = {'木': '肝', '火': '心', '土': '脾', '金': '肺', '水': '肾'}
    organ_advice = {'木': '注意肝脏保护，忌熬夜饮酒', '火': '保持心情平和，避免情绪激动', '土': '饮食规律，少吃生冷油腻', '金': '呼吸系统较弱，秋冬注意保暖', '水': '泌尿系统需注意，多喝水不憋尿'}
    body_weak = [organ_body.get(w, w) for w in weak]
    advice = [organ_advice.get(w, '') for w in weak]
    return {'weak_organs': weak, 'weak_body': body_weak, 'health_advice': advice, 'summary': '五行' + str(wx_dict) + '，需注意' + '、'.join(body_weak) if body_weak else '五行较为平衡'}

def marriage_analysis(pj):
    day_gan = pj.get('day_gan', '')
    trait = {'甲': '刚健正直', '乙': '温柔体贴', '丙': '热情开朗', '丁': '细腻内敛', '戊': '稳重踏实', '己': '包容圆融', '庚': '果断刚毅', '辛': '精致敏锐', '壬': '灵活变通', '癸': '柔和智慧'}
    trait_text = trait.get(day_gan, '性格独特')
    spouse_map = {
        '甲': {'妻星': '正财', '合适': '己土、癸水', '忌': '庚金、辛金'},
        '乙': {'妻星': '正财', '合适': '戊土、丁火', '忌': '壬水、癸水'},
        '丙': {'妻星': '正财', '合适': '辛金、壬水', '忌': '甲木、乙木'},
        '丁': {'妻星': '正财', '合适': '庚金、戊土', '忌': '癸水'},
        '戊': {'妻星': '正财', '合适': '癸水、乙木', '忌': '丙火、丁火'},
        '己': {'妻星': '正财', '合适': '甲木、丙火', '忌': '辛金'},
        '庚': {'妻星': '正财', '合适': '乙木、丁火', '忌': '壬水、癸水'},
        '辛': {'妻星': '正财', '合适': '丙火、戊土', '忌': '甲木'},
        '壬': {'妻星': '正财', '合适': '丁火、己土', '忌': '庚金、辛金'},
        '癸': {'妻星': '正财', '合适': '丙火、戊土', '忌': '乙木'},
    }
    info = spouse_map.get(day_gan, {})
    return {'day_gan': day_gan, 'personality': trait_text, 'spouse_stars': info, 'marriage_advice': f'日主{day_gan}，{trait_text}，婚配宜{info.get("合适","配合")}，忌{info.get("忌","冲克")}。'}

def bazi_pan(name='', gender='M', birth_year=1990, birth_month=1, birth_day=1, birth_hour=0):
    try:
        bd = datetime(birth_year, birth_month, birth_day)
    except ValueError:
        bd = datetime(birth_year, 1, 1)
    year_idx = (birth_year - 4) % 60
    year_gan = TIANGAN[year_idx % 10]
    year_zhi = DIZHI[year_idx % 12]
    month_cycle = (birth_year * 12 + birth_month + 3) % 60
    month_gan = TIANGAN[month_cycle % 10]
    month_zhi = DIZHI[month_cycle % 12]
    day_seconds = (bd - datetime(birth_year, 1, 1)).total_seconds()
    day_offset = int(day_seconds / 86400) % 60
    day_gan = TIANGAN[day_offset % 10]
    day_zhi = DIZHI[day_offset % 12]
    hour_idx = int(birth_hour / 2) % 12
    hour_gan_idx = (day_offset % 10 // 2 * 2 + hour_idx) % 10
    hour_gan = TIANGAN[hour_gan_idx]
    hour_zhi = DIZHI[hour_idx]
    ganzhi = {
        'year': year_gan + year_zhi,
        'month': month_gan + month_zhi,
        'day': day_gan + day_zhi,
        'hour': hour_gan + hour_zhi,
    }
    wx_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
    for gz in ganzhi.values():
        g, z = gz[0], gz[1]
        wx_count[TG_WX.get(g, '')] += 1
        wx_count[DZ_WX.get(z, '')] += 1
    wx_score = wuxing_score(wx_count)
    shishen = {
        '年': get_shishen(year_gan, SHISHEN.get(year_gan, {}).get('官', '官') or '官'),
        '月': get_shishen(month_gan, SHISHEN.get(month_gan, {}).get('官', '官') or '官'),
        '日': get_shishen(day_gan, SHISHEN.get(day_gan, {}).get('比', '比') or '比'),
        '时': get_shishen(hour_gan, SHISHEN.get(hour_gan, {}).get('官', '官') or '官'),
    }
    shishen_accurate = {}
    zhiguan_map = {'甲': {'壬': '印', '癸': '枭', '甲': '比', '乙': '劫', '丙': '食', '丁': '伤', '戊': '才', '己': '财', '庚': '官', '辛': '杀'},
                   '乙': {'丙': '印', '丁': '枭', '甲': '比', '乙': '劫', '丙': '食', '丁': '伤', '戊': '才', '己': '财', '庚': '官', '辛': '杀'},
                   '丙': {'戊': '印', '己': '枭', '丙': '比', '丁': '劫', '戊': '食', '己': '伤', '庚': '才', '辛': '财', '壬': '官', '癸': '杀'},
                   '丁': {'庚': '印', '辛': '枭', '丙': '比', '丁': '劫', '戊': '食', '己': '伤', '庚': '才', '辛': '财', '壬': '官', '癸': '杀'},
                   '戊': {'壬': '印', '癸': '枭', '戊': '比', '己': '劫', '庚': '食', '辛': '伤', '壬': '才', '癸': '财', '甲': '官', '乙': '杀'},
                   '己': {'丙': '印', '丁': '枭', '戊': '比', '己': '劫', '庚': '食', '辛': '伤', '壬': '才', '癸': '财', '甲': '官', '乙': '杀'},
                   '庚': {'戊': '印', '己': '枭', '庚': '比', '辛': '劫', '壬': '食', '癸': '伤', '甲': '才', '乙': '财', '丙': '官', '丁': '杀'},
                   '辛': {'庚': '印', '辛': '枭', '庚': '比', '辛': '劫', '壬': '食', '癸': '伤', '甲': '才', '乙': '财', '丙': '官', '丁': '杀'},
                   '壬': {'甲': '印', '乙': '枭', '壬': '比', '癸': '劫', '甲': '食', '乙': '伤', '丙': '才', '丁': '财', '戊': '官', '己': '杀'},
                   '癸': {'丙': '印', '丁': '枭', '壬': '比', '癸': '劫', '甲': '食', '乙': '伤', '丙': '才', '丁': '财', '戊': '官', '己': '杀'}}
    for col, gz in [('年', year_gan + year_zhi), ('月', month_gan + month_zhi), ('日', day_gan + day_zhi), ('时', hour_gan + hour_zhi)]:
        g, z = gz[0], gz[1]
        zhiguan = zhiguan_map.get(day_gan, {}).get(g, '')
        shishen_accurate[col] = g + '为' + (SHISHEN.get(day_gan, {}).get(zhiguan, '') or zhiguan or '待定')
    strength = day_master_strength(day_gan, wx_count)
    strength_level = '极强' if strength > 8 else '较强' if strength > 4 else '偏弱' if strength > 0 else '弱'
    yong, ji = get_yongshen(wx_score)
    dayun = calculate_dayun(birth_year, day_gan)
    gender_text = '男' if gender in ['M', '男'] else '女'
    return {
        'name': name, 'gender': gender_text,
        'birth_info': f'{birth_year}年{birth_month}月{birth_day}日{birth_hour}时',
        'pillar': ganzhi,
        'wuxing': wx_count, 'wuxing_score': wx_score,
        'shishen': shishen_accurate,
        'day_gan': day_gan, 'day_zhi': day_zhi,
        'dayun': dayun,
        'strength': {'score': round(strength, 2), 'level': strength_level},
        'yongshen': {'yong': yong, 'ji': ji},
        'health': health_analysis({'day_gan': day_gan, 'wuxing': wx_count}),
        'marriage': marriage_analysis({'day_gan': day_gan}),
    }
