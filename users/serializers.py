from rest_framework import serializers
from .models import User, Payment
from lms.models import Course, Lesson


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='paid_course.title', read_only=True)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate(self, data):
        paid_course = data.get('paid_course')
        paid_lesson = data.get('paid_lesson')
        
        if not paid_course and not paid_lesson:
            raise serializers.ValidationError('Необходимо указать либо курс, либо урок')
        if paid_course and paid_lesson:
            raise serializers.ValidationError('Нельзя указать и курс, и урок одновременно')
        
        return data


class PaymentListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='paid_course.title', read_only=True)
    lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'user_email', 'course_title', 'lesson_title', 'amount', 
                 'payment_method', 'payment_method_display', 'payment_date')
