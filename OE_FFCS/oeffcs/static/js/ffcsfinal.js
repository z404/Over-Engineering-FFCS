const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const createDataElement = (type,data) => {
    const element = document.createElement(type);
    element.innerText=data;
    return element;
};

const renderShit = lst => {
    lst.forEach(element => {
        const courseType = element[0];
        const courseName = element[1];
        const course = document.createElement("label");
        course.appendChild(createDataElement("div",courseType));
        course.appendChild(createDataElement("div",courseName));
        const table = document.createElement("table");
        const table2 = document.createElement("table");
        const thead = document.createElement("thead");
        const thead2 = document.createElement("thead");
        const headerRow = document.createElement("tr");
        const headerRow2 = document.createElement("tr");
        const headers = [
            "Employee Name",
            "ERP",
            "Slot",
            "Subject",
        ]
        headers.forEach(innertext => {
            headerRow.appendChild(createDataElement("th",innertext));
        });
        headers.forEach(innertext => {
            headerRow2.appendChild(createDataElement("th",innertext));
        });
        thead.appendChild(headerRow);
        thead2.appendChild(headerRow2);
        table.appendChild(thead);
        table2.appendChild(thead2);
        const label = document.createElement("label");
        label.appendChild(createDataElement("div","Chosen:"));
        label.appendChild(table);
        const label2 = document.createElement("label");
        label2.appendChild(createDataElement("div","Not chosen:"));
        label2.appendChild(table2);
        course.appendChild(label);
        course.appendChild(label2);
        document.getElementById("info").appendChild(course);
        document.getElementById("info").appendChild(
            document.createElement("br")
        );
        "table table-bordered table-hover table-sm table-dark"
        .split(' ').forEach(cls =>{
                table.classList.add(cls);
                table2.classList.add(cls);
        })
        const tbody = document.createElement("tbody");
        const tbody2 = document.createElement("tbody");
        element.splice(2).forEach(data => {
            const currentRow = document.createElement("tr");
            // data.forEach(cell => {
            //     currentRow.appendChild(createDataElement("td",cell));
            // });
            currentRow.appendChild(createDataElement("td",data["name"]));
            currentRow.appendChild(createDataElement("td",data["erpid"]));
            currentRow.appendChild(createDataElement("td",data["slot"]));
            currentRow.appendChild(createDataElement("td",element[1]));
            if(data["chosen"]=="C")
                tbody.appendChild(currentRow);
            else
                tbody2.appendChild(currentRow);
            
        });
        table.appendChild(tbody);
        table2.appendChild(tbody2);
    });
};

/* 
<table class="table table-bordered table-hover table-sm table-dark ui-sortable-handle">                                
    <thead>                                    
        <tr>                                    
            <th scope="col">Employee Name</th>                                    
            <th scope="col">Course Code</th>                                    
            <th scope="col">ERP</th>                                    
            <th scope="col">Slot</th>                                    
            <th scope="col">Subject</th>                                    
        </tr>
    </thead>
    <tbody class="moovable ui-sortable" id="tbodyCSE1003">
        <tr class="">                                
            <td>NAMITHA A S</td>                                
            <td>CSE1003</td>                                
            <td>16166</td>                                
            <td>L43+L44+B1+TB1</td>                                
            <td>Digital Logic and Design</td>                            
        </tr>
    </tbody>
</table> */


const pageload = () => {
    fetch("/ffcsfinalpagedata/", {
            method: "POST",
            body: JSON.stringify({}),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": csrftoken,
            },
        })
        .then(res => res.json())
        .then(res => {
            document.getElementById("info").innerHTML = JSON.stringify(res);
            renderShit(res["info"]);
        });
};
pageload();