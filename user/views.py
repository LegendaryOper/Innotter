
from django.conf import settings
from rest_framework import parsers, renderers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from .services import generate_access_token, generate_refresh_token, set_refresh_token, check_and_update_refresh_token


class JSONWebTokenAuthViewSet(ViewSet):
    throttle_classes = ()
    permission_classes = ()
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
        if refresh_token is not None:
            new_tokens = check_and_update_refresh_token(refresh_token)
            if new_tokens is not None:
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




