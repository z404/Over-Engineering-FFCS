const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const priorityChangeClick = () => {
    console.log(event.currentTarget.id);
    fetch("/rendertimetable/", {
        method: "POST",
        body: JSON.stringify({ "index": 1 }),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "X-CSRFToken": csrftoken,
        }
    }).then(res => res.json())
        .then(json => console.log(json));
};


const timetableChange = () => {
    const btnId = event.currentTarget.id;
    if (btnId !== "prev-timetable" && btnId !== "next-timetable") {
        console.log("Not there yet.");
        return;
    }
    let index = Number(document.getElementById("timetable-index").innerText) - 1;
    const total = Number(document.getElementById("timetable-total").innerText);
    if (btnId === "prev-timetable" && index > 0){
        --index;
    }
    else if(btnId== "next-timetable" && index <= total){
        ++index;
    }
    console.log(index)
    fetch("/rendertimetable/", {
        method: "POST",
        body: JSON.stringify({ "index": index }),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "X-CSRFToken": csrftoken,
        }
    }).then(res => res.json())
        .then(json => {
            let ind = document.getElementById("timetable-index");
            ind.innerText=json["index"]+1;
            let tmtbl = document.getElementById("render_table_span");
            tmtbl.innerHTML=json["render_timetable"];
            let inftbl = document.getElementById("info_table_span");
            inftbl.innerHTML=json["information_table"];
            if(ind.innerText == 1)
            {
                document.getElementById("prev-timetable").disabled = true;
            }
            else{
                document.getElementById("prev-timetable").disabled = false;
            }
            if(ind.innerText == total)
            {
                document.getElementById("next-timetable").disabled = true;
            }
            else{
                document.getElementById("next-timetable").disabled = false;
            }
        });
}
$(document).ready(() => {});