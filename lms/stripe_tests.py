from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from .models import Course, StripeProduct, StripePrice, PaymentSession
from .stripe_service import StripeService

User = get_user_model()


class StripeServiceTest(TestCase):
    """Тесты для StripeService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
    
    @patch('stripe.Product.create')
    def test_create_product_success(self, mock_stripe_create):
        """Тест успешного создания продукта"""
        mock_stripe_create.return_value = MagicMock(id='prod_test123')
        
        product = StripeService.create_product(
            course_id=self.course.id,
            name='Test Product',
            description='Test Description'
        )
        
        self.assertIsInstance(product, StripeProduct)
        self.assertEqual(product.course, self.course)
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.stripe_product_id, 'prod_test123')
    
    def test_create_product_course_not_found(self):
        """Тест создания продукта для несуществующего курса"""
        with self.assertRaises(Exception):
            StripeService.create_product(
                course_id=999,
                name='Test Product',
                description='Test Description'
            )
    
    @patch('stripe.Price.create')
    def test_create_price_success(self, mock_stripe_create):
        """Тест успешного создания цены"""
        # Создаем продукт
        product = StripeProduct.objects.create(
            course=self.course,
            stripe_product_id='prod_test123',
            name='Test Product',
            description='Test Description'
        )
        
        mock_stripe_create.return_value = MagicMock(id='price_test123')
        
        price = StripeService.create_price(
            product_id=product.id,
            amount=100.00,
            currency='usd'
        )
        
        self.assertIsInstance(price, StripePrice)
        self.assertEqual(price.product, product)
        self.assertEqual(price.amount, 100.00)
        self.assertEqual(price.currency, 'usd')
        self.assertEqual(price.stripe_price_id, 'price_test123')
    
    def test_create_price_product_not_found(self):
        """Тест создания цены для несуществующего продукта"""
        with self.assertRaises(Exception):
            StripeService.create_price(
                product_id=999,
                amount=100.00,
                currency='usd'
            )


class StripeAPITest(APITestCase):
    """Тесты для Stripe API эндпоинтов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.product = StripeProduct.objects.create(
            course=self.course,
            stripe_product_id='prod_test123',
            name='Test Product',
            description='Test Description'
        )
        self.price = StripePrice.objects.create(
            product=self.product,
            stripe_price_id='price_test123',
            amount=100.00,
            currency='usd'
        )
    
    def test_create_product_api(self):
        """Тест API создания продукта"""
        self.client.force_authenticate(user=self.user)
        
        with patch('lms.stripe_service.StripeService.create_product') as mock_create:
            mock_create.return_value = self.product
            
            url = reverse('stripeproduct-create-product')
            data = {
                'course_id': self.course.id,
                'name': 'Test Product',
                'description': 'Test Description'
            }
            response = self.client.post(url, data)
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            mock_create.assert_called_once()
    
    def test_create_price_api(self):
        """Тест API создания цены"""
        self.client.force_authenticate(user=self.user)
        
        with patch('lms.stripe_service.StripeService.create_price') as mock_create:
            mock_create.return_value = self.price
            
            url = reverse('stripeprice-create-price')
            data = {
                'product_id': self.product.id,
                'amount': 100.00,
                'currency': 'usd'
            }
            response = self.client.post(url, data)
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            mock_create.assert_called_once()
    
    def test_create_payment_session_api(self):
        """Тест API создания сессии оплаты"""
        self.client.force_authenticate(user=self.user)
        
        with patch('lms.stripe_service.StripeService.create_checkout_session') as mock_create:
            mock_create.return_value = {
                'session_id': 'cs_test123',
                'url': 'https://checkout.stripe.com/test',
                'payment_session_id': 1
            }
            
            url = reverse('paymentsession-create-session')
            data = {
                'course_id': self.course.id,
                'success_url': 'https://example.com/success',
                'cancel_url': 'https://example.com/cancel'
            }
            response = self.client.post(url, data)
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            mock_create.assert_called_once()
    
    def test_get_payment_session_status(self):
        """Тест получения статуса сессии оплаты"""
        self.client.force_authenticate(user=self.user)
        
        payment_session = PaymentSession.objects.create(
            user=self.user,
            course=self.course,
            stripe_session_id='cs_test123',
            amount=100.00,
            currency='usd',
            status='pending'
        )
        
        with patch('lms.stripe_service.StripeService.get_session_status') as mock_get_status:
            mock_get_status.return_value = 'paid'
            
            url = reverse('paymentsession-get-status', kwargs={'pk': payment_session.id})
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], 'paid')
            mock_get_status.assert_called_once()
    
    def test_unauthorized_access(self):
        """Тест доступа без авторизации"""
        url = reverse('stripeproduct-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
