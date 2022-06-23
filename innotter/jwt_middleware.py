import jwt
import traceback


from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status, renderers

User = get_user_model()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._force_auth_user = self.get_jwt_user(request)

    def process_response(self, request, response):
        if not isinstance(self.get_jwt_user(request), AnonymousUser):
            if self.get_jwt_user(request).is_blocked:
                response = Response(
                    data="You're blocked",
                    status=status.HTTP_403_FORBIDDEN
                )
                response.accepted_renderer = renderers.JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                response.render()
                return response
        return response


    @staticmethod
    def get_jwt_user(request):
        user_jwt = get_user(request)
        if user_jwt.is_authenticated:
            return user_jwt
        token = request.COOKIES.get(settings.CUSTOM_JWT['AUTH_COOKIE'], None)
        user_jwt = AnonymousUser()
        if token:
            try:
                user_jwt = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                )
                user_jwt = User.objects.get(
                    username=user_jwt['username']
                )

            except (ObjectDoesNotExist, jwt.exceptions.ExpiredSignatureError):
                traceback.print_exc()
        return user_jwt