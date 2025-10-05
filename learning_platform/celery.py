import os
from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию для программы Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_platform.settings')

app = Celery('learning_platform')

# Использование строки означает, что воркеру не нужно сериализовать объект настроек
# - namespace='CELERY' означает, что все ключи конфигурации Celery
#   должны иметь префикс `CELERY_` в настройках Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загружаем модули задач из всех зарегистрированных приложений Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    return f'Request: {self.request!r}'


