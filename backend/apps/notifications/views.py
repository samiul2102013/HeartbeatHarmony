from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer
from apps.core.response_utils import StandardizedResponseMixin, success_response

class NotificationListView(StandardizedResponseMixin, generics.ListAPIView):
    """List all notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkAllReadView(StandardizedResponseMixin, APIView):
    """Mark all unread notifications as read for the user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        
        return success_response(
            {'updated_count': updated_count},
            message=f'Marked {updated_count} notifications as read.'
        )
