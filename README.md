
# Платформа онлайн-обучения

Проект платформы онлайн-обучения с курсами, уроками, подписками и интеграцией со Stripe.

## 🌐 Демо сервер

**Адрес развернутого приложения**: `http://158.160.123.240`

**Сервер**: django-server (Yandex Cloud)

> ⚠️ **Примечание**: Для доступа к приложению на удаленном сервере необходимо настроить переменные окружения и выполнить первоначальную настройку базы данных.

## Содержание

- [Запуск через Docker Compose](#запуск-через-docker-compose)
- [Настройка удаленного сервера с Docker](#настройка-удаленного-сервера-с-docker)
- [CI/CD с GitHub Actions](#cicd-с-github-actions)
- [Локальная разработка](#локальная-разработка-без-docker)

> 📖 **Подробная инструкция по настройке сервера**: см. [SERVER_SETUP.md](SERVER_SETUP.md)  
> ☁️ **Настройка в Yandex Cloud**: см. [YANDEX_CLOUD_SETUP.md](YANDEX_CLOUD_SETUP.md)  
> 🚀 **Быстрая настройка сервера**: см. [SETUP_SERVER.md](SETUP_SERVER.md)  
> 🔒 **Информация о безопасности**: см. [SECURITY.md](SECURITY.md)

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
POSTGRES_DB=drf_db
POSTGRES_USER=drf_user
POSTGRES_PASSWORD=password12345

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

- **web** - Django приложение с Gunicorn (внутренний порт 8000)
- **nginx** - Nginx reverse proxy (порт 80)
- **db** - PostgreSQL база данных (порт 5432)
- **redis** - Redis для Celery (порт 6379)
- **celery** - Celery worker для фоновых задач
- **celery-beat** - Celery Beat для периодических задач

### Архитектура контейнеров

```
┌─────────────┐
│   Nginx     │ (порт 80)
│  (порт 80) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Django    │ (Gunicorn, порт 8000)
│   (web)     │
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌─────┐ ┌──────┐
│PostgreSQL│ │ Redis │
└─────┘ └──────┘
   │       │
   └───┬───┘
       ▼
┌─────────────┐
│   Celery    │ (Worker + Beat)
└─────────────┘
```

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

## Настройка удаленного сервера с Docker

### Предварительные требования

- Ubuntu 20.04+ или Debian 11+
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Шаг 1: Установка Docker и Docker Compose

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверка установки
docker --version
docker-compose --version

# Выход и повторный вход для применения изменений группы
exit
```

### Шаг 2: Настройка безопасности

```bash
# Настройка firewall (UFW)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable

# Настройка SSH (рекомендуется использовать ключи)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
ssh-copy-id username@158.160.123.240
```

### Шаг 3: Развертывание приложения

```bash
# Создание директории проекта
sudo mkdir -p /var/www/learning-platform
sudo chown -R $USER:$USER /var/www/learning-platform

# Клонирование репозитория
cd /var/www/learning-platform
git clone https://github.com/your-username/your-repo.git .

# Копирование и настройка .env файла
cp env.example .env
nano .env  # Отредактируйте файл с вашими настройками
```

**Важно**: В файле `.env` укажите:
- `ALLOWED_HOSTS` - `158.160.123.240,localhost,127.0.0.1`
- `DEBUG=False` - для production
- Данные БД уже настроены: `drf_db` / `drf_user` / `password12345`
- Все остальные переменные окружения

### Шаг 4: Запуск приложения

```bash
# Сборка и запуск всех контейнеров
docker-compose up -d --build

# Проверка статуса контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Создание группы модераторов
docker-compose exec web python manage.py create_moderator_group

# Сбор статических файлов
docker-compose exec web python manage.py collectstatic --noinput
```

### Шаг 5: Проверка работоспособности

```bash
# Проверка статуса всех сервисов
docker-compose ps

# Проверка логов
docker-compose logs web
docker-compose logs nginx
docker-compose logs celery

# Проверка доступности приложения
curl http://localhost/api/
```

### Полезные команды для управления

```bash
# Остановка всех контейнеров
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart web
docker-compose restart nginx

# Просмотр логов конкретного сервиса
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f celery

# Выполнение команд в контейнере
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate

# Обновление кода (после git pull)
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

## Настройка удаленного сервера (без Docker)

### Предварительные требования

- Ubuntu 20.04+ или Debian 11+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx
- Git

### Шаг 1: Установка системных пакетов

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git curl

# Установка PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE drf_db;"
sudo -u postgres psql -c "CREATE USER drf_user WITH PASSWORD 'password12345';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE drf_db TO drf_user;"
```

### Шаг 2: Настройка безопасности

```bash
# Настройка firewall (UFW)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable

# Настройка SSH (рекомендуется использовать ключи)
# Создайте SSH ключ на локальной машине:
ssh-keygen -t rsa -b 4096

# Скопируйте публичный ключ на сервер:
ssh-copy-id username@158.160.123.240
```

### Шаг 3: Развертывание приложения

```bash
# Создание директории проекта
sudo mkdir -p /var/www/learning-platform
sudo chown -R $USER:$USER /var/www/learning-platform

# Клонирование репозитория
cd /var/www/learning-platform
git clone https://github.com/your-username/your-repo.git .

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Копирование и настройка .env файла
cp env.example .env
nano .env  # Отредактируйте файл с вашими настройками
```

### Шаг 4: Настройка базы данных

```bash
# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Создание группы модераторов
python manage.py create_moderator_group

# Сбор статических файлов
python manage.py collectstatic --noinput
```

### Шаг 5: Настройка Systemd сервисов

```bash
# Копирование конфигурационных файлов
sudo cp deploy/learning-platform.service /etc/systemd/system/
sudo cp deploy/celery-worker.service /etc/systemd/system/
sudo cp deploy/celery-beat.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск сервисов
sudo systemctl enable learning-platform.service
sudo systemctl enable celery-worker.service
sudo systemctl enable celery-beat.service

sudo systemctl start learning-platform.service
sudo systemctl start celery-worker.service
sudo systemctl start celery-beat.service

# Проверка статуса
sudo systemctl status learning-platform.service
sudo systemctl status celery-worker.service
sudo systemctl status celery-beat.service
```

### Шаг 6: Настройка Nginx

```bash
# Копирование конфигурации Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/learning-platform

# Редактирование конфигурации (укажите ваш домен или IP)
sudo nano /etc/nginx/sites-available/learning-platform

# Создание символической ссылки
sudo ln -s /etc/nginx/sites-available/learning-platform /etc/nginx/sites-enabled/

# Удаление дефолтной конфигурации (опционально)
sudo rm /etc/nginx/sites-enabled/default

# Проверка конфигурации
sudo nginx -t

# Перезагрузка Nginx
sudo systemctl reload nginx
```

### Шаг 7: Создание директорий для логов

```bash
sudo mkdir -p /var/log/learning-platform
sudo chown -R www-data:www-data /var/log/learning-platform
```

### Полезные команды для управления сервисами

```bash
# Перезапуск сервисов
sudo systemctl restart learning-platform.service
sudo systemctl restart celery-worker.service
sudo systemctl restart celery-beat.service

# Просмотр логов
sudo journalctl -u learning-platform.service -f
sudo journalctl -u celery-worker.service -f
sudo journalctl -u celery-beat.service -f

# Просмотр логов приложения
tail -f /var/log/learning-platform/error.log
tail -f /var/log/learning-platform/celery-worker.log
```

## CI/CD с GitHub Actions

Проект настроен для автоматического тестирования, линтинга, проверки сборки Docker образов и деплоя через GitHub Actions.

### Этапы CI/CD Pipeline

1. **Линтинг** - Проверка кода с помощью flake8, black, isort
2. **Тестирование** - Запуск всех тестов проекта
3. **Сборка Docker образов** - Проверка возможности сборки всех Docker образов
4. **Деплой** - Автоматический деплой на сервер через Docker Compose (только при push в main/develop)

### Настройка GitHub Secrets

Для работы автоматического деплоя необходимо настроить следующие секреты в настройках репозитория GitHub:

1. Перейдите в **Settings** → **Secrets and variables** → **Actions**
2. Добавьте следующие секреты:

- `HOST` - IP-адрес вашего сервера: `158.160.123.240`
- `USERNAME` - Имя пользователя для SSH подключения (например: `ubuntu` или `root`)
- `SSH_KEY` - Приватный SSH ключ для доступа к серверу (содержимое файла `~/.ssh/id_rsa`)
- `PORT` - Порт SSH (обычно 22, можно не указывать если стандартный)
- `PROJECT_PATH` - Путь к проекту на сервере (например: `/var/www/learning-platform`)

### Как получить SSH ключ

```bash
# Если у вас еще нет SSH ключа, создайте его:
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Скопируйте приватный ключ (для GitHub Secret):
cat ~/.ssh/id_rsa

# Скопируйте публичный ключ на сервер:
ssh-copy-id username@158.160.123.240
```

### Workflow файл

Workflow находится в `.github/workflows/ci-cd.yml` и выполняет следующие шаги:

1. **Линтинг** - Запускается при каждом push и pull request
   - Проверка кода с помощью flake8
   - Проверка форматирования с помощью black
   - Проверка сортировки импортов с помощью isort

2. **Тестирование** - Запускается при каждом push и pull request
   - Устанавливает зависимости
   - Применяет миграции
   - Запускает тесты проекта

3. **Сборка Docker образов** - Запускается после успешного линтинга и тестов
   - Собирает Docker образ для Django приложения
   - Собирает Docker образ для Nginx
   - Проверяет конфигурацию docker-compose.yaml

4. **Деплой** - Запускается только после успешного прохождения всех проверок при push в `main` или `develop`
   - Подключается к серверу по SSH
   - Обновляет код из репозитория
   - Останавливает старые контейнеры
   - Собирает новые Docker образы
   - Запускает контейнеры через docker-compose
   - Применяет миграции
   - Собирает статические файлы
   - Проверяет статус контейнеров

### Запуск workflow

Workflow запускается автоматически при:
- Push в ветки `main` или `develop`
- Создании Pull Request в ветки `main` или `develop`

Вы можете также запустить workflow вручную:
1. Перейдите в **Actions** в вашем репозитории
2. Выберите workflow **CI/CD Pipeline**
3. Нажмите **Run workflow**

### Проверка статуса деплоя

1. Перейдите в раздел **Actions** вашего репозитория
2. Выберите нужный workflow run
3. Просмотрите логи выполнения каждого шага

### Устранение проблем

Если деплой не удался:

1. **Проверьте логи в GitHub Actions**
   - Перейдите в раздел Actions вашего репозитория
   - Откройте неудачный workflow run
   - Просмотрите логи каждого шага

2. **Проверьте подключение к серверу**
   ```bash
   ssh username@158.160.123.240
   ```

3. **Проверьте Docker на сервере**
   ```bash
   docker --version
   docker-compose --version
   docker ps
   ```

4. **Проверьте статус контейнеров**
   ```bash
   cd /var/www/learning-platform
   docker-compose ps
   docker-compose logs
   ```

5. **Проверьте переменные окружения**
   - Убедитесь, что файл `.env` существует и правильно настроен
   - Проверьте, что `ALLOWED_HOSTS` содержит IP или домен сервера

6. **Проверьте права доступа**
   ```bash
   ls -la /var/www/learning-platform
   ```

7. **Проверьте GitHub Secrets**
   - Убедитесь, что все секреты настроены правильно
   - Проверьте формат SSH ключа (должен быть приватный ключ)

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