const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const func = async () => {
    let result = {
        'valid_status':false
    };
    const firstCall = async () => {
        const firstres = await fetch("/loadingscreenstatus/", {
            method: "POST",
            body: JSON.stringify({}),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "X-CSRFToken": csrftoken,
            }
        });
        const json = await firstres.json();
        document.getElementById("info").innerText=`Working with ${ json['total_timetables'] } timetables here, so we appreciate your cooperation :)`
    };
    firstCall();
    const progress = document.querySelector('.progress-done');
    const repeater = setInterval(async () => {
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
            clearInterval(repeater);
            setTimeout(() => {
                window.location.href= window.location.origin + "/pickfilters/";
            }, 3000);
        }
    }, 15000);
};

func();
