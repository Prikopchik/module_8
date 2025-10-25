# Инструкция по развертыванию

## Быстрый запуск

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd module_8
```

2. **Скопируйте файл переменных окружения:**
```bash
cp env.example .env
```

3. **Отредактируйте `.env` файл** (измените SECRET_KEY и другие настройки):
```bash
# Сгенерируйте новый SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. **Запустите все сервисы:**
```bash
docker-compose up -d
```

5. **Проверьте статус сервисов:**
```bash
docker-compose ps
```

6. **Просмотрите логи (если нужно):**
```bash
docker-compose logs -f
```

## Проверка работоспособности

После запуска проверьте доступность сервисов:

- **API**: http://localhost:8000/api/
- **Документация**: http://localhost:8000/api/docs/
- **Админка**: http://localhost:8000/admin/

## Полезные команды

```bash
# Остановить все сервисы
docker-compose down

# Остановить с удалением данных
docker-compose down -v

# Пересобрать образы
docker-compose build --no-cache

# Выполнить команду в контейнере
docker-compose exec web python manage.py shell

# Просмотр логов конкретного сервиса
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

## Структура проекта

```
├── docker-compose.yaml    # Конфигурация Docker Compose
├── Dockerfile            # Образ для Django приложения
├── .env.example         # Шаблон переменных окружения
├── init-db.sh           # Скрипт инициализации БД
├── requirements.txt     # Python зависимости
└── learning_platform/   # Django проект
    ├── settings.py      # Настройки Django
    ├── celery.py        # Конфигурация Celery
    └── ...
```
