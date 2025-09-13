from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer, LessonListSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def perform_create(self, serializer):
        from users.models import User
        default_user, created = User.objects.get_or_create(
            email='default@example.com',
            defaults={'first_name': 'Default', 'last_name': 'User'}
        )
        serializer.save(owner=default_user)
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonListSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
    def perform_create(self, serializer):
        from users.models import User
        default_user, created = User.objects.get_or_create(
            email='default@example.com',
            defaults={'first_name': 'Default', 'last_name': 'User'}
        )
        serializer.save(owner=default_user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
