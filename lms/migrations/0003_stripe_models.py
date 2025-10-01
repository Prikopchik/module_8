# Generated manually for Stripe models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_payment'),
        ('lms', '0002_coursesubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_product_id', models.CharField(max_length=255, unique=True, verbose_name='ID продукта в Stripe')),
                ('name', models.CharField(max_length=255, verbose_name='Название продукта')),
                ('description', models.TextField(blank=True, verbose_name='Описание продукта')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_product', to='lms.course', verbose_name='Курс')),
            ],
            options={
                'verbose_name': 'Продукт Stripe',
                'verbose_name_plural': 'Продукты Stripe',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StripePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_price_id', models.CharField(max_length=255, unique=True, verbose_name='ID цены в Stripe')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('currency', models.CharField(choices=[('usd', 'USD'), ('eur', 'EUR'), ('rub', 'RUB')], default='usd', max_length=3, verbose_name='Валюта')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='lms.stripeproduct', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Цена Stripe',
                'verbose_name_plural': 'Цены Stripe',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PaymentSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_session_id', models.CharField(max_length=255, unique=True, verbose_name='ID сессии в Stripe')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('currency', models.CharField(default='usd', max_length=3, verbose_name='Валюта')),
                ('status', models.CharField(default='pending', max_length=50, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lms.course', verbose_name='Курс')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Сессия оплаты',
                'verbose_name_plural': 'Сессии оплаты',
                'ordering': ['-created_at'],
            },
        ),
    ]
