from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import get_object_or_404
from .models import StripeProduct, StripePrice, PaymentSession
from .serializers import (
    StripeProductSerializer, 
    StripePriceSerializer, 
    PaymentSessionSerializer,
    CreateProductSerializer,
    CreatePriceSerializer,
    CreatePaymentSessionSerializer
)
from .stripe_service import StripeService


@extend_schema_view(
    list=extend_schema(
        summary="Получить список продуктов Stripe",
        description="Возвращает список всех продуктов Stripe",
        tags=["Stripe"]
    ),
    retrieve=extend_schema(
        summary="Получить продукт Stripe",
        description="Возвращает детальную информацию о продукте Stripe",
        tags=["Stripe"]
    ),
)
class StripeProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра продуктов Stripe
    """
    queryset = StripeProduct.objects.all()
    serializer_class = StripeProductSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Создать продукт в Stripe",
        description="Создает новый продукт в Stripe для курса",
        tags=["Stripe"]
    )
    @action(detail=False, methods=['post'])
    def create_product(self, request):
        """Создает продукт в Stripe"""
        serializer = CreateProductSerializer(data=request.data)
        if serializer.is_valid():
            try:
                product = StripeService.create_product(
                    course_id=serializer.validated_data['course_id'],
                    name=serializer.validated_data['name'],
                    description=serializer.validated_data.get('description', '')
                )
                response_serializer = StripeProductSerializer(product)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="Получить список цен Stripe",
        description="Возвращает список всех цен Stripe",
        tags=["Stripe"]
    ),
    retrieve=extend_schema(
        summary="Получить цену Stripe",
        description="Возвращает детальную информацию о цене Stripe",
        tags=["Stripe"]
    ),
)
class StripePriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра цен Stripe
    """
    queryset = StripePrice.objects.all()
    serializer_class = StripePriceSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Создать цену в Stripe",
        description="Создает новую цену для продукта в Stripe",
        tags=["Stripe"]
    )
    @action(detail=False, methods=['post'])
    def create_price(self, request):
        """Создает цену в Stripe"""
        serializer = CreatePriceSerializer(data=request.data)
        if serializer.is_valid():
            try:
                price = StripeService.create_price(
                    product_id=serializer.validated_data['product_id'],
                    amount=serializer.validated_data['amount'],
                    currency=serializer.validated_data['currency']
                )
                response_serializer = StripePriceSerializer(price)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="Получить список сессий оплаты",
        description="Возвращает список сессий оплаты пользователя",
        tags=["Stripe"]
    ),
    retrieve=extend_schema(
        summary="Получить сессию оплаты",
        description="Возвращает детальную информацию о сессии оплаты",
        tags=["Stripe"]
    ),
)
class PaymentSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с сессиями оплаты
    """
    queryset = PaymentSession.objects.all()
    serializer_class = PaymentSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentSession.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Создать сессию оплаты",
        description="Создает новую сессию оплаты для курса",
        tags=["Stripe"]
    )
    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Создает сессию оплаты"""
        serializer = CreatePaymentSessionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = StripeService.create_checkout_session(
                    user=request.user,
                    course_id=serializer.validated_data['course_id'],
                    success_url=serializer.validated_data['success_url'],
                    cancel_url=serializer.validated_data['cancel_url']
                )
                return Response(result, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Получить статус сессии",
        description="Получает актуальный статус сессии оплаты",
        tags=["Stripe"]
    )
    @action(detail=True, methods=['get'])
    def get_status(self, request, pk=None):
        """Получает статус сессии оплаты"""
        payment_session = self.get_object()
        try:
            status = StripeService.get_session_status(payment_session.stripe_session_id)
            return Response({
                'session_id': payment_session.stripe_session_id,
                'status': status,
                'local_status': payment_session.status
            })
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
