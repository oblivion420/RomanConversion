import sys
import glob
from collections import defaultdict

def main():
    lexicon_dir_path = sys.argv[1]
    output_path = sys.argv[2]

    all_ipa_phone = set()

    for lexicon_path in glob.glob(f"{lexicon_dir_path}/lexicon*txt"):
        with open(lexicon_path, "r") as file:
            for line in file:
                try:
                    word, ipa = line.strip().split(" ", 1)
                except:
                    print(line)
                ipa_list = ipa.split()
                all_ipa_phone = all_ipa_phone.union(set(ipa_list))

    all_ipa_phone = all_ipa_phone - {"spn", "sil"}
    all_ipa_dict = defaultdict(lambda: [])

    for phone in all_ipa_phone:
        try:
            stem, tone = phone.split("_")
        except:
            stem = phone
        all_ipa_dict[stem] += [phone]

    with open(output_path, "w") as file:
        for key in sorted(all_ipa_dict):
            ipa_list = sorted(all_ipa_dict[key])
            file.write(" ".join(ipa_list))
            file.write("\n")

    # print(all_ipa_dict)

if __name__ == "__main__":
    main()
