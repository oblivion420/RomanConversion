function hanzi2tailo(event) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(xmlhttp.responseText);
            var tailo = response.tailo;

            document.getElementById("tailo_blk").value = tailo;
        }
    };
    xmlhttp.open("POST", "/func_hanzi2tailo");
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    var hanzi = document.getElementById("hanzi_blk").value
    var postVars = "hanzi="+hanzi;
    xmlhttp.send(postVars);
}
