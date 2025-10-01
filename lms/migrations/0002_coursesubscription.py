# Generated manually for CourseSubscription model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_payment'),
        ('lms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='lms.course', verbose_name='Курс')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписка на курс',
                'verbose_name_plural': 'Подписки на курсы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='coursesubscription',
            constraint=models.UniqueConstraint(fields=('user', 'course'), name='unique_user_course_subscription'),
        ),
    ]
