// ---------- Page elements ----------
const messagesBox = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const quickReplies = document.querySelectorAll(".quick-reply");

// One random ID per page load, so Flask knows whose chat history to use
const sessionId = crypto.randomUUID();


// ---------- Show a bubble in the chat ----------
function addMessage(text, sender) {
    const bubble = document.createElement("div");
    bubble.className = `message ${sender}`;

    if (sender === "bot") {
        const label = document.createElement("div");
        label.className = "sender";

        const logo = document.createElement("span");
        logo.className = "mini-logo";
        logo.textContent = "S";

        label.appendChild(logo);
        label.append(" ShopEasy");
        bubble.appendChild(label);
    }

    const textDiv = document.createElement("div");
    textDiv.className = "text";
    textDiv.textContent = text;          // textContent, never innerHTML (safer)
    bubble.appendChild(textDiv);

    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    return bubble;
}


// ---------- Turn the input + button off/on while waiting ----------
function setLoading(isLoading) {
    sendButton.disabled = isLoading;
    messageInput.disabled = isLoading;
    quickReplies.forEach((chip) => (chip.disabled = isLoading));
}


// ---------- Send a message to Flask and show the reply ----------
async function sendMessage(text) {
    addMessage(text, "user");
    messageInput.value = "";
    setLoading(true);

    const typingBubble = addMessage("Typing...", "bot");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message: text }),
        });

        const data = await response.json();
        typingBubble.remove();

        if (data.error) {
            addMessage("Sorry, something went wrong. Please try again.", "bot");
        } else {
            addMessage(data.reply, "bot");
        }
    } catch (error) {
        // Server is down or there's no internet
        typingBubble.remove();
        addMessage("Sorry, I can't connect right now. Please try again in a moment.", "bot");
        console.error(error);
    }

    setLoading(false);
    messageInput.focus();
}


// ---------- When the form is sent (Send button or Enter) ----------
chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const text = messageInput.value.trim();
    if (!text) return;

    sendMessage(text);
});


// ---------- Quick-reply chips ----------
quickReplies.forEach((chip) => {
    chip.addEventListener("click", () => {
        sendMessage(chip.textContent);
    });
});