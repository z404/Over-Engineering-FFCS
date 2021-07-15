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
            const ele = document.getElementById("displayPriority" + (Number(document.getElementById("timetable-index").innerText) - 1));
            if (newScore == 1) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-danger float-right\">1</span>";
                ele.parentElement.parentElement.dataset.priority = 1;
            } else if (newScore == 2) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-warning float-right\">2</span>";
                ele.parentElement.parentElement.dataset.priority = 2;
            } else if (newScore == 3) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-info float-right\">3</span>";
                ele.parentElement.parentElement.dataset.priority = 3;
            } else if (newScore == 4) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-primary float-right\">4</span>";
                ele.parentElement.parentElement.dataset.priority = 4;
            } else if (newScore == 5) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-success float-right\">5</span>";
                ele.parentElement.parentElement.dataset.priority = 5;
            } else if (newScore == 0) {
                ele.innerHTML = "<span class=\"badge badge-pill badge-danger float-right\">\
                <i class=\"fa fa-trash\" aria-hidden=\"true\"></i></span>";
                ele.parentElement.parentElement.dataset.priority = 0;
            }
            if (document.getElementById("priority-button").disabled) {
                updatePriority();
            }
        })
};

const render_timetable = tmtbl => {
    all_text = localStorage.getItem("timetable");

    const conventional = slot => '<td class="normal">' + slot + '</td>';

    const activated = (slotinfo) => '<td class="normal active">' + slotinfo + '</td>';

    tmtbl.forEach(enrollment => {
        slots_in_enrollment = enrollment.split(' ')[0].split('+');
        enrollment_data = enrollment.split(' ').slice(1).join(" ");
        slots_in_enrollment.forEach(slot => {
            all_text = all_text.replace(conventional(slot), activated(
                slot + '<br>' + enrollment_data));
        });
    });
    return all_text
};

const timetableChange = () => {
    let index;
    const total = Number(document.getElementById("timetable-total").innerText);
    const btnId = event.currentTarget.id;
    if (btnId !== "prev-timetable" && btnId !== "next-timetable") {
        index = Number(document.getElementById(btnId).dataset.index);
    } else {
        index = Number(document.getElementById("timetable-index").innerText) - 1;
        if (btnId === "prev-timetable" && index > 0) {
            --index;
        } else if (btnId == "next-timetable" && index <= total) {
            ++index;
        }
    }

    const updateTimetable = json => {
        let ind = document.getElementById("timetable-index");
        ind.innerText = json["index"] + 1;
        let tmtbl = document.getElementById("render_table_span");
        tmtbl.innerHTML = render_timetable(json["render_timetable"]);
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
        document.getElementsByClassName("current")[0].classList.remove("current");
        document.getElementById("nickname-" + String(json["index"])).classList.add("current");
        var height = $('#boxifycontent').height();
        var otherheight = $('#index-button').height();
        document.getElementById("timetablelist").style.maxHeight = (height - otherheight - 12) + "px";
    }
    try {
        const json = JSON.parse(localStorage.getItem("allstoredtimetables"))[index];
        updateTimetable(json);
    }
    catch {
        fetch("/rendertimetable/", {
                method: "POST",
                body: JSON.stringify({ "index": index }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8",
                    "X-CSRFToken": csrftoken,
                }
            }).then(res => res.json())
            .then(json => {
                updateTimetable(json);
                let tempHolder = JSON.parse(localStorage.getItem("allstoredtimetables"));
                if(tempHolder == null)
                {
                    tempHolder = {};
                }
                tempHolder[index] = json;
                localStorage.setItem("allstoredtimetables",JSON.stringify(tempHolder));
            });
    }
}

$(document).ready(() => {
    var height = $('#boxifycontent').height();
    var otherheight = $('#index-button').height();
    document.getElementById("timetablelist").style.maxHeight = (height - otherheight - 12) + "px";
    height = $('#nicknamneontop').height();
    document.getElementById("height_helper").style.paddingTop = height + "px";
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
            ele.innerText = '#' + document.getElementById("timetable-index").innerText + ': ' + newnick;
            let ele2 = document.getElementById("nicknamneontop");
            ele2.innerText = newnick;
            let tempHolder = JSON.parse(localStorage.getItem("allstoredtimetables"));
            tempHolder[index]["nickname_render"] = newnick;
            localStorage.setItem("allstoredtimetables",JSON.stringify(tempHolder));
        });
}
const indexSort = (e1, e2) => {
    if (Number(e1.dataset.index) < Number(e2.dataset.index)) return -1;
    if (Number(e1.dataset.index) > Number(e2.dataset.index)) return 1;
    return 0;
}
const prioritySort = (e1, e2) => {
    if (Number(e1.dataset.priority) > Number(e2.dataset.priority)) return -1;
    if (Number(e1.dataset.priority) < Number(e2.dataset.priority)) return 1;
    return 0;
}
const updateIndex = () => {
    let t = document.getElementById("timetablelist").childNodes[0].childNodes;
    let n = Array.from(t);
    n.sort(indexSort);
    const parent = t[0].parentElement;
    parent.innerHTML = '';
    n.forEach(ele => parent.appendChild(ele));
    document.getElementById("priority-button").disabled = false;
    document.getElementById("index-button").disabled = true;
};
const updatePriority = () => {
    let t = document.getElementById("timetablelist").childNodes[0].childNodes;
    let n = Array.from(t);
    n.sort(prioritySort);
    const parent = t[0].parentElement;
    parent.innerHTML = '';
    n.forEach(ele => parent.appendChild(ele));
    document.getElementById("index-button").disabled = false;
    document.getElementById("priority-button").disabled = true;
};