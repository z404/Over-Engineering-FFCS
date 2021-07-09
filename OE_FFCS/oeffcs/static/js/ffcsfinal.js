const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

// const renderShit()

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
            // renderShit(res["info"]);
        });
};
pageload();