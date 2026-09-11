from django.urls import re_path
from . import views

urlpatterns = [
    # User / Mobile
    re_path(r'^categories/?$', views.CategoryListView.as_view()),
    re_path(r'^habits/?$', views.HabitListCreateView.as_view()),
    re_path(r'^habits/reminders/today/?$', views.HabitReminderTodayView.as_view()),
    re_path(r'^habits/(?P<pk>\d+)/done/?$', views.HabitMarkDoneView.as_view()),

    # Admin
    re_path(r'^admin/categories/?$', views.AdminCategoryListCreateView.as_view()),
    re_path(r'^admin/categories/(?P<pk>\d+)/?$', views.AdminCategoryDetailView.as_view()),
    re_path(r'^admin/habits/?$', views.AdminHabitListView.as_view()),
    re_path(r'^admin/habits/(?P<pk>\d+)/?$', views.AdminHabitDetailView.as_view()),
    re_path(r'^admin/habit-materials/?$', views.HabitMaterialListCreateView.as_view()),
    re_path(r'^admin/habit-materials/(?P<pk>\d+)/?$', views.HabitMaterialDetailView.as_view()),
    re_path(r'^admin/habit-materials/(?P<pk>\d+)/edit/?$', views.HabitMaterialEditView.as_view()),
    re_path(r'^admin/habit-materials/(?P<pk>\d+)/delete/?$', views.HabitMaterialDeleteView.as_view()),
]