document.addEventListener('DOMContentLoaded', () => {
    // Image Preview
    const imageInput = document.getElementById('images');
    imageInput.addEventListener('change', function (event) {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'mt-3 d-flex flex-wrap gap-2';
        const files = event.target.files;

        // Generate image previews
        [...files].forEach((file) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'img-thumbnail';
                img.style.width = '100px';
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
        });

        event.target.parentElement.appendChild(previewContainer);
    });

    // Autofill Location
    const locationInput = document.getElementById('location');
    locationInput.addEventListener('focus', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;

                    // Fetch location details using geocoding API
                    fetch(`https://geocode.xyz/${latitude},${longitude}?geoit=json`)
                        .then((response) => response.json())
                        .then((data) => {
                            locationInput.value = `${data.city}, ${data.country}`;
                        })
                        .catch((error) => console.error('Geolocation error:', error));
                },
                (error) => {
                    console.error('Geolocation not available:', error);
                }
            );
        }
    });
});
