import uuid
from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import User
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    ChangePasswordSerializer, AdminUserSerializer,
    VerifyEmailSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    CustomTokenObtainPairSerializer,
)
from .utils import (
    send_verification_email,
    send_password_reset_email,
    generate_verification_token,
    generate_verification_code,
)
from apps.core.permissions import IsAdminRole
from apps.core.response_utils import StandardizedResponseMixin, success_response, error_response
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

PASSWORD_RESET_EXPIRY_HOURS = 1


class RegisterView(StandardizedResponseMixin, generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def perform_create(self, serializer):
        user = serializer.save()
        updated_fields = []
        if not user.email_verify_token:
            user.email_verify_token = generate_verification_token()
            updated_fields.append('email_verify_token')
        if not user.email_verification_code:
            user.email_verification_code = generate_verification_code()
            updated_fields.append('email_verification_code')
            user.email_verification_code_created = timezone.now()
            updated_fields.append('email_verification_code_created')
        if updated_fields:
            user.save(update_fields=updated_fields)
        # Send verification email right after registration
        send_verification_email(user, self.request)


class LoginView(StandardizedResponseMixin, APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data.get('_user')
        
        # Check if user is verified
        if not user.email_verified:
            # Send OTP for verification
            from .utils import send_login_verification_otp
            send_login_verification_otp(user)
            return success_response({
                'detail': 'Please verify your email with the OTP sent to your email.',
                'email': user.email,
                'verified': False
            })
        
        # User is verified, return tokens
        return success_response({
            'user': UserProfileSerializer(user).data,
            'refresh': validated_data['refresh'],
            'access': validated_data['access'],
        })


class ProfileView(StandardizedResponseMixin, generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user


class AvatarUploadView(StandardizedResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if 'avatar' not in request.FILES:
            return error_response('No avatar file provided.', status_code=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save(update_fields=['avatar'])
        
        avatar_url = request.build_absolute_uri(user.avatar.url)
        return success_response({
            'detail': 'Avatar uploaded successfully.',
            'avatar_url': avatar_url
        })


class ChangePasswordView(StandardizedResponseMixin, APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return success_response({'detail': 'Password updated successfully.'})


# ── Email Verification ────────────────────────────────────────

class VerifyEmailView(StandardizedResponseMixin, APIView):
    """
    User clicks link from email → hits this endpoint with token.
    Works for both mobile deep links and web.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = str(serializer.validated_data['token'])
        verification_method = serializer.validated_data.get('verification_method')
        email = serializer.validated_data.get('email') or request.query_params.get('email')

        # Development bypass support: allow verifying when token equals DEV_BYPASS_VALUE
        # and ALLOW_DEV_BYPASS is enabled. This requires providing the user's email in
        # the request body and, if configured, the DEV_BYPASS_SECRET header.
        if getattr(settings, 'ALLOW_DEV_BYPASS', False):
            dev_value = getattr(settings, 'DEV_BYPASS_VALUE', '123456')
            dev_otp = getattr(settings, 'DEV_EMAIL_OTP', dev_value)
            dev_secret = getattr(settings, 'DEV_BYPASS_SECRET', '')
            header_secret = request.headers.get('X-DEV-BYPASS') or request.META.get('HTTP_X_DEV_BYPASS', '')
            if token in {dev_value, dev_otp}:
                if not email:
                    return error_response('Email is required for dev bypass.', status_code=status.HTTP_400_BAD_REQUEST)
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return error_response('User not found for provided email.', status_code=status.HTTP_400_BAD_REQUEST)

                if dev_secret and header_secret != dev_secret:
                    return error_response('Invalid dev bypass secret.', status_code=status.HTTP_403_FORBIDDEN)

                logger.warning('DEV_BYPASS used for email verification: %s from %s', email, request.META.get('REMOTE_ADDR'))
            else:
                user = None
        else:
            user = None

        if user is None:
            if verification_method == 'otp':
                if not email:
                    return error_response(
                        'Email is required when verifying with an OTP.',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    user = User.objects.get(email=email, email_verification_code=token)
                except User.DoesNotExist:
                    return error_response(
                        'Invalid verification code for this email.',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            else:
                try:
                    user = User.objects.get(email_verify_token=token)
                except User.DoesNotExist:
                    return error_response(
                        'Invalid verification code or token.',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

        if user.email_verified:
            return error_response(
                'Email already verified.',
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user.email_verified = True
        user.email_verify_token = None
        user.email_verification_code = None
        user.email_verification_code_created = None
        user.save(update_fields=['email_verified', 'email_verify_token', 'email_verification_code', 'email_verification_code_created'])
        return success_response({'detail': 'Email verified successfully.'})


class ResendVerificationEmailView(StandardizedResponseMixin, APIView):
    """Authenticated user can resend their verification email."""

    def post(self, request):
        user = request.user
        if user.email_verified:
            return error_response(
                'Email is already verified.',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        user.email_verify_token = generate_verification_token()
        user.email_verification_code = generate_verification_code()
        user.email_verification_code_created = timezone.now()
        user.save(update_fields=['email_verify_token', 'email_verification_code', 'email_verification_code_created'])
        send_verification_email(user, request)
        return success_response({'detail': 'Verification email sent.'})


# ── Forgot / Reset Password ───────────────────────────────────

class ForgotPasswordView(StandardizedResponseMixin, APIView):
    """
    Takes email → generates reset token → sends reset email.
    Always returns 200 to prevent user enumeration.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        # Always return 200 even if email not found
        if not serializer.is_valid():
            return success_response({'detail': 'If this email exists, a reset OTP will be sent.'})

        email = serializer.validated_data['email']
        reset_token = None
        try:
            user = User.objects.get(email=email)
            user.password_reset_token = str(uuid.uuid4())
            user.password_reset_otp = generate_verification_code()
            user.password_reset_token_created = timezone.now()
            user.password_reset_otp_created = timezone.now()
            user.save(update_fields=['password_reset_token', 'password_reset_token_created', 'password_reset_otp', 'password_reset_otp_created'])
            reset_token = user.password_reset_token
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass  # Silent — don't leak user existence

        response_data = {'detail': 'If this email exists, a reset token will be sent.'}
        if reset_token:
            response_data['token'] = reset_token
        return success_response(response_data)


class VerifyResetOTPView(StandardizedResponseMixin, APIView):
    """
    Step 2: Verify the OTP sent to the user's email before allowing password change.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return error_response('Email and OTP are required.', status_code=status.HTTP_400_BAD_REQUEST)

        # Dev bypass logic
        is_dev_bypass = False
        if getattr(settings, 'ALLOW_DEV_BYPASS', False):
            dev_otp = getattr(settings, 'DEV_EMAIL_OTP', '123456')
            if otp == dev_otp:
                is_dev_bypass = True

        try:
            if is_dev_bypass:
                user = User.objects.get(email=email)
            else:
                user = User.objects.get(email=email, password_reset_otp=otp)
                if user.password_reset_otp_created:
                    expiry = user.password_reset_otp_created + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS)
                    if timezone.now() > expiry:
                        return error_response('OTP has expired.', status_code=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return error_response('Invalid email or OTP.', status_code=status.HTTP_400_BAD_REQUEST)

        return success_response({'detail': 'OTP verified successfully.', 'email': email, 'otp': otp})


class ResetPasswordView(StandardizedResponseMixin, APIView):
    """
    Takes token + new_password → validates token expiry → resets password.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = str(serializer.validated_data.get('token') or '')
        email = serializer.validated_data.get('email')
        otp = serializer.validated_data.get('otp')
        new_password = serializer.validated_data['new_password']

        if token:
            try:
                user = User.objects.get(password_reset_token=token)
            except User.DoesNotExist:
                return error_response(
                    'Invalid or expired reset token.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        else:
            try:
                user = User.objects.get(email=email, password_reset_otp=otp)
            except User.DoesNotExist:
                return error_response(
                    'Invalid or expired reset OTP.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Check token expiry
        expiry = user.password_reset_token_created + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS)
        if timezone.now() > expiry:
            return error_response(
                'Reset token has expired. Please request a new one.',
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Set password
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_otp = None
        user.password_reset_otp_created = None
        user.password_reset_new_password = None
        user.password_reset_token_created = None
        user.save(update_fields=['password', 'password_reset_token', 'password_reset_otp', 'password_reset_otp_created', 'password_reset_new_password', 'password_reset_token_created'])

        return success_response({'detail': 'Password reset successfully. You can now log in.'})


# ── Admin Views ───────────────────────────────────────────────

class AdminUserListView(StandardizedResponseMixin, generics.ListAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['plan', 'is_active', 'role', 'email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name']


class AdminUserDetailView(StandardizedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]