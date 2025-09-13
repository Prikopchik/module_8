from rest_framework import serializers
from .models import Course, Lesson


class LessonListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'preview', 'course', 'created_at')


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonListSerializer(source='lessons', many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
