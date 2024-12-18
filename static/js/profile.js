// Profile Page Specific JavaScript

const toggleButton = document.getElementById('toggle-avatars');
const avatarList = document.getElementById('avatar-list');
const chosenAvatarInput = document.getElementById('chosen_avatar');
const selectedAvatar = document.getElementById('selected-avatar');

// Initially hide the avatar list
avatarList.style.display = 'none';

// Toggle avatar list visibility
toggleButton.addEventListener('click', (e) => {
  e.stopPropagation(); // Prevent the click from bubbling up to the document
  if (avatarList.style.display === 'block') {
    avatarList.style.display = 'none';
  } else {
    avatarList.style.display = 'block';
  }
});

// Handle avatar selection
avatarList.addEventListener('click', (e) => {
  if (e.target.tagName === 'IMG') {
    const avatarUrl = e.target.getAttribute('data-avatar');
    selectedAvatar.src = avatarUrl;
    chosenAvatarInput.value = avatarUrl;
    avatarList.style.display = 'none';
  }
});

// Close avatar list when clicking outside
document.addEventListener('click', (e) => {
  if (!avatarList.contains(e.target) && e.target !== toggleButton) {
    avatarList.style.display = 'none';
  }
});

document.addEventListener("DOMContentLoaded", () => {
    const genreDropdownButton = document.getElementById("genreDropdown");
    const genreDropdownContent = document.getElementById("genreOptions");
    const genreCheckboxes = document.querySelectorAll('input[name="genres"]');
  
    let selectedGenres = [];
  
    // Initialize selected genres
    genreCheckboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        selectedGenres.push(checkbox.value);
      }
    });
    updateDropdownText();
  
    // Toggle dropdown visibility
    genreDropdownButton.addEventListener("click", (e) => {
      e.stopPropagation(); // Prevents event bubbling
      genreDropdownContent.classList.toggle("show-dropdown");
    });
  
    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
      if (!genreDropdownContent.contains(e.target) && e.target !== genreDropdownButton) {
        genreDropdownContent.classList.remove("show-dropdown");
      }
    });
  
    // Handle genre selection
    genreCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) {
          if (selectedGenres.length >= 3) {
            checkbox.checked = false;
            showPopupMessage("You can only select up to 3 genres.");
          } else {
            selectedGenres.push(checkbox.value);
          }
        } else {
          selectedGenres = selectedGenres.filter((g) => g !== checkbox.value);
        }
        updateDropdownText();
      });
    });
  
    function updateDropdownText() {
      genreDropdownButton.textContent =
        selectedGenres.length > 0
          ? selectedGenres.join(", ")
          : "Pick up to 3 of your favorite genres";
    }
  
    function showPopupMessage(message) {
      const popup = document.getElementById("popup-message");
      popup.textContent = message;
      popup.classList.add("show");
      setTimeout(() => popup.classList.remove("show"), 3000);
    }
  });
  
