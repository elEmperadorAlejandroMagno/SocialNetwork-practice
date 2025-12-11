document.addEventListener("DOMContentLoaded", function () {
  // Add event listeners or any other JavaScript code here if needed
  let newPostForm = document.querySelector("#newPostForm");
  let newPostContainer = document.querySelector("#newPost");
  let editBtn = document.querySelectorAll("#editBtn");
  let likeBtn = document.querySelectorAll("#likeBtn");

  if (newPostForm) {
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
            const USERNAME_A = document.createElement("a");
            const CONTENT_P = document.createElement("p");
            const LIKES_P = document.createElement("p");
            const LIKE_BTN = document.createElement("button");
            const TIMESTAMP = document.createElement("p");
            
            // Clases para que coincida con el HTML renderizado en el servidor
            POST_DIV.className = "post";
            CONTENT_P.className = "post-content";
            TIMESTAMP.className = "timestamp";
            LIKE_BTN.className = "like-button";
            LIKE_BTN.id = "likeBtn";

            USERNAME_A.innerHTML = `<strong>${ post.author }</strong> says:`;
            USERNAME_A.href = `/profile/${ post.author }`;
            CONTENT_P.textContent = post.content;
            LIKE_BTN.textContent = "Like";
            LIKES_P.innerHTML = `Likes: <span class=\"likes-count\">${ post.likes_count }</span>`;
            TIMESTAMP.textContent = `${ post.created_at }`;
            
            POST_DIV.setAttribute("data-post-id", post.id);
            POST_DIV.appendChild(USERNAME_A);
            POST_DIV.appendChild(CONTENT_P);
            POST_DIV.appendChild(TIMESTAMP);
            POST_DIV.appendChild(LIKES_P);
            POST_DIV.appendChild(LIKE_BTN);

            if (data.is_author) {
              const EDIT_BTN = document.createElement("button");
              EDIT_BTN.textContent = "Edit";
              EDIT_BTN.id = "editBtn";
              POST_DIV.appendChild(EDIT_BTN);
            }
            newPostContainer.prepend(POST_DIV);
            newPostContainer.style.display = "block";
            editBtn = document.querySelectorAll("#editBtn");
            likeBtn = document.querySelectorAll("#likeBtn");
          }
      });
    });
  }

  if (likeBtn.length > 0) {
    likeBtn.forEach((button) => {
      button.addEventListener("click", (e) => {
        const postDiv = e.target.closest(".post");
        const postId = postDiv.getAttribute("data-post-id");
        fetch(`/post/like`, {
          method: "POST",
          body: JSON.stringify({ post_id: postId }),
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              const likesCountSpan = postDiv.querySelector(".likes-count");
              likesCountSpan.textContent = data.likes_count;
              e.target.textContent = (data.action === "liked") ? "Unlike" : "Like";
            }
          });
      });
    });
  }

  if (editBtn.length > 0) {
    editBtn.forEach((button) => {
      button.addEventListener("click", (e) => {
        const postDiv = e.target.closest(".post");
        const postId = postDiv.getAttribute("data-post-id");
        const postContentP = postDiv.querySelector(".post-content");
        const originalContent = postContentP.textContent;

        // Create textarea for editing
        const textarea = document.createElement("textarea");
        textarea.value = originalContent;
        postDiv.replaceChild(textarea, postContentP);

        // Change Edit button to Save button
        e.target.textContent = "Save";
        e.target.id = "saveBtn";

        // Add event listener for Save button
        e.target.addEventListener("click", () => {
          const updatedContent = textarea.value;

          fetch(`/post/edit`, {
            method: "POST",
            body: JSON.stringify({
              "post_id": postId,
              "content": updatedContent
            }),
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').getAttribute("content"),
            },
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.status === "success") {
                // Update the post content
                postContentP.textContent = data.new_content;
                postDiv.replaceChild(postContentP, textarea);
                e.target.textContent = "Edit";
                e.target.id = "editBtn";
              }
            })
            .catch((error) => {
              console.error("Error updating post:", error);
            });
          });
      });
    });
  }


});