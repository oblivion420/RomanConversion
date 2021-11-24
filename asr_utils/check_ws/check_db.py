import re
import glob
import pandas as pd
from pathlib import Path

from collections import defaultdict

from lib import lib_db
from lib import lib_syl_trans
from lib import lib_align_han_tl


TAG_HEAD = "\{\(「『【"
TAG_TAIL = "\}\)」』】"


def rm_punc(line):
    line = re.sub("[―─\.，,!﹗\"#$%'()\+?=;:￥～？﹔；：．。－（）！︰、「」\]\[《》〈〉『』◎∴]", "", line)
    line = re.sub("——", " ", line)
    line = re.sub(" +", " ", line)
    return line.strip()


def outliersub(m):
    """Convert the half-space in the tag into full-space"""
    head = m.group(1)
    body = m.group(2)
    tail = m.group(3)
    return head + body.replace(" ", "　") + tail


def edu_tw_dictionary(data_path, lexicon):
    oov = set()

    df = pd.read_csv(data_path)
    for index, row in df.iterrows():
        hanzi_line = row["例句"].lower().replace("台", "臺")
        tailo_line = row["例句標音"].lower()

        hanzi_line = rm_punc(hanzi_line)
        tailo_line = rm_punc(tailo_line)
        hanzi_line = lib_syl_trans.syl_trans(hanzi_line)
        tailo_line = lib_syl_trans.syl_trans(tailo_line)

        hanzi_list, tailo_list = lib_align_han_tl.align_hanzi_tailo(hanzi_line, tailo_line)
        hz_tl_pair_list = lib_align_han_tl.group_word(hanzi_list, tailo_list, tailo_line)

        for hanzi, tailo in hz_tl_pair_list:
            _tailo = re.sub("\-+", "-", tailo)
            _pair = (hanzi, _tailo)
            if _pair not in lexicon:
                _tailo = re.sub("\-{2,}", " ", tailo)
                hanzi_list, tailo_list = lib_align_han_tl.align_hanzi_tailo(hanzi, _tailo)
                hz_tl_pair_list = lib_align_han_tl.group_word(hanzi_list, tailo_list, _tailo)
                for h, t in hz_tl_pair_list:
                    __pair = (h, t)
                    if __pair not in lexicon:
                        oov.add(__pair)

    with open("oov/edu_tw_dictionary.txt", "w") as file:
        for hanzi, tailo in sorted(list(oov), key=lambda x: x[1]):
            file.write(f"{hanzi} {tailo}\n")


def yttd(data_dir, lexicon):
    oov = set()
    lexicon_hanzi = {hanzi for hanzi, tailo in lexicon}

    for data_kind in ["train", "dev", "eval"]:
        with open(f"{data_dir}/{data_kind}/text") as file:
            for line in file:
                uid, words = line.strip().split(" ", 1)
                for word in words.split():
                    if word not in lexicon_hanzi:
                        oov.add(word)

    with open("oov/yttd.txt", "w") as file:
        for hanzi in sorted(list(oov), key=lambda x: x[0]):
            file.write(f"{hanzi}\n")


def twisas(data_dir, lexicon):
    oov = set()
    lexicon_tailo = {tailo for hanzi, tailo in lexicon}

    for filepath in glob.glob(f"{data_dir}/*"):
        with open(filepath) as file:
            for line in file:
                line = line.strip()
                if not line.startswith("<"):
                    line = re.sub(F"([{TAG_HEAD}])(.*?)([{TAG_TAIL}])", "", line)
                    for word in line.split():
                        word = word.strip("-")
                        if word not in lexicon_tailo:
                            oov.add(word)

    with open("oov/twisas.txt", "w") as file:
        for tailo in sorted(list(oov), key=lambda x: x[0]):
            file.write(f"{tailo}\n")



def tsawa(data_dir, lexicon):
    # Taiwanese speaking about world affairs
    oov = defaultdict(lambda: set())
    lexicon_hanzi = {hanzi for hanzi, tailo in lexicon}

    for filepath in glob.glob(f"{data_dir}/*uihun*"):
        with open(filepath) as file:
            for line in file:
                line = re.sub(f"([{TAG_HEAD}|])(.*?)([{TAG_TAIL}|])", "", line)
                line = rm_punc(line)
                line = re.sub("(\\\\)([A-Za-z0-9\-/ ,]+)(\\\\)", outliersub, line)
                for word in re.split(" ", line):
                    m = re.search("\\\\[A-Za-z0-9\-/　,]+\\\\", word)
                    tailo_str = m.group() if m else ""
                    hanzi = word.replace(tailo_str, "")
                    tailo_str = tailo_str.replace("　", " ")
                    tailo_list = tailo_str[1:-1].split("/") if tailo_str else [""]


                    if re.fullmatch("[0-9]+", hanzi) or re.fullmatch("[A-Za-z]+", hanzi) or \
                        re.fullmatch("[A-Za-z0-9\-/ ,]+", hanzi): continue

                    if hanzi not in lexicon_hanzi:
                        for tailo in tailo_list:
                            oov[hanzi].add(tailo)

    with open("oov/tsawa.txt", "w") as file:
        for hanzi in sorted(list(oov.keys()), key=lambda x: x):
            for tailo in sorted(list(oov[hanzi])):
                if tailo == "" and len(oov[hanzi]) != 1: continue
                if tailo != "": continue
                file.write(f"{hanzi} {tailo}\n")


def main():
    lexicon = lib_db.get_lexicon()

    edu_tw_dictionary("data/edu_tw_dictionary/example.csv", lexicon)
    # yttd("/mnt/md0/Corpora/YTTD/data/201214", lexicon) # train / dev / eval
    # twisas("/mnt/md1/user_pinyuanc/code/tyt2tl/data", lexicon) # twisas combined (tailo)
    # tsawa("data/TSAWA", lexicon)


if __name__ == "__main__":
    main()
