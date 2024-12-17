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
  
  
