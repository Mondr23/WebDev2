document.addEventListener('DOMContentLoaded', () => {
    const receivedMessagesContainer = document.getElementById('receivedMessages');
    const sentMessagesContainer = document.getElementById('sentMessages');
    const replyModal = new bootstrap.Modal(document.getElementById('replyModal'));
    const replyMessagePreview = document.getElementById('replyMessagePreview');
    const replyMessageContent = document.getElementById('replyMessageContent');
    const sendReplyBtn = document.getElementById('sendReplyBtn');

    let replyToMessageId = null;

    // Fetch messages from the server
    async function fetchMessages() {
        try {
            const response = await fetch('/api/messages');
            const { received_messages, sent_messages } = await response.json();

            populateMessages(receivedMessagesContainer, received_messages, true);
            populateMessages(sentMessagesContainer, sent_messages, false);
        } catch (err) {
            console.error('Error fetching messages:', err);
        }
    }

    // Populate messages into a container with username and timestamp
    function populateMessages(container, messages, isReceived) {
        if (!messages.length) {
            container.innerHTML = `<p class="text-muted text-center">${isReceived ? 'No received messages.' : 'No sent messages.'}</p>`;
            return;
        }
        container.innerHTML = messages
            .map((msg) => {
                const username = isReceived ? msg.sender : msg.recipient;
                const timestamp = new Date(msg.timestamp).toLocaleString();
                return `
                    <div class="message ${isReceived ? 'received' : 'sent'}">
                        <p><strong>${username}</strong></p>
                        <p>${msg.content}</p>
                        <small class="text-muted">${timestamp}</small>
                        ${
                            isReceived
                                ? `<button class="btn btn-link reply-btn" data-id="${msg.id}" data-content="${msg.content}">Reply</button>`
                                : ''
                        }
                    </div>
                `;
            })
            .join('');
    }

    // Handle reply button click
    receivedMessagesContainer.addEventListener('click', (e) => {
        if (!e.target.classList.contains('reply-btn')) return;

        replyToMessageId = e.target.dataset.id;
        replyMessagePreview.textContent = `Replying to: "${e.target.dataset.content}"`;
        replyModal.show();
    });

    // Send a reply
    sendReplyBtn.addEventListener('click', async () => {
        const content = replyMessageContent.value.trim();
        if (!content || !replyToMessageId) return;

        try {
            await fetch('/api/messages/reply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message_id: replyToMessageId, content }),
            });
            replyMessageContent.value = '';
            replyModal.hide();
            fetchMessages(); // Refresh messages
        } catch (err) {
            console.error('Error sending reply:', err);
        }
    });

    fetchMessages();
});
