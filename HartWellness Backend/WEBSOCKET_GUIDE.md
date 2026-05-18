# Hartbeat Harmony: Socket.IO Architecture & Frontend Guide

We have migrated the backend from raw WebSockets (Django Channels) to **Socket.IO** (`python-socketio`). 

This document explains the new architecture and provides instructions for your frontend developer.

---

## 1. Connection & Authentication (Headers)

**Endpoint:**
`wss://<api-domain>/` or `https://<api-domain>/` (Socket.IO handles the protocol upgrade automatically).
By default, the client library will append `/socket.io/` to your connection URL.

### How to Pass the Token
You can pass the token in one of two ways:

1. **Authorization Header (Recommended)**
   Pass the JWT token in the `extraHeaders` of the Socket.IO connection options:
   `Authorization: Bearer <your_token>`

2. **Auth Payload**
   Pass the token in the `auth` dictionary:
   `auth: { "token": "<your_token>" }`

### Groups & Rooms
- **On Connect:** The backend automatically adds the user's connection to two Socket.IO "rooms":
  1. `heartbeat_community`: The global room for all community messages.
  2. `user_<user_id>`: A personal, global notification room for the specific user.
- **On Disconnect:** The backend removes the user and broadcasts a `user_left` event to the community.

---

## 2. Client-to-Server Actions (Emit)

The frontend uses `socket.emit('event_name', data)` to send messages.

### Community Actions
```javascript
// Send a message
socket.emit('message', { "room": "community", "content": "Hello community!" });

// Typing indicators
socket.emit('typing', { "room": "community" });
socket.emit('stop_typing', { "room": "community" });
```

### Direct Message Actions
```javascript
// Send a DM message
socket.emit('message', { "room": "dm", "recipient_id": 12, "content": "Hey User 12!" });

// Typing indicators
socket.emit('typing', { "room": "dm", "recipient_id": 12 });
socket.emit('stop_typing', { "room": "dm", "recipient_id": 12 });

// Mark messages as read (Triggers blue ticks for the sender)
socket.emit('mark_read', { "recipient_id": 12 });
```

---

## 3. Server-to-Client Events (Listen)

The frontend listens for events using `socket.on('event_name', callback)`.

### Community Events
- `online_users`: Sent once on connection. Contains a list of online users.
- `user_joined` / `user_left`: Broadcast when someone connects/disconnects.
- `chat_message`: Broadcast when a new community message is sent.
- `user_typing` / `user_stop_typing`: Broadcast when someone is typing.

### Direct Message Events
- `direct_message`: A new DM. Contains `sender_id`, `receiver_id`, `content`, `room_name`, etc.
- `user_typing` / `user_stop_typing`: Partner typing status.
- `messages_read`: Partner has read your messages. Contains `count` and `reader_id`.

---

## 4. Example: Connecting from Frontend

### Flutter (`socket_io_client`)
```dart
import 'package:socket_io_client/socket_io_client.dart' as IO;

// 1. Initialize Socket
IO.Socket socket = IO.io('https://<api-domain>', 
  IO.OptionBuilder()
      .setTransports(['websocket']) // for Flutter or Web
      .setExtraHeaders({'Authorization': 'Bearer $token'}) // Passing token in Header
      .build()
);

// 2. Connect
socket.connect();

// 3. Listen to events
socket.onConnect((_) {
  print('Connected to Socket.IO!');
});

socket.on('chat_message', (data) {
  print('New community message: ${data['content']}');
});

socket.on('direct_message', (data) {
  print('New DM from ${data['sender_username']}: ${data['content']}');
});

// 4. Send events
socket.emit('message', {
  'room': 'dm',
  'recipient_id': 12,
  'content': 'Hello from Flutter Socket.IO!',
});
```

### React/JS (`socket.io-client`)
```javascript
import { io } from "socket.io-client";

// 1. Initialize Socket
const socket = io("https://<api-domain>", {
  extraHeaders: {
    Authorization: `Bearer ${token}`
  }
});

// 2. Listen to events
socket.on("connect", () => {
  console.log("Connected to Socket.IO!");
});

socket.on("chat_message", (data) => {
  console.log("Community message:", data);
});

// 3. Send events
socket.emit("message", {
  room: "community",
  content: "Hello from React!"
});
```
