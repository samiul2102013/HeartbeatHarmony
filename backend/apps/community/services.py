"""Shared helpers for saving and broadcasting community chat messages."""

from django.conf import settings
from apps.accounts.models import User
from .models import CommunityMessage, DirectMessage


def _absolute_url(path):
    if not path:
        return None
    if path.startswith(('http://', 'https://', 'ftp://')):
        return path
    base = settings.API_BASE_URL.rstrip('/')
    return f"{base}/{path.lstrip('/')}"


def avatar_url(user):
    return _absolute_url(user.avatar.url if user.avatar else None)


def dm_room_name(user_id, other_id):
    ids = sorted([user_id, other_id])
    return f'{ids[0]}_{ids[1]}'


def community_message_payload(msg, user):
    return {
        'room': 'community',
        'id': msg.id,
        'sender_id': user.id,
        'sender_username': user.username,
        'sender_avatar': avatar_url(user),
        'content': msg.content,
        'file': _absolute_url(msg.file.url if msg.file else None),
        'message_type': msg.message_type,
        'created_at': msg.created_at.isoformat(),
    }


def direct_message_payload(msg, sender, recipient_id):
    return {
        'room': 'dm',
        'room_name': dm_room_name(sender.id, recipient_id),
        'id': msg.id,
        'sender_id': sender.id,
        'sender_username': sender.username,
        'receiver_id': recipient_id,
        'content': msg.content,
        'file': None,
        'message_type': 'text',
        'created_at': msg.created_at.isoformat(),
    }


def create_community_message(user, content, file=None):
    content = (content or '').strip()
    if not content and not file:
        raise ValueError('Message content or file is required')
    msg = CommunityMessage(sender=user, content=content)
    if file:
        msg.file = file
    msg.save()
    return msg


def create_direct_message(user, recipient_id, content):
    content = (content or '').strip()
    if not content:
        raise ValueError('Message content is required')
    try:
        receiver = User.objects.get(id=recipient_id, is_active=True)
    except User.DoesNotExist as exc:
        raise ValueError('Recipient not found') from exc
    if receiver.id == user.id:
        raise ValueError('Cannot send a direct message to yourself')
    return DirectMessage.objects.create(
        sender=user,
        receiver=receiver,
        content=content,
    )


def mark_dm_read(user, other_id):
    return DirectMessage.objects.filter(
        sender_id=other_id,
        receiver=user,
        is_read=False,
    ).update(is_read=True)


def broadcast_community_message(msg, user):
    from .socketio_server import broadcast_event_sync, COMMUNITY_GROUP

    broadcast_event_sync(
        COMMUNITY_GROUP,
        'chat_message',
        community_message_payload(msg, user),
    )


def broadcast_direct_message(msg, sender, recipient_id):
    from .socketio_server import broadcast_event_sync

    payload = direct_message_payload(msg, sender, recipient_id)
    broadcast_event_sync(f'user_{sender.id}', 'direct_message', payload)
    broadcast_event_sync(f'user_{recipient_id}', 'direct_message', payload)


def broadcast_messages_read(user, other_id, count):
    from .socketio_server import broadcast_event_sync

    if not count:
        return
    payload = {
        'room': 'dm',
        'room_name': dm_room_name(user.id, other_id),
        'reader_id': user.id,
        'reader_username': user.username,
        'count': count,
    }
    broadcast_event_sync(f'user_{user.id}', 'messages_read', payload)
    broadcast_event_sync(f'user_{other_id}', 'messages_read', payload)
