from django.db import models


DEFAULT_CONTENT_PAGES = {
	'privacy-policy': {
		'title': 'Privacy Policy',
		'content': (
			'<p>We are a trusted home service company dedicated to providing reliable, affordable, and high-quality air conditioning solutions. With a team of skilled and experienced technicians, we specialize in AC installation, repair, cleaning, and maintenance for homes and businesses.</p>'
			'<p>Our goal is simple — to keep your space cool, energy-efficient comfortable, and all year round. We use proper tools, follow industry best practices, and pay attention to every detail to ensure your AC performs at its best.</p>'
			'<p>Customer satisfaction is at the heart of everything we do. From on-time service to transparent pricing and professional support, we strive to deliver a smooth and stress-free experience every time you book with us.</p>'
			'<p>Whether it’s a new installation or an urgent repair, you can count on us for fast response, honest service, and lasting results.</p>'
		),
	},
}


class ContentPage(models.Model):
	slug = models.SlugField(unique=True, max_length=80)
	title = models.CharField(max_length=150)
	content = models.TextField()
	is_active = models.BooleanField(default=True)
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
	order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)

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
