const openBtn = document.getElementById('openBtn');
const sidebar = document.querySelector('.chat-sidebar');

openBtn.addEventListener('click', () => {
  const sidebarOpen = sidebar.style.right === '0px' || sidebar.style.right === '';

  if(sidebarOpen) {
    sidebar.style.right = '-440px';
    openBtn.style.transition = 'right 0.3s ease-in-out';
    openBtn.style.right = '0';
  } else {
    sidebar.style.right = '0';
    openBtn.style.transition = 'right 0.3s ease-in-out';
    openBtn.style.right = '390px'; 
  }
});

const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');

function sendMessage() {
  const userMessage = userInput.value;
  if(userMessage.trim() !== '') {
    displayMessage('You', userMessage);
    userInput.value = '';
      
      
  }
}

function displayMessage(sender, message) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message');
  messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight; // always scroll to newest message
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', function (enter) {
    if(enter.key === 'Enter') {
    sendMessage();
    }
});