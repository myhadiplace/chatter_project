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
