from django.contrib import admin

from .models import ContentPage, FAQ, SupportContact


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
	list_display = ('slug', 'title', 'is_active', 'updated_at')
	list_filter = ('is_active',)
	search_fields = ('slug', 'title', 'content')
	prepopulated_fields = {'slug': ('title',)}


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
	list_display = ('question', 'is_active', 'order')
	list_filter = ('is_active',)
	search_fields = ('question', 'answer')
	ordering = ['order']


@admin.register(SupportContact)
class SupportContactAdmin(admin.ModelAdmin):
	list_display = ('email', 'phone')
	search_fields = ('email', 'phone')