document.addEventListener('DOMContentLoaded', () => {
    const likeButton = document.querySelector('.btn-like');
    if (likeButton) {
        likeButton.addEventListener('click', async function () {
            const button = this;
            const spinner = document.createElement('span');
            spinner.className = 'spinner-border spinner-border-sm me-2';
            const icon = button.querySelector('i');
            const text = button.querySelector('span');
            const itemId = button.getAttribute('data-id');
            const isFavorited = button.getAttribute('data-favorited') === 'true';

            button.disabled = true;
            button.insertBefore(spinner, icon);
            icon.classList.add('d-none');

            try {
                const response = await fetch('/favorites/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId })
                });

                const data = await response.json();

                if (response.ok) {
                    button.setAttribute('data-favorited', data.favorited);
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
                console.error('Request failed:', err);
            } finally {
                button.disabled = false;
                spinner.remove();
                icon.classList.remove('d-none');
            }
        });
    }
});
