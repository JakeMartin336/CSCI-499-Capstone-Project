// Show the login/register popup
const btnPopup = document.querySelector('.btnLogin-popup');
if (btnPopup) {
  btnPopup.addEventListener('click', GoToLogin);
}
function GoToLogin() {
  window.location.href = '/login';
}

// Max amount of genres able to select in survey
const limit = 3;
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
if (checkboxes.length > 0) {
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      const checked = document.querySelectorAll('input[type="checkbox"]:checked');
      if (checked.length > limit) {
        this.checked = false;
      }
    });
  });
}


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


