import os
import re
import pandas as pd
from xlrd import open_workbook

def get_chewing_tone(syllable):
    if re.match(".+ˊ", syllable): tone = 2
    elif re.match(".+ˇ", syllable): tone = 3
    elif re.match(".+ˋ", syllable): tone = 4
    elif re.match(".+˙", syllable): tone = 5
    else: tone = 1
    return tone


def get_chewingSyl2hanyuSyl():
    filename = "../static/mandarin/華語pinyinTable.xlsx"
    df = pd.read_excel(filename, usecols=["注音", "hanyu"])
    syl_mapping = {row[0]:str(row[1]) for index, row in df.iterrows()}
    return syl_mapping


def chewing2hanyu(syl_mapping, chewing):
    def rreplace(s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    # syllable
    hanyu_sign = {"a": ["ā", "á", "ǎ", "à", "a"],
                "e": ["ē", "é", "ě", "è", "e"],
                "i": ["ī", "í", "ǐ", "ì", "i"],
                "o": ["ō", "ó", "ǒ", "ò", "o"],
                "u": ["ū", "ú", "ǔ", "ù", "u"],
                "ü": ["ǖ", "ǘ", "ǚ", "ǜ", "ǜ"]}
    chewing_sign = ["!", "ˊ", "ˇ", "ˋ", "˙"]

    if chewing[-1] not in chewing_sign: chewing += "!"
    tone_idx = chewing_sign.index(chewing[-1])
    hanyu = syl_mapping[chewing[:-1]]

    aoe_matched = re.search("[aoe]", hanyu)
    iu_matched = re.search("[iuü]", hanyu[::-1])

    if aoe_matched:
        char = aoe_matched.group()
        hanyu = hanyu.replace(char, hanyu_sign[char][tone_idx], 1)
    else:
        if iu_matched:
            char = iu_matched.group()
            hanyu = rreplace(hanyu, char, hanyu_sign[char][tone_idx], 1)

    return hanyu


class TONE_MAP():
    def __init__(self, source, target):
        self.tailo_tone = ["1", "2", "3", "4", "5", "7", "8", "9", "10"]
        self.ty_t_tone = self.forpa_tone = ["1", "4", "3", "7", "5", "2", "6", "9", "8"]
        self.mix_tone = ["1", "4", "3", "6", "2", "7", "8", "9", "10"]
        self.sampa_tone = ["55", "53", "31", "3", "13", "33", "5", "", ""]

        self.source = source
        self.target = target
        self.map = self.build_mapping()

    def build_mapping(self):
        source_tone_list, target_tone_list = [], []
        if self.source == "Dai-Lor":
            source_tone_list = self.tailo_tone
        elif self.source == "TY-T":
            source_tone_list = self.ty_t_tone
        elif self.source == "ForPA":
            source_tone_list = self.forpa_tone
        elif self.source == "MIX":
            source_tone_list = self.mix_tone
        elif self.source == "SAMPA":
            source_tone_list = self.sampa_tone

        if self.target == "Dai-Lor":
            target_tone_list = self.tailo_tone
        elif self.target == "TY-T":
            target_tone_list = self.ty_t_tone
        elif self.target == "ForPA":
            target_tone_list = self.forpa_tone
        elif self.target == "MIX":
            target_tone_list = self.mix_tone
        elif self.target == "SAMPA":
            target_tone_list = self.sampa_tone

        return dict(zip(source_tone_list, target_tone_list))

    def transform(self, tone):
        return self.map[tone]

class SYLLABLE_MAP():
    def __init__(self, source, target):
        self.forpa_excel = "../static/taigi/forpa_210624.xlsx"
        self.mandarin_pinyinTable = "../static/mandarin/華語pinyinTable.xlsx"
        self.taigi_pinyinTable = "../static/taigi/台語pinyinTable.xlsx"

        self.source = source
        self.target = target
        self.map = self.build_mapping()

    def build_mapping(self):
        pinyin_map = dict()

        if self.target == "IPA":
            if self.source  == "Zhuyin":
                pinyinTable = self.mandarin_pinyinTable
                source_field = 1
            elif self.source == "Dai-Lor":
                pinyinTable = self.taigi_pinyinTable
                source_field = 1
            elif self.source == "ForPA":
                pinyinTable = self.taigi_pinyinTable
                source_field = 0

            with open_workbook(pinyinTable) as wb:
                sheet = wb.sheets()[0]

                for row_index in range(1, sheet.nrows):
                    row = sheet.row_values(row_index)
                    source, ipa_diphthong_tone = row[source_field], row[4]
                    pinyin_map[source] = ipa_diphthong_tone
        else:
            pinyin = ["TWBet", "ForPA", "Zhuyin", "Hanyu", "Dai-Lor", "TLPA", "POJ", "Uanliu", "Daiim", "TY-T", "TY-H", "TY-K"]
            col = [1, 2, 4, 6, 8, 9, 10, 11, 13, 14, 15, 16]
            pinyin2col = dict(zip(pinyin, col))

            with open_workbook(self.forpa_excel) as wb:
                sheet = wb.sheets()[0]
                nrows = sheet.nrows

                for i in range(3, nrows):
                    row = sheet.row_values(i)
                    row = [r.strip() if type(r) == str else r for r in row]
                    source_syllable, target_syllable = row[pinyin2col[self.source]], row[pinyin2col[self.target]]
                    pinyin_map[source_syllable] = target_syllable
        return pinyin_map

    def transform(self, syllable):
        if syllable in self.map: return self.map[syllable].strip()
        else:
            print("=>", syllable)
            raise Exception("No corresponding syllable in table")


if __name__ == "__main__":
    mapping = get_chewingSyl2hanyuSyl()
    r = chewing2hanyu(mapping, "ㄉㄚˋ")
    print(r)

    syllable_map = SYLLABLE_MAP(source="Zhuyin", target="IPA")
    r = syllable_map.transform("ㄐㄧㄣ")
    print(r)

    tone_map = TONE_MAP(source="Dai-Lor", target="MIX")
    r = tone_map.transform("2")
    print(r)
