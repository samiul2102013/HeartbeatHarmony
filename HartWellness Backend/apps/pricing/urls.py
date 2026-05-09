from django.urls import re_path
from . import views

urlpatterns = [
    # ── User / Mobile ─────────────────────────────────────────
    re_path(r'^pricing/plans/?$', views.PlanListView.as_view()),
    re_path(r'^pricing/subscribe/?$', views.SubscribeView.as_view()),
    re_path(r'^pricing/my-subscription/?$', views.MySubscriptionView.as_view()),
    re_path(r'^pricing/cancel/?$', views.CancelSubscriptionView.as_view()),
    re_path(r'^pricing/history/?$', views.MySubscriptionHistoryView.as_view()),

    # ── Admin ─────────────────────────────────────────────────
    re_path(r'^admin/pricing/plans/?$', views.AdminPlanListCreateView.as_view()),
    re_path(r'^admin/pricing/plans/(?P<pk>\d+)/?$', views.AdminPlanDetailView.as_view()),
    re_path(r'^admin/pricing/features/?$', views.AdminPlanFeatureListCreateView.as_view()),
    re_path(r'^admin/pricing/features/(?P<pk>\d+)/?$', views.AdminPlanFeatureDetailView.as_view()),
    re_path(r'^admin/pricing/subscriptions/?$', views.AdminSubscriptionListView.as_view()),
    re_path(r'^admin/pricing/subscriptions/(?P<pk>\d+)/?$', views.AdminSubscriptionDetailView.as_view()),
    re_path(r'^admin/pricing/stats/?$', views.AdminPricingStatsView.as_view()),
]