from django.urls import re_path
from . import views

urlpatterns = [
    # User / Mobile
    re_path(r'^categories/?$', views.CategoryListView.as_view()),
    re_path(r'^habits/?$', views.HabitListCreateView.as_view()),
    re_path(r'^habits/daily-status/?$', views.DailyHabitStatusView.as_view()),
    re_path(r'^habits/(?P<pk>\d+)/?$', views.HabitDetailView.as_view()),
    re_path(r'^habits/(?P<pk>\d+)/done/?$', views.HabitMarkDoneView.as_view()),
    re_path(r'^habits/(?P<pk>\d+)/undo/?$', views.HabitUndoView.as_view()),

    # User templates
    re_path(r'^habit-templates/?$', views.HabitTemplateListView.as_view()),

    # Admin
    re_path(r'^admin/categories/?$', views.AdminCategoryListCreateView.as_view()),
    re_path(r'^admin/categories/(?P<pk>\d+)/?$', views.AdminCategoryDetailView.as_view()),
    re_path(r'^admin/habits/?$', views.AdminHabitListView.as_view()),
    re_path(r'^admin/habit-templates/?$', views.AdminHabitTemplateListCreateView.as_view()),
    re_path(r'^admin/habit-templates/(?P<pk>\d+)/?$', views.AdminHabitTemplateDetailView.as_view()),
]