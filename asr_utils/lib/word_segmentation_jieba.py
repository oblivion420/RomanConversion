import sys
import jieba
from pathlib import Path

def load_dict(lexicon_path):
    lexicon_path = Path(lexicon_path)
    assert lexicon_path.exists()

    dict_path = Path("/home/pinyuanc/miniconda3/lib/python3.7/site-packages/jieba/dict.txt")
    if dict_path.exists():
        dict_path.unlink()

    cache = Path("/tmp/jieba.cache")
    if cache.exists():
        cache.unlink()

    word_set = set()
    with dict_path.open("w") as f:
        for line in lexicon_path.open():
            line = line.strip().split()
            if line[0] not in word_set:
                if line[0][0] != "<":
                    f.write("{} {}\n".format(line[0], len(line[0])))
                else:
                    f.write("{} {}\n".format(line[0], 1000))
                word_set.add(line[0])

    return word_set

def cut_line(word_set, text):
    # print("jieba", text)
    content = " ".join(jieba.cut(text, cut_all=False, HMM=False))
    content = content.replace("< UNK >", "<UNK>")

    return " ".join([w if w in word_set else "<UNK>" for w in content.split()])

def cut_file(lexicon_path, text_path, output_path):
    lexicon_path = Path(lexicon_path)
    assert lexicon_path.exists() and text_path.exists()

    word_set = load_dict(lexicon_path)

    with output_path.open("w") as f:
        for line in text_path.open():
            if " " in line:
                uid, text = line.strip().split(" ", 1)
            else:
                uid, text = None, line.strip()

            content = " ".join(jieba.cut(text, cut_all=False, HMM=False))
            content = content.replace("< UNK >", "<UNK>")

            new_text = " ".join([w if w in lexicon else "<UNK>" for w in content.split()])

            if uid: f.write(f"{uid} {new_text}\n")
            else: f.write(f"{new_text}\n")


if __name__ == "__main__":
    words = ['往回的', '扭尻川', '母的', '相\ue35c', '袂按算', '袂輸講']
    word_set = load_dict("/mnt/md0/LANG/dict/taigiE_321k_210709/lexicon.txt")
    results = []
    for word in words:
        results += [cut_line(word_set, word)]
    
    for word, result in zip(words, results):
        print(word, result)