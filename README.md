# Learning Platform - Django DRF API

Django-проект с Django REST Framework для платформы обучения.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Примените миграции:
```bash
python manage.py migrate
```

3. Создайте тестовые данные:
```bash
python manage.py create_payments --count 30
```

4. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

5. Запустите сервер:
```bash
python manage.py runserver
```

## API Эндпоинты

### Курсы
- `GET /api/courses/` - список курсов с количеством и списком уроков
- `POST /api/courses/` - создание курса
- `GET /api/courses/{id}/` - детальная информация о курсе
- `PUT/PATCH /api/courses/{id}/` - обновление курса
- `DELETE /api/courses/{id}/` - удаление курса
- `GET /api/courses/{id}/lessons/` - уроки курса

### Уроки
- `GET /api/lessons/` - список уроков
- `POST /api/lessons/` - создание урока
- `GET /api/lessons/{id}/` - детальная информация об уроке
- `PUT/PATCH /api/lessons/{id}/` - обновление урока
- `DELETE /api/lessons/{id}/` - удаление урока

### Платежи
- `GET /api/users/payments/` - список платежей с фильтрацией
- `POST /api/users/payments/` - создание платежа
- `GET /api/users/payments/{id}/` - детальная информация о платеже
- `PUT/PATCH /api/users/payments/{id}/` - обновление платежа
- `DELETE /api/users/payments/{id}/` - удаление платежа

## Фильтрация платежей

- `?payment_method=cash` - фильтр по способу оплаты
- `?paid_course=1` - фильтр по курсу
- `?paid_lesson=1` - фильтр по уроку
- `?amount__gte=1000` - фильтр по сумме
- `?ordering=payment_date` - сортировка по дате
- `?ordering=-amount` - сортировка по сумме (убывание)

## Модели

### User (Пользователь)
- Авторизация по email
- Поля: email, phone, city, avatar
- Наследуется от AbstractUser

### Course (Курс)
- Поля: title, preview, description, owner
- Связь с пользователем (владелец)
- Поле с количеством уроков
- Поле со списком всех уроков

### Lesson (Урок)
- Поля: title, description, preview, video_url, course, owner
- Связь с курсом и пользователем

### Payment (Платеж)
- Поля: user, payment_date, paid_course, paid_lesson, amount, payment_method
- Валидация: должен быть указан либо курс, либо урок

## Технологии

- Django 5.2.6
- Django REST Framework 3.16.1
- django-filter 25.1
- Pillow 11.3.0

## Админка

Доступна по адресу: http://127.0.0.1:8000/admin/

## Готово к использованию! 🚀