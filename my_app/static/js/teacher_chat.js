document.addEventListener('DOMContentLoaded', function () {
    const openChatBtn = document.getElementById('open-chat-btn');
    const chatWindow = document.getElementById('chat-window');
    const closeChatBtn = document.getElementById('close-chat-btn');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    openChatBtn.addEventListener('click', () => {
        chatWindow.style.display = 'flex';
        openChatBtn.style.display = 'none';
    });

    closeChatBtn.addEventListener('click', () => {
        chatWindow.style.display = 'none';
        openChatBtn.style.display = 'inline-block';
    });

    sendChatBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        appendMessage('You', message);
        chatInput.value = '';

        fetch('/teacher_chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: message,
                team_id: selectedTeamId,
                assessment_id: assessmentId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                appendMessage('Assisstant', data.response);
            } else {
                appendMessage('Assisstant', 'Error:' + data.message);
            }
        })
        .catch(error => {
            appendMessage('Assisstant', 'Error:' + error);
        });
    }

    function appendMessage(sender, text) {
        const bubble = document.createElement('div');
        bubble.classList.add('chat-bubble');
    
        if (sender === 'You') {
            bubble.classList.add('chat-right');
        } else {
            bubble.classList.add('chat-left');
        }
    
        bubble.innerText = text;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
