from django.contrib import admin
from .models import Course, Lesson, CourseSubscription, StripeProduct, StripePrice, PaymentSession


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


@admin.register(CourseSubscription)
class CourseSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'course')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(StripeProduct)
class StripeProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'stripe_product_id', 'created_at')
    list_filter = ('created_at', 'course')
    search_fields = ('name', 'description', 'course__title', 'stripe_product_id')
    readonly_fields = ('stripe_product_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(StripePrice)
class StripePriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'amount', 'currency', 'is_active', 'created_at')
    list_filter = ('is_active', 'currency', 'created_at', 'product__course')
    search_fields = ('product__name', 'stripe_price_id')
    readonly_fields = ('stripe_price_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(PaymentSession)
class PaymentSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at', 'course')
    search_fields = ('user__email', 'course__title', 'stripe_session_id')
    readonly_fields = ('stripe_session_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
