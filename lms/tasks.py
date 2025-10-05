from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings
from django.db import models

from .models import Course, Lesson, CourseSubscription
from users.models import User


@shared_task
def send_course_update_email(course_id: int, updated_object_type: str, updated_object_id: int) -> int:
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return 0

    # Собираем e-mail адреса активных подписчиков
    emails = list(
        CourseSubscription.objects.filter(course=course, is_active=True)
        .select_related('user')
        .values_list('user__email', flat=True)
    )

    if not emails:
        return 0

    subject = f'Обновление материалов курса: {course.title}'
    if updated_object_type == 'course':
        body = f'Курс "{course.title}" был обновлен.'
    elif updated_object_type == 'lesson':
        try:
            lesson = Lesson.objects.get(id=updated_object_id)
            body = f'В курсе "{course.title}" обновлен урок: {lesson.title}.'
        except Lesson.DoesNotExist:
            body = f'В курсе "{course.title}" были обновлены материалы.'
    else:
        body = f'В курсе "{course.title}" были обновлены материалы.'

    # Отправляем письмо каждому подписчику отдельно для надежности
    sent_count = 0
    for email in emails:
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
            sent_count += 1
        except Exception:
            # Игнорируем ошибки отправки для отдельных адресов
            pass

    return sent_count


@shared_task
def deactivate_inactive_users() -> int:
    cutoff = timezone.now() - timedelta(days=30)
    # Пользователи, которые никогда не входили (last_login = None) или не заходили дольше 30 дней
    qs = User.objects.filter(is_active=True).filter(
        models.Q(last_login__lt=cutoff) | models.Q(last_login__isnull=True)
    )
    updated = qs.update(is_active=False)
    return updated


