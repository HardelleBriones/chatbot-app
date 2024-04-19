const openBtn = document.getElementById('openBtn');
const sidebar = document.querySelector('.chat-sidebar');
const exitBtn = document.getElementById('exitBtn');

openBtn.addEventListener('click', () => {
  sidebar.style.right = '0';
  openBtn.style.transition = 'right 0.3s ease-in-out';
  openBtn.style.right = '440px';
  openBtn.style.display = 'none';
});

exitBtn.addEventListener('click', () => {
  sidebar.style.right = '-440px';
  openBtn.style.transition = 'right 0.3s ease-in-out';
  openBtn.style.right = '0';

  setTimeout(() => {
    openBtn.style.display = 'block';
  }, 300);
  
});

const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');

function sendMessage() {
  const userMessage = userInput.value.trim();
  if (userMessage !== '') {
    displayMessage('You', userMessage);

    fetch('/query?query=' + encodeURIComponent(userMessage), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.text())
      .then(data => {
        displayMessage('Bot', data);
      })
      .catch(error => {
        console.error('Error:', error);
        displayMessage('Bot', 'Sorry, I couldn\'t process your request.');
      });

    userInput.value = '';
  }
}


function displayMessage(sender, message) {
  const messageDiv = document.createElement('div');
  messageDiv.classList.add('message');

  if (sender === 'Bot') {
    const messageContent = `<strong>${sender}:</strong> `;
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
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}


sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', function (enter) {
    if(enter.key === 'Enter') {
    sendMessage();
    }
});