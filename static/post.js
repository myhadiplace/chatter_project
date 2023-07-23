const getCookie = function (name) {
  return document.cookie.split("=")[1];
};

let isFetching = false;

// like mechanism
let buttons = document.querySelectorAll(".like-button");
buttons.forEach(function (b) {
  b.addEventListener("click", function (e) {
    e.preventDefault();

    // prevent click if previuse fetching is running
    if (isFetching) {
      return;
    }
    b.disabled = true;
    isFetching = true;

    this.classList.toggle("active");
    this.classList.add("animated");
    generateClones(this);

    const postId = b.dataset.postid;
    const username = b.dataset.username;
    let likeNumber = document.querySelector(
      `a[data-postid="${postId}"] + span.likenum`
    );

    fetch(`/like/${username}/${postId}`, {
      method: "POST",
      headers: {
        X_CSRFToken: getCookie("csrftoken"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.already_liked) {
          this.classList.remove("active");
          likeNumber.innerHTML--;
        } else {
          likeNumber.innerHTML++;
        }
      })
      .catch((error) => console.log(error))
      .finally(() => {
        // allowed to click sins fetching is done
        isFetching = false;
        b.disabled = false;
      });
  });
});

// js code for like button animation
function generateClones(button) {
  let clones = randomInt(4, 10);
  for (let it = 1; it <= clones; it++) {
    let clone = button.querySelector("svg").cloneNode(true), // create a deep copy(clone) of SVG element
      size = randomInt(5, 16);
    button.appendChild(clone);
    clone.setAttribute("width", size);
    clone.setAttribute("height", size);
    clone.style.position = "absolute";
    clone.style.transition =
      "transform 0.5s cubic-bezier(0.12, 0.74, 0.58, 0.99) 0.3s, opacity 1s ease-out .5s";
    let animTimeout = setTimeout(function () {
      clearTimeout(animTimeout);
      clone.style.transform =
        "translate3d(" +
        plusOrMinus() * randomInt(10, 25) +
        "px," +
        plusOrMinus() * randomInt(10, 25) +
        "px,0)";
      clone.style.opacity = 0;
    }, 1);
    let removeNodeTimeout = setTimeout(function () {
      clone.parentNode.removeChild(clone);
      clearTimeout(removeNodeTimeout);
    }, 900);
    let removeClassTimeout = setTimeout(function () {
      button.classList.remove("animated");
    }, 600);
  }
}

function plusOrMinus() {
  return Math.random() < 0.5 ? -1 : 1;
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

// dropdown menu
function toggleDropdown(event) {
  event.stopPropagation(); // prevent event bubbling
  var dropdownContent = event.currentTarget.nextElementSibling;
  dropdownContent.style.display =
    dropdownContent.style.display === "none" ? "block" : "none";
}

// Close dropdown menus when clicking outside
document.addEventListener("click", function (event) {
  var dropdownContents = document.getElementsByClassName("dropdown-content");
  for (var i = 0; i < dropdownContents.length; i++) {
    var dropdownContent = dropdownContents[i];
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    }
  }
});
