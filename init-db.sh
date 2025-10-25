#!/bin/bash

# Скрипт для инициализации базы данных
echo "Ожидание запуска базы данных..."
sleep 10

echo "Применение миграций..."
python manage.py migrate

echo "Создание суперпользователя (если не существует)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'admin123')
    print('Суперпользователь создан: admin@example.com / admin123')
else:
    print('Суперпользователь уже существует')
EOF

echo "Создание группы модераторов..."
python manage.py create_moderator_group

echo "Инициализация завершена!"
