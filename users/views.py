from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import PaymentSerializer, PaymentListSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    filterset_fields = {
        'paid_course': ['exact'],
        'paid_lesson': ['exact'],
        'payment_method': ['exact'],
        'payment_date': ['gte', 'lte', 'exact'],
        'amount': ['gte', 'lte', 'exact'],
    }
    
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']
    
    search_fields = ['user__email', 'paid_course__title', 'paid_lesson__title']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        default_user, created = User.objects.get_or_create(
            email='default@example.com',
            defaults={'first_name': 'Default', 'last_name': 'User'}
        )
        serializer.save(user=default_user)