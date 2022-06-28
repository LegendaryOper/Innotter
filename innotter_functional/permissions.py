from user.permissions import IsAdmin, IsModerator
from rest_framework import permissions
from user.models import User
from django.contrib.auth.models import AnonymousUser
from .services import check_page_block


class IsPageOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsPageOwnerOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return IsAdminOrModerator.has_permission(self, request, view)\
               or IsPageOwner.has_object_permission(self, request, view, obj)


class PageIsntBlocked(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.unblock_date:
            if check_page_block(obj.unblock_date):
                return True
            return IsAdminOrModerator.has_permission(self, request, view)


class PageIsntPrivate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_private:
            return IsPageOwnerOrModeratorOrAdmin.has_object_permission(self, request, view, obj)\
                   or obj.followers.filter(id=request.user.id).exists()
        return True


class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user.role == User.Roles.ADMIN \
               or request.user.role == User.Roles.MODERATOR



