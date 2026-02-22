// DOM References
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("userInputButton");
const messagesContainer = document.getElementById("messages");
const typingIndicator = document.getElementById("typingIndicator");
const chatBox = document.querySelector(".chat_box");
const chatIcon = document.querySelector(".chat_icon");
const voiceButton = document.getElementById("voiceInputButton");

// Attach Events
sendButton.addEventListener("click", handleUserInput);
userInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        handleUserInput();
    }
});
chatIcon.addEventListener("click", () => {
    chatBox.classList.toggle("active");
});

// Eel Exposed Functions
eel.expose(addUserMsg);
eel.expose(addAppMsg);

// Handle User Message
function handleUserInput() {
    const msg = userInput.value.trim();
    if (msg) {
        userInput.value = "";
        addUserMsg(msg);
        showTyping(true);
        eel.getUserInput(msg)(response => {
            showTyping(false);
            addAppMsg(response);
        });
    }
}

// Add User Message to Chat
function addUserMsg(msg) {
    appendMessage(msg, "from", "rtol");
}

// Add App (Max) Message to Chat
function addAppMsg(msg) {
    showTyping(false);
    appendMessage(msg, "to", "ltor");
}

// General Message Appending Logic
function appendMessage(msg, direction, animationClass) {
    const message = document.createElement("div");
    message.className = `message ${direction} ready ${animationClass}`;
    message.textContent = msg;

    messagesContainer.appendChild(message);
    scrollToBottom();

    // Delay to allow animation to run before removing 'ready' class
    const index = messagesContainer.childElementCount - 1;
    setTimeout(() => changeClass(index, `message ${direction}`), 500);
}

// Change message class after animation
function changeClass(index, newClass) {
    const message = messagesContainer.children[index];
    if (message) {
        message.className = newClass;
    }
}

// Auto-scroll to latest message
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Typing indicator visibility
function showTyping(isVisible) {
    if (typingIndicator) {
        typingIndicator.style.display = isVisible ? "block" : "none";
        scrollToBottom();
    }
}

// Voice input support using Web Speech API
if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        handleUserInput();
    };

    recognition.onerror = function (event) {
        console.error("Speech recognition error:", event.error);
    };

    if (voiceButton) {
        voiceButton.addEventListener("click", () => {
            recognition.start();
        });
    }
} else {
    console.warn("Web Speech API is not supported in this browser.");
    if (voiceButton) voiceButton.style.display = "none";
}
