import re
import itertools

def get_syllable_list(word):
    syllable_seq = re.sub(", ?", " ", word)
    syllable_seq = re.sub("-", " ", word)
    return syllable_seq.split()

class TAILO():
    def __init__(self, hanzi, word):
        self.hanzi = hanzi
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
        new_word_list_post = self.post_process(self.hanzi, self.word, new_word_list)
        return list(set([modified_word.format(*varient) for varient in new_word_list_post]))

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

    def post_process(slef, hanzi, word, modify_):
        hanzi = hanzi.replace("，", "")
        word = word.replace(", ","-")
        print(hanzi, word, modify_)

        new_modify_set = []
 
        if "去" in hanzi:
            wd_index = ((hanzi.index("去")))
            for modify_seq in modify_:
                lst =[]
                new_modify_set.append(modify_seq)
                for n, modify_syl in enumerate(modify_seq):

                    if n == wd_index:
                        lst.append('i_1')
                    else:
                        lst.append(modify_syl)
                if lst not in new_modify_set:
                    new_modify_set.append(lst)
            return new_modify_set


        if '仔' in hanzi:

            h_i = hanzi.index("仔")
            convert_dict = {"2": "1", "3": "1", "4": "1",
                            "1": "7", "5":"7", "7":"7", "8":"7", "9":"9"}

            for modify_seq in modify_:
                lst =[]
     
                for n, modify_syl in enumerate(modify_seq):
                    if n == h_i-1:
                        
                        tmp_syl_lst = word.split("-")
                        pre_syl = (tmp_syl_lst[h_i-1])
                        syllable_tail, tone = pre_syl.split("_")
                        new_syllable_ = (f"{syllable_tail}_{convert_dict[tone]}")          
                        lst.append(new_syllable_)                        
                    else:
                        lst.append(modify_syl)

                if lst not in new_modify_set:
                    new_modify_set.append(lst)
        
            return new_modify_set

        special_case_set = ["欲","甲","才","較","咧"]
        for modify_seq in modify_:
            
            if 'h_1' in modify_seq:
                idx = modify_seq.index('h_1')
                if hanzi[idx] in special_case_set:
                    new_modify_set.append(modify_seq)
            else:
                new_modify_set.append(modify_seq)

        return new_modify_set



            


if __name__ == "__main__":
    test_seq = "阿不倒仔 (1)"
    testcases = ["a_1-put_4-to_2-a_2"]
    # ["liam3-khi1-lih1", "liam5-khi3-lih3", "liam7-khi1-lih1", "liam3-khi1-khi1", "liam5-khi3-khi3", "liam7-khi1-khi1"]

    for testcase in testcases:
        all = TAILO(test_seq, testcase).modify()
        all = [i.replace("_", "") for i in all]
        all = str(all).replace("'", "\"")

        print(testcase)
        print("Modified:", all, "\n")

