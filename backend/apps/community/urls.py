from django.urls import re_path
from . import views

urlpatterns = [
    # Community group
    re_path(r'^community/messages/?$', views.CommunityMessageHistoryView.as_view()),
    re_path(r'^community/messages/create/?$', views.CommunityMessageCreateView.as_view()),

    # Direct messages
    re_path(r'^community/users/?$', views.UserListForDMView.as_view()),
    re_path(r'^community/dm/(?P<user_id>\d+)/?$', views.DMThreadView.as_view()),
    re_path(r'^community/conversations/?$', views.MyConversationsView.as_view()),
]