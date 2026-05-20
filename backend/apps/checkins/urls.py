from django.urls import re_path
from . import views

urlpatterns = [
    # User / Mobile
    re_path(r'^moods/?$', views.MoodListView.as_view()),
    re_path(r'^checkins/?$', views.CheckInCreateView.as_view()),
    re_path(r'^checkins/history/?$', views.CheckInHistoryView.as_view()),
    re_path(r'^checkins/(?P<pk>\d+)/?$', views.CheckInDetailView.as_view()),
    re_path(r'^checkins/dashboard/?$', views.DashboardStatsView.as_view()),
    re_path(r'^checkins/my-progress/?$', views.MyProgressView.as_view()),

    # Admin
    re_path(r'^admin/moods/?$', views.AdminMoodListCreateView.as_view()),
    re_path(r'^admin/moods/(?P<pk>\d+)/?$', views.AdminMoodDetailView.as_view()),
    re_path(r'^admin/checkins/?$', views.AdminCheckInListView.as_view()),
    re_path(r'^admin/checkins/(?P<pk>\d+)/?$', views.AdminCheckInDetailView.as_view()),
    re_path(r'^admin/dashboard/?$', views.AdminDashboardView.as_view()),
]
