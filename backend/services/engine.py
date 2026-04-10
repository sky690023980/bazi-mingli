# -*- coding: utf-8 -*-
import math
from datetime import datetime
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)

TIANGAN = ['\u7532','\u4e59','\u4e19','\u4e01','\u620a','\u5df1','\u5e9a','\u8f9b','\u5ec9','\u695a']
DIZHI = ['\u5b50','\u4e11','\u5b5d','\u536f','\u8fb0','\u5df3','\u5348','\u672a','\u7533','\u9149','\u620c','\u4ea5']
DZ_WX = {'\u5b50':'\u6c34','\u4e11':'\u571f','\u5b5d':'\u6728','\u536f':'\u6728','\u8fb0':'\u571f','\u5df3':'\u706b','\u5348':'\u706b','\u672b':'\u571f','\u7533':'\u91d1','\u9149':'\u91d1','\u620c':'\u571f','\u4ea5':'\u6c34'}
TG_WX = {'\u7532':'\u6728','\u4e59':'\u6728','\u4e19':'\u706b','\u4e01':'\u706b','\u620a':'\u571f','\u5df1':'\u571f','\u5e9a':'\u91d1','\u8f9b':'\u91d1','\u5ec9':'\u6c34','\u695a':'\u6c34'}
SS = {('\u7532','\u7532'):'\u6bd4',('\u7532','\u4e59'):'\u52ab',('\u7532','\u4e19'):'\u98df',('\u7532','\u4e01'):'\u4f24',('\u7532','\u620a'):'\u8d22',('\u7532','\u5df1'):'\u624d',('\u7532','\u5e9a'):'\u6740',('\u7532','\u8f9b'):'\u5b98',('\u7532','\u5ec9'):'\u5c71',('\u7532','\u695a'):'\u5370',('\u4e59','\u7532'):'\u52ab',('\u4e59','\u4e59'):'\u6bd4',('\u4e59','\u4e19'):'\u4f24',('\u4e59','\u4e01'):'\u98df',('\u4e59','\u620a'):'\u624d',('\u4e59','\u5df1'):'\u8d22',('\u4e59','\u5e9a'):'\u5b98',('\u4e59','\u8f9b'):'\u6740',('\u4e59','\u5ec9'):'\u5370',('\u4e59','\u695a'):'\u5c71'}

def bazi_pan(name, gender, birth_year, birth_month, birth_day, birth_hour):
    yg = (birth_year - 4) % 10
    yz = (birth_year - 4) % 12
    mgt = [3,5,7,9,1,3,5,7,9,1,3,5]
    mg = (yg + mgt[birth_month-1]) % 10
    mz = (birth_month * 2 - 1) % 12
    base = datetime(2000,1,1)
    target = datetime(birth_year, birth_month, birth_day)
    days = (target - base).days
    cd = (days + 39) % 60
    dg = cd % 10
    dz = cd % 12
    hg = (dg * 2 + mz) % 10
    hz = (birth_hour // 2) % 12
    day_gan = TIANGAN[dg]
    pillars = {
        'year': TIANGAN[yg]+DIZHI[yz],
        'month': TIANGAN[mg]+DIZHI[mz],
        'day': TIANGAN[dg]+DIZHI[dz],
        'hour': TIANGAN[hg]+DIZHI[hz],
    }
    wx = {'\u6728':0,'\u706b':0,'\u571f':0,'\u91d1':0,'\u6c34':0}
    for k,v in pillars.items():
        wx[TG_WX[v[0]]] += 1
        wx[DZ_WX[v[1]]] += 1
    ss = {
        '\u5e74': SS.get((day_gan, pillars['year'][0]), ''),
        '\u6708': SS.get((day_gan, pillars['month'][0]), ''),
        '\u65e5': '\u65e5\u4e3b',
        '\u65f6': SS.get((day_gan, pillars['hour'][0]), ''),
    }
    ws = '\u4e2d\u548c'
    if wx['\u6728'] >= 4: ws = '\u8eab\u65fa'
    elif wx['\u706b'] >= 4: ws = '\u8eab\u65fa'
    elif wx['\u571f'] >= 4: ws = '\u8eab\u65fa'
    elif wx['\u91d1'] >= 4: ws = '\u8eab\u65fa'
    elif wx['\u6c34'] >= 4: ws = '\u8eab\u65fa'
    dy = []
    sy = birth_year + (10 if birth_month >= 4 else 9)
    dirn = 1 if gender in ['M','\u7537'] else -1
    for i in range(10):
        y = sy + i * dirn
        if y < 1900: continue
        tg = TIANGAN[(yg + i * dirn) % 10]
        dz2 = DIZHI[(yz + i * dirn) % 12]
        dy.append({'year': y, 'pillar': tg+dz2})
    return {
        'name': name, 'gender': gender,
        'birth_info': f'{birth_year}\u5e74{birth_month}\u6708{birth_day}\u65e5{birth_hour}\u65f6',
        'pillar': pillars,
        'shishen': ss,
        'wuxing': wx,
        'wangshuai': ws,
        'dayun': dy[:8],
        'day_gan': day_gan,
        'day_zhu': pillars['day'],
    }

def health_analysis(pj):
    wx = pj.get('wuxing', {})
    body = {'\u6728':'\u809d\u80c3','\u706b':'\u5fc3\u8840\u7ba1\u7406','\u571f':'\u810f\u80a0\u80c3','\u91d1':'\u80ba\u5927\u80a0\u76ae\u80a4','\u6c34':'\u80be\u818a\u80c3\u8033'}
    weak = [k for k,v in wx.items() if v == 0]
    adv = [f'{k}\u5c5e\u504f\u5f31\uff0c\u6ce8\u610f{body.get(k,\'\u76f8\u5173')}\u5065\u5eb7' for k in weak]
    return {'weak_organs': weak, 'health_advice': adv, 'summary': f'\u4e94\u884c{wx}\uff0c{\'\u9700\u6ce8\u610f\'+\'\u3001\'.join(weak) if weak else \u8f83\u4e3a\u5e73\u8861'}}

def marriage_analysis(pj):
    dg = pj.get('day_gan','')
    t = {'\u7532':'\u521a\u6b63\u660e\u667a','\u4e59':'\u6e29\u67d4\u4f53\u8d34','\u4e19':'\u70ed\u60c5\u5f00\u6717','\u4e01':'\u7ec6\u817b\u6d6a\u6f2b','\u620a':'\u7a33\u91cd\u8e0f\u5b9e','\u5df1':'\u5305\u5bb9\u7ec6\u817b','\u5e9a':'\u521a\u5f3a\u76f4\u63a5','\u8f9b':'\u7cbe\u81f4\u5185\u6563','\u5ec9':'\u7075\u6d3b\u53d8\u901a','\u695a':'\u67d4\u548c\u806a\u6167'}
    advice = f'\u65e5\u4e3b{dg}\uff0c{t.get(dg,\'\u6027\u683c\u7279\u70b9\'}\uff0c\u5fae\u5fae\u63d0\u793a\u6709\u5c0f\u89c4\u6a21\u7684\u9519\u8bef\u4e5f\u4e0d\u89c1\u5c0f\u89c1'
    return {'day_gan': dg, 'marriage_advice': advice, 'summary': advice}

def liunian_detail(birth_year, day_zhu, target_year):
    cd = sum(ord(c) for c in day_zhu) % 60
    offset = (target_year - birth_year) % 60
    yr_tg = TIANGAN[(cd + offset) % 10]
    yr_dz = DIZHI[(cd + offset) % 12]
    return {'target_year': target_year, 'year_zhu': yr_tg+yr_dz, 'luck_score': 65, 'summary': f'{target_year}\u5e74{yr_tg}{yr_dz}\uff0c\u8fd0\u52bf\u8bc4\u5206\u5047\u8bbe65/100'}
