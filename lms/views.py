from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from users.permissions import IsOwnerOrModerator, IsOwnerOrModeratorForCreate, IsOwnerOrModeratorForDelete
from .models import Course, Lesson, CourseSubscription
from .serializers import CourseSerializer, LessonSerializer, LessonListSerializer, CourseSubscriptionSerializer
from .paginators import CoursePagination, LessonPagination, SubscriptionPagination


@extend_schema_view(
    list=extend_schema(
        summary="Получить список курсов",
        description="Возвращает пагинированный список курсов с информацией о подписке",
        tags=["Курсы"]
    ),
    create=extend_schema(
        summary="Создать курс",
        description="Создает новый курс. Только авторизованные пользователи могут создавать курсы.",
        tags=["Курсы"]
    ),
    retrieve=extend_schema(
        summary="Получить курс",
        description="Возвращает детальную информацию о курсе с признаком подписки",
        tags=["Курсы"]
    ),
    update=extend_schema(
        summary="Обновить курс",
        description="Полное обновление курса. Доступно только владельцу или модератору.",
        tags=["Курсы"]
    ),
    partial_update=extend_schema(
        summary="Частично обновить курс",
        description="Частичное обновление курса. Доступно только владельцу или модератору.",
        tags=["Курсы"]
    ),
    destroy=extend_schema(
        summary="Удалить курс",
        description="Удаляет курс. Доступно только владельцу или модератору.",
        tags=["Курсы"]
    ),
    lessons=extend_schema(
        summary="Получить уроки курса",
        description="Возвращает список уроков для конкретного курса",
        tags=["Курсы"]
    ),
    subscribe=extend_schema(
        summary="Подписаться на курс",
        description="Подписывает текущего пользователя на обновления курса",
        tags=["Курсы", "Подписки"]
    ),
    unsubscribe=extend_schema(
        summary="Отписаться от курса",
        description="Отписывает текущего пользователя от обновлений курса",
        tags=["Курсы", "Подписки"]
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    pagination_class = CoursePagination
    
    def get_queryset(self):
        # Пользователи видят только свои курсы, модераторы видят все
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        # Только владельцы могут создавать курсы
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        # Проверка прав доступа через permission class
        serializer.save()
    
    def perform_destroy(self, instance):
        # Проверка прав доступа через permission class
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonListSerializer(lessons, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """
        Подписка на курс
        """
        # Для подписки нужно получить курс без фильтрации по владельцу
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        user = request.user
        
        # Проверяем, что пользователь не подписывается на свой курс
        if course.owner == user:
            return Response(
                {'error': 'Нельзя подписаться на собственный курс'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, не подписан ли уже пользователь
        subscription, created = CourseSubscription.objects.get_or_create(
            user=user,
            course=course,
            defaults={'is_active': True}
        )
        
        if not created:
            if subscription.is_active:
                return Response(
                    {'message': 'Вы уже подписаны на этот курс'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                subscription.is_active = True
                subscription.save()
                return Response(
                    {'message': 'Подписка на курс восстановлена'}, 
                    status=status.HTTP_200_OK
                )
        
        serializer = CourseSubscriptionSerializer(subscription, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def unsubscribe(self, request, pk=None):
        """
        Отписка от курса
        """
        # Для отписки нужно получить курс без фильтрации по владельцу
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        user = request.user
        
        try:
            subscription = CourseSubscription.objects.get(user=user, course=course)
            subscription.is_active = False
            subscription.save()
            return Response(
                {'message': 'Вы отписались от курса'}, 
                status=status.HTTP_200_OK
            )
        except CourseSubscription.DoesNotExist:
            return Response(
                {'error': 'Вы не подписаны на этот курс'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    list=extend_schema(
        summary="Получить список уроков",
        description="Возвращает пагинированный список уроков",
        tags=["Уроки"]
    ),
    create=extend_schema(
        summary="Создать урок",
        description="Создает новый урок. Ссылка на видео должна быть только с YouTube.",
        tags=["Уроки"]
    ),
    retrieve=extend_schema(
        summary="Получить урок",
        description="Возвращает детальную информацию об уроке",
        tags=["Уроки"]
    ),
    update=extend_schema(
        summary="Обновить урок",
        description="Полное обновление урока. Доступно только владельцу или модератору.",
        tags=["Уроки"]
    ),
    partial_update=extend_schema(
        summary="Частично обновить урок",
        description="Частичное обновление урока. Доступно только владельцу или модератору.",
        tags=["Уроки"]
    ),
    destroy=extend_schema(
        summary="Удалить урок",
        description="Удаляет урок. Доступно только владельцу или модератору.",
        tags=["Уроки"]
    ),
)
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    pagination_class = LessonPagination
    
    def get_queryset(self):
        # Пользователи видят только свои уроки, модераторы видят все
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        # Только владельцы могут создавать уроки
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        # Проверка прав доступа через permission class
        serializer.save()
    
    def perform_destroy(self, instance):
        # Проверка прав доступа через permission class
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="Получить список подписок",
        description="Возвращает пагинированный список активных подписок пользователя",
        tags=["Подписки"]
    ),
    create=extend_schema(
        summary="Создать подписку",
        description="Создает новую подписку на курс",
        tags=["Подписки"]
    ),
    retrieve=extend_schema(
        summary="Получить подписку",
        description="Возвращает детальную информацию о подписке",
        tags=["Подписки"]
    ),
    update=extend_schema(
        summary="Обновить подписку",
        description="Полное обновление подписки",
        tags=["Подписки"]
    ),
    partial_update=extend_schema(
        summary="Частично обновить подписку",
        description="Частичное обновление подписки",
        tags=["Подписки"]
    ),
    destroy=extend_schema(
        summary="Удалить подписку",
        description="Удаляет подписку (деактивирует)",
        tags=["Подписки"]
    ),
)
class CourseSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подписками на курсы
    """
    queryset = CourseSubscription.objects.all()
    serializer_class = CourseSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SubscriptionPagination
    
    def get_queryset(self):
        # Пользователи видят только свои подписки
        return CourseSubscription.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
