from rest_framework import permissions


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Пользователь может редактировать только свои объекты, 
    модераторы могут редактировать любые объекты (кроме создания и удаления)
    """
    
    def has_permission(self, request, view):
        # Разрешаем все действия для аутентифицированных пользователей
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение для всех аутентифицированных пользователей
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверяем, является ли пользователь владельцем объекта
        if hasattr(obj, 'owner'):
            if obj.owner == request.user:
                return True
        
        # Проверяем, является ли пользователь модератором
        if request.user.groups.filter(name='Модераторы').exists():
            # Модераторы не могут создавать или удалять объекты
            if request.method in ['POST', 'DELETE']:
                return False
            return True
        
        return False


class IsOwnerOrModeratorForCreate(permissions.BasePermission):
    """
    Разрешает создание только владельцам, модераторы не могут создавать
    """
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Только владельцы могут создавать объекты
            return True
        return True
    
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение для всех аутентифицированных пользователей
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверяем, является ли пользователь владельцем объекта
        if hasattr(obj, 'owner'):
            if obj.owner == request.user:
                return True
        
        # Проверяем, является ли пользователь модератором
        if request.user.groups.filter(name='Модераторы').exists():
            # Модераторы не могут создавать или удалять объекты
            if request.method in ['POST', 'DELETE']:
                return False
            return True
        
        return False


class IsOwnerOrModeratorForDelete(permissions.BasePermission):
    """
    Разрешает удаление только владельцам, модераторы не могут удалять
    """
    
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение для всех аутентифицированных пользователей
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Проверяем, является ли пользователь владельцем объекта
        if hasattr(obj, 'owner'):
            if obj.owner == request.user:
                return True
        
        # Модераторы не могут удалять объекты
        if request.user.groups.filter(name='Модераторы').exists():
            if request.method == 'DELETE':
                return False
            return True
        
        return False
