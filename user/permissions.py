from rest_framework import permissions


class IsUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role:
            return request.user.role == 'admin'


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'moderator'


class IsUserOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return IsAdmin.has_permission(self, request, view)\
               or IsUserOwner.has_object_permission(self, request, view, obj)