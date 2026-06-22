from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.core import views

@require_GET
def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('api/health/', health_check),
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/', include('apps.checkins.urls')),
    # Enabled app routes
    path('api/', include('apps.habits.urls')),
    # Future: study, community, pricing
    path('api/', include('apps.study.urls')),
    path('api/', include('apps.community.urls')),
    path('api/', include('apps.pricing.urls')),
    path('api/', include('apps.core.urls')),
    path('api/', include('apps.iap.urls')),
    path('privacy/', views.PrivacyPolicyPageView.as_view(), name='privacy-policy'),
    path('terms-condition/', views.TermsAndConditionsPageView.as_view(), name='terms-and-conditions'),
    path('delete-account/', views.DeleteAccountPolicyView.as_view(), name='delete-account-policy'),
    path('help-support/', views.HelpSupportContactView.as_view(), name='help-support'),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]