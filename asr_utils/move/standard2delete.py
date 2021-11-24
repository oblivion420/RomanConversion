import re
import sys
sys.path.append("..")

import json
from collections import defaultdict
from importlib import import_module

from lib import db
from lib import utils
from lib import get_colloquial_tone


def main():
    cfg = import_module("config.{}".format("db"))
    mydb = db.DB(cfg.taigi_DB["server_name"], cfg.taigi_DB["username"], cfg.taigi_DB["password"],
                cfg.taigi_DB["db_name"], port=cfg.taigi_DB["port"])
    mydb.build_connect()

    result = mydb.select("standard_dictionary", condition_str="`修訂狀態` LIKE 'Z'")
    for item in result:
        _id = item[0]
        item = item[:8] + item[9:]
        item = [i.strip() for i in item[1:]]
        hanzi, tl_standard, varient, synonym, mandarin, tl_colloquial, _, source, status, comment, example, editor = item

        varient = json.loads(varient)
        varient = varient[0] if len(varient) >= 1 else ""
        synonym = json.loads(synonym)
        synonym = synonym[0] if len(synonym) >= 1 else ""
        mandarin_list = json.loads(mandarin)
        tl_colloquial = json.loads(tl_colloquial)
        tl_colloquial = tl_colloquial[0]
        source = json.loads(source)
        source = source[0] if len(source) >= 1 else ""
        example_list = json.loads(example)
        example = example_list[0] if len(example_list) >= 1 else ""

        print(hanzi)

        for mandarin in mandarin_list:
            mydb.insert("to_be_deleted_dictionary",
                set_str="(`漢字`, `TL-標準`, `註`, `異用字`, `同義詞`, `華語詞`, `TL-口語`, `發音`, `來源`, `修訂狀態`, `範例1`, `範例2`, `範例3`, `範例4`, `範例5`)",
                value_str="('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                            hanzi, tl_standard, comment, varient, synonym, mandarin, tl_colloquial,
                            "", source, status, example, "", "", "", "", ""))
        
        mydb.delete("standard_dictionary", condition_str=f"ID='{_id}'")


if __name__ == "__main__":
    main()