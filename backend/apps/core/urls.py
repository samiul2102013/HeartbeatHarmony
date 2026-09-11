from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^config/?$', views.AppConfigView.as_view()),
    re_path(r'^content/help-support/?$', views.HelpSupportPageView.as_view()),
    re_path(r'^admin/content/terms-and-conditions/?$', views.AdminContentBySlugView.as_view(), {'slug': 'terms-of-service'}),
    re_path(r'^admin/content/privacy-policy/?$', views.AdminContentBySlugView.as_view(), {'slug': 'privacy-policy'}),
    re_path(r'^admin/content/account-deletion-policy/?$', views.AdminContentBySlugView.as_view(), {'slug': 'account-deletion-policy'}),
]