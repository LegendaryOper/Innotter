
from django.conf import settings
from rest_framework import parsers, renderers, status, viewsets, mixins, permissions
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from .services import generate_access_token, generate_refresh_token, set_refresh_token, check_and_update_refresh_token
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from .permissions import IsUserOwner, IsAdmin, IsModerator, IsUserOwnerOrAdmin
from rest_framework import permissions


User = get_user_model()


class JSONWebTokenAuthViewSet(viewsets.ViewSet):
    throttle_classes = ()
    permission_classes = (permissions.AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = generate_access_token(user)
            refresh_token = generate_refresh_token()
            set_refresh_token(refresh_token=refresh_token, user=user)
            response = Response({'token': token, 'refresh_token': refresh_token})
            response.set_cookie(
                key=settings.CUSTOM_JWT['AUTH_COOKIE'],
                value=token,
                expires=settings.CUSTOM_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.CUSTOM_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.CUSTOM_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.CUSTOM_JWT['AUTH_COOKIE_SAMESITE']
            )
            response.set_cookie(
                key=settings.CUSTOM_JWT['AUTH_COOKIE_REFRESH'],
                value=refresh_token,
                expires=settings.CUSTOM_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.CUSTOM_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.CUSTOM_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.CUSTOM_JWT['AUTH_COOKIE_SAMESITE']
            )

            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('post',), detail=False)
    def refresh(self, request):
        refresh_token = request.COOKIES.get(settings.CUSTOM_JWT['AUTH_COOKIE_REFRESH'])
        if refresh_token:
            new_tokens = check_and_update_refresh_token(refresh_token)
            if new_tokens:
                response = Response(new_tokens)
                response.set_cookie(
                    key=settings.CUSTOM_JWT['AUTH_COOKIE'],
                    value=new_tokens[settings.CUSTOM_JWT['AUTH_COOKIE']],
                    expires=settings.CUSTOM_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.CUSTOM_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.CUSTOM_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.CUSTOM_JWT['AUTH_COOKIE_SAMESITE']
                )
                response.set_cookie(
                    key=settings.CUSTOM_JWT['AUTH_COOKIE_REFRESH'],
                    value=new_tokens[settings.CUSTOM_JWT['AUTH_COOKIE_REFRESH']],
                    expires=settings.CUSTOM_JWT['REFRESH_TOKEN_LIFETIME'],
                    secure=settings.CUSTOM_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.CUSTOM_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.CUSTOM_JWT['AUTH_COOKIE_SAMESITE']
                )
                return response
        return Response({'message': "Your token isn't valid"})


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for all User objects"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []
    permissions_dict = {
                        'partial_update': (permissions.IsAuthenticated, IsUserOwnerOrAdmin),
                        'update': (permissions.IsAuthenticated, IsUserOwnerOrAdmin),
                        'destroy': (permissions.IsAuthenticated, IsUserOwnerOrAdmin),
                        'create': (permissions.AllowAny,),
                        'list': (permissions.IsAuthenticated, IsAdmin,),
                        'retrieve': (permissions.IsAuthenticated,),
                        }

    # a method that set permissions depending on http request methods
    def get_permissions(self):
        self.permission_classes = self.permissions_dict.get(self.action)
        return super(self.__class__, self).get_permissions()







