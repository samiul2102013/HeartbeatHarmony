from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response

from .models import ContentPage, FAQ, SupportContact
from .serializers import (
	ContentPageSerializer, AdminContentPageSerializer,
	FAQSerializer, AdminFAQSerializer,
	SupportContactSerializer, AdminSupportContactSerializer
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


# ── Admin Views ───────────────────────────────────────────────

class AdminContentPageListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
	serializer_class = AdminContentPageSerializer
	permission_classes = [IsAdminRole]
	pagination_class = None

	def get_queryset(self):
		ContentPage.ensure_defaults()
		return ContentPage.objects.all().order_by('slug')


class AdminContentPageDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
	serializer_class = AdminContentPageSerializer
	permission_classes = [IsAdminRole]
	lookup_field = 'slug'

	def get_queryset(self):
		ContentPage.ensure_defaults()
		return ContentPage.objects.all()


class AdminFAQListCreateView(StandardizedResponseMixin, generics.ListCreateAPIView):
	serializer_class = AdminFAQSerializer
	permission_classes = [IsAdminRole]
	pagination_class = None
	queryset = FAQ.objects.all().order_by('order')


class AdminFAQDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
	serializer_class = AdminFAQSerializer
	permission_classes = [IsAdminRole]
	queryset = FAQ.objects.all()


class AdminSupportContactView(StandardizedResponseMixin, APIView):
	permission_classes = [IsAdminRole]

	def get(self, request):
		contact = SupportContact.objects.first()
		if contact:
			return success_response(AdminSupportContactSerializer(contact).data)
		return success_response({})

	def post(self, request):
		contact = SupportContact.objects.first()
		serializer = AdminSupportContactSerializer(contact, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return success_response(serializer.data)
		return success_response(serializer.errors, status_code=400)
