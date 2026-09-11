from django.shortcuts import get_object_or_404
from django.core.cache import caches
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response

from .models import ContentPage, FAQ, SupportContact
from .serializers import (
	ContentPageSerializer, AdminContentPageSerializer,
	FAQSerializer,
	SupportContactSerializer,
)


class PrivacyPolicyPageView(StandardizedResponseMixin, APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		ContentPage.ensure_defaults()
		page = get_object_or_404(ContentPage, slug='privacy-policy', is_active=True)
		return success_response(ContentPageSerializer(page).data)


class HelpSupportPageView(StandardizedResponseMixin, APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		contact = SupportContact.objects.first()
		contact_data = SupportContactSerializer(contact).data if contact else None
		faqs = FAQ.objects.filter(is_active=True).order_by('order')
		faqs_data = FAQSerializer(faqs, many=True).data

		return success_response({
			'contact': contact_data,
			'faqs': faqs_data,
		})


class TermsAndConditionsPageView(StandardizedResponseMixin, APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		ContentPage.ensure_defaults()
		page = get_object_or_404(ContentPage, slug='terms-of-service', is_active=True)
		return success_response(ContentPageSerializer(page).data)


class DeleteAccountPolicyView(StandardizedResponseMixin, APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		ContentPage.ensure_defaults()
		page = get_object_or_404(ContentPage, slug='account-deletion-policy', is_active=True)
		return success_response(ContentPageSerializer(page).data)


class AppConfigView(APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		cache = caches['default']
		cached = cache.get('app-config:v1')
		if cached is None:
			cached = {
				"app_update_config": {
					"current_versions": {
						"android": "1.0.0",
						"ios": "1.0.0"
					},
					"update_urls": {
						"android": "https://play.google.com/store/apps/details?id=YOUR_PACKAGE_NAME",
						"ios": "https://apps.apple.com/app/idYOUR_APP_ID"
					},
					"force_update": False,
					"update_policy": {
						"check_on_launch": True,
						"show_update_dialog": True,
						"skip_optional_update": True
					}
				}
			}
			cache.set('app-config:v1', cached, 3600)
		return Response(cached)


# ── Admin Views ───────────────────────────────────────────────

CONTENT_ADMIN_SLUGS = ['terms-of-service', 'privacy-policy', 'account-deletion-policy']


class AdminContentBySlugView(StandardizedResponseMixin, generics.RetrieveUpdateAPIView):
    serializer_class = AdminContentPageSerializer
    permission_classes = [IsAdminRole]
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get('slug')
        if slug not in CONTENT_ADMIN_SLUGS:
            from django.http import Http404
            raise Http404('Content page not found')
        ContentPage.ensure_defaults()
        return get_object_or_404(ContentPage, slug=slug)


class HelpSupportContactView(StandardizedResponseMixin, APIView):
	permission_classes = [permissions.AllowAny]

	def post(self, request):
		name = request.data.get('name', '').strip()
		email = request.data.get('email', '').strip()
		subject = request.data.get('subject', '').strip()
		description = request.data.get('description', '').strip()

		if not all([name, email, subject, description]):
			return success_response({'error': 'All fields are required.'}, status_code=400)

		send_mail(
			subject=f"[Help & Support] {subject}",
			message=(
				f"Name: {name}\n"
				f"Email: {email}\n"
				f"Subject: {subject}\n\n"
				f"Message:\n{description}"
			),
			from_email=settings.DEFAULT_FROM_EMAIL,
			recipient_list=['support@ICSNCardiology.org'],
			fail_silently=False,
		)

		return success_response({'message': 'Your message has been sent. We will get back to you soon.'})
