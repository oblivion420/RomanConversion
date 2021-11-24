import sys
import argparse
from collections import defaultdict

en_vowel = ["ɑ", "æ", "ə", "ɔ", "aʊ", "aɪ", "ɛ", "ɝ", "eɪ", "ɪ", "i", "oʊ", "ɔɪ", "ʊ", "u"]

def default(input_path, output_path):
    all_ipa_dict = defaultdict(lambda: [])

    with open(input_path, "r") as file:
        for line in file:
            ipa_list = line.strip().split()
            for ipa in ipa_list:
                try:
                    tone = ipa.split("_")[1]
                except:
                    if ipa in en_vowel:
                        tone = "-1"
                    else: tone = ""
                all_ipa_dict[tone] += [ipa]

    with open(output_path, "w") as file:
        file.write("sil spn\n")
        for tone in sorted(all_ipa_dict):
            ipa_list = sorted(all_ipa_dict[tone])
            file.write(" ".join(ipa_list)+"\n")


def same_vowel_same_tone(input_path, output_path):
    all_ipa_dict = defaultdict(lambda: defaultdict(lambda: []))

    with open(input_path, "r") as file:
        for line in file:
            ipa_list = line.strip().split()
            for ipa in ipa_list:
                try:
                    vowel, tone = ipa.split("_")
                except:
                    continue
                all_ipa_dict["vowel"][vowel] += [ipa]
                all_ipa_dict["tone"][tone] += [ipa]

    with open(output_path, "w") as file:
        for vowel in sorted(all_ipa_dict["vowel"]):
            ipa_list = sorted(all_ipa_dict["vowel"][vowel])
            file.write(" ".join(ipa_list)+"\n")
        for tone in sorted(all_ipa_dict["tone"]):
            ipa_list = sorted(all_ipa_dict["tone"][tone])
            file.write(" ".join(ipa_list)+"\n")


def main(args):
    kind = args.kind
    nonsilence_phones_path = args.input_path
    output_path = args.output_path

    if kind == "default":
        default(nonsilence_phones_path, output_path)
    elif kind == "same_vowel_same_tone":
        same_vowel_same_tone(nonsilence_phones_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", type=str, default="default", help="default / same_vowel_same_tone")
    parser.add_argument("input_path", type=str, help="input path (non-silience phones)")
    parser.add_argument("output_path", type=str, help="output path")
    args = parser.parse_args()

    main(args)
