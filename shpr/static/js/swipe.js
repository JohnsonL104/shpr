function completeItem(itemId, callback) {
  fetch(`/${itemId}/complete`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  }).then(response => callback(response));
}

document.addEventListener("DOMContentLoaded", () => {
  const items = document.querySelectorAll(".swipe-item");

  items.forEach(item => {
    let startX, currentX, isSwiping = false;
    let completeButton = item.querySelector(".complete-button");
    if(completeButton){
      completeButton.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation(); // Prevent triggering swipe event
        const itemId = item.dataset.id;
        completeItem(itemId, (response) => {
          if (response.ok) {
            item.remove()
          } else {
            alert("Failed to complete the item.");
          }
        });
      });
    }
    else{
      item.addEventListener("touchstart", (e) => {
        startX = e.touches[0].clientX;
        isSwiping = true;
        item.style.transition = "none"; // Disable transition during swipe
      });

      item.addEventListener("touchmove", (e) => {
        if (!isSwiping) return;
        currentX = e.touches[0].clientX;
        const deltaX = currentX - startX;
        if (deltaX < 0) { // Only allow left swipe
          item.style.transform = `translateX(${deltaX}px)`;
        }
      });

      item.addEventListener("touchend", (e) => {
        if (!isSwiping) return;
        isSwiping = false;
        const endX = e.changedTouches[0].clientX;
        const deltaX = endX - startX;

        if (deltaX < -100) { // Swipe left threshold
          const itemId = item.dataset.id;

          completeItem(itemId, (response) => {
            if (response.ok) {
              item.style.transition = "transform 0.3s ease-out"; // Smooth removal
              item.style.transform = "translateX(-100%)";
              setTimeout(() => item.remove(), 300); // Remove after animation
            } else {
              alert("Failed to complete the item.");
              item.style.transform = ""; // Reset position
            }
          });
        } else {
          item.style.transition = "transform 0.3s ease-out"; // Smooth reset
          item.style.transform = ""; // Reset position
        }
      });
    }
  });
});
