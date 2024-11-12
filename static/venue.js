<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticketmaster Event Seat Map Test</title>
</head>
<body>
    <h1>Ticketmaster Event Seat Map Test</h1>
    
    <!-- Input field and search button -->
    <label for="venue-input">Enter Venue Name:</label>
    <input type="text" id="venue-input" placeholder="e.g., Madison Square Garden">
    <button id="search-venue">Search</button>

    <!-- Placeholder for seat map image -->
    <div id="result" style="margin-top: 20px;">
        <img id="venue-map" src="" alt="Venue Seat Map" style="max-width: 500px; display: none;">
        <p id="message"></p>
    </div>

    <script>
        document.getElementById('search-venue').addEventListener('click', function() {
            const venueName = document.getElementById('venue-input').value.trim();
            if (!venueName) {
                alert('Please enter a venue name.');
                return;
            }
            searchEventsByVenue(venueName);
        });

        async function searchEventsByVenue(venueName) {
            const apiKey = 'bv3fIbkBp4hjBLjVOBBessILI48oEYGG'; // <--- Replace with your Ticketmaster API key
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
    </script>
</body>
</html>

