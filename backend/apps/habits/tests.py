from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Category, Habit

User = get_user_model()


class UserHabitEditDeleteTests(APITestCase):
	def setUp(self):
		self.password = 'Test@12345'
		self.owner = User.objects.create_user(
			username='owner', email='owner@example.com', password=self.password,
		)
		self.other = User.objects.create_user(
			username='other', email='other@example.com', password=self.password,
		)
		self.admin = User.objects.create_user(
			username='adminuser', email='admin@example.com', password=self.password,
			is_staff=True,
		)
		self.category = Category.objects.create(name='Fitness')
		# Admin-created habit shown in the shared feed.
		self.admin_habit = Habit.objects.create(
			user=self.admin, category=self.category,
			activity_name='Drink water', duration=5,
		)
		# User-created habit.
		self.own_habit = Habit.objects.create(
			user=self.owner, category=self.category,
			activity_name='Morning stretch', duration=10,
		)

	def test_owner_can_edit_own_habit(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.patch('/api/habits/%d/edit/' % self.own_habit.id, {
			'activity_name': 'Evening stretch',
			'duration': 15,
		}, format='json')

		self.assertEqual(response.status_code, 200)
		self.own_habit.refresh_from_db()
		self.assertEqual(self.own_habit.activity_name, 'Evening stretch')
		self.assertEqual(self.own_habit.duration, 15)

	def test_user_cannot_edit_admin_created_habit(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.patch('/api/habits/%d/edit/' % self.admin_habit.id, {
			'activity_name': 'Hacked',
		}, format='json')

		self.assertEqual(response.status_code, 404)
		self.admin_habit.refresh_from_db()
		self.assertEqual(self.admin_habit.activity_name, 'Drink water')

	def test_user_cannot_edit_other_users_habit(self):
		self.client.force_authenticate(user=self.other)
		response = self.client.patch('/api/habits/%d/edit/' % self.own_habit.id, {
			'activity_name': 'Hacked',
		}, format='json')

		self.assertEqual(response.status_code, 404)
		self.own_habit.refresh_from_db()
		self.assertEqual(self.own_habit.activity_name, 'Morning stretch')

	def test_owner_can_delete_own_habit(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.delete('/api/habits/%d/delete/' % self.own_habit.id)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Habit.objects.filter(pk=self.own_habit.pk).exists())

	def test_user_cannot_delete_admin_created_habit(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.delete('/api/habits/%d/delete/' % self.admin_habit.id)

		self.assertEqual(response.status_code, 403)
		self.assertTrue(Habit.objects.filter(pk=self.admin_habit.pk).exists())

	def test_user_cannot_delete_other_users_habit(self):
		self.client.force_authenticate(user=self.other)
		response = self.client.delete('/api/habits/%d/delete/' % self.own_habit.id)

		self.assertEqual(response.status_code, 404)
		self.assertTrue(Habit.objects.filter(pk=self.own_habit.pk).exists())

	def test_edit_rejects_template_id_change(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.patch('/api/habits/%d/edit/' % self.own_habit.id, {
			'template_id': 1,
		}, format='json')

		self.assertEqual(response.status_code, 400)
		self.own_habit.refresh_from_db()
		self.assertEqual(self.own_habit.activity_name, 'Morning stretch')
