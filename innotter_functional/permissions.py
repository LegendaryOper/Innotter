from user.permissions import IsAdmin, IsModerator
from rest_framework import permissions
from user.models import User
from .models import Post
from django.contrib.auth.models import AnonymousUser
from .services import is_page_block


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
            return is_page_block(obj.unblock_date) or IsAdminOrModerator.has_permission(self, request, view)
        return True


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


class IsPagePostParent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return Post.objects.get(pk=view.kwargs.get('pk')).page == obj



