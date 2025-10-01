from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Course, Lesson, CourseSubscription
from .validators import validate_youtube_url
from django.core.exceptions import ValidationError

User = get_user_model()


class YouTubeURLValidatorTest(TestCase):
    """Тесты для валидатора YouTube ссылок"""
    
    def test_valid_youtube_urls(self):
        """Тест валидных YouTube ссылок"""
        valid_urls = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'https://youtu.be/dQw4w9WgXcQ',
            'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertEqual(validate_youtube_url(url), url)
    
    def test_invalid_youtube_urls(self):
        """Тест невалидных YouTube ссылок"""
        invalid_urls = [
            'https://vimeo.com/123456789',
            'https://example.com/video',
            'https://subdomain.youtube.com/watch?v=123',
            'https://youtube.com.evil.com/watch?v=123',
            'https://notyoutube.com/watch?v=123',
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValidationError):
                    validate_youtube_url(url)


class CourseCRUDTest(APITestCase):
    """Тесты CRUD операций для курсов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )
        
        # Создаем группу модераторов
        self.moderator_group = Group.objects.create(name='Модераторы')
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123'
        )
        self.moderator.groups.add(self.moderator_group)
        
        # Создаем тестовый курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user1
        )
    
    def test_course_creation(self):
        """Тест создания курса"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
    
    def test_course_creation_unauthorized(self):
        """Тест создания курса без авторизации"""
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_course_update_owner(self):
        """Тест обновления курса владельцем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('course-detail', kwargs={'pk': self.course.pk})
        data = {'title': 'Updated Course'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')
    
    def test_course_delete_owner(self):
        """Тест удаления курса владельцем"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('course-detail', kwargs={'pk': self.course.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)


class LessonCRUDTest(APITestCase):
    """Тесты CRUD операций для уроков"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        
        # Создаем тестовый курс и урок
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user1
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            course=self.course,
            owner=self.user1
        )
    
    def test_lesson_creation_valid_url(self):
        """Тест создания урока с валидной YouTube ссылкой"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('lesson-list')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_url': 'https://www.youtube.com/watch?v=test123',
            'course': self.course.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
    
    def test_lesson_creation_invalid_url(self):
        """Тест создания урока с невалидной ссылкой"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('lesson-list')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_url': 'https://vimeo.com/123456789',
            'course': self.course.pk
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourseSubscriptionTest(APITestCase):
    """Тесты функционала подписки на курсы"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )
        
        # Создаем тестовые курсы
        self.course1 = Course.objects.create(
            title='Course 1',
            description='Description 1',
            owner=self.user1
        )
        self.course2 = Course.objects.create(
            title='Course 2',
            description='Description 2',
            owner=self.user2
        )
    
    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('course-subscribe', kwargs={'pk': self.course2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.user1, 
                course=self.course2, 
                is_active=True
            ).exists()
        )
    
    def test_subscribe_to_own_course(self):
        """Тест попытки подписки на собственный курс"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('course-subscribe', kwargs={'pk': self.course1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('собственный курс', response.data['error'])
    
    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        # Сначала подписываемся
        subscription = CourseSubscription.objects.create(
            user=self.user1,
            course=self.course2,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('course-unsubscribe', kwargs={'pk': self.course2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_active)


class PaginationTest(APITestCase):
    """Тесты пагинации"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        
        # Создаем много курсов для тестирования пагинации
        for i in range(25):
            Course.objects.create(
                title=f'Course {i}',
                description=f'Description {i}',
                owner=self.user
            )
    
    def test_course_pagination(self):
        """Тест пагинации курсов"""
        self.client.force_authenticate(user=self.user)
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 10)  # page_size = 10
        self.assertEqual(response.data['count'], 25)
    
    def test_course_pagination_custom_page_size(self):
        """Тест пагинации курсов с кастомным размером страницы"""
        self.client.force_authenticate(user=self.user)
        url = reverse('course-list')
        response = self.client.get(url, {'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
