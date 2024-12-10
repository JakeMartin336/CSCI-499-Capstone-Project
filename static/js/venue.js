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
        const seatPovContainer = document.getElementById('seat-pov');
        seatPovContainer.innerHTML = '';
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
document.querySelector('.seat-finder .btn-warning').addEventListener('click', async function() {
    const venueName = document.getElementById('venue-name').value.trim();
    const section = document.getElementById('section-number').value.trim();
    const row = document.getElementById('row-number').value.trim();
    const seat = document.getElementById('seat-number').value.trim();

    if (!venueName || !section || !row || !seat) {
        alert('Please fill out all fields to search for a seat POV.');
        return;
    }

    const images = await fetchSeatPOV(venueName, section, row, seat);
    if (images.length > 0) {
        updateVenueUI(images);
    } else {
        Swal.fire({
            icon: 'error',
            title: 'No Images Found',
            text: 'We couldn\'t find any images for the specified seat. Please try again with different details.',
            confirmButtonText: 'OK'
        });
    }
});

async function fetchSeatPOV(venueName, section, row, seat) {
    console.log(`Fetching seat POV with: Venue=${venueName}, Section=${section}, Row=${row}, Seat=${seat}`); // Log inputs

    // Show the SweetAlert loading notification while fetching data
    Swal.fire({
        title: 'Fetching POV...',
        text: 'Please wait while we load the seat image.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    try {
        const response = await fetch(`/get_venue_images?venue_name=${encodeURIComponent(venueName)}&section=${encodeURIComponent(section)}&row=${encodeURIComponent(row)}&seat=${encodeURIComponent(seat)}`);
        const data = await response.json();

        console.log('Response from /get_venue_images:', data); 

        if (!response.ok) {
            console.error('Error:', data.error || data.message);
            Swal.close(); 

            Swal.fire({
                icon: 'error',
                title: 'No images found.',
                text: data.error || 'We couldn\'t find any images matching your criteria. Please try again with different details.',
                confirmButtonText: 'Retry'
            });
            return [];
        }

        // Successfully fetched data
        Swal.close(); 
        Swal.fire({
            icon: 'success',
            title: 'POV Fetched Successfully!',
            text: 'Seat POV images have been loaded.',
            confirmButtonText: 'OK'
        });

        return data.image_urls || [];
    } catch (error) {
        console.error('Network Error:', error);
        Swal.close(); 


        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: 'There was an error connecting to the server. Please try again later.',
            confirmButtonText: 'Retry'
        });

        return [];
    }
}



function updateVenueUI(images) {
    const seatPovContainer = document.getElementById('seat-pov');
    console.log('Initial display state:', seatPovContainer.style.display);

    // Clear previous content
    seatPovContainer.innerHTML = '';

    if (images.length === 0) {
        seatPovContainer.textContent = 'No images found for the specified seat.';
        seatPovContainer.style.display = 'block'; // Make container visible even if no images
        console.log('No images found. Display set to block.');
        return;
    }

    // Add images to the container
    images.forEach(image => {
        const imgElement = document.createElement('img');
        imgElement.src = image.image_url;
        imgElement.alt = 'Seat POV for the specified seat';
        imgElement.classList.add('venue-image');
        seatPovContainer.appendChild(imgElement);
    });

    // Make the container visible
    seatPovContainer.style.display = 'block';
    seatPovContainer.classList.add('active');
    console.log('Images added and display set to block.');
}






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


// Function to add a new venue image via the Flask backend
async function addVenueImage(formData) {
    Swal.fire({
        title: 'Uploading...',
        text: 'Please wait while we upload your image.',
        icon: 'info',
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading(); 
        }
    });
    fetch('/add_venue_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Close the loading SweetAlert
        Swal.close();

        // Show a success message if upload was successful
        if (data.message) {
            Swal.fire({
                icon: 'success',
                title: 'Upload Successful!',
                text: data.message,
                confirmButtonText: 'OK'
            });
        }
    })
    .catch(error => {
        // Close the loading SweetAlert
        Swal.close();

        // Show an error message in case of failure
        Swal.fire({
            icon: 'error',
            title: 'Upload Failed',
            text: 'There was an error uploading the image. Please try again.',
            confirmButtonText: 'Retry'
        });
        console.error('Error uploading image:', error);
    });

    // Fetch venue images after upload
    const venueName = document.getElementById('venue-name').value.trim();
    fetchVenueImages(venueName);
}
