from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.NotificationListView.as_view()),
    re_path(r'^(?P<pk>\d+)/read/?$', views.NotificationMarkReadView.as_view()),
    re_path(r'^read-all/?$', views.NotificationMarkAllReadView.as_view()),
]
