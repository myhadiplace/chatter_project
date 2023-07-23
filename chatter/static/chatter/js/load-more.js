const loadMoreBtn = document.querySelector(".load-more-btn");
const postContainer = document.getElementById("posts-container");
loadMoreBtn.disabled = false;


loadMoreBtn.addEventListener("click", function () {
  const lastPost = postContainer.lastElementChild;
  
  

  fetch("render-post")
    .then((response) => response.json())
    .then((data) => {
      console.log(data[0].length)
      if (data[0].length == 0) {
        console.log('no mre twitte');
        loadMoreBtn.disabled = true;
        
      }
      
      const postContainer = document.getElementById("posts-container");
      data.forEach(postTemplate => {
        postContainer.insertAdjacentHTML('beforeend', postTemplate);
        
        
        //scroll to last child elemrnt of posts container
        lastPost.scrollIntoView({behavior:"smooth"})
      });
    })
    .catch((error) => {
      console.error(error);
    });
  
});
