document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.chat-sidebar');
    const openBtn = document.getElementById('openBtn');
    const exitBtn = document.getElementById('exitBtn');
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

    function toggleSidebar(isOpen) {
        sidebar.style.right = isOpen ? '0' : '-420px';
        openBtn.style.right = isOpen ? '420px' : '10px';
    }

    openBtn.addEventListener('click', () => toggleSidebar(true));
    exitBtn.addEventListener('click', () => toggleSidebar(false));

    document.addEventListener('click', function (event) {
        if (!sidebar.contains(event.target) && !openBtn.contains(event.target)) {
            toggleSidebar(false);
        }
    });

    function displayMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
    
        if (sender === 'Chatbot') {
            const messageContent = `<strong>${sender}:</strong> `;
            messageDiv.classList.add('bot-message');
            messageDiv.innerHTML = messageContent;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
    
            let index = 0;
            const typingInterval = setInterval(() => {
                messageDiv.innerHTML = messageContent + message.slice(0, index);
                index++;
                if (index > message.length) {
                    clearInterval(typingInterval);
                }
            }, 50);
        } else {
            messageDiv.classList.add(sender === 'You' ? 'user-message' : 'system-message'); // Assuming system messages use a different style
            messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    

    function sendMessage() {
        const userMessage = userInput.value.trim();
        if (userMessage !== '') {
            if (userMessage.length > 3000) {
                displayMessage('System', 'Error: Only 3000 characters are allowed.');
                return;
            }

            displayMessage('You', userMessage);

            fetch(`http://127.0.0.1:8000/query/atlas?query=${encodeURIComponent(userMessage)}&subject=subject2&user=user`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
                .then(response => response.text())
                .then(data => {
                    displayMessage('Chatbot', data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    displayMessage('Chatbot', 'Sorry, I couldn\'t process your request.');
                });

            userInput.value = '';
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            sendMessage();
            event.preventDefault(); // Prevent the default action to stop form submission on pressing Enter
        }
    });
});