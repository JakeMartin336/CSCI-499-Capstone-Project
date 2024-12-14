document.addEventListener('DOMContentLoaded', () => {
    
    // Function to check if a date is in the past
    function isPastDate(dateString) {
      const concertDate = new Date(dateString);
      const currentDate = new Date();
      return concertDate < currentDate;
    }
  
    // Function to add a button for past concerts
    function addPastConcertButton(listSelector) {
      const concertLists = document.querySelectorAll(listSelector);
  
      concertLists.forEach((list) => {
        list.querySelectorAll('li').forEach((item) => {
          const dateElement = item.querySelector('.concert-date');
          const nameElement = item.querySelector('.concert-name');
          const imgElement = item.querySelector('.concert-image');
          if (dateElement && isPastDate(dateElement.textContent.trim())) {
            // Create the container and its content
            const container = document.createElement('div');
            container.className = 'past-concert-container';
  
            const divText = document.createElement('div');
            divText.innerText = 'Did you attend?';
           
            divText.style.color = 'charcoal';  
            divText.style.fontSize = '18px';
            divText.className = 'past-concert-text';
  
            const yesButton = document.createElement('button');
            yesButton.textContent = 'Yes';
            yesButton.className = 'past-concert-button-yes';
            yesButton.addEventListener('click', () => {
                // SendAttendance('yes', nameElement.textContent.trim(), dateElement.textContent.trim(), imgElement?.src);
                SendAttendance('yes', item);
              });
  
            const noButton = document.createElement('button');
            noButton.textContent = 'No';
            noButton.className = 'past-concert-button-no';
            noButton.addEventListener('click', () => {
                // SendAttendance('no', nameElement.textContent.trim(), dateElement.textContent.trim(), imgElement?.src);
                SendAttendance('no', item);
            });
  
            // Append elements to the container
            container.appendChild(divText);
            container.appendChild(yesButton);
            container.appendChild(noButton);
  
            // Append the container after the <li>
            item.parentElement.insertBefore(container, item.nextSibling);
          }
        });
      });
    }
  
    // Add buttons to all relevant lists
    addPastConcertButton('.goingConcerts');
    addPastConcertButton('.interestedConcerts');
    // addPastConcertButton('.attendedConcerts');
    isEmpty('.goingConcerts', 'No concerts have been selected.');
    isEmpty('.interestedConcerts', 'No concerts have been selected.');
    isEmpty('.attendedConcerts', 'No concerts have been selected.');

  });

// Function to handle the display of concerts list
function isEmpty(ulSelector, message) {
    const ulElement = document.querySelector(ulSelector);
    if (!ulElement || ulElement.children.length === 0) {
        const messageElement = document.createElement('p');
        messageElement.style.fontSize = '0.9em';
        messageElement.style.color = 'gray';
        messageElement.textContent = message;

        // Replace the ul with the message or append the message to its parent
        if (ulElement && ulElement.parentNode) {
            ulElement.parentNode.replaceChild(messageElement, ulElement);
        }
    }
}


// function SendAttendance(attendance, concert_name, concert_date, concert_image){
    function SendAttendance(attendance, item) {
        const dateElement = item.querySelector('.concert-date');
        const nameElement = item.querySelector('.concert-name');
        const imgElement = item.querySelector('.concert-image');
    
        const attendanceData = {
            attendance: attendance,
            concert_name: nameElement.textContent.trim(),
            concert_date: dateElement.textContent.trim(),
            concert_image: imgElement?.src
        };
    
        // Send the data to the Flask backend using fetch
        fetch('/concert_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(attendanceData)
        })
        .then(response => response.json()) // Parse JSON response
        .then(data => {
            console.log('Server response:', data);
    
            // Display a SweetAlert2 notification
            Swal.fire({
                icon: attendance === 'yes' ? 'success' : 'info',
                title: 'Success!',
                text: data.message,
                confirmButtonText: 'OK'
            });
    
            const parentList = item.parentElement;
            const container = item.nextElementSibling;
    
            if (attendance === 'no') {
                // Remove the concert and yes/no buttons from the current list
                if (container && container.classList.contains('past-concert-container')) {
                    container.remove();
                }
                parentList.removeChild(item);
            }
    
            // Append the concert to the Attended list
            if (attendance === 'yes') {
                // Remove the concert and yes/no buttons from the current list
                if (container && container.classList.contains('past-concert-container')) {
                    container.remove();
                }
                parentList.removeChild(item);
    
                // Append the concert to the Attended list
                const attendedList = document.querySelector('.attendedConcerts');
                if (attendedList) {
                    const newItem = document.createElement('li');
                    newItem.innerHTML = `
                        <img src="${imgElement?.src}" class="concert-image" alt="Concert Image"><br>
                        <div class="concert-text">
                          <span class="concert-name">${nameElement.textContent.trim()}</span>
                          <span class="concert-date">${dateElement.textContent.trim()}</span>
                        </div>
                    `;
                    attendedList.appendChild(newItem);
                }
            }
    
            isEmpty('.goingConcerts', 'No concerts have been selected.');
            isEmpty('.interestedConcerts', 'No concerts have been selected.');
            isEmpty('.attendedConcerts', 'No concerts have been selected.');
        })
        .catch(error => {
            console.error('Error:', error);
    
            // Display an error notification
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Something went wrong!',
                confirmButtonText: 'Try Again'
            });
        });
    }
    