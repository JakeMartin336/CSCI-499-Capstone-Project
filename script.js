const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');
const btnPopup = document.querySelector('.btnLogin-popup');
const iconClose = document.querySelector('.icon-close');

// Show registration form
registerLink.addEventListener('click', () => {
    wrapper.classList.add('active');
});

// Show login form
loginLink.addEventListener('click', () => {
    wrapper.classList.remove('active');
});

// Show the login/register popup
btnPopup.addEventListener('click', () => {
    wrapper.classList.add('active-popup');
});

// Close the login/register popup
iconClose.addEventListener('click', () => {
    wrapper.classList.remove('active-popup');
});

