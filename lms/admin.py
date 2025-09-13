from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'owner')
    search_fields = ('title', 'description', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner', 'created_at')
    list_filter = ('created_at', 'course', 'owner')
    search_fields = ('title', 'description', 'course__title', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
