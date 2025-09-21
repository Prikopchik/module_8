from rest_framework import viewsets, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import PaymentSerializer, PaymentListSerializer, UserSerializer, UserUpdateSerializer, LoginSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    filterset_fields = {
        'paid_course': ['exact'],
        'paid_lesson': ['exact'],
        'payment_method': ['exact'],
        'payment_date': ['gte', 'lte', 'exact'],
        'amount': ['gte', 'lte', 'exact'],
    }
    
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']
    
    search_fields = ['user__email', 'paid_course__title', 'paid_lesson__title']
    
    def get_queryset(self):
        # Пользователи видят только свои платежи
        return Payment.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return UserSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        if self.action == 'list':
            # Пользователи могут видеть только свой профиль
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        # Пользователи могут обновлять только свой профиль
        if serializer.instance != self.request.user:
            return Response({'error': 'Вы можете редактировать только свой профиль'}, 
                          status=status.HTTP_403_FORBIDDEN)
        serializer.save()
    
    def perform_destroy(self, instance):
        # Пользователи могут удалять только свой профиль
        if instance != self.request.user:
            return Response({'error': 'Вы можете удалить только свой профиль'}, 
                          status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Создаем JWT токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Создаем JWT токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Успешный выход'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': 'Неверный токен'}, status=status.HTTP_400_BAD_REQUEST)