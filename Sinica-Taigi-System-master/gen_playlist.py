import joblib

mydict = {
    "PL02zpjjwMEjp0Ck8Mdu9iELED7KGZToIj": {"name": "風水世家"},
    "PL02zpjjwMEjpx2-s14lxtNZY7rotQOj4_": {"name": "外鄉女"},
    "PLc8M1wVJOpHxqleY1bkvwBgAboYO4iMJz": {"name": "車站人生"},
    "PLc8M1wVJOpHwKDgSCcbUS8KFZWD48Wt-R": {"name": "百歲仁醫"},
    "PL02zpjjwMEjpPibC4Yg5vhxRz6RBZit-P": {"name": "浪淘沙"},
    "PL02zpjjwMEjrO0wgZJaSB0l7OYIOUBNao": {"name": "阿不拉的三個女人"},
    "PL02zpjjwMEjqmiQ4baO-ECJwGpqd7C3WM": {"name": "乞丐郎君千金女"},
    "PLc8M1wVJOpHzf_pTd1Qxv6Nby3fBvDo76": {"name": "奔跑吧！阿飛 "},
    "PL02zpjjwMEjqiKILYqcEO7Zi3iYYa_7JI": {"name": "嫁妝"},
    "PL02zpjjwMEjqFm_yxJrorkFxJrpsDALyB": {"name": "春花望露"},
    "PL02zpjjwMEjpgyhaob6MNOfyQ-oi7kLbm": {"name": "幸福來了"}
}
joblib.dump(mydict, "config/playlist.joblib")