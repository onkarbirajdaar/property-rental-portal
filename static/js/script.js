const chatLauncher = document.getElementById("chatLauncher");
const chatWindow = document.getElementById("propertyChat");
const chatClose = document.getElementById("chatClose");

if (chatLauncher && chatWindow) {

    chatLauncher.addEventListener("click", () => {
        chatWindow.classList.toggle("d-none");
    });

}

if (chatClose && chatWindow) {

    chatClose.addEventListener("click", () => {
        chatWindow.classList.add("d-none");
    });

}