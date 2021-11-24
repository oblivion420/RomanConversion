"""
make_text.py

INSTALL FIRST:
conda install bs4

Copyright 2020 Academia Sinica (Author: Pin-Yuan Chen, Hung-Shin Lee)
"""

import sys
python_version = float("{0}.{1}".format(*sys.version_info[:2]))
assert python_version >= 3.6

sys.path.append("../..")

import re
import gzip
import tqdm
import argparse
import itertools
from bs4 import BeautifulSoup
from joblib import Parallel, delayed

def num4year(matched):
    c_basic = "零一二三四五六七八九"

    def _num4year(num):
        return "{}".format("".join([c_basic[int(i)] for i in num]))

    matched_str = matched.group(0)
    for m in matched.groups():
        matched_str = matched_str.replace(m, _num4year(m))
    return matched_str

def num4percent(matched):
    matched = matched.group(1)
    return "百分之{}".format(num2chinese(matched[:-1]))

def num4fraction(matched):
    numerator = matched.group(1)
    denominator = matched.group(2)
    return "{}分之{}".format(num2chinese(denominator), num2chinese(numerator))

def num4general(matched):
    num = matched.group(1)
    if re.match("[A-Za-z-─]", num[0]):
        return num
    else:
        if re.match("[0-9]", num[0]):
            return "{}".format(num2chinese(num))
        else:
            return "{}{}".format(num[0], num2chinese(num[1:]))


def numZH4percent(matched):
    matched = matched.group(1)
    return "百分之{}".format(matched)


def numZH4float(matched):
    matched_1 = matched.group(1)
    matched_2 = matched.group(2)
    return f"{matched_1}點{matched_2}"


def parse_num(text):
    # year
    text = re.sub("([0-9]{4})[到至]([0-9]{4})年", num4year, text)
    text = re.sub("([^0-9])2年", r"\1兩年", text)
    text = re.sub("^2年", r"兩年", text)
    text = re.sub("([0-9]{4})年", num4year, text)

    # percentage
    text = re.sub("([0-9]+\.?[0-9]?[%％])", num4percent, text)

    # faction
    text = re.sub("([0-9]+)/([0-9]+)", num4fraction, text)

    # 特殊用詞
    text = re.sub("([0-9][0-9])[折]", num4year, text)

    # general number
    text = re.sub("([^0-9]?[0-9]+\.?[0-9]?)", num4general, text)

    # 異體字
    text = re.sub("○", "〇", text)

    # zh float
    c_basic = "零一二三四五六七八九十"
    text = re.sub(f"([{c_basic}]+)\.([{c_basic}]+)", numZH4float, text)

    # zh percentage
    c_basic = "點零一二三四五六七八九十"
    text = re.sub(f"([{c_basic}]+)[%％]", numZH4percent, text)

    return text

def remove_url(text):
    http_url_pattern = "https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=—]{1,256}\.[a-zA-Z0-9()]{1,6}\b?([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    url_pattern = "[-a-zA-Z@:%._\+~#=—]{1,256}\.[a-zA-Z()]{1,6}\b?([-a-zA-Z()@:%_\+.~#?&//=]*)"

    text = re.sub(http_url_pattern, "", text)
    text = re.sub(url_pattern, "", text)

    return text

def num2chinese(num, big=False, simp=False, o=False, twoalt=False):
    """
    Converts numbers to Chinese representations.
    https://gist.github.com/gumblex/0d65cad2ba607fd14de7
    `big`   : use financial characters.
    `simp`  : use simplified characters instead of traditional characters.
    `o`     : use 〇 for zero.
    `twoalt`: use 两/兩 for two when appropriate.
    Note that `o` and `twoalt` is ignored when `big` is used,
    and `twoalt` is ignored when `o` is used for formal representations.
    """
    # check num first
    nd = str(num)
    if abs(float(nd)) >= 1e48:
        return ""
        # raise ValueError('number out of range', nd)
    elif 'e' in nd:
        return ""
        # raise ValueError('scientific notation is not supported')
    c_symbol = '正负点' if simp else '正負點'
    if o:  # formal
        twoalt = False
    if big:
        c_basic = '零壹贰叁肆伍陆柒捌玖' if simp else '零壹貳參肆伍陸柒捌玖'
        c_unit1 = '拾佰仟'
        c_twoalt = '贰' if simp else '貳'
    else:
        c_basic = '〇一二三四五六七八九' if o else '零一二三四五六七八九'
        c_unit1 = '十百千'
        if twoalt:
            c_twoalt = '两' if simp else '兩'
        else:
            c_twoalt = '二'
    c_unit2 = '万亿兆京垓秭穰沟涧正载' if simp else '萬億兆京垓秭穰溝澗正載'
    def revuniq(l): return ''.join(
        k for k, g in itertools.groupby(reversed(l)))
    nd = str(num)
    result = []
    if nd[0] == '+':
        result.append(c_symbol[0])
    elif nd[0] == '-':
        result.append(c_symbol[1])
    if '.' in nd:
        integer, remainder = nd.lstrip('+-').split('.')
    else:
        integer, remainder = nd.lstrip('+-'), None
    if int(integer):
        splitted = [integer[max(i - 4, 0):i]
                    for i in range(len(integer), 0, -4)]
        intresult = []
        for nu, unit in enumerate(splitted):
            # special cases
            if int(unit) == 0:  # 0000
                intresult.append(c_basic[0])
                continue
            elif nu > 0 and int(unit) == 2:  # 0002
                intresult.append(c_twoalt + c_unit2[nu - 1])
                continue
            ulist = []
            unit = unit.zfill(4)
            for nc, ch in enumerate(reversed(unit)):
                if ch == '0':
                    if ulist:  # ???0
                        ulist.append(c_basic[0])
                elif nc == 0:
                    ulist.append(c_basic[int(ch)])
                elif nc == 1 and ch == '1' and all([i == "0" for i in unit[:nc]]):
                    # special case for tens
                    # edit the 'elif' if you don't like
                    # 十四, 三千零十四, 三千三百一十四
                    ulist.append(c_unit1[0])
                elif nc > 1 and ch == '2':
                    ulist.append(c_twoalt + c_unit1[nc - 1])
                else:
                    ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
            # print(ulist)
            ustr = revuniq(ulist)
            if nu == 0:
                intresult.append(ustr)
            else:
                intresult.append(ustr + c_unit2[nu - 1])
        result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    if remainder:
        result.append(c_symbol[2])
        result.append(''.join(c_basic[int(ch)] for ch in remainder))
    return ''.join(result)

def parse_sign(text):
    sign2zh = {"°": "度", "±": "正負", "×": "乘以", "÷": "除以",
                "=": "等於", "≠": "不等於", "≧": "大於等於", "≦": "小於等於"}

    for sign in sign2zh:
        text = re.sub(sign, sign2zh[sign], text)

    return text

def pre_remove_sign(text):
    pair_sign = "{}（）〈〉《》〔〕【】『』「」『』\[\]"
    sign = "～＊．–─|│*※\"”“〝〞═…╱·‧�★☆■□◆◇▲⊿█•●╳◎△○⊙✽→←↑↓"
    return re.sub(f"[{sign}{pair_sign}]", " ", text)

def post_remove_sign(text):
    sign = "\().@-"
    # Special text want to keep sign
    special = {"A-LIN": "A=LIN", "HIGH-TECH": "HIGH=TECH", "SO-SO": "SO=SO",
                "T-SHIRT": "T=SHIRT", "COVID-19": "COVID=19"}

    for k, v in special.items(): text = text.replace(k, v)
    # print(text)
    text = re.sub(f"[{sign}]", " ", text)
    for k, v in special.items(): text = text.replace(v, k)
    
    return text

def sent_segment(text):
    delimiters = "。！!？?，,、：︰:；;－\n"
    return re.split(f"[{delimiters}]", text)

def parse_special_num(text):
    # number + mandarin
    mapping = {"台北101": "臺北一零一", "101煙火": "一零一煙火", "101站": "一零一站",
                "101信義": "一零一信義", "101大樓": "一零一大樓", "101忠狗": "一零一忠狗",
                "85大樓": "八五大樓", "今彩539": "今彩五三九", "88水災": "八八水災",
                "39樂合彩": "三九樂合彩", "38樂合彩": "三八樂合彩", "49樂合彩": "四九樂合彩",
                "38婦女節": "三八婦女節", "華山1914": "華山一九一四",
                "104人力銀行": "一零四人力銀行", "1111人力銀行": "一一一一人力銀行",
                "165反詐騙": "一六五反詐騙", "1999市民熱線": "一九九九市民熱線"}
    for k, v in mapping.items():
        text = text.replace(k, v)

    # only number
    mapping = {"5566": "五五六六"}
    for k, v in mapping.items():
        text = re.sub(f"([^0-9\-]){k}([^0-9\-])", r"\1"+v+r"\2", text)
        text = re.sub(f"^{k}([^0-9\-])", v+r"\1", text)

    
    return text