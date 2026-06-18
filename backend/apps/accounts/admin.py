from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	list_display = (
		'id',
		'username',
		'institute_name',
		'email',
		'role',
		'plan',
		'email_verified',
		'is_staff',
		'is_active',
	)
	list_filter = ('role', 'plan', 'email_verified', 'is_staff', 'is_active')
	search_fields = ('username', 'institute_name', 'email', 'first_name', 'last_name', 'phone_number')

	fieldsets = BaseUserAdmin.fieldsets + (
		('Custom Fields', {'fields': ('role', 'plan', 'institute_name', 'phone_number', 'avatar')}),
	)
	add_fieldsets = BaseUserAdmin.add_fieldsets + (
		('Custom Fields', {'fields': ('role', 'plan', 'institute_name', 'phone_number')}),
	)

