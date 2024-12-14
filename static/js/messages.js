document.addEventListener("DOMContentLoaded", function () {
    // Detect Enter key press in the message input
    const messageInput = document.getElementById("messageInput");
    messageInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();  // Prevents the default form submission behavior
            sendMessage();  // Calls the function to send the message
        }
    });

    document.getElementById("chatWindow").style.display = 'none';
});
