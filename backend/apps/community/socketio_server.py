import socketio
import asyncio
import urllib.parse
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from asgiref.sync import sync_to_async

# Create the Socket.IO async server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# The main asyncio event loop — captured on first connection
main_event_loop = None

# In-memory presence
_online_users = {}
# Mapping of sid to user object
_sid_to_user = {}

COMMUNITY_GROUP = 'heartbeat_community'

@sync_to_async
def get_user_from_token(token_key):
    from apps.accounts.models import User
    try:
        token = AccessToken(token_key)
        user_id = token['user_id']
        return User.objects.get(id=user_id)
    except (TokenError, User.DoesNotExist, Exception):
        return AnonymousUser()

@sync_to_async
def _save_community_msg(user, content):
    from .models import CommunityMessage
    return CommunityMessage.objects.create(sender=user, content=content)

@sync_to_async
def _save_dm(user, content, recipient_id):
    from .models import DirectMessage
    from apps.accounts.models import User
    try:
        receiver = User.objects.get(id=recipient_id)
        return DirectMessage.objects.create(
            sender=user, receiver=receiver, content=content,
        )
    except User.DoesNotExist:
        return None

@sync_to_async
def _mark_messages_read(user, other_id):
    from .models import DirectMessage
    return DirectMessage.objects.filter(
        sender_id=other_id,
        receiver=user,
        is_read=False,
    ).update(is_read=True)

def _dm_room_name(user_id, other_id):
    ids = sorted([user_id, other_id])
    return f'{ids[0]}_{ids[1]}'

@sio.event
async def connect(sid, environ, auth):
    # Capture the main event loop on first connection
    global main_event_loop
    if main_event_loop is None:
        main_event_loop = asyncio.get_running_loop()

    token = None
    
    # 1. Try auth payload
    if auth and isinstance(auth, dict) and 'token' in auth:
        token = auth['token']

    # 2. Try Authorization header
    if not token:
        headers = dict(environ.get('asgi.scope', {}).get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode()
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            
    # 3. Try query string
    if not token:
        query_string = environ.get('asgi.scope', {}).get('query_string', b'').decode()
        params = urllib.parse.parse_qs(query_string)
        if 'token' in params:
            token = params['token'][0]

    if not token:
        raise socketio.exceptions.ConnectionRefusedError('Authentication token missing')

    user = await get_user_from_token(token)
    if isinstance(user, AnonymousUser):
        raise socketio.exceptions.ConnectionRefusedError('Invalid token')

    _sid_to_user[sid] = user
    personal_group = f"user_{user.id}"

    await sio.enter_room(sid, COMMUNITY_GROUP)
    await sio.enter_room(sid, personal_group)

    _online_users[user.id] = {
        'id': user.id,
        'username': user.username,
        'avatar': user.avatar.url if user.avatar else None,
    }

    # Notify community
    await sio.emit('user_joined', {
        'room': 'community',
        'user_id': user.id,
        'username': user.username,
        'avatar': user.avatar.url if user.avatar else None,
    }, room=COMMUNITY_GROUP, skip_sid=sid)

    # Send online users to the connecting user
    await sio.emit('online_users', {
        'room': 'community',
        'users': list(_online_users.values()),
    }, to=sid)

@sio.event
async def disconnect(sid):
    user = _sid_to_user.pop(sid, None)
    if user:
        # Check if user has other sessions
        has_other_sessions = any(u.id == user.id for u in _sid_to_user.values())
        if not has_other_sessions:
            _online_users.pop(user.id, None)
            await sio.emit('user_left', {
                'room': 'community',
                'user_id': user.id,
                'username': user.username,
            }, room=COMMUNITY_GROUP)

@sio.event
async def message(sid, data):
    user = _sid_to_user.get(sid)
    if not user:
        return
        
    room = data.get('room')
    content = data.get('content', '').strip()

    if not content:
        await sio.emit('error', {'message': 'Message content is required'}, to=sid)
        return

    if room == 'community':
        msg = await _save_community_msg(user, content)
        await sio.emit('chat_message', {
            'room': 'community',
            'id': msg.id,
            'sender_id': user.id,
            'sender_username': user.username,
            'sender_avatar': user.avatar.url if user.avatar else None,
            'content': content,
            'file': None,
            'message_type': 'text',
            'created_at': msg.created_at.isoformat(),
        }, room=COMMUNITY_GROUP)
    elif room == 'dm':
        recipient_id = data.get('recipient_id')
        if not recipient_id:
            await sio.emit('error', {'message': 'Missing "recipient_id" for DM'}, to=sid)
            return
            
        recipient_id = int(recipient_id)
        msg = await _save_dm(user, content, recipient_id)
        if not msg:
            await sio.emit('error', {'message': 'Recipient not found'}, to=sid)
            return

        payload = {
            'room': 'dm',
            'room_name': _dm_room_name(user.id, recipient_id),
            'id': msg.id,
            'sender_id': user.id,
            'sender_username': user.username,
            'receiver_id': recipient_id,
            'content': content,
            'file': None,
            'message_type': 'text',
            'created_at': msg.created_at.isoformat(),
        }
        
        await sio.emit('direct_message', payload, room=f"user_{user.id}")
        await sio.emit('direct_message', payload, room=f"user_{recipient_id}")
    else:
        await sio.emit('error', {'message': 'Invalid "room" — use "community" or "dm"'}, to=sid)

@sio.event
async def typing(sid, data):
    user = _sid_to_user.get(sid)
    if not user:
        return
        
    room = data.get('room')
    if room == 'community':
        await sio.emit('user_typing', {
            'room': 'community',
            'user_id': user.id,
            'username': user.username,
        }, room=COMMUNITY_GROUP, skip_sid=sid)
    elif room == 'dm':
        rid = data.get('recipient_id')
        if not rid:
            return
        rid = int(rid)
        payload = {
            'room': 'dm',
            'room_name': _dm_room_name(user.id, rid),
            'user_id': user.id,
            'username': user.username,
        }
        await sio.emit('user_typing', payload, room=f"user_{user.id}", skip_sid=sid)
        await sio.emit('user_typing', payload, room=f"user_{rid}")

@sio.event
async def stop_typing(sid, data):
    user = _sid_to_user.get(sid)
    if not user:
        return
        
    room = data.get('room')
    if room == 'community':
        await sio.emit('user_stop_typing', {
            'room': 'community',
            'user_id': user.id,
            'username': user.username,
        }, room=COMMUNITY_GROUP, skip_sid=sid)
    elif room == 'dm':
        rid = data.get('recipient_id')
        if not rid:
            return
        rid = int(rid)
        payload = {
            'room': 'dm',
            'room_name': _dm_room_name(user.id, rid),
            'user_id': user.id,
            'username': user.username,
        }
        await sio.emit('user_stop_typing', payload, room=f"user_{user.id}", skip_sid=sid)
        await sio.emit('user_stop_typing', payload, room=f"user_{rid}")

def emit_to_user_sync(user_id, event, data):
    """Emit any event to a user's personal room from sync code.
    Safe to call from any thread. Falls back to detecting the running event loop.
    Silently drops if no event loop is available.
    """
    global main_event_loop
    loop = main_event_loop
    if loop is None or not loop.is_running():
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        if main_event_loop is None:
            main_event_loop = loop
    asyncio.run_coroutine_threadsafe(
        sio.emit(event, data, room=f"user_{user_id}"),
        loop
    )


def send_notification_sync(user_id, title, message, notification_type='system', notification_id=None):
    """Synchronous helper to emit a notification to a user's personal Socket.IO room."""
    payload = {
        'title': title,
        'message': message,
        'notification_type': notification_type,
    }
    if notification_id is not None:
        payload['id'] = notification_id
    emit_to_user_sync(user_id, 'notification', payload)


@sio.event
async def mark_read(sid, data):
    user = _sid_to_user.get(sid)
    if not user:
        return
        
    rid = data.get('recipient_id')
    if not rid:
        await sio.emit('error', {'message': 'Missing "recipient_id"'}, to=sid)
        return
        
    rid = int(rid)
    count = await _mark_messages_read(user, rid)
    if count:
        payload = {
            'room': 'dm',
            'room_name': _dm_room_name(user.id, rid),
            'reader_id': user.id,
            'reader_username': user.username,
            'count': count,
        }
        await sio.emit('messages_read', payload, room=f"user_{user.id}")
        await sio.emit('messages_read', payload, room=f"user_{rid}")
