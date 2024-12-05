document.addEventListener('DOMContentLoaded', () => {
    // Wait until the DOM content is fully loaded before executing the script

    const likeButton = document.querySelector('.btn-like'); 

    if (likeButton) {
        // Check if the button exists to avoid errors when it is not present

        likeButton.addEventListener('click', async function () {
            // Add a click event listener to handle the "Like" toggle functionality

            const button = this; 
            const spinner = document.createElement('span'); 
            // Create a spinner element to show loading state
            spinner.className = 'spinner-border spinner-border-sm me-2'; 
            // Add Bootstrap spinner classes for styling

            const icon = button.querySelector('i'); 
            const text = button.querySelector('span'); 
            const itemId = button.getAttribute('data-id'); 
            // Retrieve the item ID from the button's data attribute
            const isFavorited = button.getAttribute('data-favorited') === 'true'; 
            // Check if the item is currently favorited

            button.disabled = true; 
            // Disable the button to prevent multiple clicks
            button.insertBefore(spinner, icon); 
            icon.classList.add('d-none'); 
            // Hide the icon during the loading state

            try {
                // Make an asynchronous request to toggle the favorite state
                const response = await fetch('/favorites/toggle', {
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ item_id: itemId }) 
                    // Send the item ID as JSON data
                });

                const data = await response.json(); 
                // Parse the JSON response from the server

                if (response.ok) {
                    button.setAttribute('data-favorited', data.favorited); 
                    // Update the button's data attribute with the new favorite state

                    if (data.favorited) {
                        icon.className = 'bi bi-heart-fill me-2'; 
                        text.textContent = 'Liked'; 
                    } else {
                        icon.className = 'bi bi-heart me-2'; 
                        text.textContent = 'Like'; 
                    }
                } else {
                    console.error('Error:', data.error);
                }
            } catch (err) {
                // Handle any errors during the fetch request
                console.error('Request failed:', err);
            } finally {
                // Restore the button's original state after the operation is complete
                button.disabled = false; 
                spinner.remove(); 
                icon.classList.remove('d-none'); 
            }
        });
    }
});
