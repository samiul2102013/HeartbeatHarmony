from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Mood


User = get_user_model()


class MoodListSvgTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='moodtester',
			email='moodtester@example.com',
			password='Test@12345',
		)
		self.mood = Mood.objects.create(
			name='Calm',
			emoji='😌',
			score=8,
			is_active=True,
		)

	def test_mood_list_includes_svg_image_payload(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.get('/api/moods/', format='json')

		self.assertEqual(response.status_code, 200)
		mood_data = response.data['data'][0]
		self.assertIn('svg', mood_data)
		self.assertIn('.svg', mood_data['svg'])
		self.assertTrue(self.mood.svg.name.endswith('.svg'))
