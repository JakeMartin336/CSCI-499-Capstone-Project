const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static('public'));

let users = {};

io.on('connection', (socket) => {
    console.log('A user connected:', socket.id);

    // socket.on('join chat', (username) => {
    //     users[socket.id] = username;
    //     io.emit('user list', Object.values(users)); 
    //     socket.broadcast.emit('notification', `${username} joined the chat`);
    // });

    // socket.on('chat message', (msg) => {
    //     const username = users[socket.id];
    //     io.emit('chat message', { username, msg });
    // });

    // socket.on('disconnect', () => {
    //     const username = users[socket.id];
    //     if (username) {
    //         delete users[socket.id];
    //         io.emit('user list', Object.values(users)); 
    //         socket.broadcast.emit('notification', `${username} left the chat`);
    //     }
    // });

    socket.on('join chat', ({ username, friend_id }) => {
        users[socket.id] = username;
        socket.join(friend_id); // Join a room for the specific chat
        io.to(friend_id).emit('notification', `${username} joined the chat`);
    });

    socket.on('chat message', ({ msg, friend_id }) => {
        io.to(friend_id).emit('chat message', { username: users[socket.id], msg });
    });

    socket.on('disconnect', () => {
        const username = users[socket.id];
        if (username) {
            delete users[socket.id];
            io.emit('notification', `${username} left the chat`);
        }
    });

});


const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});