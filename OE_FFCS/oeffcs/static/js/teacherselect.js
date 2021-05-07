function toggleview(id) {
    if (document.getElementById(id).style.display === "none") {
        document.getElementById(id).style.display = "block";
    } else if (document.getElementById(id).style.display === "block") {
        document.getElementById(id).style.display = "none";
    }
    console.log(id + ' ' + document.getElementById(id).style.display);
}