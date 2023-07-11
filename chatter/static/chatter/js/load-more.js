const loadMoreBtn = document.querySelector(".load-more");
console.log(loadMoreBtn);

loadMoreBtn.addEventListener("click", function () {
  fetch("render-post")
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
 
      const postContainer = document.getElementById("posts-container");
      data.forEach(postTemplate => {
        postContainer.insertAdjacentHTML('beforeend', postTemplate);
      });
    })
    .catch((error) => {
      console.error(error);
    });
});
