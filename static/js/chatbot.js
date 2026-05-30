const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const typingIndicator = document.getElementById("typing-indicator");
const typingSection = document.getElementById("typing-section-style");
const toggleBtn = document.getElementById("dark-mode-toggle");
const micBtn = document.getElementById("mic-btn");
const conversationIdInput = document.getElementById("conversation-id");
const newChatBtn = document.getElementById("new-chat-btn");

let currentConversationId = conversationIdInput ? conversationIdInput.value || "" : "";

function scrollToBottom() {
    if (!chatBox) return;
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });
}

window.addEventListener("load", () => {
    scrollToBottom();
});

function startNewChat() {
    currentConversationId = "";
    if (conversationIdInput) conversationIdInput.value = "";

    if (chatBox) {
        chatBox.innerHTML = `
            <div class="bot-msg neutral">
                Hi! I'm your AI Mental Health Assistant. How can I help you today?
            </div>
        `;
    }

    scrollToBottom();
}

if (newChatBtn) {
    newChatBtn.addEventListener("click", (e) => {
        e.preventDefault();
        startNewChat();
        window.history.pushState({}, "", "/chatbot");
    });
}

function addMessage(sender, text, emotion = "neutral") {
    if (!chatBox) return;

    const msg = document.createElement("div");

    if (sender === "user") {
        msg.className = "user-msg";
        msg.textContent = `You: ${text}`;
    } else {
        msg.className = `bot-msg ${emotion || "neutral"}`;
        msg.textContent = text;
    }

    chatBox.appendChild(msg);
    scrollToBottom();
}

function setTypingState(isTyping) {
    if (!typingIndicator || !typingSection) return;

    typingIndicator.style.display = isTyping ? "block" : "none";
    typingSection.classList.toggle("with-bot", isTyping);
    typingSection.classList.toggle("without-bot", !isTyping);
}

// ✅ UPDATED: injects new conversation into sidebar without reload
async function sendMessage() {
    if (!userInput) return;

    const message = userInput.value.trim();
    if (!message) return;

    const wasNewConversation = !currentConversationId;

    addMessage("user", message);
    userInput.value = "";
    setTypingState(true);

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                conversation_id: currentConversationId || null
            }),
        });

        const data = await res.json();
        setTypingState(false);

        if (!res.ok) {
            addMessage("bot", data.error || "⚠️ Error: Could not get a response.", "neutral");
            return;
        }

        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
            if (conversationIdInput) conversationIdInput.value = data.conversation_id;
        }

        if (data.reply) {
            addMessage("bot", data.reply, data.emotion || "neutral");
        } else {
            addMessage("bot", "⚠️ Error: No reply from server.", "neutral");
        }

        // ✅ NEW: inject new conversation into sidebar instantly
        if (wasNewConversation && data.conversation_id) {
            const historyList = document.getElementById('history-list');
            if (!historyList) return;

            // Remove "No chat history yet" placeholder if present
            const emptyMsg = historyList.querySelector('.empty-history');
            if (emptyMsg) emptyMsg.remove();

            // Remove active class from all existing items
            historyList.querySelectorAll('.history-item').forEach(el => {
                el.classList.remove('active');
            });

            // Format today's date e.g. "Apr 12, 2026"
            const today = new Date().toLocaleDateString('en-US', {
                month: 'short', day: '2-digit', year: 'numeric'
            });

            const title = message.slice(0, 40) || 'New Chat';

            const newItem = document.createElement('a');
            newItem.href      = `/chat/history/${data.conversation_id}`;
            newItem.className = 'history-item active';
            newItem.dataset.title = title.toLowerCase();
            newItem.innerHTML = `
                <div class="history-title">${title}</div>
                <div class="history-date">${today}</div>
            `;

            // Prepend to top (most recent first)
            historyList.insertBefore(newItem, historyList.firstChild);
        }

    } catch (err) {
        setTypingState(false);
        addMessage("bot", "⚠️ Connection error. Please check if the Flask server is running.", "neutral");
    }
}

if (sendBtn) {
    sendBtn.addEventListener("click", sendMessage);
}

if (userInput) {
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
}

if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        toggleBtn.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
    });
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (micBtn && SpeechRecognition && userInput) {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    const micImg = micBtn.querySelector("img");

    micBtn.addEventListener("click", () => {
        recognition.start();
        micBtn.classList.add("listening");
        if (micImg) micImg.style.opacity = "0.6";
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
    };

    recognition.onerror = () => {
        alert("Error occurred in speech recognition");
    };

    recognition.onend = () => {
        micBtn.classList.remove("listening");
        if (micImg) micImg.style.opacity = "1";
    };
} else if (micBtn) {
    console.warn("Speech Recognition not supported in this browser.");
}

// Chat history search
const searchInput = document.getElementById('history-search');
const historyList = document.getElementById('history-list');
const noResults   = document.getElementById('no-results');

if (searchInput && historyList) {
    searchInput.addEventListener('input', function () {
        const query = this.value.trim().toLowerCase();
        const items = historyList.querySelectorAll('.history-item');
        let visibleCount = 0;

        items.forEach(item => {
            const rawTitle = item.dataset.title || '';
            const titleEl  = item.querySelector('.history-title');

            if (!query) {
                item.style.display = '';
                if (titleEl) titleEl.innerHTML = titleEl.textContent;
                visibleCount++;
                return;
            }

            if (rawTitle.includes(query)) {
                item.style.display = '';
                visibleCount++;

                if (titleEl) {
                    const original = titleEl.textContent;
                    const idx = original.toLowerCase().indexOf(query);
                    if (idx !== -1) {
                        titleEl.innerHTML =
                            original.slice(0, idx) +
                            '<mark>' + original.slice(idx, idx + query.length) + '</mark>' +
                            original.slice(idx + query.length);
                    }
                }
            } else {
                item.style.display = 'none';
            }
        });

        if (noResults) {
            noResults.style.display = (visibleCount === 0 && query) ? 'block' : 'none';
        }
    });
}