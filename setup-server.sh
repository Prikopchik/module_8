#!/bin/bash

# Скрипт автоматической настройки сервера для проекта Learning Platform
# Использование: ./setup-server.sh

set -e

echo "=========================================="
echo "Настройка сервера Learning Platform"
echo "=========================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка, что скрипт запущен от имени пользователя (не root)
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Ошибка: Не запускайте скрипт от root. Используйте обычного пользователя.${NC}"
   exit 1
fi

# Переменные
PROJECT_DIR="/var/www/learning-platform"
REPO_URL=""

# Функция для вывода сообщений
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен. Устанавливаю..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        info "Docker установлен. Вам нужно выйти и войти снова для применения изменений."
        exit 0
    fi
    info "Docker установлен: $(docker --version)"
}

# Проверка Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose не установлен. Устанавливаю..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        info "Docker Compose установлен"
    fi
    info "Docker Compose установлен: $(docker-compose --version)"
}

# Создание директории проекта
create_project_dir() {
    if [ ! -d "$PROJECT_DIR" ]; then
        info "Создание директории проекта..."
        sudo mkdir -p $PROJECT_DIR
        sudo chown -R $USER:$USER $PROJECT_DIR
    else
        warn "Директория $PROJECT_DIR уже существует"
    fi
}

# Клонирование репозитория
clone_repo() {
    cd $PROJECT_DIR
    
    if [ -d ".git" ]; then
        warn "Репозиторий уже клонирован. Пропускаю клонирование."
        return
    fi
    
    if [ -z "$REPO_URL" ]; then
        read -p "Введите URL репозитория GitHub: " REPO_URL
    fi
    
    info "Клонирование репозитория..."
    git clone $REPO_URL .
}

# Настройка .env файла
setup_env() {
    cd $PROJECT_DIR
    
    if [ -f ".env" ]; then
        warn "Файл .env уже существует. Пропускаю создание."
        return
    fi
    
    info "Создание файла .env из шаблона..."
    cp env.example .env
    
    # Генерация SECRET_KEY
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "django-insecure-$(openssl rand -hex 32)")
    
    # Замена SECRET_KEY в .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
    fi
    
    # Получение IP адреса сервера
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || hostname -I | awk '{print $1}')
    
    warn "Файл .env создан. Необходимо отредактировать следующие параметры:"
    echo "  1. ALLOWED_HOSTS - укажите ваш IP: $SERVER_IP"
    echo "  2. POSTGRES_PASSWORD - придумайте надежный пароль"
    echo "  3. STRIPE_* - укажите ваши ключи Stripe (если используете)"
    echo ""
    read -p "Нажмите Enter для редактирования .env файла (или Ctrl+C для выхода)..."
    nano .env
}

# Запуск контейнеров
start_containers() {
    cd $PROJECT_DIR
    
    info "Сборка и запуск контейнеров..."
    docker-compose up -d --build
    
    info "Ожидание запуска сервисов..."
    sleep 10
    
    info "Проверка статуса контейнеров..."
    docker-compose ps
}

# Применение миграций
run_migrations() {
    cd $PROJECT_DIR
    
    info "Применение миграций..."
    docker-compose exec -T web python manage.py migrate --noinput
}

# Создание суперпользователя
create_superuser() {
    cd $PROJECT_DIR
    
    info "Создание суперпользователя..."
    echo "Введите данные для администратора:"
    docker-compose exec web python manage.py createsuperuser
}

# Создание группы модераторов
create_moderator_group() {
    cd $PROJECT_DIR
    
    info "Создание группы модераторов..."
    docker-compose exec -T web python manage.py create_moderator_group || warn "Группа модераторов уже существует или команда не найдена"
}

# Сбор статических файлов
collect_static() {
    cd $PROJECT_DIR
    
    info "Сбор статических файлов..."
    docker-compose exec -T web python manage.py collectstatic --noinput
}

# Основная функция
main() {
    info "Начало настройки сервера..."
    
    # Проверка зависимостей
    check_docker
    check_docker_compose
    
    # Настройка проекта
    create_project_dir
    clone_repo
    setup_env
    
    # Запуск контейнеров
    start_containers
    
    # Настройка базы данных
    run_migrations
    create_moderator_group
    collect_static
    
    # Создание суперпользователя
    echo ""
    read -p "Создать суперпользователя сейчас? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    else
        warn "Вы можете создать суперпользователя позже командой:"
        echo "  cd $PROJECT_DIR && docker-compose exec web python manage.py createsuperuser"
    fi
    
    # Итоговая информация
    echo ""
    info "=========================================="
    info "Настройка завершена!"
    info "=========================================="
    echo ""
    info "Полезные команды:"
    echo "  Просмотр статуса: cd $PROJECT_DIR && docker-compose ps"
    echo "  Просмотр логов:   cd $PROJECT_DIR && docker-compose logs -f"
    echo "  Остановка:        cd $PROJECT_DIR && docker-compose down"
    echo "  Перезапуск:       cd $PROJECT_DIR && docker-compose restart"
    echo ""
    
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || hostname -I | awk '{print $1}')
    info "Приложение должно быть доступно по адресу:"
    echo "  http://$SERVER_IP"
    echo "  http://$SERVER_IP/api/"
    echo "  http://$SERVER_IP/admin/"
    echo ""
}

# Запуск
main
