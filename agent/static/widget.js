// Opens and closes the chat bubble on the store page.
// The chat itself (sending messages, showing replies) is still done by script.js.
//
// Everything is wrapped in (function () { ... })(); so these variable names
// stay private. script.js may already use names like chatForm, and two
// "const chatForm" lines on the same page would cause an error.

(function () {
    const launcher = document.getElementById("chat-launcher");
    const closeButton = document.getElementById("chat-close");
    const widget = document.getElementById("chat-widget");
    const chatInput = document.getElementById("message-input");
    const chatForm = document.getElementById("chat-form");

    function openChat() {
        document.body.classList.add("chat-open");
        widget.setAttribute("aria-hidden", "false");
        chatInput.focus();
    }

    function closeChat() {
        document.body.classList.remove("chat-open");
        widget.setAttribute("aria-hidden", "true");
    }

    // Bubble button: open if closed, close if open
    launcher.addEventListener("click", function () {
        if (document.body.classList.contains("chat-open")) {
            closeChat();
        } else {
            openChat();
        }
    });

    closeButton.addEventListener("click", closeChat);

    // Press Escape to close
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeChat();
        }
    });

    // "Chat with us" / "Open chat" buttons on the page
    document.querySelectorAll(".open-chat").forEach(function (button) {
        button.addEventListener("click", openChat);
    });

    // "Ask about this" on a product card:
    // open the chat, type a question for the user, and send it
    document.querySelectorAll(".ask-button").forEach(function (button) {
        button.addEventListener("click", function () {
            openChat();
            chatInput.value = "Tell me about the " + button.dataset.product;
            chatForm.requestSubmit();   // same as the user pressing Send
        });
    });
})();
