import { showLoader, hiddeLoader, showBtnLoader, hiddeBtnLoader } from './utils.js';

document.addEventListener("DOMContentLoaded", function () {

  let isLoading = false;
  let counter = 10;
  const quantity = 10;
  let starts = counter;
  let ends = starts + quantity - 1;

  window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        fetchInifiteScroll(counter, starts, ends, POSTS_CONTAINER, isLoading);
    }
  };
  // Add event listeners or any other JavaScript code here if needed
  let newPostForm = document.querySelector("#newPostForm");
  let editBtn = document.querySelectorAll("#editBtn");
  let postLikeBtn = document.querySelectorAll("#postLikeBtn");
  const POSTS_CONTAINER = document.querySelector("#posts-container");

  create_new_post(newPostForm, POSTS_CONTAINER, isLoading);
  toggle_like(postLikeBtn, isLoading);
  edit_post(editBtn, isLoading);
  get_post_details(POSTS_CONTAINER);
});

function get_post_details(container) {
    if (container) {
    container.addEventListener("click", (e) => {
      const postDiv = e.target.closest(".post");
      if (!postDiv) return;
      // If the click was on an interactive element, don't navigate
      if (e.target.closest("a") || e.target.closest("button") || e.target.closest("input") || e.target.closest("textarea")) return;
      const postId = postDiv.getAttribute("data-post-id");
      if (postId) {
        window.location.href = `/post/${postId}`;
      }
    });
  }
}

function fetchInifiteScroll(counter, starts, ends, container, isLoading) {
    if (isLoading) return; // evita peticiones simultáneas 
    isLoading = true;

    showLoader("post");
    fetch('posts?starts=' + String(starts) + '&ends=' + String(ends), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
    .then(data => {
      if (data.status == "success") {
        data.posts.forEach( post => add_post(post, false, "bottom", container))
        counter = ends + 1
        isLoading = false;
      }
      hiddeLoader("post");
    })
  }

function add_post(post, is_author = false, position = "bottom", POSTS_CONTAINER) {
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
    LIKE_BTN.id = "postLikeBtn";

    USERNAME_A.innerHTML = `<strong>${ post.author }</strong> says:`;
    USERNAME_A.href = `/profile/${ post.author }`;
    CONTENT_P.textContent = post.content;
    LIKE_BTN.textContent = "Like";
    LIKES_P.innerHTML = `Likes: <span class="likes-count">${ post.likes_count }</span>`;
    TIMESTAMP.textContent = `${ post.formatted_created_at }`;

    POST_DIV.setAttribute("data-post-id", post.id);
    POST_DIV.appendChild(USERNAME_A);
    POST_DIV.appendChild(CONTENT_P);
    POST_DIV.appendChild(TIMESTAMP);
    POST_DIV.appendChild(LIKES_P);
    POST_DIV.appendChild(LIKE_BTN);

    if (is_author) {
        const EDIT_BTN = document.createElement("button");
        EDIT_BTN.textContent = "Edit";
        EDIT_BTN.id = "editBtn";
        POST_DIV.appendChild(EDIT_BTN);
    }

    // 🔹 Aquí decides si va arriba o abajo
    if (position === "top") {
        POSTS_CONTAINER.prepend(POST_DIV);   // nuevo post → arriba
    } else {
        POSTS_CONTAINER.appendChild(POST_DIV); // infinite scroll → abajo
    }

    POSTS_CONTAINER.style.display = "block";

    // Actualizar referencias
    edit_post(POST_DIV.querySelectorAll("#editBtn"));
    toggle_like(POST_DIV.querySelectorAll("#postLikeBtn"));
}

function create_new_post(postForm, container, isLoading) {
  if (postForm) {
      postForm.addEventListener("submit", (e) => {
      console.log("algo");
      e.preventDefault();
      if (isLoading == true) return;
      isLoading = true;
      showLoader("form");
      const formData = new FormData(postForm);
      fetch("/post/new_post", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            const post = data.new_post;
            // Clear the textarea
            postForm.reset();
            isLoading = false;
            add_post(post, data.is_author, "top", container);
          }
          hiddeLoader("form");
      });
    });
  }
}

function toggle_like(btn, isLoading) {
    if (btn) {
    btn.forEach((button) => {
      button.addEventListener("click", (e) => {
        if (isLoading) return;
        isLoading = true;
        const postDiv = e.target.closest(".post");
        const postId = postDiv.getAttribute("data-post-id");
        showBtnLoader(e.target);
        fetch(`/post/like`, {
          method: "POST",
          body: JSON.stringify({ 
            post_id: postId,
            content_type: "post"
          }),
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
              hiddeBtnLoader(e.target, (data.action === "liked") ? "Unlike" : "Like")
            }
            isLoading = false;
          });
      });
    });
  }
}

function edit_post(btn, isLoading) {
    if (btn) {
    btn.forEach((button) => {
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
          showLoader(e.target.closest.dataset.loader);
          isLoading = true;

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
              hiddeLoader(e.target.closest.dataset.loader);
              isLoading = false;
            })
            .catch((error) => {
              console.error("Error updating post:", error);
            });
          });
      });
    });
  }
}