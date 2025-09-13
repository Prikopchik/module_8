from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator


class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватарка')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    payment_date = models.DateTimeField(verbose_name='Дата оплаты')
    paid_course = models.ForeignKey('lms.Course', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Оплаченный курс')
    paid_lesson = models.ForeignKey('lms.Lesson', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Оплаченный урок')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Сумма оплаты')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name='Способ оплаты')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']
    
    def __str__(self):
        course_or_lesson = self.paid_course.title if self.paid_course else self.paid_lesson.title if self.paid_lesson else 'Неизвестно'
        return f"{self.user.email} - {course_or_lesson} - {self.amount} руб."
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Необходимо указать либо курс, либо урок')
        if self.paid_course and self.paid_lesson:
            raise ValidationError('Нельзя указать и курс, и урок одновременно')
