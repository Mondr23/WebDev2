document.addEventListener('DOMContentLoaded', () => {

    // Chart for Listings by Category
    const categoryCtx = document.getElementById('listingsByCategoryChart').getContext('2d');
    // Get the context for the "Listings by Category" chart
    const listingsByCategoryChart = new Chart(categoryCtx, {
        type: 'bar', // Specify the chart type as a bar chart
        data: {
            labels: categoryLabels, // Labels representing different categories
            datasets: [{
                label: 'Number of Listings', // Legend for the dataset
                data: categoryCounts, // Data points for each category
                backgroundColor: 'rgba(54, 162, 235, 0.7)', // Bar color with transparency
                borderColor: 'rgba(54, 162, 235, 1)', // Border color for the bars
                borderWidth: 1 // Thickness of the bar borders
            }]
        },
        options: {
            responsive: true, // Make the chart responsive to window size
            plugins: {
                legend: { display: true }, // Display the legend
                title: { display: true, text: 'Listings by Category' } // Title for the chart
            },
            scales: {
                x: { title: { display: true, text: 'Categories' } }, // Label for the x-axis
                y: { beginAtZero: true, title: { display: true, text: 'Number of Listings' } } // Label and range for the y-axis
            }
        }
    });

    // Chart for Listings by Location
    const locationCtx = document.getElementById('listingsByLocationChart').getContext('2d');
    // Get the context for the "Listings by Location" chart
    const listingsByLocationChart = new Chart(locationCtx, {
        type: 'bar', // Specify the chart type as a bar chart
        data: {
            labels: locationLabels, // Labels representing different locations
            datasets: [{
                label: 'Number of Listings', // Legend for the dataset
                data: locationCounts, // Data points for each location
                backgroundColor: 'rgba(153, 102, 255, 0.7)', // Bar color with transparency
                borderColor: 'rgba(153, 102, 255, 1)', // Border color for the bars
                borderWidth: 1 // Thickness of the bar borders
            }]
        },
        options: {
            responsive: true, // Make the chart responsive to window size
            plugins: {
                legend: { display: true }, // Display the legend
                title: { display: true, text: 'Listings by Location' } // Title for the chart
            },
            scales: {
                x: { title: { display: true, text: 'Locations' } }, // Label for the x-axis
                y: { beginAtZero: true, title: { display: true, text: 'Number of Listings' } } // Label and range for the y-axis
            }
        }
    });
});
