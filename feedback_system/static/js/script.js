// APP INTERFACE BUTTONS
const labelWelcome = document.querySelector(".welcome"),
  labelDate = document.querySelector(".date"),
  labelBalance = document.querySelector(".amount"),
  labelSumIn = document.querySelector(".income_amt"),
  labelSumOut = document.querySelector(".expense_amt"),
  labelSavings = document.querySelector(".save_amt"),
  labelTimer = document.querySelector(".timer"),
  btnTransfer = document.querySelector(".form__btn--transfer"),
  btnLoan = document.querySelector(".form__btn--loan"),
  btnFormClose = document.querySelector(".form__btn--close"),
  inputTransferTo = document.querySelector(".form__input--to"),
  inputTransferAmount = document.querySelector(".form__input--amount"),
  inputLoanAmount = document.querySelector(".form__input--loan-amount"),
  inputLoanPin = document.querySelector(".form__input--loan-pin"),
  transferPin = document.querySelector(".form__input--pin"),
  inputCloseUsername = document.querySelector(".form__input--user"),
  inputClosePin = document.querySelector(".form__close--pin"),
  inputLoginUsername = document.querySelector(".login__input--user"),
  inputLoginPin = document.querySelector(".login__input--pin"),
  btnLogin = document.querySelector(".login__btn"),
  containerMovements = document.querySelector(".movements_amount"),
  btnSort = document.querySelector(".exp_sort"),
  app = document.querySelector(".container"),
  profileName = document.querySelector(".profile_name"),
  profileImg = document.querySelector(".profile_img"),
  transferPinModel = document.querySelector(".form__btn--pin-model"),
  nextBtn = document.querySelector(".next-btn"),
  submitBtn = document.querySelector(".next-btn--2");

// WEBSITE BUTTONS
const setBtn = document.querySelectorAll(".set-btn"),
  setBtn2 = document.querySelectorAll(".set-btn2"),
  sidebar = document.querySelector(".sidebar"),
  menuList = document.querySelector(".menu_list"),
  logOutBtn = document.getElementById("log_out"),
  logOutModel = document.querySelector(".log-out--model"),
  logOut = document.querySelector(".logout-btn"),
  deleteAccount = document.querySelector(".confirm-btn"),
  transferModel = document.querySelector(".transfer_model"),
  transferMsg = document.querySelector(".transfer-msg"),
  loanModel = document.querySelector(".loan_model"),
  section1 = document.querySelector(".features "),
  nav = document.querySelector(".nav"),
  tabs = document.querySelectorAll(".operations-tab"),
  tabsContainer = document.querySelector(".operation-tab--container"),
  tabsContent = document.querySelectorAll(".operations-content"),
  slides = document.querySelectorAll(".slide"),
  btnLeft = document.querySelector(".slider__btn--left"),
  btnRight = document.querySelector(".slider__btn--right"),
  maxSlides = slides.length,
  dotsContainer = document.querySelector(".dots"),
  imageTargets = document.querySelectorAll(".feature-img"),
  openAccModel = document.querySelectorAll(".open-acc"),
  closeBtn = document.querySelector(".close-btn"),
  overlay = document.querySelector(".overlay"),
  loginForm = document.querySelector(".login-form"),
  openLogModel = document.querySelector(".log-btn"),
  logModel = document.querySelector(".logform"),
  logOverlay = document.querySelector(".overlay-log--form"),
  btnClose = document.querySelector(".btn-close"),
  switchLog = document.querySelector(".exist-user"),
  switchReg = document.querySelector(".switch-to--reg"),
  header = document.querySelector("header"),
  btnPrivacy = document.querySelector(".privacy-btn"),
  btnTerms = document.querySelector(".terms-btn"),
  btnContacts = document.querySelector(".contact-btn"),
  closeFooter = document.querySelector(".footer-link"),
  btnOk = document.querySelectorAll(".btn-ok"),
  privacy = document.querySelector(".privacy"),
  terms = document.querySelector(".terms"),
  contacts = document.querySelector(".contacts"),
  mainOverlay = document.querySelector(".overlay-main"),
  notFound = document.querySelector(".not-found"),
  containerApp = document.querySelector(".app"),
  containerWeb = document.querySelector(".web_container"),
  logOutAcc = document.querySelector(".log_out--acc"),
  menuBar = document.querySelector(".menu_bar"),
  menuBarIcon = document.querySelectorAll(".menu_bar--icon");

// DARK MODE
let getMode = localStorage.getItem("mode");
console.log(getMode);
const body = document.querySelector("body");
const toggle = document.querySelector(".toggle");

function darkMode() {}
if (getMode && getMode === "dark") {
  body.classList.add("dark");
  toggle.classList.add("active");
}

toggle.addEventListener("click", () => {
  body.classList.toggle("dark");
  if (!body.classList.contains("dark")) {
    return localStorage.setItem("mode", "light");
  }
  return localStorage.setItem("mode", "dark");
});
toggle.addEventListener("click", () => toggle.classList.toggle("active"));
// STICKY NAVIGATION

const stickyNav = function (entries) {
  const [entry] = entries;
  if (!entry.isIntersecting) {
    nav.classList.add("sticky");
  } else {
    nav.classList.remove("sticky");
  }
};

const headerObserver = new IntersectionObserver(stickyNav, {
  root: null,
  threshold: 0,
});
headerObserver.observe(header);

// TABBED COMPONENT OPERATIONS

tabsContainer.addEventListener("click", function (e) {
  const clicked = e.target.closest(".operations-tab");
  console.log(clicked);
  if (!clicked) return;
  tabs.forEach((t) => t.classList.remove("operations-tab--active"));
  clicked.classList.add("operations-tab--active");
  tabsContent.forEach((c) => c.classList.remove("operations-content--active"));
  document
    .querySelector(`.operations-content--${clicked.dataset.tab}`)
    .classList.add("operations-content--active");
});

//SLIDER

let curSlide = 0;

slides.forEach((s, i) => (s.style.transform = `translateX(${100 * i}%)`));

const createDots = function () {
  slides.forEach((_, i) => {
    dotsContainer.insertAdjacentHTML(
      "beforeend",
      `<button class="dots__dot" data-slide="${i}"></button>`
    );
  });
};
createDots();

const activateDots = function (slide) {
  document
    .querySelectorAll(".dots__dot")
    .forEach((dot) => dot.classList.remove("dots__dot--active"));

  document
    .querySelector(`.dots__dot[data-slide="${slide}"]`)
    .classList.add("dots__dot--active");
};
activateDots(0);

const goToSlide = function (slide) {
  slides.forEach(
    (s, i) => (s.style.transform = `translateX(${100 * (i - slide)}%)`)
  );
};
goToSlide(0);

const nextSlide = function () {
  if (curSlide === maxSlides - 1) {
    curSlide = 0;
  } else {
    curSlide++;
  }
  goToSlide(curSlide);
  activateDots(curSlide);
};

const prevSlide = function () {
  if (curSlide === 0) {
    curSlide = maxSlides - 1;
  } else {
    curSlide--;
  }
  goToSlide(curSlide);
  activateDots(curSlide);
};

btnRight.addEventListener("click", nextSlide);
btnLeft.addEventListener("click", prevSlide);

document.addEventListener("keydown", function (e) {
  if (e.key === "ArrowLeft") prevSlide();
  if (e.key === "ArrowRight") nextSlide();
});

dotsContainer.addEventListener("click", function (e) {
  if (e.target.classList.contains("dots__dot")) {
    const { slide } = e.target.dataset;
    goToSlide(slide);
    activateDots(slide);
  }
});

// REVEAL SECTIONS
const allSections = document.querySelectorAll(".section");

const revealSection = function (entries, observer) {
  const [entry] = entries;
  if (!entry.isIntersecting) return;
  entry.target.classList.remove("section--hidden");
  observer.unobserve(entry.target);
};

const sectionObserver = new IntersectionObserver(revealSection, {
  root: null,
  threshold: 0.075,
});

allSections.forEach(function (section) {
  sectionObserver.observe(section);
  section.classList.add("section--hidden");
});

// LAZY LOADING IMAGES

const loading = function (entries, observer) {
  const [entry] = entries;
  if (!entry.isIntersecting) return;
  entry.target.classList.remove("lazy-img");
};

const imgObserver = new IntersectionObserver(loading, {
  root: null,
  threshold: 0.3,
});

imageTargets.forEach((img) => imgObserver.observe(img));

// OTHER WEBSITE COMPONENTS
// PIN VISIBILITY
btnPrivacy.addEventListener("click", function (e) {
  e.preventDefault();
  privacy.classList.add("active");
  mainOverlay.classList.remove("hidden");
});

btnTerms.addEventListener("click", function (e) {
  e.preventDefault();
  terms.classList.add("active");
  mainOverlay.classList.remove("hidden");
  var check = document.querySelector(".terms-agree");
  if (check.checked === true) check.checked = "";
});

btnContacts.addEventListener("click", function (e) {
  e.preventDefault();
  contacts.classList.add("active");
  mainOverlay.classList.remove("hidden");
});

btnOk.forEach(function (btn) {
  btn.addEventListener("click", function (e) {
    e.preventDefault();
    privacy.classList.remove("active");
    terms.classList.remove("active");
    contacts.classList.remove("active");
    // logOutModel.classList.remove("active");
    // deleteModel.classList.remove("active");
    mainOverlay.classList.add("hidden");
  });
});

function enable() {
  var check = document.querySelector(".terms-agree");
  var btn = document.querySelector("#terms-btn");
  if (check.checked) {
    btn.removeAttribute("disabled");
  } else {
    btn.addAttribute("disabled");
  }
}
document.querySelector(".bx-menu").addEventListener("click", function (e) {
  e.preventDefault();
  document.querySelector(".nav-links").classList.toggle("active");
  document.querySelector(".bx-menu").style.display = "none";
  document.querySelector(".bx-x").style.display = "block";
});

document.querySelector(".bx-x").addEventListener("click", function (e) {
  e.preventDefault();
  document.querySelector(".nav-links").classList.toggle("active");
  document.querySelector(".bx-menu").style.display = "block";
  document.querySelector(".bx-x").style.display = "none";
});

setBtn.forEach(function (btn) {
  btn.onclick = function (e) {
    e.preventDefault();
    sidebar.classList.toggle("active");
  };
});
menuBarIcon.forEach(function (btn) {
  btn.onclick = function (e) {
    e.preventDefault();
    menuBar.classList.toggle("active");
  };
});

// DATE FUNCTIONS
// const d = new Date();
// let day = `${d.getDate()}`.padStart(2, 0);
// let month = `${d.getMonth() + 1}`.padStart(2, 0);
// let year = d.getFullYear();
// const hour = `${d.getHours()}`.padStart(2, 0);
// const min = `${d.getMinutes()}`.padStart(2, 0);
// labelDate.textContent = `${day}/${month}/${year}, ${hour}:${min}`;
let prev = document.querySelector(".prev");
let next = document.querySelector(".next");
function nextFun() {
  next.addEventListener("click", function () {
    let items = document.querySelectorAll(".item");
    document.querySelector(".heroSlide").appendChild(items[0]);
  });
}

function prevFun() {
  prev.addEventListener("click", function () {
    let items = document.querySelectorAll(".item");
    document.querySelector(".heroSlide").prepend(items[items.length - 1]);
  });
}

prev.addEventListener("click", prevFun());
next.addEventListener("click", nextFun());

setInterval(() => {
  document.querySelector(".next").click();
}, 5000);
