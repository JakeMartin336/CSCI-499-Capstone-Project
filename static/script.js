const btnPopup = document.querySelector('.btnLogin-popup');
const iconClose = document.querySelector('.icon-close');

// Show the login/register popup
btnPopup.addEventListener('click', GoToLogin);
    function GoToLogin() {
        window.location.href = '/login'
}
