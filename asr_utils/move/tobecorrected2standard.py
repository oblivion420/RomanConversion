# 預檢查 並查看台羅標準是否有重複
# SELECT * FROM `standard_dictionary` where 漢字 in (select 漢字 from to_be_corrected_dictionary where 修訂狀態='Y')

import re
import sys
sys.path.append("..")

import json
from collections import defaultdict
from importlib import import_module

from lib import db
from lib import utils
from lib import get_colloquial_tone

cfg = import_module("config.{}".format("db"))

def parse_item(item, source):
    item = [i.strip() for i in item[1:]]
    comment, synonym_seq, mandarin, taigi, varient, tl_standard, tl_colloquial, _, source_seq, status, ex1, ex2, ex3, ex4, ex5 = item

    if status != "Y": return

    taigi = re.sub(",|, ", "，", taigi)
    taigi = re.sub(" +", "", taigi).replace("(", " (")
    mandarin = re.sub(",|, ", "，", mandarin)

    if mandarin:
        new_dict[(taigi, tl_standard)]["華語詞"].add(mandarin)

    new_dict[(taigi, tl_standard)]["註"] = comment.replace("'", "\'")

    if status in ["", "Y"] and new_dict[(taigi, tl_standard)]["修訂狀態"] == "Y":
        new_dict[(taigi, tl_standard)]["修訂狀態"] = "Y"
    else:
        if status == "": status = "Y"
        new_dict[(taigi, tl_standard)]["修訂狀態"] = status

    if varient != taigi and varient:
        varient = re.sub(", ?", "，", varient)
        new_dict[(taigi, tl_standard)]["異用詞"].add(varient)

    for synonym in re.split("[/、]", synonym_seq):
        if synonym:
            new_dict[(taigi, tl_standard)]["同義詞"].add(synonym.strip())

    if tl_standard:
        new_dict[(taigi, tl_standard)]["TL-口語"].add(tl_standard)
    if tl_colloquial:
        new_dict[(taigi, tl_standard)]["TL-口語"].add(tl_colloquial)

    for item_source in re.split("[,、]", source_seq):
        item_source = item_source.strip()
        if item_source:
            new_dict[(taigi, tl_standard)]["來源"].add(item_source)

    for ex in [ex1, ex2, ex3, ex4, ex5]:
        if ex:
            ex = re.sub(" +", " ", ex)
            ex = re.sub("'", "\'", ex)
            new_dict[(taigi, tl_standard)]["範例"].add(ex)

    if "," in tl_standard or source == "phrase":
        new_dict[(taigi, tl_standard)]["成語"] = 1


mydb = db.DB(cfg.taigi_DB["server_name"], cfg.taigi_DB["username"], cfg.taigi_DB["password"],
            cfg.taigi_DB["db_name"], port=cfg.taigi_DB["port"])
mydb.build_connect()

new_dict = defaultdict(lambda: {"華語詞": set(), "註": "", "異用詞": set(), "同義詞": set(),
                                "TL-口語": set(), "發音": set(), "來源": set(), "修訂狀態": "",
                                "範例": set(), "編輯者": "", "成語": "0"})


result = mydb.select("to_be_corrected_dictionary") # , condition_str="漢字='𩸙仔魚食著皇帝肉,暢到無鰾'"
for item in result:
    parse_item(item, source="all")


for pair in new_dict.keys():
    if new_dict[pair]["修訂狀態"] not in ["", "Y"]: continue

    # all Pinyin
    tailo_list = [utils.transform_pinyin_format(tailo) for tailo in new_dict[pair]["TL-口語"]]
    for tailo in tailo_list:
        pinyin_set = set(get_colloquial_tone.TAILO(tailo).modify())
        pinyin_set = {pinyin.replace("_", "") for pinyin in pinyin_set}
        new_dict[pair]["發音"].update(pinyin_set)

    # Editor
    editor = ""
    for source_name in new_dict[pair]:
        if re.search(" [A-Z]+$", source_name):
            editor = source_name.split()[-1]
            new_dict[(taigi, tl_standard)]["編輯者"] = editor

for taigi, tl_standard in new_dict.keys():
    new_dict[(taigi, tl_standard)]["華語詞"] = sorted(new_dict[(taigi, tl_standard)]["華語詞"])
    new_dict[(taigi, tl_standard)]["異用詞"] = sorted(new_dict[(taigi, tl_standard)]["異用詞"])
    new_dict[(taigi, tl_standard)]["同義詞"] = sorted(new_dict[(taigi, tl_standard)]["同義詞"])
    new_dict[(taigi, tl_standard)]["TL-口語"] = sorted(new_dict[(taigi, tl_standard)]["TL-口語"])
    new_dict[(taigi, tl_standard)]["發音"] = sorted(new_dict[(taigi, tl_standard)]["發音"])
    new_dict[(taigi, tl_standard)]["來源"] = sorted(new_dict[(taigi, tl_standard)]["來源"])
    new_dict[(taigi, tl_standard)]["範例"] = sorted(new_dict[(taigi, tl_standard)]["範例"])

    mydb.insert("standard_dictionary",
        set_str="(`漢字`, `TL-標準`, `註`, `異用字`, `同義詞`, `華語詞`, `TL-口語`, `發音`, `成語`, `來源`, `修訂狀態`, `範例`, `編輯者`)",
        value_str="('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}')".format(
                    taigi, tl_standard, new_dict[(taigi, tl_standard)]["註"],
                    json.dumps(new_dict[(taigi, tl_standard)]["異用詞"], ensure_ascii=False),
                    json.dumps(new_dict[(taigi, tl_standard)]["同義詞"], ensure_ascii=False),
                    json.dumps(new_dict[(taigi, tl_standard)]["華語詞"], ensure_ascii=False),
                    json.dumps(new_dict[(taigi, tl_standard)]["TL-口語"], ensure_ascii=False),
                    json.dumps(new_dict[(taigi, tl_standard)]["發音"], ensure_ascii=False),
                    new_dict[(taigi, tl_standard)]["成語"],
                    json.dumps(new_dict[(taigi, tl_standard)]["來源"], ensure_ascii=False), new_dict[(taigi, tl_standard)]["修訂狀態"],
                    json.dumps(new_dict[(taigi, tl_standard)]["範例"], ensure_ascii=False), new_dict[(taigi, tl_standard)]["編輯者"]))