from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
    '''Доступ для безопасных запросов или для автора.'''

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
