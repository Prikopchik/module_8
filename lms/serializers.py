from rest_framework import serializers
from .models import Course, Lesson, CourseSubscription
from .validators import validate_youtube_url, YouTubeURLValidator


class LessonListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'preview', 'course', 'created_at')


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonListSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseSubscription.objects.filter(
                user=request.user, 
                course=obj, 
                is_active=True
            ).exists()
        return False


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[validate_youtube_url])
    
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner', 'created_at', 'updated_at')
        validators = [YouTubeURLValidator(field='video_url')]


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CourseSubscription
        fields = ('id', 'course', 'user', 'created_at', 'is_active')
        read_only_fields = ('user', 'created_at')
    
    def create(self, validated_data):
        # Устанавливаем пользователя из контекста запроса
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
