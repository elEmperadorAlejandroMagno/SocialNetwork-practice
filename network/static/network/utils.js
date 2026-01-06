export function showLoader(name) { 
  const loader = document.querySelector(`[data-loader="${name}"]`); 
  if (loader) loader.style.display = "block"; 
} 
export function hiddeLoader(name) { 
  const loader = document.querySelector(`[data-loader="${name}"]`); 
  if (loader) loader.style.display = "none"; 
}

export function showBtnLoader(btn) {
  btn.disabled = true;
  btn.textContent = "Loading...";
}

export function hiddeBtnLoader(btn, content="") {
  btn.disabled = false;
  btn.textContent = content;
}

export function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = "block";
}

export function hiddeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = "none";
}

export function fetchCommentLike(likeBtn) {
  if (likeBtn) {
    const commentEl = likeBtn.closest('.comment');
    const commentId = commentEl.getAttribute('data-id');
    const likeCount = commentEl.querySelector('.likes-count');
    showBtnLoader(likeBtn);

    fetch('/post/comment/like', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
      },
      body: JSON.stringify({ comment_id: commentId, content_type: 'comment' }),
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        likeCount.textContent = data.likes_count;
        hiddeBtnLoader(likeBtn, (data.action === 'liked') ? 'Unlike' : 'Like');
      } else {
        hiddeBtnLoader(likeBtn, "Like");
      }
    })
    .catch(err => console.error(err));
    return;
  }
}