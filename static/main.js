const Action = Object.freeze({
    message: 'message',
    participants: 'participants',
    history: 'history'
});

let ws;
let username = localStorage.getItem('username');
let chatId = localStorage.getItem('chatId');
let chat = document.getElementById('chat');
let chatInput = document.getElementById('chatInput');
let chatIdInput = document.getElementById('chatIdInput');
let usernameInput = document.getElementById('usernameInput');

if (chatId !== null) {chatIdInput.value = chatId}
if (username !== null) {usernameInput.value = username}

chatInput.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    handleChatMessage();
  }
});

const connect = () => {
    if (usernameInput.value !== "") {
        let chatId = chatIdInput.value === null ? 'default' : chatIdInput.value
        localStorage.setItem('chatId', chatId);
        localStorage.setItem('username', usernameInput.value);
        username = usernameInput.value;
        ws = new WebSocket(`ws://localhost:8080/ws/chat/${chatId}/${username}`)
        ws.onmessage = (event) => {
            handleEvent(event);
        }
        usernameInput.disabled = true;
        chatIdInput.disabled = true;
        chatInput.removeAttribute('disabled');

        document.getElementById('connect').disabled = true;
        document.getElementById('sendMessage').removeAttribute('disabled');
    }
    else {
        alert('Please enter a username')
    }
}

const handleEvent = (event) => {
    event = JSON.parse(event.data)
    console.log(event)
    switch (event.event_type) {
        case Action.history:
            renderHistory(event.messages)
            break;
        case Action.message:
            chat.innerHTML = otherChatMessage(event.username, event.message) + chat.innerHTML;
            break;
        case Action.participants:
            renderParticipants(event.participants)
            break;
        default:
            console.log(`Event type ${event.event_type} not supported`)
    }
}

const renderHistory = (messages) => {
    messages.forEach((message) => {
        if (message.username === username) {
            chat.innerHTML = myChatMessage(message.username, message.message) + chat.innerHTML
        } else {
            chat.innerHTML = otherChatMessage(message.username, message.message) + chat.innerHTML
        }
    })
}

const handleChatMessage = () => {
  if (chatInput.value !== "") {
    chat.innerHTML = myChatMessage('You', chatInput.value) + chat.innerHTML
    let msg = JSON.stringify({message: chatInput.value, username: username, timestamp: Date.now()})
    ws.send(msg)
    chatInput.value = null
  }
};

const myChatMessage = (username, msg) => {
    return `
    <div class="pl-4 row">
      <div class="col-md-10 alert alert-dark">
        ${msg}
      </div>
      <div class="col-md-2 pb-3">
          <div class="col-md-12">
            <p class="text-center"><strong>${username}</strong></p>
          </div>
          <div class="col-md-12">
            <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp" class="img-thumbnail rounded-circle shadow-4" alt="Avatar">
          </div>
      </div>
    </div>
    <div class="border-top my-3"></div>
    `
}

const otherChatMessage = (username, msg) => {
    return `
    <div class="pr-4 row">
      <div class="col-md-2 pb-3">
          <div class="col-md-12">
            <p class="pr-10 text-left"><strong>${username}</strong></p>
          </div>
          <div class="col-md-12">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava1-bg.webp" class="img-thumbnail rounded-circle shadow-4" alt="Avatar">
          </div>
      </div>
      <div class="col-md-10 alert alert-light" role="alert">
        ${msg}
      </div>
    </div>
    <div class="border-top my-3"></div>
    `
}

const renderParticipants = (participants) => {
    let participantList = document.getElementById('participantList')
    participantList.innerHTML = ''
    participants.forEach((participant) => {
        participantList.innerHTML += `<p><small>${participant}</small></p>`
    })
}