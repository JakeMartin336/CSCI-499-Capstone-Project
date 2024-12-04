
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



let currentIndex = 0;

document.addEventListener("DOMContentLoaded", function () {
    updateConcertDetails(currentIndex);
    document.getElementById('prevTicket').style.display = "none";
});

function updateConcertDetails(index) {
    // if (allConcertsData.length === 0){
    //     displayEmptyConcertList();
    // }
    // else{
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
    // }
};

// function displayEmptyConcertList(){
//     document.getElementById('prevTicket').style.display = "none";
//     document.getElementById('nextTicket').style.display = "none";
//     document.getElementById('saveConcertButton').style.display = "none";
//     document.getElementById('infoButton').style.display = "none";
// }

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


