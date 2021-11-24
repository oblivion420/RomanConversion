import string
import re
import codecs
from pathlib import Path
import sys
from collections import defaultdict

text_path = Path(sys.argv[1])
uniq_word_path = Path(sys.argv[2])
ws_text_path = Path(sys.argv[3])
no_match_path = Path(sys.argv[4])
try:
    unk = sys.argv[5] == "True"
except:
    unk = False

# =============================================================================
# Functions
# =============================================================================
def get_word_len(word):
    length = len(re.sub("[^0-9]", "", word)) + len(re.sub("[A-Za-z0-9\-\{\}\(\)]", "", word)) + len(re.sub("[^(]", "", word))
    return length if length != 0 else 1


def split_text(text):
    # <non-tailo><tailo> -> <non-tailo>-<tailo>
    text = re.sub("([^A-Za-z0-9\-])(?=[A-Za-z]+[0-9])", r"\1-", text)
    # <tailo><non-tailo> -> <tailo>-<non-tailo>
    text = re.sub("([A-Za-z][0-9])(?=[^A-Za-z0-9\-])", r"\1-", text)
    # <ch><en> -> -<ch>-<en>-
    for i in "{(": text = re.sub("\{}".format(i), "-{}".format(i), text)
    for i in "})": text = re.sub("\{}".format(i), "{}-".format(i), text)
    text = re.sub("\-\-", "-", text)

    new_text = []
    for words in re.split("-", text):
        if re.fullmatch("[A-Za-z]+[0-9]|\([A-Za-z]+\)|\{[^A-Za-z0-9]\}", words):
            new_text += [words]
        else:
            for w in words: new_text += [w]
    return new_text


def remove_punctuation(line):
    # Not remove english ', but remove all chinese related punctuation
    punctuation = "[:?<>/\"...：；;.$,“”+——！！，。？、~@#￥%……&*（）\[\]「」《》【】｢｣『』]+"
    line = re.sub(punctuation, "", line.strip())

    for m in re.findall(".*\'", line):
        if re.findall("[A-Za-z]+\'", m):
            continue
        else:
            line = line.replace(m, re.sub("\'", "", m))
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

            # tailo in hanzi: use "-" to join closed tailo
            tmp = []
            if re.search("[a-z0-9]", "".join(text[n:n+i])):
                for index in range(n+1, n+i):
                    if re.fullmatch("[A-Za-z]+[0-9]", text[index]) and re.fullmatch("\-?[A-Za-z]+[0-9]", text[index-1]):
                        tmp += ["-"+text[index]]
                    else: tmp += [text[index]]

            if tmp: word = text[n]+"".join(tmp)
            else: word = "".join(text[n:n+i])

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

            # tailo in hanzi: use "-" to join closed tailo
            tmp = []
            if re.search("[a-z0-9]", "".join(text[n-i:n])):
                for index in range(n-i+1, n):
                    if re.fullmatch("[A-Za-z]+[0-9]", text[index]) and re.fullmatch("\-?[A-Za-z]+[0-9]", text[index-1]):
                        tmp += [ "-"+text[index]]
                    else:tmp += [text[index]]

            if tmp: word = text[n-i]+"".join(tmp)
            else: word = "".join(text[n-i:n])

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

# =============================================================================
# Load uniq word
# =============================================================================
uniq_word_list = []
for line in uniq_word_path.open("r"):
    uniq_word_list.append(line.strip())

# =============================================================================
# Compute MAX length of word
# =============================================================================
max_len = 0
for word in uniq_word_list:
    length = get_word_len(word)
    if length > max_len:
        max_len = length

# =============================================================================
# Store word in dict based on length
# =============================================================================
dict_list = defaultdict(lambda: defaultdict(lambda: 0))

for word in uniq_word_list:
    length = get_word_len(word)
    dict_list[length-1][word] = 0

# =============================================================================
# Do word segmentation for given text file
# =============================================================================
results = []
not_match_word = defaultdict(lambda: 0)

for line in text_path.open("r"):
    if not line: continue

    line = remove_punctuation(line.strip())

    result_fwd, not_match_fwd = cut_sentence_fwd(line, dict_list, max_len)
    result_bwd, not_match_bwd = cut_sentence_bwd(line, dict_list, max_len)

    if len(result_fwd) <= len(result_bwd):
        for index, word in enumerate(result_fwd):
            length = get_word_len(word)

            if word in dict_list[length-1]:
                dict_list[length-1][word] += 1
            elif word in not_match_fwd:
                not_match_word[word] += 1
                if unk: result_fwd[index] = "<UNK>"

        results.append(result_fwd)
    else:
        for index, word in enumerate(result_bwd):
            length = get_word_len(word)

            if word in dict_list[length-1]:
                dict_list[length-1][word] += 1
            elif word in not_match_bwd:
                not_match_word[word] += 1
                if unk: result_bwd[index] = "<UNK>"

        results.append(result_bwd)

with ws_text_path.open("w") as file:
    for result in results:
        file.write(' '.join(result)+'\n')

with no_match_path.open("a") as file:
    for word in not_match_word.keys():
        file.write(word+'\n')
