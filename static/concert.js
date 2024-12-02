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



async function updateCardWithNewUser(userId) {
    try {
        // Call the backend to get user information
        const response = await fetch(`/api/user-info/${userId}`);
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

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

// document.addEventListener("DOMContentLoaded", function() {
//     firstConcert(allConcerts);
// });

// function firstConcert(allConcerts) {
//     let concert = allConcerts[0];

//     document.getElementById('concertImage').querySelector('img').src = concert.thumbnail;
//     document.getElementById('concertName').innerText = concert.name;
//     document.getElementById('concertDescription').innerText = concert.description;
//     document.getElementById('concertStartTime').innerText = concert.start_time;

//     document.getElementById('concertVenueName').innerText = concert.venue_name;
//     document.getElementById('concertVenueAddress').innerText = concert.venue_address;

//     document.getElementById('prevTicket').style = "display: none";

//     const ticketLinks = document.getElementById('ticketLinks');
//     let concertTickets = concert.ticket_links
//     concertTickets.forEach(function(ticket) {
//         const li = document.createElement('li');
//         li.innerHTML = `<strong>${ticket.source}:</strong> <a href="${ticket.link}" target="_blank">${ticket.link}</a>`;
//         ticketLinks.appendChild(li);
//     });
//     document.getElementById('ticketInfo').style.display = 'block';
// }



// let concertIndex = 0;
// function showConcertIndex(direction) {
//     // Ensure prev and next buttons visibility
//     if (concertIndex == 0) {
//         document.getElementById('prevTicket').style.display = "none";
//     } else {
//         document.getElementById('prevTicket').style.display = "block";
//     }

//     if (concertIndex == allConcerts.length - 1) {
//         document.getElementById('nextTicket').style.display = "none";
//     } else {
//         document.getElementById('nextTicket').style.display = "block";
//     }

//     // Update concertIndex based on direction
//     if (direction == 'next' && concertIndex < allConcerts.length - 1) {
//         concertIndex++;
//     } else if (direction == 'previous' && concertIndex > 0) {
//         concertIndex--;
//     }

//     // Update concert details on the page
//     document.getElementById('concertImage').src = allConcerts[concertIndex].thumbnail;
//     document.getElementById('concertName').textContent = allConcerts[concertIndex].name;
//     document.getElementById('concertDescription').textContent = allConcerts[concertIndex].description;
//     document.getElementById('concertStartTime').textContent = allConcerts[concertIndex].start_time;

//     // Update venue details
//     document.getElementById('concertVenueName').textContent = allConcerts[concertIndex].venue_name;
//     document.getElementById('concertVenueAddress').textContent = allConcerts[concertIndex].venue_address;

//     // Update ticket information dynamically
//     const ticketLinks = document.getElementById('ticketLinks');
//     ticketLinks.innerHTML = '';  // Clear existing ticket links
//     let concertTickets = allConcerts[concertIndex].ticket_links;
//     concertTickets.forEach(function(ticket) {
//         const li = document.createElement('li');
//         li.innerHTML = `<strong>${ticket.source}:</strong> <a href="${ticket.link}" target="_blank">${ticket.link}</a>`;
//         ticketLinks.appendChild(li);
//     });
//     document.getElementById('ticketInfo').style.display = 'block';
// }



let currentInfo = null; // Track the currently displayed info section
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


function saveConcertInfo(status, name, thumbnail, start_time) {
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
        // Handle the response from Python here (optional)
        console.log('Server response:', data);
        alert(data.message);  // Example: show a message from Python
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Re-enable the button if necessary
    setTimeout(() => { button.disabled = false; }, 500);

}


// function OldsaveConcertInfo(status, concertName, concertImage, concertDate) {
//     $.ajax({
//         type: 'POST',
//         url: "~/app.py",
//         contentType: 'application/json',
//         data: {
//             concert_status: status,
//             concert_name: concertName,
//             concert_image : concertImage,
//             concert_date: concertDate
//         },
//         success: function(response) {
//             alert(`Marked as ${status.charAt(0).toUpperCase() + status.slice(1)}: ${concertName}`);
//         },
//         error: function(error) {
//             console.error('Error saving concert info:', error);
//             alert('There was an error. Please try again.');
//         }
//     });
//   }