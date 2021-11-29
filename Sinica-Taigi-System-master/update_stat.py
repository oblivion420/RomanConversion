import joblib

from lib import db


def format_data(mydict):
    # Limit floats to two decimal points and do type conversion to string
    new_data = {}
    for k in ["time", "checked_time", "usable_time"]:
        new_data[k] = str("%.2f"%mydict[k])
    for k in ["sent", "checked_sent", "usable_sent"]:
        new_data[k] = str(mydict[k])
    return new_data


def main():
    # Load playlist file
    playlist = joblib.load("config/playlist.joblib")

    total = {"id": "total", "name": "Total", "time": 0, "checked_time": 0, "usable_time": 0,
            "sent": 0, "checked_sent": 0, "usable_sent": 0}
    stat_info = []
    for playlist_id in playlist.keys():
        mydict = db.get_drama_statistics(playlist_id)
        stat_info += [{"id": playlist_id, "name": playlist[playlist_id]["name"],
                        **format_data(mydict)}]

        for k in ["time", "checked_time", "usable_time", "sent", "checked_sent", "usable_sent"]:
            total[k] += mydict[k]

    total.update(format_data(total))

    stat_info = [total] + stat_info
    joblib.dump(stat_info, "static/stat/play_stat.joblib")

if __name__ == "__main__":
    main()
