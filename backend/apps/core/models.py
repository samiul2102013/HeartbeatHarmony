from django.db import models


DEFAULT_CONTENT_PAGES = {
	'privacy-policy': {
		'title': 'Privacy Policy',
		'content': (
			'<h2>Your Privacy Matters</h2>'
			'<p>Heartbeat Harmony is committed to protecting your privacy. This policy explains how we collect, use, and safeguard your personal information when you use our app.</p>'
			'<h3>Information We Collect</h3>'
			'<p>We collect information you provide directly, such as your name, email address, and health-related check-in data (mood, ratings, gratitude entries). We also collect usage data to improve your experience.</p>'
			'<h3>How We Use Your Information</h3>'
			'<p>Your data is used to calculate your Heart Balance score, personalize your wellness journey, and connect you with the community. We never share your personal health data with third parties without your explicit consent.</p>'
			'<h3>Data Security</h3>'
			'<p>We use industry-standard encryption and security practices to protect your data. Your account is protected by your password, and we recommend using a strong, unique password.</p>'
			'<h3>Your Rights</h3>'
			'<p>You can access, modify, or delete your data at any time through your profile settings. Contact us at support@heartbeatharmony.tech for any privacy-related requests.</p>'
		),
	},
	'terms-of-service': {
		'title': 'Terms of Service',
		'content': (
			'<h2>Terms of Service</h2>'
			'<p>By using Heartbeat Harmony, you agree to these terms. Please read them carefully.</p>'
			'<h3>Acceptance of Terms</h3>'
			'<p>By creating an account and using the app, you agree to be bound by these Terms of Service and our Privacy Policy.</p>'
			'<h3>User Responsibilities</h3>'
			'<p>You are responsible for maintaining the confidentiality of your account credentials. You agree not to misuse the app for any unlawful purpose or to harass other community members.</p>'
			'<h3>Service Availability</h3>'
			'<p>We strive to provide uninterrupted service but do not guarantee 100% availability. We reserve the right to modify or discontinue features with reasonable notice.</p>'
			'<h3>Limitation of Liability</h3>'
			'<p>Heartbeat Harmony is a wellness tracking tool and does not replace professional medical advice. Consult your healthcare provider for medical concerns.</p>'
		),
	},
	'about-us': {
		'title': 'About Us',
		'content': (
			'<h2>Our Mission</h2>'
			'<p>Heartbeat Harmony was created to help individuals track, understand, and improve their emotional and mental well-being through daily check-ins, habit tracking, and community support.</p>'
			'<h2>Our Story</h2>'
			'<p>Founded by a team of wellness enthusiasts and technologists, we believe that small daily habits and self-awareness lead to lasting positive change. Our Heart Balance scoring system provides a holistic view of your well-being by combining mood, gratitude, and lifestyle factors.</p>'
			'<h2>Our Values</h2>'
			'<p>We prioritize user privacy, scientific wellness practices, inclusive community building, and continuous improvement based on user feedback.</p>'
		),
	},
	'account-deletion-policy': {
		'title': 'Account Deletion Policy',
		'content': (
			'<h2>Account Deletion Policy</h2>'
			'<p>You have the right to delete your account and associated data at any time.</p>'
			'<h3>What Happens When You Delete Your Account</h3>'
			'<p>When you request account deletion, all your personal data including profile information, check-in history, habits, community messages, and study progress will be permanently removed from our servers.</p>'
			'<h3>How to Delete Your Account</h3>'
			'<p>You can delete your account from the app settings by selecting "Delete Account". Confirm your choice and your account will be permanently deleted.</p>'
			'<h3>Data Retention</h3>'
			'<p>Some anonymized data may be retained for analytics purposes. This data cannot be linked back to you.</p>'
			'<h3>Contact Us</h3>'
			'<p>If you have questions about account deletion, contact us at support@heartbeatharmony.tech</p>'
		),
	},
	'help-and-support': {
		'title': 'Help & Support',
		'content': (
			'<h2>How Can We Help You?</h2>'
			'<p>We are here to support you on your wellness journey. Browse common topics below or reach out to our team.</p>'
			'<h3>Getting Started</h3>'
			'<p>Create an account, complete your first check-in, and explore your Heart Balance dashboard. Check out our FAQ for quick answers to common questions.</p>'
			'<h3>Account & Billing</h3>'
			'<p>Manage your profile, change your password, and upgrade or cancel your subscription from the Settings page.</p>'
			'<h3>Technical Support</h3>'
			'<p>If you experience technical issues, try restarting the app or clearing your cache. For persistent issues, contact us with details about the problem.</p>'
			'<h3>Contact Us</h3>'
			'<p>Email: support@heartbeatharmony.tech</p>'
			'<p>We aim to respond within 24 hours on weekdays.</p>'
		),
	},
}


class ContentPage(models.Model):
	slug = models.SlugField(unique=True, max_length=80)
	title = models.CharField(max_length=150)
	content = models.TextField()
	is_active = models.BooleanField(default=True, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'content_pages'
		ordering = ['slug']

	def __str__(self):
		return self.title

	@classmethod
	def ensure_defaults(cls):
		for slug, defaults in DEFAULT_CONTENT_PAGES.items():
			cls.objects.get_or_create(slug=slug, defaults=defaults)


class FAQ(models.Model):
	question = models.CharField(max_length=255)
	answer = models.TextField()
	order = models.PositiveIntegerField(default=0, db_index=True)
	is_active = models.BooleanField(default=True, db_index=True)

	class Meta:
		db_table = 'faqs'
		ordering = ['order']

	def __str__(self):
		return self.question


class SupportContact(models.Model):
	email = models.EmailField(blank=True, null=True)
	phone = models.CharField(max_length=50, blank=True, null=True)

	class Meta:
		db_table = 'support_contacts'

	def __str__(self):
		return f"Support Contact: {self.email} / {self.phone}"
