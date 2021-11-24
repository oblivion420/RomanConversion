import re
import sys
import codecs
import string
import argparse
from pathlib import Path
from collections import defaultdict


# =============================================================================
# Functions
# =============================================================================
def get_word_len(word):
    return len(re.split("[\- ]", word.replace(",", "")))

def split_text(text):
    new_text = []
    for words in re.split('-', text):
        if re.fullmatch('[A-Za-z0-9]+', words):
            new_text += [words]
        else:
            for w in words: new_text += [w]

    return new_text

def remove_punctuation(line):
    # Not remove english ', but remove all chinese related punctuation
    punctuation = '[\-:?<>/"... ：；;.$,“”+——！！，。？、~@#￥%……&*（）\[\]「」《》【】｢｣『』]+'
    line = re.sub(punctuation, "", line.strip())

    for m in re.findall('.*\'', line):
        if re.findall('[A-Za-z]+\'', m):
            continue
        else:
            line = line.replace(m, re.sub('\'', '', m))
    return line

def cut_sentence_fwd(text, dict_list, max_len):
    result, not_match = [], []

    text = split_text(text)
    text_len = len(text)
    no_word = ""
    n = 0

    while n < text_len:
        matched = 0
        for i in range(min(max_len, text_len), 0, -1):
            if n + i > text_len: continue

            word = "-".join(text[n:n+i])
            if word in dict_list[i-1]:
                matched = 1
                result.append(word)
                n = n + i
                break
        if not matched:
            not_match.append(text[n])
            result.append(text[n])
            n = n + 1
    return result, not_match

def cut_sentence_bwd(text, dict_list, max_len):
    result, not_match = [], []

    text = split_text(text)
    text_len = len(text)
    no_word = ""
    n = text_len

    while n > 0:
        matched = 0
        for i in range(min(max_len, text_len), 0, -1):
            if n - i < 0: continue

            word = "-".join(text[n-i:n])
            if word in dict_list[i-1]:
                matched = 1
                result.append(word)
                n = n - i
                break
        if not matched:
            not_match.append(text[n-1])
            result.append(text[n-1])
            n = n - 1
    result.reverse()
    return result, not_match


def load_dict(lexicon_path):
    # Load word
    word_set = set()
    with open(lexicon_path) as file:
        for line in file:
            try:
                word, ipa = line.strip().split(" ", 1)
                word_set.add(word)
            except:
                word_set.add(line.strip())
                # print(line)

    # Compute MAX length of word
    max_len = 0
    for word in word_set:
        length = get_word_len(word)
        if length > max_len:
            max_len = length

    # Store word in dict based on length
    mydict = defaultdict(lambda: defaultdict(lambda: 0))

    for word in word_set:
        length = get_word_len(word)
        mydict[length-1][word] = 0

    return word_set, max_len, mydict


if __name__ == "__main__":
    line = "你也知道他事業心很強"
    line = remove_punctuation(line.strip())

    lexicon_path = "/mnt/md1/user_pinyuanc/asr_util/get_ipa_dictionary/output/mandarinE_dictionary.txt"
    word_set, max_len, dict_list = load_dict(lexicon_path)

    result_fwd, not_match_fwd = cut_sentence_fwd(line, dict_list, max_len)
    result_bwd, not_match_bwd = cut_sentence_bwd(line, dict_list, max_len)
    print(result_fwd)
    print(result_bwd)
