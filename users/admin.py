from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Payment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'city', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'city')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'paid_course', 'paid_lesson', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date', 'paid_course', 'paid_lesson')
    search_fields = ('user__email', 'paid_course__title', 'paid_lesson__title')
    readonly_fields = ('created_at',)
    ordering = ('-payment_date',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'payment_date', 'amount', 'payment_method')
        }),
        ('Оплаченный контент', {
            'fields': ('paid_course', 'paid_lesson'),
            'description': 'Укажите либо курс, либо урок (не оба одновременно)'
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
