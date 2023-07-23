//show or hidden form
// Get references to the link and the hidden div
const newTwitteBtn = document.querySelector(".new-twitte-btn");
const hiddenForm = document.querySelector(".form-container");
const overlayDiv = document.querySelector("#overlay");

// Add a click event listener to the link
newTwitteBtn.addEventListener("click", function (event) {
  event.preventDefault(); // Prevent the link from navigating to the URL
  // Toggle the visibility of the hidden div
    hiddenForm.classList.toggle('shown'); // Show the div
    overlayDiv.classList.toggle("shown") //show overlay screen

});


//textarea settings
let textarea = document.querySelector(".medium-editor-element");
const charTyped = document.querySelector(".limit-number");
const submitTwitteBtn = document.querySelector(".submit-twitte");

textarea.addEventListener("keydown", function () {
  setTimeout(function () {
    const twitteLength = textarea.textContent.length;
    charTyped.textContent = `${twitteLength}/120`;
    if (twitteLength > 120) {
      submitTwitteBtn.disabled = true;
      charTyped.style.color = "red";
      textarea.style.setProperty("background-color", "rgba(255, 0, 0, 0.562)");
    } else {
      submitTwitteBtn.disabled = false;
      charTyped.style.color = null;
      textarea.style.removeProperty("background-color");
    }
  }, 50);
});


