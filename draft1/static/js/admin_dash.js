document.addEventListener('DOMContentLoaded', () => {
    // Chart for Listings by Category
    const categoryCtx = document.getElementById('listingsByCategoryChart').getContext('2d');
    const listingsByCategoryChart = new Chart(categoryCtx, {
        type: 'bar',
        data: {
            labels: categoryLabels, // Use the variables initialized above
            datasets: [{
                label: 'Number of Listings',
                data: categoryCounts,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
                title: { display: true, text: 'Listings by Category' }
            },
            scales: {
                x: { title: { display: true, text: 'Categories' } },
                y: { beginAtZero: true, title: { display: true, text: 'Number of Listings' } }
            }
        }
    });

    // Chart for Listings by Location
    const locationCtx = document.getElementById('listingsByLocationChart').getContext('2d');
    const listingsByLocationChart = new Chart(locationCtx, {
        type: 'bar',
        data: {
            labels: locationLabels,
            datasets: [{
                label: 'Number of Listings',
                data: locationCounts,
                backgroundColor: 'rgba(153, 102, 255, 0.7)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true },
                title: { display: true, text: 'Listings by Location' }
            },
            scales: {
                x: { title: { display: true, text: 'Locations' } },
                y: { beginAtZero: true, title: { display: true, text: 'Number of Listings' } }
            }
        }
    });
});
