import socketio
import asyncio
import urllib.parse
from datetime import datetime
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from channels.db import database_sync_to_async

# Create the Socket.IO async server with Redis manager for multi-worker broadcasts
import os
_client_manager = None
try:
    redis_url = os.environ.get('REDIS_URL', 'redis://hartbeat-redis:6379/0')
    _client_manager = socketio.AsyncRedisManager(redis_url)
except Exception:
    pass

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    client_manager=_client_manager,
)

# The main asyncio event loop — captured on first connection
main_event_loop = None

# In-memory presence: user_id -> {id, username, avatar}
_online_users = {}
# Mapping of sid -> {id, username, avatar}
_sid_to_user = {}

COMMUNITY_GROUP = 'heartbeat_community'


def _user_info_from_model(user):
    from .services import _absolute_url
    return {
        'id': user.id,
        'username': user.username,
        'avatar': _absolute_url(user.avatar.url if user.avatar else None),
    }


@database_sync_to_async
def get_user_from_token(token_key):
    from apps.accounts.models import User
    try:
        token = AccessToken(token_key)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)
        return _user_info_from_model(user)
    except (TokenError, User.DoesNotExist, Exception):
        return None


@database_sync_to_async
def _mark_messages_read(user_id, other_id):
    from apps.accounts.models import User
    from .services import mark_dm_read
    user = User.objects.get(pk=user_id)
    return mark_dm_read(user, other_id)


@sio.event
async def connect(sid, environ, auth):
    global main_event_loop
    if main_event_loop is None:
        main_event_loop = asyncio.get_running_loop()

    token = None

    if auth and isinstance(auth, dict) and 'token' in auth:
        token = auth['token']

    if not token:
        headers = dict(environ.get('asgi.scope', {}).get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode()
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]

    if not token:
        query_string = environ.get('asgi.scope', {}).get('query_string', b'').decode()
        params = urllib.parse.parse_qs(query_string)
        if 'token' in params:
            token = params['token'][0]

    if not token:
        raise socketio.exceptions.ConnectionRefusedError('Authentication token missing')

    user_info = await get_user_from_token(token)
    if not user_info:
        raise socketio.exceptions.ConnectionRefusedError('Invalid token')

    _sid_to_user[sid] = user_info
    personal_group = f"user_{user_info['id']}"

    await sio.enter_room(sid, COMMUNITY_GROUP)
    await sio.enter_room(sid, personal_group)

    _online_users[user_info['id']] = {
        'id': user_info['id'],
        'username': user_info['username'],
        'avatar': user_info['avatar'],
    }

    await sio.emit('user_joined', {
        'room': 'community',
        'user_id': user_info['id'],
        'username': user_info['username'],
        'avatar': user_info['avatar'],
    }, room=COMMUNITY_GROUP, skip_sid=sid)

    await sio.emit('online_users', {
        'room': 'community',
        'users': list(_online_users.values()),
    }, to=sid)


@sio.event
async def disconnect(sid):
    user_info = _sid_to_user.pop(sid, None)
    if user_info:
        has_other_sessions = any(
            u['id'] == user_info['id'] for u in _sid_to_user.values()
        )
        if not has_other_sessions:
            _online_users.pop(user_info['id'], None)
            await sio.emit('user_left', {
                'room': 'community',
                'user_id': user_info['id'],
                'username': user_info['username'],
            }, room=COMMUNITY_GROUP)


def _community_payload(msg, user_info):
    from .services import _absolute_url
    return {
        'room': 'community',
        'id': msg.id,
        'sender_id': user_info['id'],
        'sender_username': user_info['username'],
        'sender_avatar': _absolute_url(user_info.get('avatar')),
        'content': msg.content,
        'file': _absolute_url(msg.file.url if msg.file else None),
        'message_type': msg.message_type,
        'created_at': msg.created_at.isoformat(),
    }


@sio.event
async def message(sid, data):
    user_info = _sid_to_user.get(sid)
    if not user_info:
        return

    room = data.get('room')
    content = data.get('content', '').strip()
    file_url = data.get('file', '').strip()

    if not content and not file_url:
        await sio.emit('error', {'message': 'Message content or file is required'}, to=sid)
        return

    try:
        if room == 'community':
            await sio.emit(
                'chat_message',
                {
                    'room': 'community',
                    'sender_id': user_info['id'],
                    'sender_username': user_info['username'],
                    'sender_avatar': user_info.get('avatar'),
                    'content': content,
                    'file': file_url or None,
                    'message_type': data.get('message_type', 'text'),
                    'created_at': datetime.utcnow().isoformat(),
                },
                room=COMMUNITY_GROUP,
            )
        elif room == 'dm':
            recipient_id = data.get('recipient_id')
            if not recipient_id:
                await sio.emit('error', {'message': 'Missing "recipient_id" for DM'}, to=sid)
                return

            recipient_id = int(recipient_id)
            from .services import dm_room_name
            payload = {
                'room': 'dm',
                'room_name': dm_room_name(user_info['id'], recipient_id),
                'sender_id': user_info['id'],
                'sender_username': user_info['username'],
                'sender_avatar': user_info.get('avatar'),
                'receiver_id': recipient_id,
                'content': content,
                'file': file_url or None,
                'message_type': data.get('message_type', 'text'),
                'created_at': datetime.utcnow().isoformat(),
            }
            await sio.emit('direct_message', payload, room=f"user_{user_info['id']}")
            await sio.emit('direct_message', payload, room=f"user_{recipient_id}")
        else:
            await sio.emit('error', {'message': 'Invalid "room" — use "community" or "dm"'}, to=sid)
    except ValueError as exc:
        await sio.emit('error', {'message': str(exc)}, to=sid)
    except Exception:
        await sio.emit('error', {'message': 'Failed to save message'}, to=sid)


@sio.event
async def typing(sid, data):
    user_info = _sid_to_user.get(sid)
    if not user_info:
        return

    room = data.get('room')
    if room == 'community':
        await sio.emit('user_typing', {
            'room': 'community',
            'user_id': user_info['id'],
            'username': user_info['username'],
        }, room=COMMUNITY_GROUP, skip_sid=sid)
    elif room == 'dm':
        rid = data.get('recipient_id')
        if not rid:
            return
        rid = int(rid)
        from .services import dm_room_name
        payload = {
            'room': 'dm',
            'room_name': dm_room_name(user_info['id'], rid),
            'user_id': user_info['id'],
            'username': user_info['username'],
        }
        await sio.emit('user_typing', payload, room=f"user_{user_info['id']}", skip_sid=sid)
        await sio.emit('user_typing', payload, room=f"user_{rid}")


@sio.event
async def stop_typing(sid, data):
    user_info = _sid_to_user.get(sid)
    if not user_info:
        return

    room = data.get('room')
    if room == 'community':
        await sio.emit('user_stop_typing', {
            'room': 'community',
            'user_id': user_info['id'],
            'username': user_info['username'],
        }, room=COMMUNITY_GROUP, skip_sid=sid)
    elif room == 'dm':
        rid = data.get('recipient_id')
        if not rid:
            return
        rid = int(rid)
        from .services import dm_room_name
        payload = {
            'room': 'dm',
            'room_name': dm_room_name(user_info['id'], rid),
            'user_id': user_info['id'],
            'username': user_info['username'],
        }
        await sio.emit('user_stop_typing', payload, room=f"user_{user_info['id']}", skip_sid=sid)
        await sio.emit('user_stop_typing', payload, room=f"user_{rid}")


def broadcast_event_sync(room, event, data):
    """Emit an event to a Socket.IO room from sync code (e.g. REST views)."""
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
        sio.emit(event, data, room=room),
        loop,
    )


def emit_to_user_sync(user_id, event, data):
    """Emit any event to a user's personal room from sync code."""
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
        loop,
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
    user_info = _sid_to_user.get(sid)
    if not user_info:
        return

    rid = data.get('recipient_id')
    if not rid:
        await sio.emit('error', {'message': 'Missing "recipient_id"'}, to=sid)
        return

    rid = int(rid)
    count = await _mark_messages_read(user_info['id'], rid)
    if count:
        from .services import dm_room_name
        payload = {
            'room': 'dm',
            'room_name': dm_room_name(user_info['id'], rid),
            'reader_id': user_info['id'],
            'reader_username': user_info['username'],
            'count': count,
        }
        await sio.emit('messages_read', payload, room=f"user_{user_info['id']}")
        await sio.emit('messages_read', payload, room=f"user_{rid}")
