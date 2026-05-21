# Community & DM REST API

**Base URL:** `https://heartbitharmony.kodevio.com/api`

**Auth:** `Authorization: Bearer <access_token>` on every request.

All successful responses use:

```json
{
  "success": true,
  "message": "Success",
  "status": 200,
  "data": { ... },
  "metadata": { ... }
}
```

---

## Community group chat

### List messages (history)

`GET /community/messages?page=1&limit=10`

**Response `data`:** array of messages (newest first).

```json
{
  "id": 1,
  "sender": 5,
  "sender_username": "jane",
  "sender_avatar": "/media/avatars/jane.png",
  "content": "Hello!",
  "file": null,
  "message_type": "text",
  "created_at": "2026-05-21T10:00:00Z"
}
```

### Send community message

`POST /community/messages/create/`

**Body:**

```json
{
  "content": "Hello community!"
}
```

**Response:** `201` — created message in `data`. Also broadcasts `chat_message` on Socket.IO.

---

## Direct messages

### List users (start DM)

`GET /community/users?page=1&per_page=10`

### DM thread — history

`GET /community/dm/{user_id}/?page=1&limit=10`

Marks messages from `{user_id}` as read. Returns paginated DM history.

### DM thread — send message

`POST /community/dm/{user_id}/`

**Body:**

```json
{
  "content": "Hey there!"
}
```

**Response:** `201` — created message in `data`. Also broadcasts `direct_message` on Socket.IO to both users.

### Mark DMs as read (optional)

`POST /community/dm/{user_id}/read/`

**Response `data`:** `{ "count": 3 }`

---

## Conversations inbox

`GET /community/conversations/`

List of users you have chatted with, last message preview, unread count.

---

## Socket.IO (real-time, optional)

Connect to `https://heartbitharmony.kodevio.com` with the same JWT in headers.

You can use **REST only**, **Socket.IO only**, or **both** (REST send also broadcasts to connected clients).

| Action | Socket event |
|--------|----------------|
| Send community msg | `emit('message', { room: 'community', content: '...' })` |
| Send DM | `emit('message', { room: 'dm', recipient_id: 38, content: '...' })` |
| Listen community | `on('chat_message')` |
| Listen DM | `on('direct_message')` |

---

## Example curl

```bash
TOKEN="your_access_token"

# Send community message
curl -X POST "https://heartbitharmony.kodevio.com/api/community/messages/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from REST"}'

# Send DM to user 38
curl -X POST "https://heartbitharmony.kodevio.com/api/community/dm/38/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from REST"}'

# Load DM history
curl "https://heartbitharmony.kodevio.com/api/community/dm/38/?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```
