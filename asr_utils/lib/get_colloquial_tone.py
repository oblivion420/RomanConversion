import re
import itertools

def get_syllable_list(word):
    syllable_seq = re.sub(", ?", " ", word)
    syllable_seq = re.sub("-", " ", word)
    return syllable_seq.split()

class TAILO():
    def __init__(self, word):
        self.word = word
        self.special = {"tshut_8": "tshut_10"} # original tshut_4

    def modify_tone(self, tail, h=0, south_north=0):
        convert_dict = {"1": ["7"], "7": ["3"], "3": ["2"], "2": ["1"],
                        "5": ["7", "3"], "9": ["9"],
                        "p_4": ["8"], "t_4": ["8"], "k_4": ["8"],
                        "p_8": ["10"], "t_8": ["10"], "k_8": ["10"],
                        "h_8": ["3", "7"], "h_4": ["2", "1"]}
        try:
            syllable_tail, tone = tail.split("_")
            key = tone if tone not in ["4", "8"] else f"{syllable_tail}_{tone}"
            if key == "5": return f"{syllable_tail}_{convert_dict[key][int(south_north)]}"
            elif key in ["h_8", "h_4"]: return f"{syllable_tail}_{convert_dict[key][int(h)]}"
            else: return f"{syllable_tail}_{convert_dict[key][0]}"
        except:
            print("Failed to modify tone:", self.word, "=>", syllable_tail)
            return self.word

    def modify(self):
        ori_tone_list = re.findall("[a-z]_[0-9]|,", self.word)
        modified_word = re.sub("[a-z]_[0-9]", "{}", self.word)

        # Split into sentences
        size = len(ori_tone_list)

        idx_list = [idx + 1 for idx, val in enumerate(ori_tone_list) if val == ","]
        start_pos_list = [0]+idx_list
        end_pos_list = (idx_list + ([size] if idx_list[-1] != size else [])) if idx_list else [size]

        sents = []
        for i, j in zip(start_pos_list, end_pos_list):
            if j in idx_list:
                sents += [ori_tone_list[i: j-1]]
            else:
                sents += [ori_tone_list[i: j]]

        # Modify tone
        sn_runs = "01" if "5" in self.word else "0"
        sa_runs = "01"
        h_runs = "01" if re.search("h_4|h_8", self.word)  else "0"
        new_word_list = []

        for sn in sn_runs: # 南北調
            for sa in sa_runs: # 全部/部份轉調
                for h in h_runs:
                    new_sent_list = []

                    for sent in sents:
                        if len(sents) > 1:
                            new_sent_list += [self.apply_n_gram(sent, sn, sa, h, is_sentence=True)]
                        else:
                            new_sent_list += [self.apply_n_gram(sent, sn, sa, h, is_sentence=False)]

                    new_word_list += [new_sent_list]

        new_word_list = [[syl for sent in varient for syl in sent] for varient in new_word_list]
        return list(set([modified_word.format(*varient) for varient in new_word_list]))

    def apply_n_gram(self, syl_list, sn, sa, h, is_sentence=False):
        length = len(syl_list)
        candidate_list = []

        # position 本調規則
        rule = {3: {"0": [0, 2], "1": [2]},
                4: {"0": [1, 3], "1": [3]},
                5: {"0": [1, 4], "1": [4]}} # default 0->-1 / 1->None
        if is_sentence:
            if length not in rule.keys():
                rule[length] = {"0": [length-1], "1": [length-1]}
        else:
            if length not in [4, 5]:
                rule[length] = {"0": [length-1], "1": []}

        for idx, syl in enumerate(syl_list):
            if idx in rule[length][sa]: # 本調
                candidate_list += [syl]
            else: # 變調
                candidate_list += [self.modify_tone(syl, h, sn)]

        return candidate_list


if __name__ == "__main__":
    testcases = ["peh_4-tiam_2-tong_3"]

    for testcase in testcases:
        all = TAILO(testcase).modify()
        all = [i.replace("_", "") for i in all]
        all = str(all).replace("'", "\"")

        print(testcase)
        print("Modified:", all, "\n")
