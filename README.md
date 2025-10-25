
# Платформа онлайн-обучения

Проект платформы онлайн-обучения с курсами, уроками, подписками и интеграцией со Stripe.

## Запуск через Docker Compose

### Предварительные требования
- Docker
- Docker Compose

### Быстрый старт

1. **Скопируйте файл с переменными окружения:**
```bash
cp env.example .env
```

2. **Отредактируйте файл `.env`** (при необходимости измените настройки):
```bash
# Основные настройки Django
DEBUG=True
SECRET_KEY=your-secret-key-here

# Настройки базы данных
POSTGRES_DB=learning_platform
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Настройки Redis
REDIS_URL=redis://redis:6379/0

# Настройки Stripe (замените на ваши ключи)
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

3. **Запустите все сервисы:**
```bash
docker-compose up -d
```

4. **Примените миграции базы данных:**
```bash
docker-compose exec web python manage.py migrate
```

5. **Создайте суперпользователя:**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Создайте тестовые данные (опционально):**
```bash
docker-compose exec web python manage.py create_payments --count 30
```

### Проверка работоспособности сервисов

После запуска все сервисы будут доступны по следующим адресам:

- **Django API**: http://localhost:8000/api/
- **API документация (Swagger)**: http://localhost:8000/api/docs/
- **Админ-панель**: http://localhost:8000/admin/
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Полезные команды

**Просмотр логов:**
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

**Остановка сервисов:**
```bash
docker-compose down
```

**Остановка с удалением данных:**
```bash
docker-compose down -v
```

**Перезапуск конкретного сервиса:**
```bash
docker-compose restart web
```

**Выполнение команд в контейнере:**
```bash
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py collectstatic
```

### Структура сервисов

- **web** - Django приложение (порт 8000)
- **db** - PostgreSQL база данных (порт 5432)
- **redis** - Redis для Celery (порт 6379)
- **celery** - Celery worker для фоновых задач
- **celery-beat** - Celery Beat для периодических задач

### Фоновые задачи

Проект включает следующие фоновые задачи:
- **Отправка email уведомлений** при обновлении курсов/уроков
- **Деактивация неактивных пользователей** (ежедневно, пользователи не заходившие >30 дней)

## Локальная разработка (без Docker)

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения (скопируйте из `env.example`)

3. Примените миграции:
```bash
python manage.py migrate
```

4. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

5. Запустите сервер:
```bash
python manage.py runserver
```

6. Запустите Celery worker (в отдельном терминале):
```bash
celery -A learning_platform worker -l info
```

7. Запустите Celery Beat (в отдельном терминале):
```bash
celery -A learning_platform beat -l info
```

## Структура файлов Docker

- `docker-compose.yaml` - Конфигурация всех сервисов
- `Dockerfile` - Образ для Django приложения  
- `env.example` - Шаблон переменных окружения
- `init-db.sh` - Скрипт инициализации базы данных
- `.dockerignore` - Исключения для Docker сборки
- `DEPLOYMENT.md` - Подробная инструкция по развертыванию

## Переменные окружения

Все чувствительные данные вынесены в файл `.env`:

- `SECRET_KEY` - Секретный ключ Django
- `POSTGRES_*` - Настройки базы данных PostgreSQL
- `REDIS_URL` - URL для подключения к Redis
- `STRIPE_*` - Ключи для интеграции со Stripe
- `EMAIL_*` - Настройки email

## Мониторинг и логи

Для мониторинга работы сервисов используйте:

```bash
# Статус всех сервисов
docker-compose ps

# Логи в реальном времени
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f celery-beat
```