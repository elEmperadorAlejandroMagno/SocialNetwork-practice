document.addEventListener("DOMContentLoaded", function () {
  // Add event listeners or any other JavaScript code here if needed
  newPostForm = document.querySelector("#newPostForm");
  newPostContainer = document.querySelector("#newPost");

  newPostForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const formData = new FormData(newPostForm);
    fetch("/post/new_post", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          const post = data.post;
          // Clear the textarea
          newPostForm.reset();

          const POST_DIV = document.createElement("div");
          const USERNAME_P = document.createElement("p");
          const CONTENT_P = document.createElement("p");
          const LIKES_P = document.createElement("p");
          const LIKE_BTN = document.createElement("button");
          const TIMESTAMP = document.createElement("p");
          
          POST_DIV.className = "post";
          CONTENT_P.className = "post-content";
          LIKE_BTN.className = "like-button";
          USERNAME_P.innerHTML = `<strong>${ post.author }</strong>`;
          CONTENT_P.textContent = post.content;
          LIKES_P.innerHTML = `Likes: <span class="likes-count">${ post.likes_count }</span>`;
          TIMESTAMP.textContent = `Posted at: ${ post.timestamp }`;
          
          POST_DIV.setAttribute("data-post-id", post.id);
          POST_DIV.appendChild(USERNAME_P);
          POST_DIV.appendChild(CONTENT_P);
          POST_DIV.appendChild(LIKES_P);
          POST_DIV.appendChild(TIMESTAMP);

          if (data.is_author) {
            const EDIT_BTN = document.createElement("button");
            EDIT_BTN.textContent = "Edit";
            EDIT_BTN.id = "editBtn";
            POST_DIV.appendChild(EDIT_BTN);
          }
          newPostContainer.prepend(POST_DIV);
        }
    });
  });

});