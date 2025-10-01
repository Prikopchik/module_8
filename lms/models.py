from django.db import models
from django.core.exceptions import ValidationError
from users.models import User


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/previews/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(verbose_name='Описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/previews/', blank=True, null=True, verbose_name='Превью')
    video_url = models.URLField(verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['created_at']
    
    def __str__(self):
        return self.title


class CourseSubscription(models.Model):
    """
    Модель подписки на обновления курса
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Курс')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    
    class Meta:
        verbose_name = 'Подписка на курс'
        verbose_name_plural = 'Подписки на курсы'
        unique_together = ('user', 'course')  # Один пользователь может подписаться на курс только один раз
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"
    
    def clean(self):
        # Проверяем, что пользователь не подписывается на свой собственный курс
        if self.user == self.course.owner:
            raise ValidationError('Нельзя подписаться на собственный курс')


class StripeProduct(models.Model):
    """
    Модель для хранения информации о продуктах Stripe
    """
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='stripe_product', verbose_name='Курс')
    stripe_product_id = models.CharField(max_length=255, unique=True, verbose_name='ID продукта в Stripe')
    name = models.CharField(max_length=255, verbose_name='Название продукта')
    description = models.TextField(blank=True, verbose_name='Описание продукта')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Продукт Stripe'
        verbose_name_plural = 'Продукты Stripe'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (Stripe ID: {self.stripe_product_id})"


class StripePrice(models.Model):
    """
    Модель для хранения информации о ценах Stripe
    """
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('rub', 'RUB'),
    ]
    
    product = models.ForeignKey(StripeProduct, on_delete=models.CASCADE, related_name='prices', verbose_name='Продукт')
    stripe_price_id = models.CharField(max_length=255, unique=True, verbose_name='ID цены в Stripe')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd', verbose_name='Валюта')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Цена Stripe'
        verbose_name_plural = 'Цены Stripe'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.amount} {self.currency} (Stripe ID: {self.stripe_price_id})"


class PaymentSession(models.Model):
    """
    Модель для хранения информации о сессиях оплаты Stripe
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')
    stripe_session_id = models.CharField(max_length=255, unique=True, verbose_name='ID сессии в Stripe')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    currency = models.CharField(max_length=3, default='usd', verbose_name='Валюта')
    status = models.CharField(max_length=50, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Сессия оплаты'
        verbose_name_plural = 'Сессии оплаты'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.stripe_session_id} - {self.user.email} - {self.course.title}"
