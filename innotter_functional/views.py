from django.conf import settings
from .models import Page, Tag, Post
from user.models import User
from rest_framework import parsers, renderers, status, viewsets, mixins, permissions, serializers
from .serializers import PageModelUserSerializer, PageModelAdminOrModerSerializer, PageModelFollowRequestsSerializer,\
                         PostModelSerializer
from rest_framework import permissions
from .permissions import IsPageOwner, IsAdminOrModerator, IsPageOwnerOrModeratorOrAdmin, PageIsntBlocked, \
                         PageIsntPrivate
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import add_follow_requests_to_request_data, check_user_in_page_follow_requests, \
                      check_user_in_page_followers, add_user_to_page_follow_requests, add_user_to_page_followers,\
                      add_parent_page_id_to_request_data
from rest_framework_extensions.mixins import NestedViewSetMixin


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
                        'follow_requests': (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin),
                        'follow': (permissions.IsAuthenticated, PageIsntPrivate, PageIsntBlocked,)
                        }

    # a method that set permissions depending on http request methods
    def get_permissions(self):
        self.permission_classes = self.permissions_dict.get(self.action)
        return super(self.__class__, self).get_permissions()

    def check_permissions(self, request):
        obj = Page.objects.get(id=self.kwargs.get('pk'))
        self.check_object_permissions(request, obj)
        return super().check_permissions(request)

    def get_serializer_class(self):
        if self.request.user.role in (User.Roles.ADMIN, User.Roles.MODERATOR):
            self.serializer_class = PageModelAdminOrModerSerializer
        else:
            self.serializer_class = PageModelUserSerializer
        return super(self.__class__, self).get_serializer_class()

    @action(detail=True, methods=('get', 'post'))
    def follow_requests(self, request, pk=None):
        page = self.get_object()
        self.check_permissions(request)
        self.check_object_permissions(request, self.get_object())
        if page.is_private:
            if request.method == "GET":
                serializer = PageModelFollowRequestsSerializer(page)
                return Response({'follow_requests': serializer.data['follow_requests'],
                                 'followers': serializer.data['followers']},  status.HTTP_200_OK)
            elif request.method == 'POST':
                add_follow_requests_to_request_data(request.data, page.follow_requests)
                serializer = PageModelFollowRequestsSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.update(page, request.data)
                    return Response({'message': 'Ok'}, status.HTTP_200_OK)
                return Response({'message': 'Your data is not valid'}, status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Your page isn't private"}, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=('post',))
    def follow(self, request, pk=None):
        page = self.get_object()
        self.check_permissions(request)
        self.check_object_permissions(request, self.get_object())
        if check_user_in_page_follow_requests(request.user, page) or \
                check_user_in_page_followers(request.user, page):
            return Response({"message": "You are already sent follow request"}, status.HTTP_400_BAD_REQUEST)
        if page.is_private:
            add_user_to_page_follow_requests(request.user, page)
        else:
            add_user_to_page_followers(request.user, page)
        return Response({'message': 'Ok'},  status.HTTP_200_OK)


class PostViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = PostModelSerializer
    permission_classes = []
    queryset = Post.objects.all()
    permissions_dict = {
        'partial_update': (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin,
                           PageIsntBlocked,),
        'update': (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin,
                   PageIsntBlocked,),
        'destroy': (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin),
        'create': (permissions.IsAuthenticated, IsPageOwner),
        'list': (permissions.IsAuthenticated, PageIsntPrivate, PageIsntBlocked,),
        'retrieve': (permissions.IsAuthenticated, PageIsntPrivate, PageIsntBlocked),
    }

    def create(self, request, *args, **kwargs):
        add_parent_page_id_to_request_data(request.data, self.kwargs.get('parent_lookup_page_id'))
        return super().create(request, *args, **kwargs)

    def get_permissions(self):
        self.permission_classes = self.permissions_dict.get(self.action)
        return super().get_permissions()

    def check_permissions(self, request):
        obj = Page.objects.get(id=self.kwargs.get('parent_lookup_page_id'))
        self.check_object_permissions(request, obj)
        return super().check_permissions(request)

    def get_object(self):
        return Post.objects.get(pk=self.kwargs['pk'])




