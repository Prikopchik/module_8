from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группу модераторов с правами на редактирование курсов и уроков'

    def handle(self, *args, **options):
        # Создаем группу модераторов
        group, created = Group.objects.get_or_create(name='Модераторы')
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Модераторы" создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Группа "Модераторы" уже существует')
            )
        
        # Получаем ContentType для Course и Lesson
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)
        
        # Получаем разрешения для курсов (без создания и удаления)
        course_permissions = Permission.objects.filter(
            content_type=course_content_type,
            codename__in=['view_course', 'change_course']
        )
        
        # Получаем разрешения для уроков (без создания и удаления)
        lesson_permissions = Permission.objects.filter(
            content_type=lesson_content_type,
            codename__in=['view_lesson', 'change_lesson']
        )
        
        # Добавляем разрешения к группе
        all_permissions = list(course_permissions) + list(lesson_permissions)
        group.permissions.set(all_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Добавлено {len(all_permissions)} разрешений для группы "Модераторы"'
            )
        )
        
        # Выводим список разрешений
        self.stdout.write('\nРазрешения группы "Модераторы":')
        for permission in all_permissions:
            self.stdout.write(f'  - {permission.name} ({permission.codename})')
