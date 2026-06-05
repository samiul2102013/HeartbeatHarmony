from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import CommunityMessage, DirectMessage
from .serializers import (
    CommunityMessageSerializer,
    CommunityMessageCreateSerializer,
    DirectMessageSerializer,
    DirectMessageCreateSerializer,
    UserListSerializer,
)
from .pagination import CommunityPagination
from . import services
from apps.accounts.models import User
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, error_response, success_response


# ── Community Group ───────────────────────────────────────────

class CommunityMessageHistoryView(StandardizedResponseMixin, generics.ListAPIView):
    """
    REST: Load community message history (paginated).
    Real-time updates can also use Socket.IO.
    """
    serializer_class = CommunityMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommunityPagination

    def get_queryset(self):
        return CommunityMessage.objects.select_related('sender').order_by('-created_at')


class CommunityMessageCreateView(StandardizedResponseMixin, APIView):
    """POST a new community group message and broadcast to Socket.IO."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CommunityMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            file = request.FILES.get('file')
            msg = services.create_community_message(
                request.user,
                serializer.validated_data.get('content', ''),
                file=file,
            )
        except ValueError as exc:
            return error_response(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data.get('message_type'):
            msg.message_type = serializer.validated_data['message_type']
            msg.save(update_fields=['message_type'])

        services.broadcast_community_message(msg, request.user)
        data = CommunityMessageSerializer(msg, context={'request': request}).data
        return success_response(
            data=data,
            message='Community message sent',
            status_code=status.HTTP_201_CREATED,
        )


# ── Direct Messages ───────────────────────────────────────────

class UserListForDMView(StandardizedResponseMixin, generics.ListAPIView):
    """
    List of all other users to start a DM with.
    Excludes the current user.
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommunityPagination

    def get_queryset(self):
        return User.objects.filter(
            is_active=True
        ).exclude(id=self.request.user.id).order_by('username')


class DMThreadView(StandardizedResponseMixin, APIView):
    """
    GET: DM history with a user (marks received messages as read).
    POST: Send a DM to that user and broadcast via Socket.IO.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommunityPagination

    def get(self, request, user_id):
        user = request.user
        count = services.mark_dm_read(user, user_id)
        services.broadcast_messages_read(user, user_id, count)

        queryset = DirectMessage.objects.filter(
            Q(sender=user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=user)
        ).select_related('sender', 'receiver').order_by('created_at')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = DirectMessageSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, user_id):
        serializer = DirectMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            msg = services.create_direct_message(
                request.user,
                user_id,
                serializer.validated_data['content'],
            )
        except ValueError as exc:
            return error_response(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        services.broadcast_direct_message(msg, request.user, int(user_id))
        data = DirectMessageSerializer(msg).data
        return success_response(
            data=data,
            message='Direct message sent',
            status_code=status.HTTP_201_CREATED,
        )


class DMMarkReadView(StandardizedResponseMixin, APIView):
    """Mark all DMs from a user as read and notify via Socket.IO."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        count = services.mark_dm_read(request.user, user_id)
        services.broadcast_messages_read(request.user, user_id, count)
        return success_response(
            data={'count': count},
            message='Messages marked as read',
        )


class MyConversationsView(StandardizedResponseMixin, APIView):
    """
    List of all users the current user has had a DM conversation with.
    Shows latest message per conversation — for the community page inbox.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all user IDs we've talked to
        sent_to = DirectMessage.objects.filter(sender=user).values_list('receiver_id', flat=True)
        received_from = DirectMessage.objects.filter(receiver=user).values_list('sender_id', flat=True)
        contact_ids = set(list(sent_to) + list(received_from))

        conversations = []
        for other_id in contact_ids:
            other = User.objects.filter(id=other_id).first()
            if not other:
                continue

            last_msg = DirectMessage.objects.filter(
                Q(sender=user, receiver_id=other_id) |
                Q(sender_id=other_id, receiver=user)
            ).order_by('-created_at').first()

            unread_count = DirectMessage.objects.filter(
                sender_id=other_id, receiver=user, is_read=False
            ).count()

            conversations.append({
                'user': UserListSerializer(other, context={'request': request}).data,
                'last_message': last_msg.content if last_msg else '',
                'last_message_at': last_msg.created_at if last_msg else None,
                'unread_count': unread_count,
            })

        # Sort by most recent
        conversations.sort(
            key=lambda x: x['last_message_at'] or '',
            reverse=True
        )
        return Response(conversations)


# ── Admin ─────────────────────────────────────────────────────

class AdminCommunityMessageListView(StandardizedResponseMixin, generics.ListAPIView):
    queryset = CommunityMessage.objects.select_related('sender').order_by('-created_at')
    serializer_class = CommunityMessageSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None


class AdminCommunityMessageDeleteView(StandardizedResponseMixin, generics.DestroyAPIView):
    queryset = CommunityMessage.objects.all()
    serializer_class = CommunityMessageSerializer
    permission_classes = [IsAdminRole]  