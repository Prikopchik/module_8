from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from users.models import User, Payment
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает тестовые данные для платежей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Количество платежей для создания (по умолчанию 20)',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        users = list(User.objects.all())
        if not users:
            self.stdout.write(
                self.style.WARNING('Нет пользователей в базе данных. Создаем тестовых пользователей...')
            )
            users = self.create_test_users()
        
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())
        
        if not courses and not lessons:
            self.stdout.write(
                self.style.WARNING('Нет курсов и уроков в базе данных. Создаем тестовые данные...')
            )
            courses = self.create_test_courses(users[0])
            lessons = self.create_test_lessons(courses[0], users[0])
        
        payments_created = 0
        payment_methods = ['cash', 'transfer']
        
        for i in range(count):
            user = random.choice(users)
            payment_date = timezone.now() - timedelta(days=random.randint(0, 365))
            amount = round(random.uniform(100, 5000), 2)
            payment_method = random.choice(payment_methods)
            
            if random.choice([True, False]) and courses:
                paid_course = random.choice(courses)
                paid_lesson = None
            elif lessons:
                paid_lesson = random.choice(lessons)
                paid_course = None
            else:
                continue
            
            payment = Payment.objects.create(
                user=user,
                payment_date=payment_date,
                paid_course=paid_course,
                paid_lesson=paid_lesson,
                amount=amount,
                payment_method=payment_method
            )
            payments_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {payments_created} платежей')
        )

    def create_test_users(self):
        users = []
        for i in range(5):
            user = User.objects.create_user(
                email=f'user{i+1}@example.com',
                password='password123',
                first_name=f'Пользователь{i+1}',
                last_name='Тестовый',
                phone=f'+7{9000000000 + i}',
                city='Москва'
            )
            users.append(user)
        return users

    def create_test_courses(self, owner):
        courses = []
        course_titles = [
            'Python для начинающих',
            'Django Web Development',
            'JavaScript Fundamentals',
            'React.js Advanced',
            'Machine Learning Basics'
        ]
        
        for title in course_titles:
            course = Course.objects.create(
                title=title,
                description=f'Описание курса: {title}',
                owner=owner
            )
            courses.append(course)
        return courses

    def create_test_lessons(self, course, owner):
        lessons = []
        lesson_titles = [
            'Введение в тему',
            'Основные концепции',
            'Практические примеры',
            'Продвинутые техники',
            'Итоговое задание'
        ]
        
        for title in lesson_titles:
            lesson = Lesson.objects.create(
                title=title,
                description=f'Описание урока: {title}',
                video_url=f'https://youtube.com/watch?v=lesson_{len(lessons)+1}',
                course=course,
                owner=owner
            )
            lessons.append(lesson)
        return lessons
