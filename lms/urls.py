from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonViewSet, CourseSubscriptionViewSet
from .stripe_views import StripeProductViewSet, StripePriceViewSet, PaymentSessionViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'subscriptions', CourseSubscriptionViewSet)
router.register(r'stripe/products', StripeProductViewSet)
router.register(r'stripe/prices', StripePriceViewSet)
router.register(r'stripe/sessions', PaymentSessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
