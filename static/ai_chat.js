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
   SEND MESSAGE
========================================================= */

function sendMessage() {

    const message =
        aiChatInput.value.trim();


    if (message === "") {

        return;

    }


    /* Show user's message */

    addMessage(message, "user");


    /* Clear input */

    aiChatInput.value = "";


    /* Show typing indicator */

    aiTyping.style.display = "block";


    aiChatMessages.scrollTop =
        aiChatMessages.scrollHeight;


    /*
       TEMPORARY RESPONSE

       We will replace this with
       Flask + AI API later.
    */

    setTimeout(function () {

        aiTyping.style.display = "none";

        addMessage(
            "I'm your Cafe Finder AI assistant. I can help you find cafes, menus, offers and other information.",
            "ai"
        );

    }, 1000);

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