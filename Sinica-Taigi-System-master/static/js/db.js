function get_node_data(nodes) {
    var uid = nodes[1].id.split("|")[0];
    var chinese = nodes[1].value;
    var hanzi = nodes[5].value;

    // cut
    if (nodes[9].checked === true) var cut = "none";
    else if (nodes[11].checked === true) var cut = "start";
    else if (nodes[13].checked === true) var cut = "end";
    else if (nodes[15].checked === true) var cut = "both";

    var discarded = nodes[19].checked;
    var review = nodes[21].checked;

    return {
        uid: uid,
        chinese: chinese,
        hanzi: hanzi,
        cut: cut,
        discarded: discarded,
        review: review,
    };
}

function update() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            var status = response.status;
            var msg = response.msg;

            checked_elm.className = "badge badge-success"
            checked_elm.innerText = "已檢查"

            alert("Action: 更新\nStatus: "+status+"\n"+msg);
    }};
    xmlhttp.open("POST", "/update_db");
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    var form = event.target.parentElement;
    var nodes = form.childNodes;
    var checked_elm = event.target.parentElement.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.childNodes[7];

    data = get_node_data(nodes)
    var postVars = "type=update"+"&uid="+data["uid"]+"&chinese="+data["chinese"]+"&hanzi="+data["hanzi"]+"&cut="+data["cut"]+"&discarded="+data["discarded"]+"&review="+data["review"];
    xmlhttp.send(postVars);
}

function undo() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            var status = response.status;
            var msg = response.msg;

            checked_elm.className = "badge badge-danger"
            checked_elm.innerText = "未檢查"

            var chinese = nodes[1];
            chinese.value = response.chinese;
            var hanzi = nodes[5];
            hanzi.value = response.hanzi;
            var cut_none = nodes[9];
            cut_none.checked = true;
            var discarded = nodes[19];
            discarded.checked = false;
            var review = nodes[21];
            review.checked = false;

            alert("Action: 復原\nStatus: "+status+"\n"+msg);
    }};
    xmlhttp.open("POST", "/update_db");
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    var form = event.target.parentElement;
    var nodes = form.childNodes;
    var checked_elm = event.target.parentElement.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.childNodes[7];

    var uid = nodes[1].id.split("|")[0];

    var postVars = "type=undo"+"&uid="+uid;

    xmlhttp.send(postVars);
}

function bulk_update() {
    var badge_elms = document.getElementsByClassName("badge-warning");
    var num = badge_elms.length
    var xmlhttp2checked_elm = [];
    var result = {"Success": 0, "Fail": 0, "failed_uid": []};

    for (index = 0; index < num; index++) {
        xmlhttp2checked_elm.push([new XMLHttpRequest(), ""]);
    }

    for (index = 0; index < num; index++) {
        badge_elm = badge_elms[index];
        var form = badge_elm.parentElement.nextElementSibling.nextElementSibling.nextElementSibling.nextElementSibling.nextElementSibling.childNodes[1];
        var nodes = form.childNodes;
        var checked_elm = form.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.childNodes[7];

        var xmlhttp = xmlhttp2checked_elm[index][0];
        xmlhttp2checked_elm[index][1] = checked_elm;
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                var status = response.status;
                var msg = response.msg;
                var index = response.index;

                xmlhttp2checked_elm[index][1].className = "badge badge-success"
                xmlhttp2checked_elm[index][1].innerText = "已檢查"

                // 統計成功失敗的次數
                result[status] += 1;

                // 紀錄失敗的uid
                if (status == "Fail") {
                    var uid = xmlhttp2checked_elm[index][1].parentElement.nextElementSibling.childNodes[2].innerText;
                    result["failed_uid"].push(uid)
                }

                // 在最後一筆回應印出統計結果
                if (result["Success"]+result["Fail"] == num) {
                    alert("Action: 更新\n"+
                            "Status: 成功（"+result["Success"]+"）, "+
                            "失敗（"+result["Fail"]+"）\n"+
                            "失敗uttid: "+result["failed_uid"].join(", ")+"\n");
                }
        }};
        xmlhttp.open("POST", "/update_db");
        xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

        data = get_node_data(nodes)
        var postVars = "type=update"+"&index="+index+"&uid="+data["uid"]+
                        "&chinese="+data["chinese"]+"&hanzi="+data["hanzi"]+"&cut="+data["cut"]+
                        "&discarded="+data["discarded"]+"&review="+data["review"];
        xmlhttp.send(postVars);
    }
}
