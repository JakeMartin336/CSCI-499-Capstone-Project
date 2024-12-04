// Function to fetch venue images from the Flask backend
async function fetchVenueImages(venueName) {
    try {
        const response = await fetch(`/get_venue_images?venue_name=${encodeURIComponent(venueName)}`);
        const data = await response.json();
        
        if (response.ok) {
            console.log('Venue images:', data);
            updateVenueUI(data); // Update the UI with fetched images
        } else {
            console.error('Error:', data.message);
            document.getElementById('message').textContent = data.message || "Error fetching venue images.";
        }
    } catch (error) {
        console.error('Error fetching venue images:', error);
        document.getElementById('message').textContent = "Unable to retrieve venue images. Please try again.";
    }
}

// Function to update the UI with fetched venue images
function updateVenueUI(images) {
    const venueMapContainer = document.getElementById('venue-map-container');
    venueMapContainer.innerHTML = ''; // Clear any previous content

    if (images.length > 0) {
        images.forEach(image => {
            const imgElement = document.createElement('img');
            imgElement.src = image.image_url; // Use the `image_url` field from your Supabase database
            imgElement.alt = `Image for ${image.venue_name}`;
            imgElement.classList.add('venue-image');
            venueMapContainer.appendChild(imgElement);
        });
        document.getElementById('message').textContent = `Found ${images.length} images for the venue.`;
    } else {
        document.getElementById('message').textContent = "No images found for this venue.";
    }
}

// Function to add a new venue image via the Flask backend
async function addVenueImage(imageData) {
    try {
        const response = await fetch('/add_venue_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(imageData),
        });
        const data = await response.json();

        if (response.ok) {
            console.log(data.message);
            document.getElementById('message').textContent = data.message;
        } else {
            console.error('Error:', data.error);
            document.getElementById('message').textContent = data.error || "Error adding venue image.";
        }
    } catch (error) {
        console.error('Error adding venue image:', error);
        document.getElementById('message').textContent = "Unable to add venue image. Please try again.";
    }
}

// Event listener for the search button
document.getElementById('search-btn').addEventListener('click', function () {
    const venueName = document.getElementById('venue-name').value.trim();
    if (venueName) {
        document.getElementById('venue-title').innerText = venueName;
        document.getElementById('venue-header').style.display = 'block';
        document.getElementById('map-section').style.display = 'block';

        // Call the fetchVenueImages function to get venue images
        fetchVenueImages(venueName);
    } else {
        alert('Please enter a venue name.');
    }
});

// Event listener for adding a new venue image
document.getElementById('upload-pov').addEventListener('click', function () {
    const venueName = document.getElementById('venue-name').value.trim();
    const section = document.getElementById('section-number').value.trim();
    const row = document.getElementById('row-number').value.trim();
    const seat = document.getElementById('seat-number').value.trim();
    const imageUrl = document.getElementById('image-url').value.trim();

    if (venueName && section && row && seat && imageUrl) {
        const imageData = {
            venue_name: venueName,
            section: section,
            row: row,
            seat: seat,
            image_url: imageUrl
        };

        // Call the addVenueImage function to add the new image
        addVenueImage(imageData);
    } else {
        alert('Please fill out all fields before uploading.');
    }
});

