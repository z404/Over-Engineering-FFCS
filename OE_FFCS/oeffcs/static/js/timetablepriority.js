const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const scoreChange = () => {
    const newScore = Number(event.currentTarget.id.slice(-1))
    fetch("/scorechange/", {
            method: "POST",
            body: JSON.stringify({
                "index": Number(document.getElementById("timetable-index").innerText) - 1,
                "score": newScore
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": csrftoken,
            }
        }).then(res => res.json())
        .then(json => {
            let ele = document.getElementById("displayPriority" + (Number(document.getElementById("timetable-index").innerText) - 1));
            if (newScore === 1) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-danger float-right\">1</span>"
            } else if (newScore === 2) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-warning float-right\">2</span>"
            } else if (newScore === 3) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-info float-right\">3</span>"
            } else if (newScore === 4) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-primary float-right\">4</span>"
            } else if (newScore === 5) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-success float-right\">5</span>"
            } else if (newScore === 0) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-danger float-right\">\
                <i class=\"fa fa-trash\" aria-hidden=\"true\"></i></span>"
            }
        });
};


const timetableChange = () => {
    let index;
    const total = Number(document.getElementById("timetable-total").innerText);
    const btnId = event.currentTarget.id;
    if (btnId !== "prev-timetable" && btnId !== "next-timetable") {
        index = Number(btnId);
    } else {
        index = Number(document.getElementById("timetable-index").innerText) - 1;
        if (btnId === "prev-timetable" && index > 0) {
            --index;
        } else if (btnId == "next-timetable" && index <= total) {
            ++index;
        }
    }

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
            ind.innerText = json["index"] + 1;
            let tmtbl = document.getElementById("render_table_span");
            tmtbl.innerHTML = json["render_timetable"];
            let inftbl = document.getElementById("info_table_span");
            inftbl.innerHTML = json["information_table"];
            let nickname = document.getElementById("nickname-" + (json["index"]));
            document.getElementById("nickname-box").value = (nickname.childNodes[0].nodeValue);
            let nicktextbox = document.getElementById("nickname-box");
            nicktextbox.value = json["nickname_render"]
            if (ind.innerText == 1) {
                document.getElementById("prev-timetable").disabled = true;
            } else {
                document.getElementById("prev-timetable").disabled = false;
            }
            if (ind.innerText == total) {
                document.getElementById("next-timetable").disabled = true;
            } else {
                document.getElementById("next-timetable").disabled = false;
            }
            var height = $('#boxifycontent').height();
            document.getElementById("timetablelist").style.maxHeight = height + "px";
        });
}

$(document).ready(() => {
    var height = $('#boxifycontent').height();
    document.getElementById("timetablelist").style.maxHeight = height + "px";
});

const nicknameChange = () => {
    const newnick = document.getElementById("nickname-box").value;
    fetch("/nicknamechange/", {
            method: "POST",
            body: JSON.stringify({
                "nick": newnick,
                "index": Number(document.getElementById("timetable-index").innerText) - 1,
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": csrftoken,
            },
        }).then(res => res.json())
        .then(json => {
            let ele = document.getElementById("displayNickname" + (Number(document.getElementById("timetable-index").innerText) - 1));
            ele.innerText = newnick;
        });
}