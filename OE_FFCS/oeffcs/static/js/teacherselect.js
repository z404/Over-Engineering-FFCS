function toggleview(id, tickbox_id) {
    if (document.getElementById(tickbox_id).checked === true) {
        document.getElementById(id).style.display = "block";
    } else if (document.getElementById(tickbox_id).checked === false) {
        document.getElementById(id).style.display = "none";
    }
    console.log(id + ' ' + document.getElementById(id).style.display);
    console.log(document.getElementById(tickbox_id).checked);
}

window.addEventListener("load", () => {
    var x = document.getElementsByClassName('custom-control-input');
    for (var i of x) {
        if (i.checked === true) {
            document.getElementById('teacherlist' + i.classList[1].match(/\d/g)[0]).style.display = "block";
        } else if (i.checked === false) {
            document.getElementById('teacherlist' + i.classList[1].match(/\d/g)[0]).style.display = "none";
        }
    }
});