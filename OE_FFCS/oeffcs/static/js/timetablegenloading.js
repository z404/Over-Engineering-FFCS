const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const firstCall = async () => {
    let result = {
        'valid_status':false
    };
    const res = await fetch("/loadingscreenstatus/", {
        method: "POST",
        body: JSON.stringify({}),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "X-CSRFToken": csrftoken,
        }
    });
    result = {
        ...result,
        ...(await res.json())
    }
    let percentage = Number(result['completed_timetables'])/Number(result['total_timetables'])*100;
    percentage = percentage.toPrecision(3);
    progress.style.width = percentage + '%';
    progress.style.opacity = 1;
    document.getElementById("progress-done").innerText= String(percentage) +"%";
    document.getElementById("valid-timetables").innerText= String(result['valid_timetables']) + " valid found!";
};

const func = async () => {
    let result = {
        'valid_status':false
    };
    
    // setTimeout(() => {
    //     firstCall();
    // }, 1000);
    firstCall();
    const loadingRefresh = async () => {
        const res = await fetch("/loadingscreenstatus/", {
            method: "POST",
            body: JSON.stringify({}),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": csrftoken,
            }
        });
        result = {
            ...result,
            ...(await res.json())
        }
        let percentage = Number(result['completed_timetables'])/Number(result['total_timetables'])*100;
        percentage = percentage.toPrecision(3);
        progress.style.width = percentage + '%';
        progress.style.opacity = 1;
        document.getElementById("progress-done").innerText= String(percentage) +"%";
        document.getElementById("valid-timetables").innerText= String(result['valid_timetables']) + " valid found!";
        console.log(result);
        if (result['valid_status']!=false) {
            setTimeout(() => {
                window.location.href= window.location.origin + "/pickfilters/";
            }, 3000);
        }
        else{
            setTimeout(loadingRefresh, Math.random()*10000 + 10000);
        }
    };
    console.log("I'm here");
    const progress = document.querySelector('.progress-done');
    loadingRefresh();
};

func();
