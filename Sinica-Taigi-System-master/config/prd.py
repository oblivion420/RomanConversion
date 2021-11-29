db = {
    "server_name": "140.109.23.160",
    "port": 3307,
    "db_name": "Taigi",
    "trans_table": "drama_transcript",
    "playlist_table": "drama",
    "standard_dictionary_table": "standard_dictionary",
    "username": "admin",
    "password": "unknown",
    "field_index": {
        "uid": 1, "playlist_id": 2, "chinese": 3, "hanzi": 4, "original_chinese": 5,
        "original_hanzi": 6, "score": 7, "start": 8, "end": 9, "checked": 10,
        "discarded": 11, "review": 12, "cut": 13, "modified_by": 14
    },
    "mapping2db": {
        "chinese": "華語",
        "hanzi": "台語",
        "original_chinese": "原始華語",
        "original_hanzi": "原始台語",
    }
}

users = {
        "admin": {"password": "1111"},
}

interface = {
    "sort": {
        "sortby": {
            "time": "時間",
            "score": "良好度"
        },
        "orderby": {
            "DESC": "降序",
            "ASC": "升序"
        },
        "button": "排序"
    },
    "filter": {
        "already": {
            "done": "已",
            "undone": "未"
        },
        "attribute": {
            "checked": "檢查",
            "discarded": "捨棄",
            "review": "待確認"
        },
        "button": "過濾"
    },
    "cut": {
        "none": "無",
        "start": "開始",
        "end": "結束",
        "both": "都有",
    }
}

# interface maps to db
mapping2db = {
    interface["sort"]["sortby"]["time"]: "start",
    interface["sort"]["sortby"]["score"]: "score",
    interface["filter"]["attribute"]["checked"]: "checked",
    interface["filter"]["attribute"]["discarded"]: "discarded",
    interface["filter"]["attribute"]["review"]: "review",
    interface["filter"]["already"]["done"]: 1,
    interface["filter"]["already"]["undone"]: 0,

    "none": 0,
    "start": 1,
    "end": 2,
    "both": 3,

}
