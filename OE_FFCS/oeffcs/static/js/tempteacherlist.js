// $(".thunder").on("sortupdate", function(event, ui) {
//     console.log(event.target.tagName);
//     var arr = event.target.textContent.split("                                                            ");
//     var arr2d = [
//         []
//     ];
//     for (lol in arr) {
//         arr2d.push(arr[lol].split("                                "));
//     }
//     console.log(arr2d);
// })
const Save = () => {
    let updatedData = [];
    const allTables = document.querySelector('.thunder').children;
    let index = 0;
    for (table of allTables) {
        let rows = table.children[1].children
        updatedData[index] = Array(rows[0].children[1].innerText, Array.from(rows).map(ele => ele.children[2].innerText))
        index++;
    }
    const redirect = () => { window.location.href = window.location.origin + "/winffcs/"; }
    console.table(updatedData);
    fetch("/savepreference/", {
        method: "POST",
        body: JSON.stringify({
            "data": updatedData,
            "ttid": document.getElementById("ttid").dataset['ttid'],
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "X-CSRFToken": csrftoken,
        },
    }).then(redirect)
};