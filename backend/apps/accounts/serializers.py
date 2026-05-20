from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'password']

    def validate_email(self, value):
        return value.lower().strip()

    def create(self, validated_data):
        email = validated_data.get('email')
        
        # If frontend didn't pass a username, generate one from email
        if not validated_data.get('username'):
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            validated_data['username'] = username

        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    check_ins = serializers.SerializerMethodField()
    quiz_test = serializers.SerializerMethodField()
    Rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'avatar', 'plan', 'role', 'email_verified', 'created_at',
                  'check_ins', 'quiz_test', 'Rating']
        read_only_fields = ['id', 'username', 'email', 'plan', 'role', 'email_verified', 'created_at']

    def get_check_ins(self, obj):
        return obj.checkins.count()

    def get_quiz_test(self, obj):
        return obj.quiz_attempts.count()

    def get_Rating(self, obj):
        from django.db.models import Avg
        result = obj.checkins.aggregate(avg=Avg('heart_balance_score'))
        avg = result.get('avg') or 0
        return round(avg)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
 
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

# ── Email verification ────────────────────────────────────────
 
class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, allow_blank=True)
    otp = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        token = (attrs.get('token') or '').strip()
        otp = (attrs.get('otp') or '').strip()
        if not token and not otp:
            raise serializers.ValidationError('Verification token or OTP is required.')
        if token:
            attrs['token'] = token
            attrs['verification_method'] = 'token'
        else:
            attrs['token'] = otp
            attrs['verification_method'] = 'otp'
        return attrs
 
 
# ── Forgot / Reset password ───────────────────────────────────
 
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
 
    def validate_email(self, value):
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            # Return same message to avoid user enumeration
            raise serializers.ValidationError(
                'If this email exists, a reset link will be sent.'
            )
        return value
 
 
class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    otp = serializers.CharField(required=False, allow_blank=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        token = (attrs.get('token') or '').strip()
        email = (attrs.get('email') or '').strip().lower()
        otp = (attrs.get('otp') or '').strip()

        if not token and not (email and otp):
            raise serializers.ValidationError(
                'Provide token, or provide both email and otp.'
            )

        if token:
            attrs['token'] = token
        if email:
            attrs['email'] = email
        if otp:
            attrs['otp'] = otp
        return attrs
 
# Admin serializers
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'avatar', 'plan', 'role', 'email_verified', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def _build_token_pair(self, user):
        token = RefreshToken.for_user(user)
        token['email_verified'] = user.email_verified
        token['role'] = user.role
        token['plan'] = user.plan
        return {
            'refresh': str(token),
            'access': str(token.access_token),
        }

    def validate(self, attrs):
        username = (attrs.get('username') or '').strip()
        email = (attrs.get('email') or '').strip().lower()
        password = attrs.get('password')

        if not username and not email:
            raise serializers.ValidationError('Username or email is required.')

        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                if username:
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        raise serializers.ValidationError('No account found with the provided email or username.')
                else:
                    raise serializers.ValidationError('No account found with the provided email.')
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError('No account found with the provided username.')

        if username and email and user.username != username and user.email != email:
            raise serializers.ValidationError('Username and email do not belong to the same account.')

        authenticated_user = authenticate(
            request=self.context.get('request'),
            username=user.username,
            password=password,
        )
        if authenticated_user is None:
            raise serializers.ValidationError('Unable to log in with the provided credentials.')

        data = self._build_token_pair(authenticated_user)
        data['user'] = UserProfileSerializer(authenticated_user).data
        data['_user'] = authenticated_user  # For LoginView to access the user object
        return data