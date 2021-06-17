const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const priorityChangeClick = () => {
    console.log(event.currentTarget.id);
    fetch("/rendertimetable/", {
            method: "POST",
            data: { "index": 1 },
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": csrftoken,
            }
        }).then(res => res.json())
        .then(json => console.log(json));
};

// const priorityChangeRequest = async() => {
//     await

// };

const renderListTable = (list) => {
    //   let tbl = document.createElement("table");
    //   tbl.id="timetablelist";
    //   tbl.classList=["table", "table-dark"];
    let tbd = document.createElement("tbody");
    tbd.style.width = "100%";
    tbd.style.display = "table";
    list.forEach(element => {
        let text = document.createTextNode("")
        let td = document.createElement("td");
        let tr = document.createElement("tr");
        tr.appendChild(td);
        tbd.appendChild(tr);
    });
    let tbl = document.getElementById("timetablelist");
    tbl.appendChild(tbd);

};