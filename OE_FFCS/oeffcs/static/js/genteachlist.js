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

function toggle_modal(modal) {
  modal.style.display = "block";

  window.onclick = function (event) {
    //Logic for close
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
  span_close = document.getElementById(modal.id + "close");
  span_close.onclick = function () {
    modal.style.display = "none";
  };
  const TTID = event.target.dataset.ttid;
  if (document.getElementById(TTID + "main").innerHTML == "") {
    fetch("/modaldata/", {
      method: "POST",
      body: JSON.stringify({
        ttid: TTID,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((res) => res.json())
      .then((res) => {
        document.getElementById(TTID + "main").innerHTML = render_timetable(
          res["render_timetable"]
        );
        document.getElementById(TTID + "info").innerHTML =
          res["information_table"];
      });
  }
  // .catch(err => console.error(err));
}

// // Get the modal
// var modal = document.getElementById("myModal");

// // Get the button that opens the modal
// var btn = document.getElementById("myBtn");

// // Get the <span> element that closes the modal
// var span = document.getElementsByClassName("close")[0];

// // When the user clicks on the button, open the modal
// btn.onclick = function() {
//     modal.style.display = "block";
// }

// // When the user clicks on <span> (x), close the modal

// // When the user clicks anywhere outside of the modal, close it
