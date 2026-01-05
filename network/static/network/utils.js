export function showLoader(name) { 
  const loader = document.querySelector(`[data-loader="${name}"]`); 
  if (loader) loader.style.display = "block"; 
} 
export function hideLoader(name) { 
  const loader = document.querySelector(`[data-loader="${name}"]`); 
  if (loader) loader.style.display = "none"; 
}

export function showBtnLoader(btn) {
  btn.disabled = true;
  btn.textContent = "Loading...";
}

export function hideBtnLoader(btn, content="") {
  btn.disabled = false;
  btn.textContent = content;
}