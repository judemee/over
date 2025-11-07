function openModal(src) {
  const modal = document.getElementById("imageModal");
  const modalImg = document.getElementById("modalImg");
  modal.style.display = "block";
  modalImg.src = src;
}

function closeModal() {
  document.getElementById("imageModal").style.display = "none";
}

// Example: Popup Ad (You can trigger this later)
function showPopupAd() {
  alert("🔥 Special Offer: Buy 2 Packs and Get Free Shipping!");
}
