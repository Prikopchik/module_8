from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from users.permissions import IsOwnerOrModerator, IsOwnerOrModeratorForCreate, IsOwnerOrModeratorForDelete
from .models import Course, Lesson, CourseSubscription
from .serializers import CourseSerializer, LessonSerializer, LessonListSerializer, CourseSubscriptionSerializer
from .paginators import CoursePagination, LessonPagination, SubscriptionPagination


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
