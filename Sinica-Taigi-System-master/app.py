import os
import json
import math
import joblib
from datetime import timedelta
from importlib import import_module
from flask import Flask, render_template, request, url_for, send_file, jsonify, redirect, Response
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user

from lib import db
from lib import syl_trans
from lib.asr import prepare_data
from lib import word_segmentation_jieba


cfg = import_module("config.prd")
interface = cfg.interface
users = cfg.users
mapping2db = cfg.mapping2db

# Load playlist information
playlist = joblib.load("config/playlist.joblib")

app = Flask(__name__)
app.config["DEBUG"] = "True"
app.config["SECRET_KEY"] = "Your Key"
app.jinja_options["extensions"].append("jinja2.ext.loopcontrols")

# ====================================================
# Start of Function
# ====================================================
def dict2list(mydict, sort_=None, filter_=None):
    def filter_func(item):
        match = 1
        for attribute, value in filter_.items():
            match *= item[1][attribute] == value
        return match

    mylist = list(mydict.items())
    if filter_:
        mylist = filter(filter_func, mylist)
    if sort_:
        mylist = sorted(mylist, key=lambda x: float(x[1][sort_["sortby"]])*sort_["orderby"])
    return mylist


def preprocess_dict(mydict_):
    def second2hms(seconds):
        m, s = divmod(float(seconds), 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    for k in sorted(list(mydict_.keys())):
        if mydict_[k]["score"] == "nan":
            mydict_[k]["score"] = 0
        else:
            mydict_[k]["score"] = "%.5f" % mydict_[k]["score"]
        mydict_[k]["start_format"] = second2hms(mydict_[k]["start"])
        mydict_[k]["end_format"] = second2hms(mydict_[k]["end"])
    return mydict_
# ====================================================
# End of Function
# ====================================================

# ====================================================
# Start of login_manager
# ====================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "basic"
login_manager.login_view = "login"
login_manager.login_message = "請先登入"

class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in users: return
    else:
        user = User()
        user.id = username
        return user
# ====================================================
# End of login_manager
# ====================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        cfg_bulletin = import_module("config.bulletin")
        bulletin = cfg_bulletin.bulletin
        return render_template("login.html", bulletin=bulletin)

    username = request.form["username"]
    if request.form["password"] == users[username]["password"]:
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for("list_drama"))

    return "Bad login"


@app.route("/")
@app.route("/list_drama")
@login_required
def list_drama():
    playlist = joblib.load("static/stat/play_stat.joblib")
    return render_template("list_drama.html", playlist=playlist)


@app.route("/edit_trans")
@login_required
def edit_trans():
    drama_name = request.args.get("drama_name")
    episode_id = request.args.get("episode_id")
    mydict = db.get_episode(episode_id)
    mydict = preprocess_dict(mydict)
    mylist = dict2list(mydict)
    return render_template("edit_trans.html", drama_name=drama_name, episode_id=episode_id, interface=interface, data=mylist)


@app.route("/sort_filter")
@login_required
def sort_filter():
    drama_name = request.args.get("drama_name")
    episode_id = request.args.get("episode_id")

    sortby = request.args.get("sortby")
    orderby = request.args.get("orderby")
    checked = request.args.get("checked")
    discarded = request.args.get("discarded")
    review = request.args.get("review")

    mydict = db.get_episode(episode_id)

    # Prepare parameter
    sort, filter = {"sortby": "score", "orderby": -1}, None

    # Sort
    if sortby and orderby:
        sortby = mapping2db[sortby] if sortby else None
        orderby = -1 if orderby == interface["sort"]["orderby"]["DESC"] else 1
        sort = {"sortby": sortby, "orderby": orderby}

    # Filter
    if checked == interface["filter"]["already"]["done"]+interface["filter"]["attribute"]["checked"]:
        checked = 1
    elif checked == interface["filter"]["already"]["undone"]+interface["filter"]["attribute"]["checked"]:
        checked = 0
    discarded = 1 if discarded == "on" else 0
    review = 1 if review == "on" else 0
    filter = {"checked": checked, "discarded": discarded, "review": review}
    if checked in ["全部", None]: filter.pop("checked")

    mydict = preprocess_dict(mydict)
    mylist = dict2list(mydict, sort_=sort, filter_=filter)

    return render_template("edit_trans.html", drama_name=drama_name, episode_id=episode_id, interface=interface, data=mylist)


@app.route("/changelog")
def changelog():
    cfg_log = import_module("config.changeLog")
    log = cfg_log.log
    return render_template("changelog.html", log=log)


@app.route("/download/<filetype>/<id>", methods=["GET"])
def download(filetype, id):
    try:
        if filetype == "epitext":
            filename = f"{id}.text"
            mydict = db.get_episode(id, retrieve_list=["uid", "hanzi"])
            mylist = dict2list(mydict)
            prepare_data.gen_epitext(id, mylist)
        return send_file(f"download/{filename}", as_attachment=True)
    except Exception as e:
        return str(e)


# Service: Hanzi2tailo
@app.route("/hanzi2tailo")
def hanzi2tailo():
    return render_template("hanzi2tailo.html")

# Service: Sign2digit
@app.route("/sign2digit")
def sign2digit():
    return render_template("sign2digit.html")

# ==========================================================================
# AJAX
# ==========================================================================
@app.route("/get_episode_list", methods = ["POST"])
@login_required
def get_episode_list():
    drama_id = request.form["drama_id"]
    episode_start = int(request.form["episode_start"])

    # get_drama_episode_list
    drama_name = playlist[drama_id]["name"]
    total_episode_ids = db.get_drama_episode_list(drama_id)
    current_episode_ids = total_episode_ids[episode_start:episode_start+20]
    pagenum = math.ceil(len(total_episode_ids)/20)
    statistics = db.get_episode_statistics(current_episode_ids)

    return jsonify(drama_name=drama_name,
                        pagenum=pagenum,
                        statistics=statistics)


@app.route("/update_db", methods = ["POST"])
@login_required
def update_db():
    type_ = request.form["type"]
    uid = request.form["uid"]
    modified_by = current_user.id
    try:
        index = request.form["index"]
    except:
        index = None

    if type_ == "update":
        chinese = request.form["chinese"]
        hanzi = request.form["hanzi"]
        checked = 1
        discarded = 1 if request.form["discarded"] == "true" else 0
        cut = mapping2db[request.form["cut"]]
        review = request.form["review"]
    elif type_ == "undo":
        utt = db.get_utt(uid)
        chinese, hanzi =  utt[4], utt[5]
        checked, discarded, cut, review = 0, 0, 0, 0

    # return jsonify(status="test", msg="測試")

    # Check
    if len(chinese.split()) != len(hanzi.split()):
        return jsonify(status="Fail",
                        msg="華語與台語字數不一致")
    else:
        result = db.update_utt(uid, chinese, hanzi, checked, discarded, cut, review, modified_by)
        return jsonify(status=result[0], msg=result[1], index=index, chinese=chinese, hanzi=hanzi)

# Service: Hanzi2tailo
@app.route("/func_hanzi2tailo", methods = ["POST"])
def func_hanzi2tailo():
    hanzi_text = request.form["hanzi"]

    hanzi2tailo, taigi_lexicon_path = db.dump_taigi_dict()
    word_set = word_segmentation_jieba.load_dict(taigi_lexicon_path)
    words = word_segmentation_jieba.cut_line(word_set, hanzi_text).split()

    tailo_list = []
    for word in words:
        tailo_list += [hanzi2tailo[word]]

    tailo_seq = " ".join(tailo_list)

    return jsonify(tailo=tailo_seq)


# Service: Sign2digit
@app.route("/func_sign2digit", methods = ["POST"])
def func_sign2digit():
    sign_text = request.form["sign"]
    digit_text = syl_trans.syl_trans(sign_text)
    
    return jsonify(digit=digit_text)


# static url cache buster
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values["q"] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8787")
