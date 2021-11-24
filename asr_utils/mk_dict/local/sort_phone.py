import sys

src = sys.argv[1]
trg = sys.argv[2]

phones = list()

with open(src, "r") as file:
    for line in file:
        phones += [line.strip()]

with open(trg, "w") as file:
    for phone in sorted(phones, key=lambda x: (x.split("_")[0], int(x.split("_")[1]) if len(x.split("_")) == 2 else 0)):
        file.write("{}\n".format(phone))
