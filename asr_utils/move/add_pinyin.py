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

def parse_item(mydb, item, source):
    id, tl_standard, tl_collo = item
    tl_collo_set = set(json.loads(tl_collo)).union({tl_standard})
    tl_collo_list = sorted(list(tl_collo_set))

    # all Pinyin
    all_pinyin_set = set()
    tailo_list = [utils.transform_pinyin_format(tailo) for tailo in tl_collo_list]
    for tailo in tailo_list:
        pinyin_set = set(get_colloquial_tone.TAILO(tailo).modify())
        pinyin_set = {pinyin.replace("_", "") for pinyin in pinyin_set}
        all_pinyin_set = set.union(pinyin_set, all_pinyin_set)
    all_pinyin_list = sorted(all_pinyin_set)

    tl_collo = json.dumps(tl_collo_list)
    all_pinyin = json.dumps(all_pinyin_list)
    mydb.update("standard_dictionary", set_str=f"`TL-口語`='{tl_collo}', `發音`='{all_pinyin}', 註=''", condition_str=f"ID='{id}'")

    print(f"Detect ID: {id}, TL: {tl_standard}")
    print(f"--> Pinyin: {all_pinyin}")


if __name__ == "__main__":
    mydb = db.DB(cfg.taigi_DB["server_name"], cfg.taigi_DB["username"], cfg.taigi_DB["password"],
                cfg.taigi_DB["db_name"], port=cfg.taigi_DB["port"])
    mydb.build_connect()

    result = mydb.select("standard_dictionary", condition_str="註='*' and 修訂狀態='Y' and (發音='[]' or 發音='')",
                                                retrieve_str="ID, `TL-標準`, `TL-口語`")
    for item in result:
        parse_item(mydb, item, source="all")
