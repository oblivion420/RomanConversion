import os
import re
import glob
import pymysql
from pathlib import Path
from datetime import date
from importlib import import_module


cfg = import_module("config.prd")
for i in [cfg.db]:
    for key, value in i.items():
        assert key not in globals()
        globals()[key] = value

def get_episode(episode_id, retrieve_list=["*"]):
    mydict = {}
    retrieve_str = ", ".join([field if field not in mapping2db else mapping2db[field] for field in retrieve_list])
    if retrieve_list == ["*"]: retrieve_list = list(field_index.keys())

    conn = pymysql.connect(server_name, username, password, db_name, port=port)
    cursor = conn.cursor()
    try:
        sql = f"SELECT {retrieve_str} FROM {trans_table} WHERE UID LIKE '{episode_id}%'"
        cursor.execute(sql)
        results = cursor.fetchall()
        for utt in results:
            uid, utt_dict = None, {}
            for index, field in enumerate(retrieve_list):
                if field == "uid":
                    uid = utt[index]
                elif field in ["playlist_id", "modified_by"]: continue
                else:
                    utt_dict[field] = utt[index]
            mydict[uid] = utt_dict
    except:
       print ("Error: unable to fetch data")
    finally:
        cursor.close()
        conn.close()
        return mydict

def get_drama_episode_list(playlist_id):
    episode_list = []
    conn = pymysql.connect(server_name, username, password, db_name, port=port)
    cursor = conn.cursor()
    try:
        sql = f"SELECT DISTINCT SUBSTRING(UID, 1, 11) FROM {trans_table} WHERE PLAYLIST_ID LIKE '{playlist_id}'"
        cursor.execute(sql)
        episode_list = sorted([i for ii in cursor.fetchall() for i in ii], key=lambda x: x)
    except:
       print ("Error: unable to fetch data")
    finally:
        cursor.close()
        conn.close()
        return episode_list

def get_drama_statistics(playlist_id):
    mydict = {
        "time": 0, "checked_time": 0, "usable_time": 0,
        "sent": 0, "checked_sent": 0, "usable_sent": 0
    }

    conn = pymysql.connect(server_name, username, password, db_name, port=port)
    cursor = conn.cursor()
    try:
        sql = f"SELECT 小時數 FROM {playlist_table} WHERE PLAYLIST_ID LIKE '{playlist_id}'"
        cursor.execute(sql)
        mydict["time"] = cursor.fetchone()[0]

        # select all utterence of the drama
        sql = f"SELECT UID, START, END, CHECKED, DISCARDED, REVIEW, CUT FROM {trans_table} "\
                f"WHERE PLAYLIST_ID LIKE '{playlist_id}' AND CHECKED=1"
        cursor.execute(sql)
        result = cursor.fetchall()

        mydict["sent"] = len(result)
        for item in result:
            duration = (item[2]-item[1]) / 3600
            mydict["checked_time"] += duration
            mydict["checked_sent"] += 1
            if item[4] == 0 and item[5] == 0 and item[6] == 0:
                mydict["usable_time"] += duration
                mydict["usable_sent"] += 1
    except:
       print ("Error: unable to fetch data")
    finally:
        cursor.close()
        conn.close()
        return mydict

def get_episode_statistics(episode_ids):
    mydict = {}

    conn = pymysql.connect(server_name, username, password, db_name, port=port)
    cursor = conn.cursor()

    try:
        for episode_id in episode_ids:
            mydict[episode_id] = {}

            sql = f"SELECT COUNT(*) FROM {trans_table} WHERE UID LIKE '{episode_id}%'"
            cursor.execute(sql)
            mydict[episode_id]["total_sent"] = cursor.fetchone()[0]

            sql = f"SELECT COUNT(*) FROM {trans_table} WHERE UID LIKE '{episode_id}%' AND CHECKED=1"
            cursor.execute(sql)
            mydict[episode_id]["checked_sent"] = cursor.fetchone()[0]
    except:
       print ("Error: unable to fetch data")
       mydict = {}
    finally:
        cursor.close()
        conn.close()
        return mydict

def get_utt(uid):
    result = None

    conn = pymysql.connect(server_name, username, password, db_name, port=port)
    cursor = conn.cursor()

    try:
        sql = f"SELECT * FROM {trans_table} WHERE UID LIKE '{uid}'"
        cursor.execute(sql)
        result = cursor.fetchone()
    except:
        print ("Error: unable to select data")
    finally:
        cursor.close()
        conn.close()
        return result

def update_utt(uid, mandarin, hanzi, checked, discarded, cut, review, modified_by):
    result = None
    status_msg = {True: ("Success", "更新成功"), False: ("Fail", "更新失敗")}

    conn = pymysql.connect(server_name, username, password, db_name, port=port)
    cursor = conn.cursor()

    try:
        sql = f"UPDATE {trans_table} SET 華語='{mandarin}', 台語='{hanzi}', CHECKED={checked}, DISCARDED={discarded},"\
                f"CUT={cut}, REVIEW={review}, MODIFIED_BY='{modified_by}' WHERE UID LIKE '{uid}'"
        cursor.execute(sql)
        conn.commit()
        result = True
    except:
        conn.rollback()
        print ("Error: unable to update data")
        result = False
    finally:
        cursor.close()
        conn.close()
        return status_msg[result]


def dump_taigi_dict():
    lexicon_name = "static/lexicon"

    today = date.today()
    suffix = today.strftime("%Y%m%d")
    new_lexicon_path = Path(f"{lexicon_name}_{suffix}.txt")

    mydict = {"<UNK>": "<UNK>"}

    if new_lexicon_path.exists():
        print("Load existing lexicon...")

        with open(new_lexicon_path, "r") as file:
            for line in file:
                hanzi, tailo = line.strip().split("\t")
                mydict[hanzi] = tailo

        return mydict, new_lexicon_path

    else:
        print("Get database data...")

        for old_lexicon in glob.glob(f"{lexicon_name}*"):
            os.remove(old_lexicon)

        conn = pymysql.connect(server_name, username, password, db_name, port=port)
        cursor = conn.cursor()

        try:
            sql = f"SELECT `漢字`, `TL-標準` FROM {standard_dictionary_table} WHERE 修訂狀態='Y' AND 註 NOT LIKE BINARY '%*%' ORDER BY ID"
            cursor.execute(sql)
            results = cursor.fetchall()
            for item in results:
                hanzi, tailo = item
                if not hanzi or not tailo: continue

                hanzi = re.sub("，", "", hanzi)
                hanzi = re.sub(" ?\([0-9]\)", "", hanzi).strip()
                tailo = tailo.replace(", ", " ").strip().lower()

                # Ignore 破音字
                mydict[hanzi] = tailo
        except:
           print ("Error: unable to fetch data")
        finally:
            cursor.close()
            conn.close()

        with open(new_lexicon_path, "w") as file:
            for hanzi in mydict:
                tailo = mydict[hanzi]
                file.write(f"{hanzi}\t{tailo}\n")

        return mydict, new_lexicon_path
