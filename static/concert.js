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




function showMatchingSection() {
    document.querySelector('.matching').style.display = 'block';
}

function saveConcertInfo(status) {
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
