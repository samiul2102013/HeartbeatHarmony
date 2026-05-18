# Flutter Socket.IO Integration Context for AI Agents

**Objective:** Generate a fully working, professional, and modular Socket.IO integration for a Flutter mobile application communicating with a Python (ASGI) Socket.IO backend.

---

## 1. Backend Architecture Context

The backend uses `python-socketio` (Socket.IO v4/v5). 
- **Base URL:** `https://<api-domain>`
- **Transport:** WebSocket with polling fallback (`transports: ['websocket', 'polling']`).
- **Authentication:** Token-based. The JWT token MUST be passed in the HTTP Headers as `Authorization: Bearer <token>` during the initial connection.

### 1.1 Rooms and Routing
When a user connects, the backend automatically joins them to two global rooms:
1. `heartbeat_community`: For global community group chat.
2. `user_<user_id>`: A private room for receiving Direct Messages (DMs) globally, even if the user is not actively on the chat screen.

### 1.2 Emit Events (Flutter to Backend)
All outbound messages are sent using specific Socket.IO event names.

| Action | Event Name | Payload (JSON) |
| :--- | :--- | :--- |
| Send Community Message | `message` | `{"room": "community", "content": "Hello!"}` |
| Send Direct Message | `message` | `{"room": "dm", "recipient_id": 12, "content": "Hey!"}` |
| Start Typing (Community)| `typing` | `{"room": "community"}` |
| Stop Typing (Community) | `stop_typing` | `{"room": "community"}` |
| Start Typing (DM) | `typing` | `{"room": "dm", "recipient_id": 12}` |
| Stop Typing (DM) | `stop_typing` | `{"room": "dm", "recipient_id": 12}` |
| Mark DM as Read | `mark_read` | `{"recipient_id": 12}` |

### 1.3 Listen Events (Backend to Flutter)
The Flutter app must listen for these events using `socket.on(...)`.

- `online_users`: Sent once upon connection. Payload: `{"room": "community", "users": [...]}`
- `user_joined` / `user_left`: Payload: `{"room": "community", "user_id": 1, "username": "..."}`
- `chat_message`: New community message. Payload: `{"room": "community", "sender_id": 1, "content": "..."}`
- `direct_message`: New DM. Payload: `{"room": "dm", "room_name": "1_12", "sender_id": 1, "content": "..."}`
- `user_typing` / `user_stop_typing`: Payload: `{"room": "dm", "room_name": "1_12", "user_id": 1, "username": "..."}`
- `messages_read`: Payload: `{"room": "dm", "room_name": "1_12", "reader_id": 1, "count": 2}`
- `error`: Payload: `{"message": "Error description"}`

---

## 2. Flutter Implementation Requirements

AI Agent, please adhere strictly to the following architectural guidelines when generating the Flutter code:

### 2.1 Dependency
Use `socket_io_client: ^2.0.3` (or the latest stable version).

### 2.2 Modular Architecture
Implement a clear separation of concerns:
1. **`SocketService` (Singleton or global Provider):** Responsible ONLY for the raw `IO.Socket` connection, managing the connection lifecycle, reconnect logic, and exposing Dart `Stream`s for incoming events.
2. **`ChatRepository` (Optional/Recommended):** Acts as an intermediary, parsing raw JSON from the `SocketService` into Dart Data Models (`ChatMessage`, `User`, etc.).
3. **State Management (Riverpod / Bloc / GetX / Provider):** Consumes the Streams from the `SocketService` and updates the UI state.
    - **Global Listener:** Ensure DMs (`direct_message` events) are listened to globally at the root of the app. This allows the app to update unread badges or trigger local notifications even if the user is on the Home screen.

### 2.3 Required Boilerplate Code Structure
Please generate the code following this structure:

#### Step 1: Initialization & Connection
Generate the `SocketService` class with an `initSocket(String token)` method. 
Ensure the socket is configured perfectly for the backend:
```dart
socket = IO.io('https://<api-domain>', IO.OptionBuilder()
    .setTransports(['websocket', 'polling'])
    .setExtraHeaders({'Authorization': 'Bearer $token'})
    .disableAutoConnect()
    .build()
);
socket.connect();
```

#### Step 2: Stream Controllers
Instead of passing UI callbacks deep into the service layer, expose `StreamController`s.
```dart
final _communityMessageController = StreamController<Map<String, dynamic>>.broadcast();
Stream<Map<String, dynamic>> get communityMessageStream => _communityMessageController.stream;

// Inside socket.on('chat_message', (data) => _communityMessageController.add(data));
```

#### Step 3: Outbound Methods
Create strict, typed methods in the `SocketService` for emitting events.
```dart
void sendDirectMessage({required int recipientId, required String content}) {
  socket.emit('message', {
    'room': 'dm',
    'recipient_id': recipientId,
    'content': content,
  });
}
```

#### Step 4: Error Handling & Lifecycle
Include standard event listeners for `onConnect`, `onDisconnect`, `onConnectError`, and the custom `error` event. Add logic to attempt reconnection if the socket drops.

---

## 3. Final Output Generation Request

AI Agent, when the user provides you with this file, you must output:
1. The complete `SocketService.dart` file (with all streams, connect, and emit methods).
2. The associated Dart Data Models (e.g., `MessageModel.dart`).
3. A sample State Management snippet showing how to listen to the `SocketService` globally to handle incoming direct messages and update unread counts gracefully.
