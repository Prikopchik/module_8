# Быстрый запуск проекта

## 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

## 2. Применение миграций
```bash
python manage.py migrate
```

## 3. Создание тестовых данных
```bash
python manage.py create_payments --count 30
```

## 4. Создание суперпользователя (опционально)
```bash
python manage.py createsuperuser
```

## 5. Запуск сервера
```bash
python manage.py runserver
```

## 6. Доступ к API
- **API документация:** http://127.0.0.1:8000/api/
- **Админка:** http://127.0.0.1:8000/admin/
- **Курсы:** http://127.0.0.1:8000/api/courses/
- **Уроки:** http://127.0.0.1:8000/api/lessons/
- **Платежи:** http://127.0.0.1:8000/api/users/payments/