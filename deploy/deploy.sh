#!/bin/bash

# Скрипт для деплоя на сервер
# Использование: ./deploy.sh

set -e

echo "Начало деплоя..."

# Переменные
PROJECT_DIR="/var/www/learning-platform"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/your-username/your-repo.git"  # Замените на ваш репозиторий

# Создание директории проекта
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Создание директории проекта..."
    sudo mkdir -p $PROJECT_DIR
    sudo chown -R $USER:$USER $PROJECT_DIR
fi

cd $PROJECT_DIR

# Клонирование репозитория (если еще не клонирован)
if [ ! -d ".git" ]; then
    echo "Клонирование репозитория..."
    git clone $REPO_URL .
fi

# Обновление кода
echo "Обновление кода из репозитория..."
git pull origin main || git pull origin develop

# Создание виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv $VENV_DIR
fi

# Активация виртуального окружения и установка зависимостей
echo "Установка зависимостей..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Копирование .env файла (если его нет)
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Создание .env файла из шаблона..."
    cp env.example .env
    echo "ВАЖНО: Отредактируйте файл .env перед запуском!"
fi

# Применение миграций
echo "Применение миграций..."
python manage.py migrate --noinput

# Сбор статических файлов
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

# Создание директорий для логов
echo "Создание директорий для логов..."
sudo mkdir -p /var/log/learning-platform
sudo chown -R www-data:www-data /var/log/learning-platform

# Установка systemd сервисов
echo "Установка systemd сервисов..."
sudo cp deploy/learning-platform.service /etc/systemd/system/
sudo cp deploy/celery-worker.service /etc/systemd/system/
sudo cp deploy/celery-beat.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск сервисов
echo "Запуск сервисов..."
sudo systemctl enable learning-platform.service
sudo systemctl enable celery-worker.service
sudo systemctl enable celery-beat.service

sudo systemctl restart learning-platform.service
sudo systemctl restart celery-worker.service
sudo systemctl restart celery-beat.service

# Настройка Nginx
if [ ! -f "/etc/nginx/sites-available/learning-platform" ]; then
    echo "Настройка Nginx..."
    sudo cp deploy/nginx.conf /etc/nginx/sites-available/learning-platform
    sudo ln -sf /etc/nginx/sites-available/learning-platform /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
fi

echo "Деплой завершен успешно!"
echo "Проверьте статус сервисов:"
echo "  sudo systemctl status learning-platform.service"
echo "  sudo systemctl status celery-worker.service"
echo "  sudo systemctl status celery-beat.service"
