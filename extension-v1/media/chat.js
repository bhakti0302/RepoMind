
    (function() {
      const vscode = acquireVsCodeApi();
      const messagesContainer = document.getElementById('messages');
      const userInput = document.getElementById('userInput');
      const sendButton = document.getElementById('sendButton');
      
      // Handle sending messages
      function sendMessage() {
        const text = userInput.value.trim();
        if (text) {
          vscode.postMessage({
            command: 'sendMessage',
            text: text
          });
          userInput.value = '';
        }
      }
      
      // Send message on button click
      sendButton.addEventListener('click', sendMessage);
      
      // Send message on Enter (but allow Shift+Enter for new lines)
      userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
      
      // Handle messages from the extension
      window.addEventListener('message', event => {
        const message = event.data;
        switch (message.command) {
          case 'addMessage':
            addMessageToUI(message.message);
            break;
        }
      });
      
      // Add a message to the UI
      function addMessageToUI(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', message.role);
        
        // Process markdown-like code blocks
        let content = message.content;
        content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        messageElement.innerHTML = content;
        messagesContainer.appendChild(messageElement);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }());
    