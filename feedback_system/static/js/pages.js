const tabs = document.querySelectorAll(".nav_item");
const tabPanes = document.querySelectorAll(".tab-pane");

tabs.forEach((tab, index) => {
  tab.addEventListener("click", (e) => {
    tabs.forEach((tab) => {
      tab.classList.remove("active");
    });
    tab.classList.add("active");

    tabPanes.forEach((content) => {
      content.classList.remove("active");
    });
    tabPanes[index].classList.add("active");
  });
});

const cardTabs = document.querySelectorAll(".card_nav_item");
const cardTabPanes = document.querySelectorAll(".cardTabPane");

cardTabs.forEach((tab, index) => {
  tab.addEventListener("click", (e) => {
    cardTabs.forEach((tab) => {
      tab.classList.remove("active");
    });
    tab.classList.add("active");

    cardTabPanes.forEach((content) => {
      content.classList.remove("active");
    });
    cardTabPanes[index].classList.add("active");
  });
});

const accordionContent = document.querySelectorAll(".accordion_content");
accordionContent.forEach((item, index) => {
  let header = item.querySelector(".accordion_header");
  header.addEventListener("click", () => {
    item.classList.toggle("open");
    let description = item.querySelector(".accordion_desc");
    if (item.classList.contains("open")) {
      description.style.height = `${description.scrollHeight}px`;
      item
        .querySelector("i")
        .classList.replace("bx-chevron-down", "bx-chevron-up");
    } else {
      description.style.height = "0px";
      item
        .querySelector("i")
        .classList.replace("bx-chevron-up", "bx-chevron-down");
    }
    removeOpen(index);
  });
});
function removeOpen(index1) {
  accordionContent.forEach((item2, index2) => {
    if (index1 != index2) {
      item2.classList.remove("open");
      let des = item2.querySelector(".accordion_desc");
      des.style.height = "0px";
      item2
        .querySelector("i")
        .classList.replace("bx-chevron-up", "bx-chevron-down");
    }
  });
}

const dropdownContent = document.querySelectorAll(".dropdown_content");
dropdownContent.forEach((item, index) => {
  let header = item.querySelector(".dropdown_header");
  header.addEventListener("click", () => {
    item.classList.toggle("open");
    let description = item.querySelector(".dropdown_desc");
    if (item.classList.contains("open")) {
      description.style.height = `${description.scrollHeight}px`;
      item
        .querySelector(".down")
        .classList.replace("bx-chevron-down", "bx-chevron-up");
    } else {
      description.style.height = "0px";
      item
        .querySelector(".down")
        .classList.replace("bx-chevron-up", "bx-chevron-down");
    }
    removeOpen(index);
  });
});

const inputs = document.querySelectorAll(".pinInput"),
  button = document.querySelector(".pinInputBtn");

inputs.forEach((input, index1) => {
  input.addEventListener("keyup", (e) => {
    const currentInput = input,
      nextInput = input.nextElementSibling,
      prevInput = input.previousElementSibling;

    if (currentInput.value.length > 1) {
      currentInput.value = "";
      return;
    }
    if (
      nextInput &&
      nextInput.hasAttribute("disabled") &&
      currentInput.value !== ""
    ) {
      nextInput.removeAttribute("disabled");
      nextInput.focus();
    }
    if (e.key === "Backspace") {
      inputs.forEach((input, index2) => {
        if (index1 <= index2 && prevInput) {
          input.setAttribute("disabled", true);
          currentInput.value = "";
          prevInput.focus();
        }
      });
    }
    if (!inputs[3].disabled && !inputs[3].value !== "") {
      button.classList.add("active");
      return;
    }
    button.classList.remove("active");
  });
});
// window.addEventListener("load", () => inputs[0].focus());

const openPinModel = function () {
  const transferBtns = document.querySelectorAll(".transfer_btn"),
    pinForm = document.querySelector(".pinForm"),
    amount = document.querySelector("#amount");

  transferBtns.forEach(function (btn) {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      pinForm.classList.add("active");
      amount.blur();
    });
  });
};

let toast = document.getElementById("toast");
setTimeout((e) => {
  // e.preventDefault();
  toast.remove();
}, 8000);

document.getElementById("rollBack").addEventListener("click", openPinModel());
