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

async function searchEventsByVenue(venueName) {
    const apiKey = 'bv3fIbkBp4hjBLjVOBBessILI48oEYGG'; // Replace with your Ticketmaster API key
    try {
        const response = await fetch(`https://app.ticketmaster.com/discovery/v2/events.json?keyword=${encodeURIComponent(venueName)}&apikey=${apiKey}`);
        console.log("Response received:", response);

        const data = await response.json();
        console.log(data);

        if (data._embedded && data._embedded.events.length > 0) {
            const event = data._embedded.events[0];
            // console.log("Event Data:", event);
            displaySeatMapFromEvent(event);
        } else {
            document.getElementById('venue-map').style.display = 'none';
            // document.getElementById('message').textContent = `No events found for "${venueName}".`;
        }
    } catch (error) {
        console.error("Error fetching event data:", error);
        // document.getElementById('message').textContent = "There was an error retrieving the event information.";
    }
}

// Function to display the seat map from event data
function displaySeatMapFromEvent(event) {
    if (event.seatmap && event.seatmap.staticUrl) {
        if (event._embedded && event._embedded.venues && event._embedded.venues[0] && event._embedded.venues[0].name) {
            document.getElementById('venue-title').innerText = event._embedded.venues[0].name;
        }
        document.getElementById('venue-map').src = event.seatmap.staticUrl;
        document.getElementById('venue-map').style.display = 'block';
        // document.getElementById('message').textContent = `Seat map for ${event.name}`;
    } else {
        document.getElementById('venue-map').style.display = 'none';
        // document.getElementById('message').textContent = "Seat map not available for this event.";
    }
}

// Event listener for "Seat POV Finder" button to display seat images
document.querySelector('.seat-finder .btn-warning').addEventListener('click', function() {
    // Show the seat POV section and images only after clicking "Seat POV Finder"
    document.getElementById('seat-pov').style.display = 'flex';
    const venueName = document.getElementById('venue-name').value.trim();
    // First, try to fetch venue images from the database
    fetchVenueImages(venueName).then(images => {
        // If there are images in the database, use them
        if (images.length > 0) {
            updateVenueUI(images);
        } else {
            // If no images are found, use the default images
            useDefaultImages();
        }
    }).catch(error => {
        console.error('Error fetching venue images:', error);
        useDefaultImages();
    });
});

// Function to use default images when no images are available from the database
function useDefaultImages() {
    document.getElementById('seat-view-1').style.display = 'block';
    document.getElementById('seat-view-2').style.display = 'block';
    document.getElementById('seat-view-3').style.display = 'block';
}

let formData = null;
document.getElementById('upload-image').addEventListener('change', function(event) {
    const file = event.target.files[0]; // Get the uploaded file
    if (file) {
        // Create a FormData object to send the image to the Flask server
        formData = new FormData();
        formData.append('image', file);
    }
});


document.getElementById('upload-pov').addEventListener('click', function () {
    const venueName = document.getElementById('venue-name').value.trim();
    const section = document.getElementById('section-number').value.trim();
    const row = document.getElementById('row-number').value.trim();
    const seat = document.getElementById('seat-number').value.trim();
    
    if (venueName && section && row && seat && formData) {
        formData.append('venue_name', venueName);
        formData.append('section', section);
        formData.append('row', row);
        formData.append('seat', seat);

        addVenueImage(formData);
    } else {
        alert('Please fill out all fields before uploading.');
    }
});



async function fetchVenueImages(venueName) {
    try {
        const response = await fetch(`/get_venue_images?venue_name=${encodeURIComponent(venueName)}`);
        const data = await response.json();

        if (!response.ok) {
            console.error('Server Error:', data.error || data.message || 'Unknown error occurred');
            return []; // Return an empty array for errors
        }

        console.log('Fetched Venue Images:', data.image_urls); // Debug log
        return data.image_urls || []; // Return the images if available
    } catch (error) {
        console.error('Network Error:', error);
        return []; // Return an empty array for network errors
    }
}


// Function to update the UI with fetched venue images
function updateVenueUI(images) {
    const venueMapContainer = document.getElementById('seat-pov');
    venueMapContainer.innerHTML = ''; // Clear any previous content

    images.forEach(image => {
        const imgElement = document.createElement('img');
        imgElement.src = image.image_url; // Use the `image_url` field from your Supabase database
        imgElement.alt = `Image for ${image.venue_name}`;
        imgElement.classList.add('venue-image');
        venueMapContainer.appendChild(imgElement);
    });
}

// Function to add a new venue image via the Flask backend
async function addVenueImage(formData) {
    fetch('/add_venue_image', {
        method: 'POST',
        body: formData // Send the FormData object to Flask
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message); // Handle the response
        }
    })
    .catch(error => {
        console.error('Error uploading image:', error);
    });

    const venueName = document.getElementById('venue-name').value.trim();
    fetchVenueImages(venueName);
}