
// document.addEventListener("DOMContentLoaded", function () {
//     document.getElementById("chatWindow").style.display = 'none';
// });

// let GlobalfriendID = null;
// let GlobalfriendName = null;

// function StartChat(friendID, friendName) {
//     document.getElementById("chatWindow").style.display = 'block';
//     document.getElementById("chatroomTitle").textContent = `Chat with ${friendName}`;
//     GlobalfriendID = friendID;
//     GlobalfriendName = friendName;
//     socketio.emit('join', { username: username, friendID: friendID});
// };

// function CloseChat(){
//     document.getElementById("chatWindow").style.display = 'none';
//     socketio.emit('leave', { username: username, friendID: GlobalfriendID});
//     GlobalfriendID = null;
//     GlobalfriendName = null;
// };

// const CreateMessage = (name, msg) => {
//     var chatMessages = document.getElementById("chatMessages");
//     const newMessage = document.createElement('div');
//     if (name !== username) {
//         newMessage.classList.add('message', 'received');
//     }
//     else{
//         newMessage.classList.add('message', 'sent');
//     }
//     newMessage.textContent = msg;
//     chatMessages.appendChild(newMessage);
// };

// socketio.on("message", (data) => {
//     CreateMessage(data.name, data.message);
// });

// function sendMessage(){
//     const send_message = document.getElementById("messageInput");
//     if (send_message.value == "") return;
//     socketio.emit('message', { username: username, friendID: GlobalfriendID, message: send_message.value });
//     CreateMessage(username, send_message.value);
//     send_message.value = "";
// };


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("chatWindow").style.display = 'none';
});

let GlobalfriendID = null;
let GlobalfriendName = null;

function StartChat(friendID, friendName) {
    document.getElementById("chatWindow").style.display = 'block';
    document.getElementById("chatroomTitle").textContent = `Chat with ${friendName}`;
    GlobalfriendID = friendID;
    GlobalfriendName = friendName;

    // Emit 'join' event to join the chat room
    socketio.emit('join', { friendID: friendID });
};

function CloseChat(){
    document.getElementById("chatWindow").style.display = 'none';
    // Emit 'leave' event to leave the chat room
    socketio.emit('leave', { friendID: GlobalfriendID });
    GlobalfriendID = null;
    GlobalfriendName = null;
};

const CreateMessage = (name, msg) => {
    var chatMessages = document.getElementById("chatMessages");
    const newMessage = document.createElement('div');
    if (name !== username) {
        newMessage.classList.add('message', 'received');
    }
    else{
        newMessage.classList.add('message', 'sent');
    }
    newMessage.textContent = msg;
    chatMessages.appendChild(newMessage);
};

socketio.on("message", (data) => {
    CreateMessage(data.name, data.message);
});

function sendMessage(){
    const send_message = document.getElementById("messageInput");
    if (send_message.value == "") return;
    
    // Emit 'message' event to send a message
    socketio.emit('message', { friendID: GlobalfriendID, message: send_message.value });
    CreateMessage(username, send_message.value);  // Display sent message in the chat window
    send_message.value = "";
};
