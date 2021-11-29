import sys
import jieba
from pathlib import Path

def load_dict(lexicon_path):
    lexicon_path = Path(lexicon_path)
    assert lexicon_path.exists()

    dict_path = Path("/home/pinyuanc/miniconda3/lib/python3.8/site-packages/jieba/dict.txt")
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
    content = " ".join(jieba.cut(text, cut_all=False, HMM=False))
    content = content.replace("< UNK >", "<UNK>")

    return " ".join([w if w in word_set else "<UNK>" for w in content.split()])
