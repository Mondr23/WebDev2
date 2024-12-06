// JavaScript for Messaging System

document.addEventListener('DOMContentLoaded', () => {
    const receivedMessagesContainer = document.getElementById('receivedMessages');
    const sentMessagesContainer = document.getElementById('sentMessages');
    const newMessageForm = document.getElementById('newMessageForm');
    const replyModal = document.getElementById('replyModal');
    const replyMessageContent = document.getElementById('replyMessageContent');
    const replyMessagePreview = document.getElementById('replyMessagePreview');
    const sendReplyBtn = document.getElementById('sendReplyBtn');

    // Function to load messages
    const loadMessages = () => {
        fetch('/api/messages', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Populate received messages
            receivedMessagesContainer.innerHTML = '';
            data.received_messages.forEach(msg => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message');
                messageElement.innerHTML = `
                    <div class="message-header">
                        <strong>From:</strong> ${msg.sender}
                        <span class="message-timestamp">${new Date(msg.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="message-content">${msg.content}</div>
                    <button class="btn btn-link reply-btn" data-message-id="${msg.id}" data-sender="${msg.sender}">Reply</button>
                `;
                receivedMessagesContainer.appendChild(messageElement);
            });

            // Add reply button event listeners
            document.querySelectorAll('.reply-btn').forEach(btn => {
                btn.addEventListener('click', event => {
                    const messageId = btn.getAttribute('data-message-id');
                    const sender = btn.getAttribute('data-sender');
                    replyMessagePreview.textContent = `Replying to ${sender}`;
                    sendReplyBtn.setAttribute('data-message-id', messageId);
                    const modal = new bootstrap.Modal(replyModal);
                    modal.show();
                });
            });

            // Populate sent messages
            sentMessagesContainer.innerHTML = '';
            data.sent_messages.forEach(msg => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message');
                messageElement.innerHTML = `
                    <div class="message-header">
                        <strong>To:</strong> ${msg.recipient}
                        <span class="message-timestamp">${new Date(msg.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="message-content">${msg.content}</div>
                `;
                sentMessagesContainer.appendChild(messageElement);
            });
        })
        .catch(error => console.error('Error loading messages:', error));
    };

    // Function to send a new message
    newMessageForm.addEventListener('submit', event => {
        event.preventDefault();

        const recipient = document.getElementById('recipientUsername').value;
        const content = document.getElementById('newMessageContent').value;

        fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ recipient, content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Message sent successfully!');
                newMessageForm.reset();
                loadMessages();
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => console.error('Error sending message:', error));
    });

    // Function to reply to a message
    sendReplyBtn.addEventListener('click', () => {
        const messageId = sendReplyBtn.getAttribute('data-message-id');
        const content = replyMessageContent.value;

        fetch('/api/messages/reply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message_id: messageId, content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Reply sent successfully!');
                replyMessageContent.value = '';
                const modal = bootstrap.Modal.getInstance(replyModal);
                modal.hide();
                loadMessages();
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => console.error('Error sending reply:', error));
    });

    // Load messages on page load
    loadMessages();
});
