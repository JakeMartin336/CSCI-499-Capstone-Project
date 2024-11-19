const socket = io();
let username;

while (!username) {
    username = prompt('Enter your username:');
}

socket.emit('join chat', username);

const form = document.getElementById('chatForm');
const input = document.getElementById('messageInput');
const messages = document.getElementById('messages');
const usersList = document.getElementById('users');

form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (input.value) {
        socket.emit('chat message', input.value);
        input.value = '';
    }
});

socket.on('chat message', ({ username, msg }) => {
    const item = document.createElement('li');
    item.innerHTML = `<strong>${username}:</strong> ${msg}`;
    messages.appendChild(item);
    messages.scrollTop = messages.scrollHeight;
});

socket.on('notification', (msg) => {
    const item = document.createElement('li');
    item.style.fontStyle = 'italic';
    item.textContent = msg;
    messages.appendChild(item);
    messages.scrollTop = messages.scrollHeight;
});

socket.on('user list', (users) => {
    usersList.innerHTML = '';
    users.forEach((user) => {
        const item = document.createElement('li');
        item.textContent = user;
        usersList.appendChild(item);
    });
});
