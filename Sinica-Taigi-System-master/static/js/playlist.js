function genEpisodeSelect(pagenum) {
    var select = "";
    for (var index = 1; index <= pagenum; index++) {
        select += "<option value="+index+">"+index+"</option>";
    }
    return select;
}

function genEpisodeTable(drama_name, statistics, curr_page) {
    // curr_page: starts from 1
    var table = "";
    var tmp_episode_id = "";

    var keys = Object.keys(statistics);

    for (var i = 0; i < keys.length; i++) {
        var index = (curr_page-1)*20 + i + 1;
        var episode_id = keys[i];

        table += "<tr>";
        table += "<td align='center'>"+index+"</td>";
        table += "<td align='center' value='"+episode_id+"'>"+episode_id+"</td>";
        table += "<td align='center'>"+statistics[episode_id]["total_sent"]+"</td>";
        table += "<td align='center'>"+statistics[episode_id]["checked_sent"]+"</td>";
        table += "<td align='center'><form action='sort_filter' style='float:left'>"
        table += "<input name='drama_name' class='form-control' value="+drama_name+" style='display: none;'>"
        table += "<input name='episode_id' class='form-control' value="+episode_id+" style='display: none;'>"
        table += "<button type='submit' class='btn btn-info'>編輯</button>"
        table += "</form><form action='download/epitext/"+episode_id+"' style='float:right'>"
        table += "<button type='submit' class='btn btn-secondary'>下載</button>"
        table += "</form></td>"
        table += "</tr>";
    }
    return table;
}

function changeEpiList(event) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(xmlhttp.responseText);
            var pagenum = response.pagenum;
            var statistics = response.statistics;

            var select = genEpisodeSelect(pagenum);
            var table = genEpisodeTable(drama_name, statistics, curr_page);

            document.getElementById("pagelist").innerHTML = select;
            document.getElementById("episode_table_body").innerHTML = table;

            document.getElementById("pagelist").value = curr_page;
        }
    };
    xmlhttp.open("POST", "/get_episode_list");
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    var drama_id, drama_name;
    if ($(event.target).hasClass("drama-title")) {
        drama_id = event.target.attributes.value.value;
        
        var cln = event.target.cloneNode(true)
        cln.removeChild(cln.childNodes[1]);     
        drama_name = cln.innerText;
        // drama_name = event.target.innerText;
        
        document.getElementById("cur_drama_id").value = drama_id;
        document.getElementById("cur_drama_name").value = drama_name;
    } else if (event.target.id === "pagelist") {
        drama_id = document.getElementById("cur_drama_id").value;
        drama_name = document.getElementById("cur_drama_name").value;
    } else {return;}
    var curr_page = document.getElementById("pagelist").value;
    if (curr_page === "") curr_page = 1;
    var episode_start = (curr_page-1)*20;
    var postVars = "drama_id="+drama_id+"&episode_start="+episode_start;
    xmlhttp.send(postVars);
}
