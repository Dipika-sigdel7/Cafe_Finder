/* =========================================================
   CAFE FINDER AI CHAT
========================================================= */

const aiChatButton = document.getElementById("aiChatButton");

const aiChatWindow = document.getElementById("aiChatWindow");

const aiChatClose = document.getElementById("aiChatClose");

const aiChatInput = document.getElementById("aiChatInput");

const aiChatSend = document.getElementById("aiChatSend");

const aiChatMessages =
    document.getElementById("aiChatMessages");

const aiTyping =
    document.getElementById("aiTyping");


/* =========================================================
   OPEN CHAT
========================================================= */

aiChatButton.addEventListener("click", function () {

    aiChatWindow.style.display = "flex";

    aiChatButton.style.display = "none";

    aiChatInput.focus();

});


/* =========================================================
   CLOSE CHAT
========================================================= */

aiChatClose.addEventListener("click", function () {

    aiChatWindow.style.display = "none";

    aiChatButton.style.display = "block";

});


/* =========================================================
   ADD MESSAGE
========================================================= */

function addMessage(message, sender) {

    const messageContainer =
        document.createElement("div");

    const messageText =
        document.createElement("div");


    if (sender === "user") {

        messageContainer.className = "user-message";

        messageText.className =
            "user-message-text";

    }

    else {

        messageContainer.className = "ai-message";

        messageText.className =
            "ai-message-text";

    }


    messageText.textContent = message;


    messageContainer.appendChild(messageText);


    aiChatMessages.appendChild(
        messageContainer
    );


    aiChatMessages.scrollTop =
        aiChatMessages.scrollHeight;

}


/* =========================================================
   SEND MESSAGE (UPDATED WITH FETCH)
========================================================= */

async function sendMessage() {

    const message = aiChatInput.value.trim();

    if (message === "") {
        return;
    }

    /* Show user's message and clear input */
    addMessage(message, "user");
    aiChatInput.value = "";

    /* Show typing indicator and scroll to bottom */
    aiTyping.style.display = "block";
    aiChatMessages.scrollTop = aiChatMessages.scrollHeight;

    try {
        /* Make a POST request to your Flask backend */
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        /* Hide typing indicator */
        aiTyping.style.display = "none";

        /* Show the AI's real response */
        if (response.ok) {
            // Assuming your Flask app sends back JSON like: { "reply": "Hello!" }
            addMessage(data.reply, "ai");
        } else {
            addMessage("Oops! The server returned an error.", "ai");
        }

    } catch (error) {
        console.error("Chat Error:", error);
        aiTyping.style.display = "none";
        addMessage("Sorry, I can't connect to the server right now.", "ai");
    }
}


/* =========================================================
   SEND BUTTON
========================================================= */

aiChatSend.addEventListener(
    "click",
    sendMessage
);


/* =========================================================
   ENTER KEY
========================================================= */

aiChatInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    }
);