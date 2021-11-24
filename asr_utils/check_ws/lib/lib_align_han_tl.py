import re

ranges = [
  {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},         # compatibility ideographs
  {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},         # compatibility ideographs
  {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},         # compatibility ideographs
  {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")}, # compatibility ideographs
  {'from': ord(u'\u3040'), 'to': ord(u'\u309f')},         # Japanese Hiragana
  {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")},         # Japanese Katakana
  {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},         # cjk radicals supplement
  {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
  {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
  {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
  {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
  {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
  {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
]


def is_cjk(char):
  return any([range["from"] <= ord(char) <= range["to"] for range in ranges])


def recontruct(_str):
    output = ""
    for char in _str:
        if is_cjk(char) or char in ["‘", "’", "『", "』"]:
            output += f" {char} "
        elif char == "-":
            output += " "
        else:
            output += char
    return re.sub(" +", " ", output).strip()


def align_hanzi_tailo(hanzi, tailo):
    MANDARIN_TAGS = {"‘", "’", "『", "』"}

    # Process "/" tag
    if re.search("/", hanzi) and re.search("/", tailo):
        hanzi = hanzi.replace("/", "")
        tailo = tailo.replace("/", " ")
    elif not re.search("/", hanzi) and re.search("/", tailo):
        tailo = re.sub("/.+? |/.+?$", " ", tailo)

    hanzi = hanzi.strip()
    new_tailo = recontruct(tailo)
    tailo_seq = new_tailo.split()

    hanzi2tailo_list = []
    hanzi_word = ""
    syl_idx_of_tailo = 0
    hanzi_length = len(hanzi)

    for char_idx_of_hanzi, char_of_hanzi in enumerate(hanzi):
        if is_cjk(char_of_hanzi) or char_of_hanzi in MANDARIN_TAGS:
            hanzi2tailo_list += [(char_of_hanzi, tailo_seq[syl_idx_of_tailo])]
            syl_idx_of_tailo += 1
        elif char_of_hanzi in [" ", "-"] and hanzi_word == "": continue
        else:
            hanzi_word += char_of_hanzi
            # print("->", hanzi_word, tailo_seq[syl_idx_of_tailo])
            if char_idx_of_hanzi == hanzi_length-1 or \
                is_cjk(hanzi[char_idx_of_hanzi+1]) or \
                hanzi[char_idx_of_hanzi+1] == " " or \
                hanzi[char_idx_of_hanzi+1] in MANDARIN_TAGS or \
                hanzi_word == tailo_seq[syl_idx_of_tailo] or \
                (re.fullmatch("[a-zA-Z]+[0-9]", hanzi_word) and re.fullmatch("[a-zA-Z]+[0-9]", tailo_seq[syl_idx_of_tailo])) or \
                (char_of_hanzi == "-" and hanzi[char_idx_of_hanzi-1] == "-"):
                num_syl = len(hanzi_word.strip("-").split("-")) if re.match("[a-zA-Z]+[0-9]", hanzi_word) or re.fullmatch("[a-zA-Z]+", hanzi_word) else len(hanzi_word)
                if hanzi_word == tailo_seq[syl_idx_of_tailo] and re.fullmatch("[0-9]+", hanzi_word):
                    num_syl = 1
                # print("=>", tailo_word, "-".join(tailo_seq[syl_idx_of_tailo:syl_idx_of_tailo+num_syl]))
                tailo_word = "-".join(tailo_seq[syl_idx_of_tailo:syl_idx_of_tailo+num_syl])
                hanzi2tailo_list += [(hanzi_word, tailo_word)]
                syl_idx_of_tailo += num_syl
                hanzi_word = ""
        # print(hanzi2tailo_list)
    # print(hanzi2tailo_list)
    assert syl_idx_of_tailo == len(tailo_seq)

    hanzi_seq, tailo_seq = zip(*hanzi2tailo_list)
    return list(hanzi_seq), list(tailo_seq)


def group_word(hanzi_list, tailo_list, tailo_line):
    tailo_word_seq = [i for i in re.split(" ", tailo_line) if i]
    tmp_syl_start = -1
    tl_wd_idx = 0

    hz_tl_pair_list = []
    for tl_syl_idx in range(len(tailo_list)):
        if tmp_syl_start == -1: tmp_syl_start = tl_syl_idx

        if "-".join(tailo_list[tmp_syl_start:tl_syl_idx+1]) == re.sub("\-+", "-", tailo_word_seq[tl_wd_idx]):
            hanzi_word = hanzi_list[tmp_syl_start:tl_syl_idx+1]
            tailo_word = tailo_list[tmp_syl_start:tl_syl_idx+1]
            if "".join(hanzi_word) == "".join(tailo_word):
                hanzi_word = "-".join(hanzi_word) # tl-tl
            else:
                hanzi_word = "".join(hanzi_word)
                # lan7爛, 爛lan7
                hanzi_word = re.sub("([0-9])([^A-Za-z0-9])", r"\1-\2", hanzi_word)
                hanzi_word = re.sub("([^A-Za-z0-9])([A-Za-z])", r"\1-\2", hanzi_word)
                # 關-nuai1teh4
                hanzi_word = re.sub("([0-9])([A-Za-z])", r"\1-\2", hanzi_word)

            hz_tl_pair_list.append([hanzi_word, tailo_word_seq[tl_wd_idx]]) # "-".join(tailo_word)
            # print("->", tailo_list[tmp_syl_start:tl_syl_idx+1], " == ", hanzi_word)
            tmp_syl_start = -1
            tl_wd_idx += 1


    return hz_tl_pair_list


if __name__ == "__main__":
    hanzi = "下晡我欲揣阿美仔去𨑨迌"
    tailo = "e7-poo1 gua2 beh4 tshue7 a1-bi2--a2 khi3 tshit4-tho5"
    hanzi_list, tailo_list = align_hanzi_tailo(hanzi, tailo)
    print(hanzi_list)
    print(tailo_list)
    hz_tl_pair_list = group_word(hanzi_list, tailo_list, tailo)
    print(hz_tl_pair_list)
