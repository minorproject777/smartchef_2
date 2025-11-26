document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".review-form form");
  const reviewsBox = document.querySelector(".reviews");
  const MAX = 3; // show only 3 reviews

  form.addEventListener("submit", (e) => {
    e.preventDefault(); // stop page reload

    const name = form.querySelector("input").value.trim();
    const comment = form.querySelector("textarea").value.trim();

    if (!name || !comment) {
      alert("Please enter both name and comment!");
      return;
    }

    // Make a new review
    const card = document.createElement("div");
    card.className = "review-card";
    card.innerHTML = `<p>"${comment}"</p><h4>– ${name}</h4>`;

    // Insert it just after the heading
    reviewsBox.insertBefore(card, reviewsBox.querySelector(".review-card"));

    // If more than MAX reviews, delete the last one
    const allReviews = reviewsBox.querySelectorAll(".review-card");
    if (allReviews.length > MAX) {
      reviewsBox.removeChild(allReviews[allReviews.length - 1]);
    }

    form.reset(); // clear form
    alert("Thanks for your review!");
  });
});


document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const href = btn.getAttribute("href");

    // Only prevent default for truly dummy links
    if (!href || href.trim() === "#" || href.trim() === "") {
      e.preventDefault();
      console.log("Dummy link clicked, no navigation.");
    } else {
      // For real links, allow normal navigation
      // No need to call preventDefault
      // Optional: you can log the navigation
      console.log("Navigating to:", href);
    }
  });
});


