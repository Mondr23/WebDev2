// JavaScript file for custom interactions and functionality

// Smooth scrolling for anchor links
document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll("a[href^='#']");
    links.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });
});

// Dynamic alert close functionality
document.addEventListener("DOMContentLoaded", function () {
    const alertCloseButtons = document.querySelectorAll(".alert .btn-close");
    alertCloseButtons.forEach(button => {
        button.addEventListener("click", function () {
            this.closest(".alert").remove();
        });
    });
});

// Example: AJAX request for favoriting a listing (requires a corresponding backend route)
function favoriteListing(listingId) {
    fetch(`/favorite/${listingId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        }
    })
    .then(response => {
        if (response.ok) {
            alert("Listing added to favorites!");
        } else {
            alert("Failed to add listing to favorites.");
        }
    })
    .catch(error => console.error("Error:", error));
}

// Utility: Get CSRF token from meta tag
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : "";
}

// Example: Confirm before deleting a listing
function confirmDelete(listingId) {
    const confirmed = confirm("Are you sure you want to delete this listing?");
    if (confirmed) {
        fetch(`/delete-listing/${listingId}`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => {
            if (response.ok) {
                alert("Listing deleted successfully.");
                location.reload();
            } else {
                alert("Failed to delete listing.");
            }
        })
        .catch(error => console.error("Error:", error));
    }
}

// Real-time character count for textarea fields (e.g., message form)
document.addEventListener("DOMContentLoaded", function () {
    const textareas = document.querySelectorAll("textarea[maxlength]");
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute("maxlength");
        const counter = document.createElement("small");
        counter.textContent = `0 / ${maxLength} characters`;
        textarea.parentNode.appendChild(counter);

        textarea.addEventListener("input", function () {
            counter.textContent = `${textarea.value.length} / ${maxLength} characters`;
        });
    });
});
