import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Course, StripeProduct, StripePrice, PaymentSession

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Сервис для работы с Stripe API"""
    
    @staticmethod
    def create_product(course_id, name, description=""):
        """
        Создает продукт в Stripe и сохраняет его в базе данных
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise ValidationError("Курс не найден")
        
        # Проверяем, не создан ли уже продукт для этого курса
        if hasattr(course, 'stripe_product'):
            raise ValidationError("Продукт для этого курса уже создан")
        
        # Создаем продукт в Stripe
        stripe_product = stripe.Product.create(
            name=name,
            description=description,
            metadata={
                'course_id': course_id,
                'type': 'course'
            }
        )
        
        # Сохраняем продукт в базе данных
        product = StripeProduct.objects.create(
            course=course,
            stripe_product_id=stripe_product.id,
            name=name,
            description=description
        )
        
        return product
    
    @staticmethod
    def create_price(product_id, amount, currency='usd'):
        """
        Создает цену в Stripe и сохраняет ее в базе данных
        """
        try:
            product = StripeProduct.objects.get(id=product_id)
        except StripeProduct.DoesNotExist:
            raise ValidationError("Продукт не найден")
        
        # Конвертируем сумму в центы (Stripe работает с центами)
        amount_cents = int(float(amount) * 100)
        
        # Создаем цену в Stripe
        stripe_price = stripe.Price.create(
            product=product.stripe_product_id,
            unit_amount=amount_cents,
            currency=currency,
            metadata={
                'product_id': product_id,
                'course_id': product.course.id
            }
        )
        
        # Сохраняем цену в базе данных
        price = StripePrice.objects.create(
            product=product,
            stripe_price_id=stripe_price.id,
            amount=amount,
            currency=currency
        )
        
        return price
    
    @staticmethod
    def create_checkout_session(user, course_id, success_url, cancel_url):
        """
        Создает сессию оплаты в Stripe
        """
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise ValidationError("Курс не найден")
        
        # Проверяем, есть ли продукт для курса
        if not hasattr(course, 'stripe_product'):
            raise ValidationError("Для курса не создан продукт в Stripe")
        
        # Получаем активную цену для продукта
        try:
            price = course.stripe_product.prices.filter(is_active=True).first()
            if not price:
                raise ValidationError("Для продукта не найдена активная цена")
        except StripeProduct.DoesNotExist:
            raise ValidationError("Продукт не найден")
        
        # Создаем сессию в Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price.stripe_price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user.email,
            metadata={
                'course_id': course_id,
                'user_id': user.id,
                'price_id': price.id
            }
        )
        
        # Сохраняем сессию в базе данных
        payment_session = PaymentSession.objects.create(
            user=user,
            course=course,
            stripe_session_id=session.id,
            amount=price.amount,
            currency=price.currency,
            status='pending'
        )
        
        return {
            'session_id': session.id,
            'url': session.url,
            'payment_session_id': payment_session.id
        }
    
    @staticmethod
    def get_session_status(session_id):
        """
        Получает статус сессии оплаты из Stripe
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session.payment_status
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка при получении статуса сессии: {str(e)}")
    
    @staticmethod
    def update_payment_status(session_id, status):
        """
        Обновляет статус платежа в базе данных
        """
        try:
            payment_session = PaymentSession.objects.get(stripe_session_id=session_id)
            payment_session.status = status
            payment_session.save()
            return payment_session
        except PaymentSession.DoesNotExist:
            raise ValidationError("Сессия оплаты не найдена")
