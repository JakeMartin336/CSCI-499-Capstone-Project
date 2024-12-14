async function showMatchingSection() {
    const matchingSection = document.querySelector('.matching');
    matchingSection.style.display = 'none';

    await generateNewBuddy();  

    matchingSection.style.display = 'block';
}

async function generateNewBuddy() {
    try {
        const response = await fetch('/api/buddy/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

       

        if (!response.ok) {
            try {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Network response was not ok');
            } catch (jsonError) {
                // If JSON parsing fails, throw error
                throw new Error('Network response was not ok');
            }
        }

        const data = await response.json();
        console.log("Im data", data)
        const recommendedUserIds = data.recommended_user_ids.id;
        console.log(recommendedUserIds)
        // Only select one
        if (recommendedUserIds) {
            console.log(recommendedUserIds)
            await updateCardWithNewUser(recommendedUserIds);  // wait for the update
            
        } else {
            alert('No new recommendations available!');
        }

    } catch (error) {
        console.error('Error fetching new buddy:', error);
    }
}
let currentCardID = null;
async function updateCardWithNewUser(userId) {
    try {
        // Call the backend to get user information
        const response = await fetch(`/api/user-info/${userId}`);
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        currentCardID = userId;

        const userData = await response.json();
        let formattedGenres = '';
        if (Array.isArray(userData.music_genre) && userData.music_genre.length > 0) {
            formattedGenres = userData.music_genre.join(', ');  
        } else {
            formattedGenres = 'Not specified'; 
        }

        // Format the card content with user information or we can use the explanation to convince ppl that they should "say hi" to this person :)
        const formattedText = `Hey, my name is ${userData.user_name}! I am from ${userData.user_location}, and I love listening to ${formattedGenres}.`;

        console.log("I am userData", userData)

        // Update card content with the fetched user data
        document.querySelector('.card-title').textContent = userData.user_name || 'Unknown User';
        document.querySelector('.card-text').textContent = formattedText || 'No description available.';
        
        if (userData.image_url) {
            document.querySelector('#card-img').src = userData.image_url;
        }

    } catch (error) {
        console.error('Error updating card content:', error);
    }
}





let currentIndex = 0;

document.addEventListener("DOMContentLoaded", function () {
    updateConcertDetails(currentIndex);
    document.getElementById('prevTicket').style.display = "none";
});

function updateConcertDetails(index) {
    const concert = allConcertsData[index];
    document.getElementById("concertImage").src = concert.thumbnail || "";
    document.getElementById("concertName").textContent = concert.name || "No Name";
    document.getElementById("concertDescription").textContent = concert.description || "No Description";
    document.getElementById("concertTime").textContent = concert.start_time || "No Time";

    document.getElementById('concertVenueName').innerText = concert.venue_name;
    document.getElementById('concertVenueAddress').innerText = concert.venue_address;

    const ticketLinks = document.getElementById('ticketLinks');
    ticketLinks.innerHTML = '';
    let concertTickets = concert.ticket_links
    concertTickets.forEach(function(ticket) {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${ticket.source}:</strong> <a href="${ticket.link}" target="_blank">${ticket.link}</a>`;
        ticketLinks.appendChild(li);
    });
};

function showConcertIndex(direction) { 
    if (direction === 'next' && currentIndex < allConcertsData.length - 1) {
        currentIndex++;
    }
    if (direction === 'previous' && currentIndex > 0) {
        currentIndex--;
    }

    if (currentIndex === 0) {
        document.getElementById('prevTicket').style.display = "none";
    } else {
        document.getElementById('prevTicket').style.display = "block";
    }

    if (currentIndex === allConcertsData.length - 1) {
        document.getElementById('nextTicket').style.display = "none";
    } else {
        document.getElementById('nextTicket').style.display = "block";
    }

    updateConcertDetails(currentIndex);
}



let currentInfo = null;
function showInfo(type) {
    var venueInfo = document.getElementById("venueInfo");
    var ticketInfo = document.getElementById("ticketInfo");
    var infoButton = document.getElementById("infoButton");

    // Hide both sections by default
    venueInfo.style.display = "none";
    ticketInfo.style.display = "none";

    // Toggle the selected information section
    if (type === "venue") {
        if (currentInfo === "venue") {
            currentInfo = null; // If the same section is clicked again, hide it
            infoButton.innerText = "More Information"; // Reset button text
        } else {
            currentInfo = "venue"; // Set current section to venue
            venueInfo.style.display = "block"; // Show venue info
            ticketInfo.style.display = "none"; // Ensure ticket info is hidden
        }
    } else if (type === "tickets") {
        if (currentInfo === "tickets") {
            currentInfo = null; // If the same section is clicked again, hide it
            infoButton.innerText = "More Information"; // Reset button text
        } else {
            currentInfo = "tickets"; // Set current section to tickets
            ticketInfo.style.display = "block"; // Show ticket info
            venueInfo.style.display = "none"; // Ensure venue info is hidden
        }
    }
}


function saveConcertInfo(status, event) {
    if (event) {
        event.preventDefault(); // Prevent default link behavior
        event.stopPropagation(); // Stop the event from bubbling
    }
    
    var name = document.getElementById("concertName").textContent;
    var thumbnail = document.getElementById("concertImage").src;
    var start_time = document.getElementById("concertTime").textContent;
    
    const button = event.currentTarget;
    button.disabled = true;  // Disable button to prevent double-clicking
    
    // Prepare the data to send
    const concertData = {
        status: status,
        name: name,
        thumbnail: thumbnail,
        start_time: start_time
    };

    // Send the data to the Flask backend using fetch
    fetch('/save_concert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(concertData)
    })
    .then(response => response.json()) // Parse JSON response
    .then(data => {
        console.log('Server response:', data);

        // Display a SweetAlert2 notification
        Swal.fire({
            icon: status === 'saved' ? 'success' : 'info',
            title: 'Concert Saved',
            text: data.message,
            confirmButtonText: 'OK',
        });
    })
    .catch(error => {
        console.error('Error:', error);

        // Display an error notification
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Something went wrong while saving the concert!',
            confirmButtonText: 'Try Again'
        });
    })
    .finally(() => {
        // Re-enable the button after the operation is complete
        button.disabled = false;
    });
}

document.getElementById('request-button').addEventListener('click', function() {
    AddFriend(currentCardID);
    Swal.fire({
        title: 'Request Sent!',
        text: 'Your request has been sent! Hang tight while we connect you both. 🎶✨',
        icon: 'success',
        confirmButtonText: 'OK'
    });

});



// Simple implement to immediately add a user as a friend
async function AddFriend(userId) {
    try {
        const response = await fetch(`/add_friend/${userId}`, {
            method: 'POST', // Explicitly set to POST
            headers: {
                'Content-Type': 'application/json' // Define the content type
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Server response:', data);

    } catch (error) {
        console.error('Error updating card content:', error);
    }
}

//concert search bar 
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const genreInput = document.getElementById('genre');
    const locationInput = document.getElementById('location');
    const resultsDiv = document.getElementById('concertResults');

    // Handle the form submission
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
        
        // Get genre and location values
        const genre = genreInput.value.trim();
        const location = locationInput.value.trim();

        // Validate the input
        if (!genre || !location) {
            alert('Please enter both genre and location.');
            return;
        }

        // Display loading message while fetching results
        resultsDiv.innerHTML = '<p>Loading concerts...</p>';
        
        // Fetch concert data from the backend
        fetch(`/api/searchConcerts?genre=${encodeURIComponent(genre)}&location=${encodeURIComponent(location)}`)
            .then(response => response.json())
            .then(data => {
                // Clear previous results
                resultsDiv.innerHTML = '';

                // Check if no results found
                if (data.length === 0) {
                    resultsDiv.innerHTML = '<p>No concerts found.</p>';
                    return;
                }

                // Loop through the concert data and create the cards
                data.forEach(concert => {
                    const concertCard = document.createElement('div');
                    concertCard.classList.add('col-md-4', 'mb-4'); // Adjust as per your grid system (e.g., Bootstrap)

                    concertCard.innerHTML = `
                        <div class="card h-100">
                            <img src="${concert.thumbnail}" class="card-img-top" alt="${concert.name}">
                            <div class="card-body">
                                <h5 class="card-title">${concert.name}</h5>
                                <p class="card-text">${concert.description}</p>
                                <p><strong>Start Time:</strong> ${new Date(concert.start_time).toLocaleString()}</p>
                                <p><strong>Venue:</strong> ${concert.venue_name}</p>
                                <p><strong>Address:</strong> ${concert.venue_address}</p>
                                <a href="${concert.venue_website}" class="btn btn-primary" target="_blank">Visit Venue</a>
                            </div>
                            <div class="card-footer">
                                <strong>Buy Tickets:</strong>
                                ${concert.ticket_links.map(ticket => `
                                    <a href="${ticket.link}" class="btn btn-secondary btn-sm" target="_blank">${ticket.source}</a>
                                `).join(' ')}
                            </div>
                        </div>
                    `;

                    // Append the concert card to the results div
                    resultsDiv.appendChild(concertCard);
                });
            })
            .catch(error => {
                console.error('Error fetching concert data:', error);
                resultsDiv.innerHTML = '<p>There was an error fetching the concerts. Please try again later.</p>';
            });
    });
});
