
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



//Confirm before deleting a listing
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


