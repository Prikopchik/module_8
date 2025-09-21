from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
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


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'password', 'password_confirm')
        read_only_fields = ('id',)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar')
        read_only_fields = ('id', 'email')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Неверные учетные данные')
            if not user.is_active:
                raise serializers.ValidationError('Аккаунт отключен')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Необходимо указать email и пароль')
