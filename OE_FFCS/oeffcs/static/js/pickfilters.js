const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
$(document).ready(function() {
    $('#error-message').hide();
    const linearSearch = (val) => {
        const arr = 'A1 F1 D1 TB1 TG1 L1 L2 L3 L4 L5 L6 B1 G1 E1 TC1 TAA1 L7 L8 L9 L10 L11 L12 C1 A1 F1 V1 V2 L13 L14 L15 L16 L17 L18 D1 B1 G1 TE1 TCC1 L19 L20 L21 L22 L23 L24 E1 C1 TA1 TF1 TD1 L25 L26 L27 L28 L29 L30 A2 F2 D2 TB2 TG2 L31 L32 L33 L34 L35 L36 B2 G2 E2 TC2 TAA2 L37 L38 L39 L40 L41 L42 C2 A2 F2 TD2 TBB2 L43 L44 L45 L46 L47 L48 D2 B2 G2 TE2 TCC2 L49 L50 L51 L52 L53 L54 E2 C2 TA2 TF2 TDD2 L55 L56 L57 L58 L59 L60 V7 V6 V5 V4 V3'.split(' ');
        for (var i = 0; i < arr.length; i++) {
            if (arr[i] === val)
                return true;
        }
        return false;
    }
    const validList = strng => {
        lst = strng.toUpperCase().split(',').filter(e => e !== ' ').map(e => e.trim());
        return lst
    }
    const ValidForm = () => {
        const that = $('input[name=slots]')
        if ((that.val().length != 0 && validList(that.val()).length === validList(that.val()).map(linearSearch).filter(e => e).length && validList(that.val()).length !== 0) || (that.val().length == 0)) {
            $('#error-message').hide();
            $('#slots').removeClass('is-invalid');
            return true;
        } else {
            $('#error-message').show();
            $('#slots').addClass('is-invalid');
        }
    }
    $('input#pre-check').on('click', function() {
        var that = $('form.ajax'),
            type = that.attr('method'),
            data = {};
        if (ValidForm()) {
            that.find('input[type=radio]:checked,input[type=number],input[type=text]').each((index, valv) => {
                var that = $(valv),
                    name = that.attr('name'),
                    id = that.attr('id'),
                    value = that.val();
                // console.log(id,value);
                if (name == 'category')
                    data[id] = value;
                else {
                    data[name] = value;
                }
            });
            // console.log(data);
            fetch("/precheck/", {
                method: 'POST',
                'body': JSON.stringify(data),
                headers: {
                    'Content-type': 'application/json; charset=UTF-8',
                    'X-CSRFToken': csrftoken
                }
            }).then(
                response => response.json()
            ).then(json => {
                $("#pre-check-info").text("These filters generated " + JSON.stringify(json['ret']) + " Timetables!");
            });
        }
        event.preventDefault();

    });
    $('input#save-filters').on('click', ()=> {
        var that = $('form.ajax'),
            data = {};
        if (ValidForm()) {
            that.find('input[type=radio]:checked,input[type=number],input[type=text]').each((index, valv) => {
                var that = $(valv),
                    name = that.attr('name'),
                    id = that.attr('id'),
                    value = that.val();
                // console.log(id,value);
                if (name == 'category')
                    data[id] = value;
                else {
                    data[name] = value;
                }
            });
        }
        else
            event.preventDefault();

    });
});