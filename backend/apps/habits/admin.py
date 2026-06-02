from django.contrib import admin
from .models import Category, Habit, HabitCompletion, HabitTemplate, HabitMaterial


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'created_at']
    list_editable = ['is_active']


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_name', 'category', 'duration', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['user__username', 'activity_name']

@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'habit', 'completed_date', 'created_at']
    list_filter = ['completed_date']
    search_fields = ['user__username', 'habit__activity_name']
    date_hierarchy = 'completed_date'

@admin.register(HabitTemplate)
class HabitTemplateAdmin(admin.ModelAdmin):
    list_display = ['activity_name', 'category', 'duration', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['activity_name']


@admin.register(HabitMaterial)
class HabitMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'habit', 'material_type', 'is_active', 'created_at']
    list_filter = ['material_type', 'is_active']
    search_fields = ['title', 'habit__activity_name']