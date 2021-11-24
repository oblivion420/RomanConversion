import re
import sys
sys.path.append("..")

import json
import tqdm
import joblib
import argparse
from xlrd import open_workbook
from collections import defaultdict
from importlib import import_module

from lib import db
from lib import utils
from lib import pinyin_transform
from lib import get_colloquial_tone


def get_taigi_dict(db):
    syllable_transformer = pinyin_transform.SYLLABLE_MAP(source="Dai-Lor", target="IPA")
    tone_transformer = pinyin_transform.TONE_MAP(source="Dai-Lor", target="MIX")

    def tl2ipa(tl_seq):
        tl_seq = tl_seq.replace(", ", " ")
        tl_seq = utils.transform_pinyin_format(tl_seq.lower())
        tl_list = [(tl.split("_")[0], tl.split("_")[1]) for tl in re.split("[ \-]", tl_seq)]
        ipa_list = [f"{syllable_transformer.transform(syl)}".format(tone_transformer.transform(tone)) for syl, tone in tl_list]
        ipa_seq = " ".join(ipa_list)
        return ipa_seq

    mydict = defaultdict(lambda: defaultdict(lambda: list()))

    result = []
    table_list = [cfg.taigi_DB["table_all_dictionary"]]
    for table in table_list:
        result += db.select(table, condition_str="(修訂狀態='Y' OR 修訂狀態='') AND 註 NOT LIKE BINARY '%D%' AND 註 != '*'")

    # Extract basic data
    for item in result:
        item = [i.strip() if idx not in [0, 8] else i for idx, i in enumerate(item)]
        id, hanzi, tl_std, varient_list, synonym_list, mandarin_list, tl_collo_list, tone_sandhi_list, is_phrase, _, _, _, _, _ = item
        tl_std = tl_std.lower()
        tone_sandhi_list = tone_sandhi_list.lower()

        try:
            varient_list = json.loads(varient_list)
            synonym_list = json.loads(synonym_list)
            mandarin_list = json.loads(mandarin_list)
            tl_collo_list = json.loads(tl_collo_list)
            tone_sandhi_list = json.loads(tone_sandhi_list)
        except Exception as e:
            print(item)
            print(e)
            continue

        if not hanzi or not tl_std: continue
        if re.fullmatch("[A-Z]+", hanzi) and hanzi not in ["AH", "LIOH"]: continue

        # Preprocess
        hanzi = re.sub("=", "", hanzi)
        hanzi = re.sub("[，,]", "，", hanzi)
        hanzi = re.sub("[，]", "", hanzi)
        hanzi = re.sub(" +?\([0-9]+\)", "", hanzi)
        hanzi = re.sub("\([0-9]+\)", "", hanzi)

        mydict[(hanzi, tl_std)]["mandarin"] = mydict[(hanzi, tl_std)]["mandarin"].union(set(mandarin_list)) if (hanzi, tl_std) in mydict else set(mandarin_list)
        mydict[(hanzi, tl_std)]["mandarin"] = {i for i in mydict[(hanzi, tl_std)]["mandarin"] if i != ""}
        mydict[(hanzi, tl_std)]["tailo_collo"] = tl_collo_list
        mydict[(hanzi, tl_std)]["tailo_tone_sandhi"] = list(set(tone_sandhi_list))

    # Transform tone sandhi to the syllable i want
    for hanzi, tl_std in tqdm.tqdm(mydict):
        removed_tl_seq = set()
        for tl_seq in mydict[(hanzi, tl_std)]["tailo_tone_sandhi"]:
            try:
                ipa_seq = tl2ipa(tl_seq)
                mydict[(hanzi, tl_std)]["ipa_tone_sandhi"].append(ipa_seq)
            except:
                print(hanzi, tl_std)
                print("Error", tl_seq)
                removed_tl_seq.add(tl_seq)

        for tl_seq in removed_tl_seq:
            mydict[(hanzi, tl_std)]["tailo_tone_sandhi"].remove(tl_seq)

    # Clean no valid tone sandhi word
    removed_key = set()
    for hanzi, tl_std in mydict:
        if len(mydict[(hanzi, tl_std)]["tailo_tone_sandhi"]) == 0:
            removed_key.add((hanzi, tl_std))
    for key in removed_key:
        mydict.pop(key, None)
    return mydict


def get_mandarin_dict_src(db):
    word2src = dict()

    results = db.select(cfg.mandarin_DB["table_all_dictionary"], retrieve_str="詞, 來源", condition_str="低頻=0")
    for item in results:
        word, source = item
        word2src[word] = source

    return word2src


def get_mandarin_dict(db):
    lexicon = defaultdict(lambda: set())
    mydict = defaultdict(lambda: defaultdict(lambda: set()))

    syllable_map_chewing2hanyu = pinyin_transform.get_chewingSyl2hanyuSyl()
    syllable_map = pinyin_transform.SYLLABLE_MAP(source="Zhuyin", target="IPA")

    results = db.select(cfg.mandarin_DB["table_all_dictionary"], retrieve_str="詞, 注音, IPA", condition_str="低頻=0")
    for item in results:
        word, chewing, ipa = item
        word = word.replace("，", "")
        if word == "": print(item)
        try:
            if ipa:
                lexicon[word].add(ipa)
            elif chewing:
                ipa_list, hanyu_list = [], []
                for c in chewing.split():
                    tone = pinyin_transform.get_chewing_tone(c)
                    syllable = re.sub("[ˊˇˋ˙]", "", c)
                    ipa = syllable_map.transform(syllable)
                    ipa_list += [ipa.format(tone)]
                    hanyu = pinyin_transform.chewing2hanyu(syllable_map_chewing2hanyu, c)
                    hanyu_list += [hanyu]
                ipa_syl_seq = " ".join(ipa_list)
                ipa_phone_seq = ipa_syl_seq.replace("-", " ")
                hanyu_syl_seq = " ".join(hanyu_list)
                lexicon[word].add(ipa_phone_seq)
                mydict[(word, ipa_phone_seq)]["ipa"] = ipa_syl_seq
                mydict[(word, ipa_phone_seq)]["pinyin"] = hanyu_syl_seq

        except:
            print(item, "->", chewing)

    for word, ipa_phone_seq in mydict:
        mydict[(word, ipa_phone_seq)] = dict(mydict[(word, ipa_phone_seq)])

    return lexicon, dict(mydict)


def get_mandarin_varient(db):
    varient2normal = defaultdict(lambda: set())

    results = db.select(cfg.mandarin_DB["table_all_dictionary"], retrieve_str="詞, 異體字", condition_str="低頻=0")
    for item in results:
        normal, varient = item
        if varient.strip() == "": continue
        varient2normal[varient] = normal

    return varient2normal


def get_zh_en_dict(db):
    lexicon = defaultdict(lambda: set())

    results = db.select("zh_en_dictionary", retrieve_str="詞, IPA")
    for item in results:
        item = [i.strip() for i in item]
        word, ipa = item
        if ipa == "": continue
        if "ɾ" not in ipa: # current model not support ɾ
            lexicon[word].add(ipa)

    return lexicon


def get_zh_en_varient(db):
    varient2normal = defaultdict(lambda: set())

    results = db.select("zh_en_dictionary", retrieve_str="詞, 異體字")
    for item in results:
        normal, varient = item
        if varient.strip() == "": continue
        varient2normal[varient] = normal

    return varient2normal


def get_common_en_dict(db):
    lexicon = defaultdict(lambda: set())

    results = db.select("common_en_dictionary", retrieve_str="詞, IPA")
    for item in results:
        item = [i.strip() for i in item]
        word, ipa = item
        if ipa == "": continue
        if "ɾ" not in ipa: # current model not support ɾ
            lexicon[word].add(ipa)

    return lexicon


def to_dict(mydict):
    for hanzi, tl_std in mydict:
        # mydict[(hanzi, tl_std)].pop("mandarin", None)
        mydict[(hanzi, tl_std)].pop("tailo_collo", None)
        # mydict[(hanzi, tl_std)].pop("tailo_tone_sandhi", None)
        # mydict[(hanzi, tl_std)]["ipa_tone_sandhi"] = dict(mydict[(hanzi, tl_std)]["ipa_tone_sandhi"])
        mydict[(hanzi, tl_std)] = dict(mydict[(hanzi, tl_std)])
    return dict(mydict)


def check_tai_format(filepath):
    print("Following is the Hanzi with wrong format:")
    with open(filepath) as file:
        for line in file:
            word, _ = line.strip().split(" ", 1)
            if re.fullmatch("[A-Za-z\-0-9']+", word) or \
                re.fullmatch("[^A-Za-z0-9]+", word) or \
                not re.search("[0-9]", word): continue
            else:
                syls = word.split("-")
                for syl in syls:
                    if re.fullmatch("[A-Za-z]+[0-9]", syl) or \
                        len(syl) == 1: continue
                    else: print(word)


if __name__ == "__main__":
    cfg = import_module("config.db")

    # ======================== Config ========================
    parser = argparse.ArgumentParser()
    parser.add_argument("--taigi", action="store_true")
    parser.add_argument("--mandarin", action="store_true")
    parser.add_argument("--english", action="store_true")
    args = parser.parse_args()

    taigi = args.taigi
    mandarin = args.mandarin
    common_en = args.english
    zh_en = True if args.mandarin and args.english else False

    lexicon = defaultdict(lambda: set())
    varient2normal = dict()

    # ======================== Taigi ========================
    mydb = db.DB(cfg.taigi_DB["server_name"], cfg.taigi_DB["username"], cfg.taigi_DB["password"],
                cfg.taigi_DB["db_name"], port=cfg.taigi_DB["port"])
    mydb.build_connect()

    if taigi:
        taigi_dict = get_taigi_dict(mydb)
        for hanzi, tl_std in sorted(taigi_dict.keys()):
            for ipa in sorted(taigi_dict[(hanzi, tl_std)]["ipa_tone_sandhi"]):
                ipa_ = ipa.replace("-", " ")
                lexicon[hanzi].add(ipa_)

    mydb.close_connect()

    # ======================== Mandarin ========================
    mydb = db.DB(cfg.mandarin_DB["server_name"], cfg.mandarin_DB["username"], cfg.mandarin_DB["password"],
                cfg.mandarin_DB["db_name"], port=cfg.mandarin_DB["port"])
    mydb.build_connect()

    if mandarin:
        lexicon, mandarin_dict = get_mandarin_dict(mydb)
        for word, ipa_set in lexicon.items():
            lexicon[word] = lexicon[word].union(ipa_set)
        varient2normal.update(get_mandarin_varient(mydb))
        word2src = get_mandarin_dict_src(mydb)

    if common_en:
        for word, ipa_set in get_common_en_dict(mydb).items():
            lexicon[word] = lexicon[word].union(ipa_set)

    if zh_en:
        for word, ipa_set in get_zh_en_dict(mydb).items():
            lexicon[word] = lexicon[word].union(ipa_set)
        varient2normal.update(get_zh_en_varient(mydb))

    mydb.close_connect()

    # ======================== Dump lexicon to file ========================
    if taigi and mandarin: filename = "taidarin"
    elif taigi and not mandarin: filename = "taigi"
    elif not taigi and mandarin: filename = "mandarin"
    if common_en or zh_en: filename += "E"

    with open(f"output/{filename}_dictionary.txt", "w") as file:
        for word in sorted(lexicon):
            for ipa in sorted(lexicon[word]):
                file.write(f"{word} {ipa}\n")

    # ======================== Check hanzi format ========================
    if taigi:
        check_tai_format(f"output/{filename}_dictionary.txt")


    # ======================== Dump varient to file ========================
    if mandarin:
        with open(f"output/{filename}_+varient_dictionary.txt", "w") as file:
            for word in sorted(lexicon):
                for ipa in sorted(lexicon[word]):
                    file.write(f"{word} {ipa}\n")
            for varient, _ in varient2normal.items():
                file.write(f"{varient} ?\n")

    # ======================== Dump to joblib ========================
    if taigi:
        taigi_dict = to_dict(taigi_dict)
        filename = re.sub("E$", "", filename)
        joblib.dump(taigi_dict, f"output/{filename}_dictionary_old.joblib")
        for hanzi, tl_std in taigi_dict:
            taigi_dict[(hanzi, tl_std)].pop("mandarin", None)
        joblib.dump(taigi_dict, f"output/{filename}_dictionary.joblib")

    if mandarin:
        filename = re.sub("E$", "", filename)
        joblib.dump(varient2normal, f"output/{filename}_varient2normal.joblib")
        joblib.dump(word2src, f"output/{filename}_word2src.joblib")
        joblib.dump(mandarin_dict, f"output/{filename}_dictionary.joblib")
