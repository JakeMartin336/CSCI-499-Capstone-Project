// Show sections when the search button is clicked
document.getElementById('search-btn').addEventListener('click', function() {
    const venueName = document.getElementById('venue-name').value.trim();

    if (venueName) {
        document.getElementById('venue-title').innerText = venueName;
        document.getElementById('venue-header').style.display = 'block';
        document.getElementById('map-section').style.display = 'block';
        document.getElementById('seat-finder').style.display = 'block';
        document.getElementById('seat-pov').style.display = 'none'; // Ensure seat POV section is hidden initially
        
        // Call the function to search for events and display seat map
        searchEventsByVenue(venueName);
    } else {
        alert('Please enter a venue name.');
    }
});

// Function to search for events by venue name
async function searchEventsByVenue(venueName) {
    const apiKey = 'bv3fIbkBp4hjBLjVOBBessILI48oEYGG'; // Replace with your Ticketmaster API key
    try {
        const response = await fetch(`https://app.ticketmaster.com/discovery/v2/events.json?keyword=${encodeURIComponent(venueName)}&apikey=${apiKey}`);
        const data = await response.json();

        console.log(data); // Log the data to see the response structure

        if (data._embedded && data._embedded.events.length > 0) {
            const event = data._embedded.events[0];
            console.log("Event Data:", event);
            displaySeatMapFromEvent(event);
        } else {
            document.getElementById('venue-map').style.display = 'none';
            document.getElementById('message').textContent = `No events found for "${venueName}".`;
        }
    } catch (error) {
        console.error("Error fetching event data:", error);
        document.getElementById('message').textContent = "There was an error retrieving the event information.";
    }
}

// Function to display the seat map from event data
function displaySeatMapFromEvent(event) {
    if (event.seatmap && event.seatmap.staticUrl) {
        document.getElementById('venue-map').src = event.seatmap.staticUrl;
        document.getElementById('venue-map').style.display = 'block';
        document.getElementById('message').textContent = `Seat map for ${event.name}`;
    } else {
        document.getElementById('venue-map').style.display = 'none';
        document.getElementById('message').textContent = "Seat map not available for this event.";
    }
}

// Event listener for "Seat POV Finder" button to display seat images
document.querySelector('.seat-finder .btn-warning').addEventListener('click', function() {
    // Show the seat POV section and images only after clicking "Seat POV Finder"
    document.getElementById('seat-pov').style.display = 'flex';
    document.getElementById('seat-view-1').style.display = 'block';
    document.getElementById('seat-view-2').style.display = 'block';
    document.getElementById('seat-view-3').style.display = 'block';
});

// Simulate POV upload button
document.getElementById('upload-pov').addEventListener('click', function() {
    const section = document.getElementById('section-number').value;
    const row = document.getElementById('row-number').value;
    const seat = document.getElementById('seat-number').value;

    if (section && row && seat) {
        alert(`Seat POV for Section: ${section}, Row: ${row}, Seat: ${seat} uploaded!`);
        // Logic to fetch and display seat views can go here
    } else {
        alert('Please fill in all the fields.');
    }
});
