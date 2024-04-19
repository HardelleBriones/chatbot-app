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

  function sendMessage() {
      const messageText = userInput.value.trim();
      if (messageText) {
          const messageDiv = document.createElement('div');
          messageDiv.classList.add('message', 'user-message');
          messageDiv.textContent = messageText;
          chatMessages.appendChild(messageDiv);
          userInput.value = '';
          chatMessages.scrollTop = chatMessages.scrollHeight;

          // Simulate a bot response
          setTimeout(() => {
              const botMessage = document.createElement('div');
              botMessage.classList.add('message', 'bot-message');
              botMessage.textContent = "Here's a placeholder reply from the bot!";
              chatMessages.appendChild(botMessage);
              chatMessages.scrollTop = chatMessages.scrollHeight;
          }, 1000);
      }
  }

  sendBtn.addEventListener('click', sendMessage);
  userInput.addEventListener('keypress', function (event) {
      if (event.key === 'Enter') {
          sendMessage();
      }
  });
});
