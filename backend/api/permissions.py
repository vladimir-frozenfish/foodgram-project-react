from rest_framework import permissions


class IsUserOrReadAndCreate(permissions.BasePermission):
    def has_object_permission(self, request, view, user):
        return (
            request.method in permissions.SAFE_METHODS
            or user == request.user
        )


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in
                permissions.SAFE_METHODS or obj.author == request.user)