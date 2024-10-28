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
