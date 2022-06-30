from django.conf import settings

import user.serializers
from .models import Page, Tag, Post
from user.models import User
from rest_framework import parsers, renderers, status, viewsets, mixins, permissions, serializers, views
from .serializers import PageModelUserSerializer, PageModelAdminOrModerSerializer, PageModelFollowRequestsSerializer,\
                         PostModelSerializer, TagModelSerializer
from rest_framework import permissions
from .permissions import IsPageOwner, IsAdminOrModerator, IsPageOwnerOrModeratorOrAdmin, PageIsntBlocked, \
                         PageIsntPrivate
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import add_follow_requests_to_request_data, is_user_in_page_follow_requests, \
                      is_user_in_page_followers, add_user_to_page_follow_requests, add_user_to_page_followers,\
                      add_parent_page_id_to_request_data, add_like_to_post, get_edited_query_params
from rest_framework_extensions.mixins import NestedViewSetMixin
from django.utils import timezone
from user.serializers import UserSerializer
from django.db.models import Q


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
                        'list': (permissions.IsAuthenticated,),
                        'retrieve': (permissions.IsAuthenticated, PageIsntPrivate, PageIsntBlocked),
                        'follow_requests': (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin),
                        'follow': (permissions.IsAuthenticated, PageIsntPrivate, PageIsntBlocked,)
                        }

    # a method that set permissions depending on http request methods
    def get_permissions(self):
        self.permission_classes = self.permissions_dict.get(self.action)
        return super(self.__class__, self).get_permissions()

    def list(self, request, *args, **kwargs):
        self.queryset = Page.objects.filter(is_private=False, unblock_date__lt=timezone.now())
        return super().list(request, *args, **kwargs)

    def check_permissions(self, request):
        try:
            obj = Page.objects.get(id=self.kwargs.get('pk'))
        except Page.DoesNotExist:  # exception when 'get' request on /pages/
            pass
        else:
            self.check_object_permissions(request, obj)
        finally:
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
        if (is_user_in_page_follow_requests(request.user, page)
            or is_user_in_page_followers(request.user, page)):
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
        'like': (permissions.IsAuthenticated, PageIsntPrivate, PageIsntBlocked),
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

    @action(detail=True, methods=('post',))
    def like(self, request, pk=None, parent_lookup_page_id=None):
        post = self.get_object()
        self.check_permissions(request)
        add_like_to_post(post)
        return Response({'message': 'Ok'}, status.HTTP_200_OK)


class TagViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
                 mixins.ListModelMixin):

    queryset = Tag.objects.all()
    serializer_class = TagModelSerializer
    permission_classes = []
    permissions_dict = {
        'destroy': (permissions.IsAuthenticated, IsAdminOrModerator),
        'create': (permissions.IsAuthenticated, IsAdminOrModerator),
        'list': (permissions.IsAuthenticated,),
        'retrieve': (permissions.IsAuthenticated,),
    }

    def get_permissions(self):
        self.permission_classes = self.permissions_dict.get(self.action)
        return super().get_permissions()


class SearchUserViewSet(viewsets.ViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.none()
        username = self.request.query_params.get('username')
        if username:
            queryset = User.objects.filter(username__icontains=username)
        return queryset

    def list(self, request):
        self.check_permissions(request)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class SearchPageViewSet(SearchUserViewSet):
    serializer_class = PageModelUserSerializer

    def get_queryset(self):
        edited_query_params = get_edited_query_params(self.request.query_params)
        queryset = Page.objects.prefetch_related('tags')\
                       .filter(Q(name__icontains=edited_query_params.get('name')),
                               Q(tags__name__icontains=edited_query_params.get('tag')),
                               Q(uuid__icontains=edited_query_params.get('uuid'))).distinct()
        return queryset








