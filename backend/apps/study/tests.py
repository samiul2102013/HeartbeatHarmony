from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Quiz, Question, StudyTopic


class QuizSubmissionTopicSummaryTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='tester',
			email='tester@example.com',
			password='password123',
		)
		self.client.force_authenticate(user=self.user)

	def _create_question(self, quiz, topic, text, option_a, option_b, option_c, option_d, correct_option, order):
		return Question.objects.create(
			quiz=quiz,
			topic=topic,
			text=text,
			option_a=option_a,
			option_b=option_b,
			option_c=option_c,
			option_d=option_d,
			correct_option=correct_option,
			order=order,
		)

	def test_mixed_quiz_submission_updates_each_topic_summary(self):
		topic_one = StudyTopic.objects.create(title='Topic One', description='First topic')
		topic_two = StudyTopic.objects.create(title='Topic Two', description='Second topic')
		topic_three = StudyTopic.objects.create(title='Topic Three', description='Third topic')

		quiz = Quiz.objects.create(topic=topic_one, title='Mixed Topic Quiz', description='Question Set')

		q1 = self._create_question(quiz, topic_one, 'Question 1', 'A1', 'B1', 'C1', '', 'A', 1)
		q2 = self._create_question(quiz, topic_one, 'Question 2', 'A2', 'B2', 'C2', '', 'B', 2)
		q3 = self._create_question(quiz, topic_two, 'Question 3', 'A3', 'B3', 'C3', '', 'C', 3)
		q4 = self._create_question(quiz, topic_two, 'Question 4', 'A4', 'B4', 'C4', '', 'A', 4)
		q5 = self._create_question(quiz, topic_three, 'Question 5', 'A5', 'B5', 'C5', '', 'D', 5)

		response = self.client.post(
			'/api/study/quizzes/submit/',
			{
				'quiz_id': quiz.id,
				'answers': [
					{'question_id': q1.id, 'selected_option': 'A'},
					{'question_id': q2.id, 'selected_option': 'A'},
					{'question_id': q3.id, 'selected_option': 'C'},
					{'question_id': q4.id, 'selected_option': 'A'},
					{'question_id': q5.id, 'selected_option': 'D'},
				],
			},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		payload = response.json()['data']
		self.assertEqual(payload['score'], 4)
		self.assertEqual(payload['total_questions'], 5)
		self.assertEqual(len(payload['topic_results']), 3)

		topic_response = self.client.get('/api/study/topics/')
		self.assertEqual(topic_response.status_code, 200)
		topics = topic_response.json()['data']
		topic_map = {item['id']: item for item in topics}

		self.assertEqual(topic_map[topic_one.id]['last_correct_answers'], 1)
		self.assertEqual(topic_map[topic_one.id]['last_total_questions'], 2)
		self.assertEqual(topic_map[topic_one.id]['last_attempted_score'], 50.0)

		self.assertEqual(topic_map[topic_two.id]['last_correct_answers'], 2)
		self.assertEqual(topic_map[topic_two.id]['last_total_questions'], 2)
		self.assertEqual(topic_map[topic_two.id]['last_attempted_score'], 100.0)

		self.assertEqual(topic_map[topic_three.id]['last_correct_answers'], 1)
		self.assertEqual(topic_map[topic_three.id]['last_total_questions'], 1)
		self.assertEqual(topic_map[topic_three.id]['last_attempted_score'], 100.0)


class QuizListLatestOnlyTests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='quiz-list-user',
			email='quiz-list-user@example.com',
			password='password123',
		)
		self.client.force_authenticate(user=self.user)

	def test_quiz_list_returns_only_latest_active_quiz(self):
		topic = StudyTopic.objects.create(title='Shared Topic', description='Topic for quizzes')
		Quiz.objects.create(topic=topic, title='Older Quiz', description='Old')
		latest_quiz = Quiz.objects.create(topic=topic, title='Newest Quiz', description='New')

		response = self.client.get('/api/study/quizzes/')

		self.assertEqual(response.status_code, 200)
		payload = response.json()['data']
		self.assertEqual(len(payload), 1)
		self.assertEqual(payload[0]['id'], latest_quiz.id)
		self.assertEqual(payload[0]['title'], 'Newest Quiz')
