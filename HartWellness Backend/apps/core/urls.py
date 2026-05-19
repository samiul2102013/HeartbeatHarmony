from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^content/help-support/?$', views.HelpSupportPageView.as_view()),
    re_path(r'^content/privacy-policy/?$', views.PrivacyPolicyPageView.as_view()),
    
    re_path(r'^admin/content-pages/?$', views.AdminContentPageListCreateView.as_view()),
    re_path(r'^admin/content-pages/(?P<slug>[-\w]+)/?$', views.AdminContentPageDetailView.as_view()),
    
    re_path(r'^admin/faqs/?$', views.AdminFAQListCreateView.as_view()),
    re_path(r'^admin/faqs/(?P<pk>\d+)/?$', views.AdminFAQDetailView.as_view()),
    
    re_path(r'^admin/support-contact/?$', views.AdminSupportContactView.as_view()),
    
    re_path(r'^config/?$', views.AppConfigView.as_view()),
]