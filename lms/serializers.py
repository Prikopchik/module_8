from rest_framework import serializers
from .models import Course, Lesson, CourseSubscription, StripeProduct, StripePrice, PaymentSession
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


class StripeProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StripeProduct
        fields = ('id', 'course', 'stripe_product_id', 'name', 'description', 'created_at', 'updated_at')
        read_only_fields = ('stripe_product_id', 'created_at', 'updated_at')


class StripePriceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StripePrice
        fields = ('id', 'product', 'stripe_price_id', 'amount', 'currency', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('stripe_price_id', 'created_at', 'updated_at')


class PaymentSessionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentSession
        fields = ('id', 'user', 'course', 'stripe_session_id', 'amount', 'currency', 'status', 'created_at', 'updated_at')
        read_only_fields = ('user', 'stripe_session_id', 'status', 'created_at', 'updated_at')


class CreateProductSerializer(serializers.Serializer):
    """Сериализатор для создания продукта в Stripe"""
    course_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)


class CreatePriceSerializer(serializers.Serializer):
    """Сериализатор для создания цены в Stripe"""
    product_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.ChoiceField(choices=StripePrice.CURRENCY_CHOICES, default='usd')


class CreatePaymentSessionSerializer(serializers.Serializer):
    """Сериализатор для создания сессии оплаты"""
    course_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
