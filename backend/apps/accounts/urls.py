from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    re_path(r'^auth/register/?$', views.RegisterView.as_view()),
    re_path(r'^auth/login/?$', views.LoginView.as_view()),
    re_path(r'^auth/google/?$', views.GoogleLoginView.as_view()),
    re_path(r'^auth/token/refresh/?$', TokenRefreshView.as_view()),

    # Email verification
    re_path(r'^auth/verify-email/?$', views.VerifyEmailView.as_view()),
    re_path(r'^auth/resend-verification/?$', views.ResendVerificationEmailView.as_view()),

    # Forgot / Reset password
    re_path(r'^auth/forgot-password/?$', views.ForgotPasswordView.as_view()),
    re_path(r'^auth/verify-reset-otp/?$', views.VerifyResetOTPView.as_view()),
    re_path(r'^auth/reset-password/?$', views.ResetPasswordView.as_view()),

    # User
    re_path(r'^users/profile/?$', views.ProfileView.as_view()),
    re_path(r'^users/profile/avatar/?$', views.AvatarUploadView.as_view()),
    re_path(r'^users/change-password/?$', views.ChangePasswordView.as_view()),
    re_path(r'^users/delete-account/?$', views.DeleteAccountView.as_view()),

    # Admin
    re_path(r'^admin/users/?$', views.AdminUserListView.as_view()),
    re_path(r'^admin/users/(?P<pk>\d+)/?$', views.AdminUserDetailView.as_view()),
]