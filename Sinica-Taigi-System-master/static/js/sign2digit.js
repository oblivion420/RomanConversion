function sign2digit(event) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(xmlhttp.responseText);
            var digit = response.digit;

            document.getElementById("digit_blk").value = digit;
        }
    };
    xmlhttp.open("POST", "/func_sign2digit");
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    var sign = document.getElementById("sign_blk").value
    var postVars = "sign="+sign;
    xmlhttp.send(postVars);
}
