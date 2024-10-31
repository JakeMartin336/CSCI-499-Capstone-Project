document.getElementById('search-btn').addEventListener('click', function() {
    const venueName = document.getElementById('venue-name').value;

    if (venueName) {
        // Display venue name in header and show the other sections
        document.getElementById('venue-title').innerText = venueName;
        document.getElementById('venue-header').style.display = 'block';
        document.getElementById('map-section').style.display = 'block';
        document.getElementById('seat-finder').style.display = 'block';
        document.getElementById('seat-pov').style.display = 'flex'; // Display seat POV section
        
        // You could dynamically change the map or other elements here based on the venueName if needed
    } else {
        alert('Please enter a venue name.');
    }
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
