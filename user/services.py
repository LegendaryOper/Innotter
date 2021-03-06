from .models import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils import timezone
import jwt
import datetime
from innotter_functional.models import Page
from innotter_functional.AWS_clients import S3Client
from django.contrib.auth.models import AnonymousUser
from django.http import QueryDict
from .utils import get_file_extension


def generate_access_token(user):
    token = jwt.encode({
        'username': user.username,
        'iat': datetime.datetime.utcnow(),
        'nbf': datetime.datetime.utcnow() + datetime.timedelta(minutes=-5),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    }, settings.SECRET_KEY)
    return token


def generate_refresh_token():
    refresh_token = jwt.encode({
        'iat': datetime.datetime.utcnow(),
        'nbf': datetime.datetime.utcnow() + datetime.timedelta(minutes=-5),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    }, settings.SECRET_KEY)
    return refresh_token


def get_refresh_token_obj(refresh_token):
    try:
        old_token = RefreshToken.objects.get(refresh_token=refresh_token)
    except ObjectDoesNotExist:
        return None
    return old_token


def set_refresh_token(refresh_token, user):
    refresh_token = RefreshToken(user=user, refresh_token=refresh_token,
                                 exp_time=settings.CUSTOM_JWT['REFRESH_TOKEN_LIFETIME_MODEL'])
    refresh_token.save()


def check_and_update_refresh_token(refresh_token):
    old_token = get_refresh_token_obj(refresh_token)
    if old_token:
        if timezone.now() - datetime.timedelta(days=old_token.exp_time) > old_token.created_at:
            return None
        new_access_token = generate_access_token(old_token.user)
        new_refresh_token = generate_refresh_token()
        set_refresh_token(new_refresh_token, old_token.user)
        old_token.delete()
        return {settings.CUSTOM_JWT['AUTH_COOKIE']: new_access_token,
                settings.CUSTOM_JWT['AUTH_COOKIE_REFRESH']: new_refresh_token}


def block_all_users_pages(user):
    try:
        unblock_date = timezone.make_aware(timezone.datetime.max, timezone.get_default_timezone())
        Page.objects.filter(owner=user).update(unblock_date=unblock_date)
    except ObjectDoesNotExist:
        pass


def unblock_all_users_pages(user):
    try:
        unblock_date = timezone.now()
        Page.objects.filter(owner=user).update(unblock_date=unblock_date)
    except ObjectDoesNotExist:
        pass


def add_image_s3_path_to_request_data(url, request_data):
    if isinstance(request_data, QueryDict):
        request_data._mutable = True
        request_data['image_s3_path'] = url
        request_data._mutable = False
        return
    request_data['image_s3_path'] = url


def handle_image(image, request):
    if image:
        extension = get_file_extension(image.name)
        if isinstance(request.user, AnonymousUser):
            file_key = request.data.get('email') + extension
        else:
            file_key = request.user.email + extension
        S3Client.upload_file(image, file_key)
        add_image_s3_path_to_request_data(file_key, request.data)
        return
    add_image_s3_path_to_request_data('', request.data)


