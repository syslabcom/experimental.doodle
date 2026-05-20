(function () {
  "use strict";

  function initProposeDates() {
    var addButton = document.getElementById("doodle-propose-add");
    var list = document.querySelector(".doodle-propose-dates");
    var template = document.getElementById("doodle-propose-date-template");
    if (!addButton || !list || !template) {
      return;
    }

    addButton.addEventListener("click", function () {
      list.appendChild(template.content.cloneNode(true));
    });

    list.addEventListener("change", function (event) {
      var input = event.target.closest(".doodle-propose-date");
      if (!input || !input.value) {
        return;
      }
      var checkbox = document.getElementById("doodle-date-" + input.value);
      if (checkbox) {
        checkbox.checked = true;
      }
    });

    list.addEventListener("click", function (event) {
      var removeButton = event.target.closest(".doodle-propose-remove");
      if (!removeButton || !list.contains(removeButton)) {
        return;
      }
      var row = removeButton.closest("li");
      if (row) {
        row.remove();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProposeDates);
  } else {
    initProposeDates();
  }
})();
