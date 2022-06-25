from django.conf import settings
from .models import Page, Tag, Post
from user.models import User
from rest_framework import parsers, renderers, status, viewsets, mixins, permissions
from .serializers import PageModelUserSerializer, PageModelAdminOrModerSerializer
from rest_framework import permissions
from .permissions import IsPageOwner, IsAdminOrModerator, IsPageOwnerOrModeratorOrAdmin, PageIsntBlocked, \
    PageIsntPrivate


class PageViewSet(viewsets.ModelViewSet):
    """ViewSet for all User objects"""
    queryset = Page.objects.all()
    serializer_class = PageModelUserSerializer
    permission_classes = []
    permissions_dict = {
                        'partial_update': (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin,
                                           PageIsntBlocked, PageIsntPrivate),
                        'update': (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin,
                                   PageIsntBlocked, PageIsntPrivate),
                        'destroy': (permissions.IsAuthenticated, IsPageOwner),
                        'create': (permissions.IsAuthenticated,),
                        'list': (permissions.IsAuthenticated, IsAdminOrModerator,),
                        'retrieve': (permissions.IsAuthenticated, PageIsntPrivate, PageIsntBlocked),
                        }

    # a method that set permissions depending on http request methods
    def get_permissions(self):
        self.permission_classes = self.permissions_dict.get(self.action)
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.request.user.role in (User.Roles.ADMIN, User.Roles.MODERATOR):
            self.serializer_class = PageModelAdminOrModerSerializer
        else:
            self.serializer_class = PageModelUserSerializer
        return super(self.__class__, self).get_serializer_class()
