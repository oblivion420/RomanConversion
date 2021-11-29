function toTop() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

function toUnchecked() {
    var list = document.getElementsByClassName("badge-danger");

    if ( typeof toUnchecked.counter == "undefined" ) {
        toUnchecked.counter = 0;
    } else {
        if (toUnchecked.counter >= list.length) {
            toUnchecked.counter = 0;
        } else {
            toUnchecked.counter += 1;
        }
    }

    list[toUnchecked.counter].scrollIntoView();
    window.scrollBy(0, -130);
}
