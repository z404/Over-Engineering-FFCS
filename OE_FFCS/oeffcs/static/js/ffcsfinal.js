const CSRFTOKEN = document.querySelector("[name=csrfmiddlewaretoken]").value;
const TRUE = "TRUE";
const FALSE = "FALSE";
const GREEN = "GREEN";
const YELLOW = "YELLOW";
const RED = "RED";

const createDataElement = (type, data) => {
    const element = document.createElement(type);
    element.innerText = data;
    return element;
};
const collapseAll = () => {
    Array.from(document.getElementsByClassName(RED))
        .forEach(redrow => {
            redrow.style.visibility = "collapse";
        });
};
const renderShit = lst => {
    lst.forEach(element => {
        const courseType = element[0];
        const courseName = element[1];
        const course = document.createElement("label");
        course.appendChild(createDataElement("div", courseType));
        course.appendChild(createDataElement("div", courseName));
        const table = document.createElement("table");
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        const headers = [
            "Employee Name",
            "ERP",
            "Slot",
            "Subject",
        ]
        headers.forEach(innertext => {
            headerRow.appendChild(createDataElement("th", innertext));
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        const label = document.createElement("label");
        label.appendChild(table);
        course.appendChild(label);
        document.getElementById("info").appendChild(course);
        document.getElementById("info").appendChild(
            document.createElement("br")
        );
        "table table-bordered table-hover table-sm table-dark"
            .split(' ').forEach(cls => {
                table.classList.add(cls);
            });
        const tbody = document.createElement("tbody");
        const tbody2 = document.createElement("tbody");
        const collapseCurrent = obj => {
            console.log(obj.children);
            Array.from(obj.children)
            .forEach(row => {
                if(row.dataset['state']==RED){
                    row.style.visibility = "collapse";
                }
            });
        };
        const expandCurrent = obj => {
            console.log(obj.children);
            Array.from(obj.children)
            .forEach(row => {
                if(row.dataset['state']==RED){
                    row.style.visibility = "visible";
                }
            });
        };
        element.splice(2).forEach(data => {
            const currentRow = document.createElement("tr");
            currentRow.appendChild(createDataElement("td", data["name"]));
            currentRow.appendChild(createDataElement("td", data["erpid"]));
            currentRow.appendChild(createDataElement("td", data["slot"]));
            currentRow.appendChild(createDataElement("td", element[1]));
            if (data["chosen"] == "C") {
                currentRow.dataset['state'] = YELLOW;
                currentRow.classList.add(YELLOW);
                tbody.appendChild(currentRow);
            }
            else {
                currentRow.dataset['state'] = RED;
                currentRow.classList.add(RED);
                tbody2.appendChild(currentRow);
            }
        });

        const currentRow = document.createElement("tr");
        currentRow.dataset['state'] = "GREY";
        currentRow.dataset['collapsed'] = TRUE;
        currentRow.classList.add("GREY");
        currentRow.addEventListener("click", () => {
            if (currentRow.dataset['collapsed'] == TRUE) {
                console.log(currentRow.dataset['collapsed'])
                expandCurrent(event.target.parentElement.parentElement);
                event.target.parentElement.dataset['collapsed'] = FALSE;
            }
            else {
                console.log(currentRow.dataset['collapsed'])
                collapseCurrent(event.target.parentElement.parentElement);
                event.target.parentElement.dataset['collapsed'] = TRUE;
            }
        });
        for (let index = 0; index < 4; index++) {
            currentRow.appendChild(createDataElement("td", ""));
        }
        tbody.appendChild(currentRow);

        Array.from(tbody2.children).forEach(element => {
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
        .then(res => res.json())
        .then(res => {
            renderShit(res["info"]);
        });
};
pageload();