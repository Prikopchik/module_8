from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """
    Пагинация для курсов
    """
    page_size = 10  # Количество курсов на странице
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 50  # Максимальный размер страницы


class LessonPagination(PageNumberPagination):
    """
    Пагинация для уроков
    """
    page_size = 15  # Количество уроков на странице
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 100  # Максимальный размер страницы


class SubscriptionPagination(PageNumberPagination):
    """
    Пагинация для подписок
    """
    page_size = 20  # Количество подписок на странице
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 100  # Максимальный размер страницы
