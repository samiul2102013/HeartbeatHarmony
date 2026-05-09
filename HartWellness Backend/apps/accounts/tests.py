from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase


User = get_user_model()


class LoginIdentifierTests(APITestCase):
	def setUp(self):
		self.password = 'Test@12345'
		self.user = User.objects.create_user(
			username='testalice',
			email='alice.test@example.com',
			password=self.password,
		)
		# Verify the user so they can login
		self.user.email_verified = True
		self.user.save()

	def test_login_with_username(self):
		response = self.client.post('/api/auth/login/', {
			'username': 'testalice',
			'password': self.password,
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertIn('data', response.data)
		self.assertIn('access', response.data['data'])
		self.assertIn('refresh', response.data['data'])

	def test_login_with_email(self):
		response = self.client.post('/api/auth/login/', {
			'email': 'alice.test@example.com',
			'password': self.password,
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertIn('data', response.data)
		self.assertIn('access', response.data['data'])
		self.assertIn('refresh', response.data['data'])

	def test_login_unverified_user_sends_otp(self):
		"""Test that unverified users get OTP instead of tokens."""
		unverified_user = User.objects.create_user(
			username='unverified',
			email='unverified@example.com',
			password=self.password,
		)
		# Don't verify the user
		
		response = self.client.post('/api/auth/login/', {
			'email': 'unverified@example.com',
			'password': self.password,
		}, format='json')
		
		self.assertEqual(response.status_code, 200)
		self.assertIn('data', response.data)
		self.assertIn('verified', response.data['data'])
		self.assertFalse(response.data['data']['verified'])
		self.assertIn('detail', response.data['data'])

	def test_forgot_password_returns_reset_token_and_otp(self):
		response = self.client.post('/api/auth/forgot-password/', {
			'email': 'alice.test@example.com',
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.assertIn('data', response.data)
		self.assertIn('token', response.data['data'])
		self.user.refresh_from_db()
		self.assertEqual(response.data['data']['token'], self.user.password_reset_token)
		self.assertIsNone(self.user.password_reset_new_password)

	def test_reset_password_with_token_only(self):
		self.user.password_reset_token = 'reset-token-123'
		self.user.password_reset_token_created = timezone.now()
		self.user.save(update_fields=['password_reset_token', 'password_reset_token_created'])

		response = self.client.post('/api/auth/reset-password/', {
			'token': 'reset-token-123',
			'new_password': 'NewPass@12345',
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('NewPass@12345'))


class PaginationMetadataTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username='adminuser',
			email='admin@example.com',
			password='Admin@12345',
			role=User.Role.ADMIN,
		)
		self.admin.email_verified = True
		self.admin.save()

		for index in range(21):
			User.objects.create_user(
				username=f'user{index}',
				email=f'user{index}@example.com',
				password='User@12345',
			)

	def test_admin_user_list_places_pagination_in_metadata(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.get('/api/admin/users/', format='json')

		self.assertEqual(response.status_code, 200)
		self.assertIn('metadata', response.data)
		self.assertIn('data', response.data)
		self.assertEqual(len(response.data['data']), 20)
		self.assertEqual(response.data['metadata']['count'], 22)
		self.assertIsNotNone(response.data['metadata']['next'])
		self.assertIsNone(response.data['metadata']['previous'])
