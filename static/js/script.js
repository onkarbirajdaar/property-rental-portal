document.addEventListener("DOMContentLoaded", () => {
    function getCookie(name) {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const [key, value] = cookie.trim().split("=");

        if (key === name) {
            return decodeURIComponent(value);
        }
    }

    return null;
}
    const launcher = document.getElementById("chatLauncher");
    const chat = document.getElementById("propertyChat");
    const closeButton = document.getElementById("chatClose");
    const messagesContainer = document.getElementById("chatMessages");
    const form = document.getElementById("chatForm");
    const input = document.getElementById("chatInput");

    if (!launcher || !chat || !form || !input) {
        return;
    }

    const conversationId = chat.dataset.conversationId;
    const currentUserId = Number(chat.dataset.userId);
    const websocketScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(
        `${websocketScheme}://${window.location.host}/ws/chat/${conversationId}/`,
    );

    async function loadMessages() {
        try {
            const response = await fetch(
                `/chat/conversation/${conversationId}/messages/`
            );

            if (!response.ok) {
                throw new Error("failed to load messages");
            }

            const data = await response.json();

            messagesContainer.innerHTML = "";

            if (data.messages.length === 0) {
                messagesContainer.innerHTML = `
                    <div class="chat-empty">
                        <i class="bi bi-chat-dots"></i>
                        <p>start a conversation with the property owner.</p>
                    </div>
                `;

                return;
            }

            data.messages.forEach(renderMessage);

            messagesContainer.scrollTop =
                messagesContainer.scrollHeight;

        } catch (error) {
            console.error("error loading messages:", error);
        }
    }

    function renderMessage(message) {
        const messageElement = document.createElement("div");

        const isOwnMessage = message.sender_id === currentUserId;
        messageElement.classList.add(
            "chat-message",
            isOwnMessage ? "chat-message-own" : "chat-message-other",
        );

        const meta = document.createElement("div");
        meta.className = "chat-message-meta";

        const author = document.createElement("strong");
        author.textContent = message.sender;

        const time = document.createElement("time");
        time.textContent = new Date(message.created_at).toLocaleTimeString(
            [],
            {
                hour: "numeric",
                minute: "2-digit",
            },
        );

        const body = document.createElement("div");
        body.className = "chat-message-body";
        body.textContent = message.body;

        meta.append(author, time);
        messageElement.append(meta, body);

        messagesContainer.appendChild(messageElement);
    }

    launcher.addEventListener("click", () => {
        chat.classList.toggle("d-none");

        if (!chat.classList.contains("d-none")) {
            loadMessages();
        }
    });

    closeButton.addEventListener("click", () => {
        chat.classList.add("d-none");
    });

    socket.addEventListener("message", (event) => {
        const data = JSON.parse(event.data);

        if (data.error) {
            console.error("failed to send message:", data.error);
            return;
        }

        renderMessage(data);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });

    form.addEventListener("submit", (event) => {
    event.preventDefault();

    const body = input.value.trim();

    if (!body) {
        return;
    }

    if (socket.readyState !== WebSocket.OPEN) {
        console.error("chat websocket is not connected");
        return;
    }

    socket.send(JSON.stringify({ body }));
    input.value = "";
    input.focus();
});

    window.addEventListener("beforeunload", () => socket.close());
});