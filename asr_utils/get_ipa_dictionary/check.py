"""
Check mandarin dictionary
    (1) chewing in word not show in 1-char pinyin list
    (2) char number == chewning number
"""


import re
import pymysql
from collections import defaultdict





def get_char2pinyin(conn):
    # collect all char pinyin
    char2pinyin = defaultdict(lambda: set())
    with conn.cursor() as cursor:
        sql = f"SELECT 詞,注音 FROM standard_dictionary WHERE 低頻='0' AND (來源='MOE' or 來源='ckip')"
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            mandarin, chewing = row
            if chewing == "": continue
            char_list = [c for c in mandarin]
            chewing_list = chewing.split()
            for char, chew in zip(char_list, chewing_list):
                char2pinyin[char].add(chew)
    return char2pinyin


def check(conn, char2pinyin):
    with conn.cursor() as cursor:
        sql = f"SELECT 詞,注音 FROM standard_dictionary WHERE 低頻='0' AND 來源='SLAM'"
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            mandarin, chewing = row
            if chewing == "": continue

            mandarin = mandarin.replace("，", "")
            char_list = [c for c in mandarin]
            chewing_list = chewing.split()
            
            if len(char_list) != len(chewing_list):
                print(row)
                continue

            for char, chew in zip(char_list, chewing_list):
                if len(char2pinyin[char]) > 1:
                    if chew not in char2pinyin[char]:
                        print(f"{row} - ({char}) - {char2pinyin[char]}")
            
            

if __name__ == "__main__":
    conn = pymysql.connect("140.109.23.160", "henson", "yitang1220", "Taigi", port=3307)
    char2pinyin = get_char2pinyin(conn)
    check(conn, char2pinyin)
