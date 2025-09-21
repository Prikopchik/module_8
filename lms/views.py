from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsOwnerOrModerator, IsOwnerOrModeratorForCreate, IsOwnerOrModeratorForDelete
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer, LessonListSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    
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


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    
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
