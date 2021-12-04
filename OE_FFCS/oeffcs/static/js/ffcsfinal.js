const CSRFTOKEN = document.querySelector("[name=csrfmiddlewaretoken]").value;
const TRUE = "TRUE";
const FALSE = "FALSE";
const GREEN = "GREEN";
const YELLOW = "YELLOW";
const RED = "RED";
const GREY = "GREY";
let blockedSlotsText = "";

const SLOT_CONFLICT_DATA = {
    A1: ["L1", "L14"],
    F1: ["L2", "L15", "L16"],
    D1: ["L3", "L19", "L4"],
    TB1: ["L4", "L5"],
    TG1: ["L5", "L6"],
    A2: ["L31", "L44"],
    F2: ["L32", "L45", "L46"],
    D2: ["L33", "L49", "L34"],
    TB2: ["L34", "L35"],
    TG2: ["L35", "L36"],
    L1: ["A1"],
    L2: ["F1"],
    L3: ["D1"],
    L4: ["TB1"],
    L5: ["TG1"],
    L6: [],
    L31: ["A2"],
    L32: ["F2"],
    L33: ["D2"],
    L34: ["TB2"],
    L35: ["TG2"],
    L36: [],
    B1: ["L7", "L20"],
    G1: ["L8", "L21", "L22"],
    E1: ["L9", "L25", "L10"],
    TC1: ["L10", "L11"],
    TAA1: ["L11", "L12"],
    B2: ["L37", "L50"],
    G2: ["L38", "L51", "L52"],
    E2: ["L39", "L55", "L40"],
    TC2: ["L40", "L41"],
    TAA2: ["L41", "L42"],
    L7: ["B1"],
    L8: ["G1"],
    L9: ["E1"],
    L10: ["TC1"],
    L11: ["TAA1"],
    L12: [],
    L37: ["B2"],
    L38: ["G2"],
    L39: ["E2"],
    L40: ["TC2"],
    L41: ["TAA2"],
    L42: [],
    C1: ["L13", "L26"],
    V1: ["L16", "L17"],
    V2: ["L17", "L18"],
    C2: ["L43", "L56"],
    TD2: ["L46", "L47"],
    TBB2: ["L47", "L48"],
    L13: ["C1"],
    L14: ["A1"],
    L15: ["F1"],
    L16: ["V1"],
    L17: ["V2"],
    L18: [],
    L43: ["C2"],
    L44: ["A2"],
    L45: ["F2"],
    L46: ["TD2"],
    L47: ["TBB2"],
    L48: [],
    TE1: ["L22", "L23"],
    TCC1: ["L23", "L24"],
    TE2: ["L52", "L53"],
    TCC2: ["L53", "L54"],
    L19: ["D1"],
    L20: ["B1"],
    L21: ["G1"],
    L22: ["TE1"],
    L23: ["TCC1"],
    L24: [],
    L49: ["D2"],
    L50: ["B2"],
    L51: ["G2"],
    L52: ["TE2"],
    L53: ["TCC2"],
    L54: [],
    TA1: ["L27", "L28"],
    TF1: ["L28", "L29"],
    TD1: ["L29", "L30"],
    TA2: ["L57", "L58"],
    TF2: ["L58", "L59"],
    TDD2: ["L59", "L60"],
    L25: ["E1"],
    L26: ["C1"],
    L27: ["TA1"],
    L28: ["TF1"],
    L29: ["TD1"],
    L30: [],
    L55: ["E2"],
    L56: ["C2"],
    L57: ["TA2"],
    L58: ["TF2"],
    L59: ["TDD2"],
    L60: [],
};

const LIST_ALL_SLOTS = [
    "L1",
    "TF1",
    "L52",
    "A2",
    "L33",
    "B1",
    "TAA2",
    "L9",
    "L53",
    "L13",
    "E1",
    "G1",
    "L26",
    "L47",
    "V1",
    "L46",
    "L21",
    "TG2",
    "L17",
    "L41",
    "C2",
    "L23",
    "C1",
    "L51",
    "TD1",
    "L31",
    "TCC1",
    "V2",
    "L19",
    "TB2",
    "L39",
    "L25",
    "TCC2",
    "L57",
    "L58",
    "TB1",
    "TAA1",
    "L43",
    "A1",
    "L7",
    "L40",
    "TE2",
    "B2",
    "L34",
    "L22",
    "D1",
    "L49",
    "G2",
    "L59",
    "D2",
    "TBB2",
    "L27",
    "L10",
    "L35",
    "L44",
    "TD2",
    "L37",
    "L14",
    "L4",
    "TE1",
    "TF2",
    "TG1",
    "L38",
    "TDD2",
    "TC2",
    "L15",
    "L16",
    "L3",
    "F1",
    "L8",
    "L50",
    "TA1",
    "L32",
    "F2",
    "L56",
    "TA2",
    "L55",
    "E2",
    "TC1",
    "L29",
    "L5",
    "L20",
    "L2",
    "L28",
    "L45",
    "L11",
];

const createDataElement = (type, data) => {
    const element = document.createElement(type);
    element.innerText = data;
    return element;
};

const fallbackCopyTextToClipboard = (text) => {
    var textArea = document.createElement("textarea");
    textArea.value = text;

    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        document.execCommand("copy");
    } catch (err) {
        console.error("Fallback: Oops, unable to copy", err);
    }

    document.body.removeChild(textArea);
};

const nameCopyButton = () => {
    const element = document.createElement("button");
    let copiedText = "";
    let subjectText = "";
    "button name-copy-btn"
        .split(" ")
        .forEach((cls) => element.classList.add(cls));
    element.innerHTML = "Copy!";
    element.addEventListener("click", () => {
        const e = element.parentElement.parentElement.children[0];
        fallbackCopyTextToClipboard(e.innerText);
        copiedText = e.innerText;
        subjectText =
            e.parentElement.parentElement.parentElement.parentElement
                .parentElement.children[1].children[0].innerText;
        event.stopImmediatePropagation();
        fetch("/lowlevellog_success/", {
            method: "POST",
            body: JSON.stringify({
                message: ` just copied ${copiedText} for ${subjectText}`,
                title: "Win FFCS Log",
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": CSRFTOKEN,
            },
        });
    });

    return element;
};

const courseCodeCopyButton = () => {
    const btn = document.createElement("button");
    "button course-code-copy-btn"
        .split(" ")
        .forEach((cls) => btn.classList.add(cls));
    btn.innerHTML = "For searching Course Code";
    btn.addEventListener("click", () => {
        const arr =
            btn.parentElement.children[0].children[0].innerText.split(" ");
        const coursecode = arr[arr.length - 1];
        fallbackCopyTextToClipboard(coursecode);
        fetch("/lowlevellog_info/", {
            method: "POST",
            body: JSON.stringify({
                message: ` copied ${coursecode}`,
                title: "Win FFCS Log",
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": CSRFTOKEN,
            },
        });
    });
    return btn;
};

const collapseAll = () => {
    Array.from(document.getElementsByClassName(RED)).forEach((redrow) => {
        redrow.style.visibility = "collapse";
    });
};

const rowGeneratesConflict = (row) => {
    try {
        const slots = row.dataset.slots.split("+");
        // console.log(row)
        // console.log(slots)
        const data = JSON.parse(localStorage.getItem("booked"));
        // console.log(data)
        for (const slot of slots) {
            if (data[slot] == TRUE) {
                // console.log("Generates conflict:",data[slot])
                return 1;
            }
        }
    } catch {
        return 2;
    }
    // console.log("Generates conflict:","FALSE")
    return 0;
};

const updateComputedInfo = () => {
    const allCourses = document.getElementById("info").children;
    for (currCourse of allCourses) {
        if (currCourse.dataset["selected"] == TRUE) {
            continue;
        }
        const rows = Array.from(
            currCourse.children[2].children[0].children[1].children
        );
        for (row of rows) {
            if (
                rowGeneratesConflict(row) == 1 &&
                row.dataset["selected"] == FALSE
            ) {
                // console.log("Here!")
                row.style.visibility = "collapse";
            }
            if (rowGeneratesConflict(row) == 0) {
                if (
                    row.parentElement.dataset["expanded"] == TRUE ||
                    row.dataset["state"] == YELLOW
                ) {
                    row.style.visibility = "visible";
                }
            }
        }
    }
};

const render_timetable = (tmtbl) => {
    all_text = localStorage.getItem("timetable");

    const conventional = (slot) => '<td class="normal">' + slot + "</td>";

    const activated = (slotinfo) =>
        '<td class="normal active">' + slotinfo + "</td>";

    tmtbl.forEach((enrollment) => {
        slots_in_enrollment = enrollment.split(" ")[0].split("+");
        enrollment_data = enrollment.split(" ").slice(1).join(" ");
        slots_in_enrollment.forEach((slot) => {
            all_text = all_text.replaceAll(
                conventional(slot),
                activated(slot + "<br>" + enrollment_data)
            );
        });
    });
    return all_text;
};

const getSelectedTimetables = () => {
    // ["L39+L40+L47+L48+L49+L50 CSE1002","L11+L12+A1+TA1 CSE2011","A2+TA2+TAA2+V3 MAT1014"]
    const allCourses = document.getElementById("info").children;
    const finalTmtbl = [];
    for (currCourse of allCourses) {
        if (currCourse.dataset["selected"] != TRUE) {
            continue;
        }
        finalTmtbl.push(
            ((currCourse) => {
                let currStr = "";

                // currStr += currCourse.children[2].children[0].children[1].children[0].children[2].innerText;
                // currStr += " ";
                // currStr += currCourse.children[2].children[0].children[1].children[0].children[3].innerText.split(',')[1];
                currStr += currCourse.dataset["slots"];
                currStr += " ";
                currStr += currCourse.dataset["course_code"];
                return currStr;
            })(currCourse)
        );
    }
    console.log(finalTmtbl);
    return finalTmtbl;
};

const updateTimetable = () => {
    document.getElementById("dynamic-timetable").innerHTML = render_timetable(
        getSelectedTimetables()
    );
};

const update = (e) => {
    const slotText = document.querySelector("#update-text").value;
    const slots = slotText.split("+");
    const temp_booked_slots = JSON.parse(localStorage.getItem("booked"));
    console.log(blockedSlotsText);
    slots.forEach((slot) => {
        temp_booked_slots[slot] = TRUE;
        // console.log(SLOT_CONFLICT_DATA[slot]);
        try {
            Array.from(SLOT_CONFLICT_DATA[slot]).forEach(
                (i) => (temp_booked_slots[i] = TRUE)
            );
        } catch {}
    });
    const blockedSlots = blockedSlotsText.split("+");
    const unblockedSlots = blockedSlots.filter((ele) => !slots.includes(ele));
    console.log(unblockedSlots);
    unblockedSlots.forEach((slot) => {
        temp_booked_slots[slot] = FALSE;
        // console.log(SLOT_CONFLICT_DATA[slot]);
        try {
            Array.from(SLOT_CONFLICT_DATA[slot]).forEach(
                (i) => (temp_booked_slots[i] = FALSE)
            );
        } catch {}
    });
    localStorage.setItem("booked", JSON.stringify(temp_booked_slots));
    updateComputedInfo();
    blockedSlotsText = slotText;
    console.log(blockedSlotsText);

    console.log(temp_booked_slots);
};

const rowUpdate = (e) => {
    const OLD_STATE = e.currentTarget.dataset["state"];
    const SELECTED = e.currentTarget.dataset["selected"];
    const TEACHER_NAME = e.currentTarget.children[0].innerText;
    const ERPID = e.currentTarget.children[1].innerText;
    const SLOT = e.currentTarget.children[2].innerText;
    const SUBJECT = e.currentTarget.children[3].innerText;
    const PARENT = e.currentTarget.parentElement;
    let temp_booked_slots = {};
    let str_all_curr_slots;
    if (SELECTED === FALSE) {
        e.currentTarget.classList.add("green");
        e.currentTarget.dataset["selected"] = TRUE;
        e.currentTarget.parentElement.parentElement.parentElement.parentElement.dataset[
            "selected"
        ] = TRUE;
        for (row of PARENT.children) {
            if (row !== e.currentTarget) {
                row.style.visibility = "collapse";
            } else {
                temp_booked_slots = JSON.parse(localStorage.getItem("booked"));
                str_all_curr_slots = row.children[2].innerText;
                e.currentTarget.parentElement.parentElement.parentElement.parentElement.dataset[
                    "slots"
                ] = str_all_curr_slots;
                console.log(str_all_curr_slots);
                all_curr_slots = str_all_curr_slots.split("+");
                all_curr_slots.forEach((slot) => {
                    temp_booked_slots[slot] = TRUE;
                    // console.log(SLOT_CONFLICT_DATA[slot]);
                    try {
                        Array.from(SLOT_CONFLICT_DATA[slot]).forEach(
                            (i) => (temp_booked_slots[i] = TRUE)
                        );
                    } catch {}
                });
                console.log(temp_booked_slots);
                console.log(SLOT_CONFLICT_DATA);
                localStorage.setItem(
                    "booked",
                    JSON.stringify(temp_booked_slots)
                );
                updateComputedInfo();
            }
        }
        fetch("/lowlevellog_info/", {
            method: "POST",
            body: JSON.stringify({
                message: `Just selected ${TEACHER_NAME} for ${SUBJECT}`,
                title: "Win FFCS Log",
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": CSRFTOKEN,
            },
        });
    } else {
        e.currentTarget.classList.remove("green");
        e.currentTarget.dataset["selected"] = FALSE;
        e.currentTarget.parentElement.parentElement.parentElement.parentElement.dataset[
            "selected"
        ] = FALSE;
        temp_booked_slots = JSON.parse(localStorage.getItem("booked"));
        str_all_curr_slots = e.currentTarget.children[2].innerText;
        all_curr_slots = str_all_curr_slots.split("+");
        all_curr_slots.forEach((slot) => {
            temp_booked_slots[slot] = FALSE;
            try {
                Array.from(SLOT_CONFLICT_DATA[slot]).forEach(
                    (i) => (temp_booked_slots[i] = FALSE)
                );
            } catch {}
        });
        localStorage.setItem("booked", JSON.stringify(temp_booked_slots));
        for (row of PARENT.children) {
            if (row.dataset["state"] !== RED) {
                row.style.visibility = "visible";
            } else {
                row.style.visibility = "collapse";
            }
        }
        fetch("/lowlevellog_error/", {
            method: "POST",
            body: JSON.stringify({
                message: `Just unselected ${TEACHER_NAME} for ${SUBJECT}`,
                title: "Win FFCS Log",
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": CSRFTOKEN,
            },
        });
        updateComputedInfo();
    }
    updateTimetable();
};

const addClass = (obj, classes) => {
    obj.className = "";
    classes.split(" ").forEach((cls) => obj.classList.add(cls));
};

const renderShit = (lst) => {
    // $.unbind('hover')
    init_state_values = {};
    LIST_ALL_SLOTS.forEach((slot) => (init_state_values[slot] = FALSE));
    localStorage.setItem("booked", JSON.stringify(init_state_values));
    lst.forEach((element) => {
        const courseType = element[0];
        const courseName = element[1];
        const course = document.createElement("label");
        course.appendChild(createDataElement("div", ""));
        const contentDiv = createDataElement("div", "");
        const textSpan = createDataElement("span", "");
        const subjectSpan = createDataElement(
            "span",
            `${courseName.split(",")[0]} ${courseName.split(",")[1]}`
        );
        addClass(subjectSpan, "subject-span");
        const courseTypeSpan = createDataElement("span", `${courseType}`);
        addClass(courseTypeSpan, "course-type-span");
        addClass(textSpan, "subject-details");
        textSpan.appendChild(subjectSpan);
        textSpan.appendChild(courseTypeSpan);
        contentDiv.appendChild(textSpan);
        contentDiv.appendChild(courseCodeCopyButton());
        course.appendChild(contentDiv);
        const table = document.createElement("table");
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        const headers = [
            "Employee Name",
            "ERP",
            "Slot",
            "Subject",
            "Copy to clipboard",
        ];
        headers.forEach((innertext) => {
            headerRow.appendChild(createDataElement("th", innertext));
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);
        const label = document.createElement("label");
        label.appendChild(table);
        course.appendChild(label);
        course.dataset["selected"] = FALSE;
        course.dataset["slots"] = "";
        course.dataset["course_code"] = courseName.split(",")[1];
        // course.appendChild(document.createElement("br"));
        document.getElementById("info").appendChild(course);

        "table table-bordered table-hover table-sm table-dark"
            .split(" ")
            .forEach((cls) => {
                table.classList.add(cls);
            });
        const tbody = document.createElement("tbody");
        const tbody2 = document.createElement("tbody");
        const collapseCurrent = (obj) => {
            // console.log(obj.children);
            obj.dataset["expanded"] = FALSE;
            Array.from(obj.children).forEach((row) => {
                if (row.dataset["state"] == RED) {
                    row.style.visibility = "collapse";
                }
            });
        };
        const expandCurrent = (obj) => {
            // console.log(obj.children);
            obj.dataset["expanded"] = TRUE;
            Array.from(obj.children).forEach((row) => {
                if (
                    row.dataset["state"] == RED &&
                    row.dataset["invalid"] == FALSE
                ) {
                    row.style.visibility = "visible";
                    if (rowGeneratesConflict(row) == 1) {
                        row.style.visibility = "collapse";
                        // console.log("OMGHERE!");
                    }
                }
            });
        };
        element.splice(2).forEach((data) => {
            const generateRow = (row) => {
                const cleanedSlotData = (str) => {
                    const slots = str.split("+").filter((v) => v !== "NIL");
                    let finalSlots = "";
                    for (const slot of slots) {
                        finalSlots += slot + "+";
                    }
                    return finalSlots.slice(0, -1);
                };
                row["slot"] = cleanedSlotData(row["slot"]);
                const currentRow = document.createElement("tr");
                currentRow.appendChild(createDataElement("td", row["name"]));
                currentRow.appendChild(createDataElement("td", row["erpid"]));
                currentRow.appendChild(createDataElement("td", row["slot"]));
                currentRow.appendChild(createDataElement("td", element[1]));
                let copyElement = createDataElement("td", "");
                copyElement.appendChild(nameCopyButton());
                currentRow.appendChild(copyElement);
                currentRow.dataset.selected = FALSE;
                currentRow.dataset.slots = row["slot"];
                currentRow.addEventListener("click", rowUpdate);
                currentRow.dataset["invalid"] = FALSE;
                if (row["chosen"] == "C") {
                    //C is for chosen(YELLOW)
                    currentRow.dataset["state"] = YELLOW;
                    currentRow.classList.add(YELLOW);
                    tbody.appendChild(currentRow);
                } else {
                    currentRow.dataset["state"] = RED;
                    currentRow.classList.add(RED);
                    tbody2.appendChild(currentRow);
                }
            };
            data["name"].forEach((placeholder, idx) => {
                const row = {
                    name: data["name"][idx],
                    erpid: data["erpid"][idx],
                    slot: data["slot"],
                    chosen: data["chosen"],
                };
                generateRow(row);
            });
        });

        const currentRow = document.createElement("tr");
        addClass(currentRow, "toggle-button");
        currentRow.dataset["state"] = GREY;
        currentRow.dataset["collapsed"] = TRUE;
        currentRow.classList.add("GREY");
        currentRow.addEventListener("click", () => {
            if (currentRow.dataset["collapsed"] == TRUE) {
                // console.log(currentRow.dataset['collapsed'])
                expandCurrent(event.target.parentElement.parentElement);
                event.target.parentElement.dataset["collapsed"] = FALSE;
            } else {
                // console.log(currentRow.dataset['collapsed'])
                collapseCurrent(event.target.parentElement.parentElement);
                event.target.parentElement.dataset["collapsed"] = TRUE;
            }
        });
        for (let index = 0; index < 1; index++) {
            const blankTD = createDataElement("td", "Click to expand");
            blankTD.setAttribute("colspan", "5");
            addClass(blankTD, "center");
            currentRow.appendChild(blankTD);
        }
        tbody.appendChild(currentRow);
        tbody.dataset["expanded"] = FALSE;
        Array.from(tbody2.children).forEach((element) => {
            tbody.appendChild(element);
        });
        table.appendChild(tbody);
    });
    collapseAll();
};

const pageload = () => {
    fetch("/ffcsfinalpagedata/", {
        method: "POST",
        body: JSON.stringify({}),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "X-CSRFToken": CSRFTOKEN,
        },
    })
        .then((res) => res.json())
        .then((res) => {
            // document.getElementById("info").innerText=JSON.stringify(res["info"]);
            localStorage.setItem("info", JSON.stringify(res["info"]));
            console.log(res);
            renderShit(res["info"]);
        });
    document.querySelector("#update-btn").addEventListener("click", (e) => {
        update(e);
    });
};
pageload();
