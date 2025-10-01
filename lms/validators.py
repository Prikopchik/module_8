from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    """
    if not value:
        return value
    
    try:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()
        
        # Проверяем, что домен содержит youtube.com
        if 'youtube.com' not in domain and 'youtu.be' not in domain:
            raise ValidationError(
                'Разрешены только ссылки на YouTube (youtube.com или youtu.be)'
            )
        
        # Дополнительная проверка для youtube.com
        if 'youtube.com' in domain:
            # Проверяем, что это именно youtube.com, а не поддомен
            if not re.match(r'^(www\.)?youtube\.com$', domain):
                raise ValidationError(
                    'Разрешены только ссылки на youtube.com'
                )
        
        return value
        
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise ValidationError('Некорректная ссылка')


class YouTubeURLValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """
    
    def __init__(self, field='video_url'):
        self.field = field
    
    def __call__(self, attrs):
        if self.field in attrs:
            validate_youtube_url(attrs[self.field])
        return attrs
