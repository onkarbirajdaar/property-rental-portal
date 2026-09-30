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

    if (!chat || !form || !input || !messagesContainer) {
        return;
    }

    const conversationId = chat.dataset.conversationId;
    const currentUserId = Number(chat.dataset.userId);
    const websocketScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const statusElement = document.getElementById("chatStatus");
    let socket;
    let reconnectTimer;
    let reconnectAttempt = 0;
    let shouldReconnect = true;

    function updateStatus(status) {
        if (statusElement) {
            statusElement.textContent = status;
        }
    }

    function connectSocket() {
        updateStatus(reconnectAttempt ? "reconnecting" : "connecting");
        socket = new WebSocket(
            `${websocketScheme}://${window.location.host}/ws/chat/${conversationId}/`,
        );

        socket.addEventListener("open", () => {
            reconnectAttempt = 0;
            updateStatus("online");
        });

        socket.addEventListener("close", () => {
            updateStatus("offline");
            if (!shouldReconnect) {
                return;
            }

            reconnectAttempt += 1;
            clearTimeout(reconnectTimer);
            reconnectTimer = setTimeout(connectSocket, 2000);
        });

        socket.addEventListener("error", () => {
            updateStatus("offline");
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
    }

    connectSocket();

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

    if (launcher) {
        launcher.addEventListener("click", () => {
            chat.classList.toggle("d-none");

            if (!chat.classList.contains("d-none")) {
                loadMessages();
            }
        });
    } else {
        loadMessages();
    }

    if (closeButton) {
        closeButton.addEventListener("click", () => {
            chat.classList.add("d-none");
        });
    }

    form.addEventListener("submit", (event) => {
    event.preventDefault();

    const body = input.value.trim();

    if (!body) {
        return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        updateStatus("connecting");
        return;
    }

    socket.send(JSON.stringify({ body }));
    input.value = "";
    input.focus();
});

    window.addEventListener("beforeunload", () => {
        shouldReconnect = false;
        clearTimeout(reconnectTimer);
        socket.close();
    });
});