const linearSearch = (val) => {
    const arr =
        "A1 F1 D1 TB1 TG1 L1 L2 L3 L4 L5 L6 B1 G1 E1 TC1 TAA1 L7 L8 L9 L10 L11 L12 C1 A1 F1 V1 V2 L13 L14 L15 L16 L17 L18 D1 B1 G1 TE1 TCC1 L19 L20 L21 L22 L23 L24 E1 C1 TA1 TF1 TD1 L25 L26 L27 L28 L29 L30 A2 F2 D2 TB2 TG2 L31 L32 L33 L34 L35 L36 B2 G2 E2 TC2 TAA2 L37 L38 L39 L40 L41 L42 C2 A2 F2 TD2 TBB2 L43 L44 L45 L46 L47 L48 D2 B2 G2 TE2 TCC2 L49 L50 L51 L52 L53 L54 E2 C2 TA2 TF2 TDD2 L55 L56 L57 L58 L59 L60 V7 V6 V5 V4 V3".split(
            " "
        );
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] === val) return true;
    }
    return false;
};

const validList = (strng) => {
    lst = strng
        .toUpperCase()
        .split(",")
        .filter((e) => e !== " ")
        .map((e) => e.trim());
    return lst;
};

const ValidForm = () => {
    const that = $("input[name=slots]");
    if (
        (that.val().length != 0 &&
            validList(that.val()).length ===
            validList(that.val())
            .map(linearSearch)
            .filter((e) => e).length &&
            validList(that.val()).length !== 0) ||
        that.val().length == 0
    ) {
        $(".invalid-feedback").hide();
        $("#slots").removeClass("is-invalid");
        return true;
    }
    $("#zero-timetables-error").hide();
    $("#slots").addClass("is-invalid");
    $("#pre-check-info").text("");
    return false;
};

const request = async() => {
    var data = {},
        that = $("form.ajax");
    that
        .find("input[type=radio]:checked,input[type=number],input[type=text]")
        .each((index, valv) => {
            var that = $(valv),
                name = that.attr("name"),
                id = that.attr("id"),
                value = that.val();
            // console.log(id,value);
            if (name == "category") data[id] = value;
            else {
                data[name] = value;
            }
        });
    const response = await fetch("/precheck/", {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "X-CSRFToken": csrftoken,
        },
    });
    const json = await response.json();
    // console.log(json);
    return json;
};

$(document).ready(() => {
    $(".invalid-feedback").hide();
    $("#zero-timetables-error").hide();

    $("#pre-check").on("click", async() => {
        if (ValidForm()) {
            event.preventDefault();
            json = await request();
            console.log(json);
            if (json["ret"] != 0) {
                $("#pre-check-info").text(
                    "These filters generated " +
                    JSON.stringify(json["ret"]) +
                    " Timetables!"
                );
                $("#pre-check-info").show();
                $("#error-message1").hide();
                $("#zero-timetables-error").hide();
            } else {
                $("#zero-timetables-error").show();
                $("#pre-check-info").hide();
            }
        } else {
            $("#error-message1").show();
            $("#pre-check-info").text("");
            event.preventDefault();
        }
    });

    $("#save-filters").on("click", async() => {
        if (ValidForm()) {
            event.preventDefault();
            json = await request();
            if (json["ret"] == 0) {
                $("#zero-timetables-error").show();
                $("#pre-check-info").hide("");
                $("form.ajax").submit();
            } else {
                localStorage.setItem("allstoredtimetables", null);
                $("form.ajax").submit();
            }
        } else {
            event.preventDefault();
            $("#error-message1").show();
            $("#pre-check-info").text("");
        }
    });
});