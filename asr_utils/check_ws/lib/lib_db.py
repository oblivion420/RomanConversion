import re
import json
import pymysql


def rm_tag(word):
    word = re.sub("=", "", word)
    word = re.sub("[，,]", "，", word)
    word = re.sub("[，]", "", word)
    word = re.sub(" +?\([0-9]+\)", "", word)
    word = re.sub("\([0-9]+\)", "", word)
    return word


def get_lexicon():
    lexicon = set()
    conn = pymysql.connect(host="140.109.23.160", user="henson", password="yitang1220",database="Taigi", port=3307)
    with conn.cursor() as cursor:
        sql = f"SELECT `漢字`, `TL-口語` FROM standard_dictionary WHERE 修訂狀態='Y' AND 註!='*'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for hanzi, tailo_list in results:
            hanzi = rm_tag(hanzi)
            hanzi = hanzi.strip()
            tailo_list = json.loads(tailo_list)
            for tailo in tailo_list:
                lexicon.add((hanzi.lower(), tailo.lower()))

    return lexicon
