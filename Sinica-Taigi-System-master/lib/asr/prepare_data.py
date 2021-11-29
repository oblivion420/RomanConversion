import os


def gen_epitext(episode_id, utt_list):
    if not os.path.exists("download"):
        os.makedirs("download")

    with open("download/{}.text".format(episode_id), "w") as file:
        utt_list = sorted(utt_list, key=lambda x: x[0])
        for uid, trans in utt_list:
            file.write("{} {}\n".format(uid, trans["hanzi"]))
