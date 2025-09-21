
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