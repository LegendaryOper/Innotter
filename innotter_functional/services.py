from django.utils import timezone
from django.db.models import F, Manager
from django.http import QueryDict
from .models import Page
from user.services import get_file_extension
from .aws_s3_conn import upload_file_to_s3



def is_page_block(unblock_date):
    if timezone.now() < unblock_date:
        return False
    return True


def add_follow_requests_to_request_data(request_data, follow_requests):
    follow_requests = list(follow_requests.values_list('pk', flat=True))
    request_data.update({'follow_requests': follow_requests})
    return request_data


def is_user_in_page_followers(user, page):
    return page.followers.filter(id=user.pk).exists()


def is_user_in_page_follow_requests(user, page):
    return page.follow_requests.filter(id=user.pk).exists()


def add_user_to_page_follow_requests(user, page):
    page.follow_requests.add(user)


def add_user_to_page_followers(user, page):
    page.followers.add(user)


def add_parent_page_id_to_request_data(request_data, page_id):
    if isinstance(request_data, QueryDict):
        request_data._mutable = True
        request_data['page'] = page_id
        request_data._mutable = False
        return
    request_data['page'] = page_id


def add_like_to_post(post):
    post.likes = F('likes') + 1
    post.save()


def get_edited_query_params(query_params):
    query_params_dict = {'name': query_params.get('name'),
                         'tag': query_params.get('tag'),
                         'uuid': query_params.get('uuid')}

    for query_param_name, query_param in query_params_dict.items():
        if query_param is not None:
            continue
        query_params_dict[query_param_name] = ''
    return query_params_dict


def prepare_mail_data(post_data):
    followers_list = [element['email'] for element in list(Page.objects.prefetch_related('followers')
                                                           .get(pk=post_data.get('page')).followers.values('email'))]
    page_name = Page.objects.get(pk=post_data.get('page')).name
    post_url = f'/innotter/pages/{post_data.get("page")}/posts/{post_data.get("id")}'
    mail_data = (followers_list, page_name, post_url)
    return mail_data


def add_page_image_to_request_data(url, request_data):
    if isinstance(request_data, QueryDict):
        request_data._mutable = True
        request_data['image'] = url
        request_data._mutable = False
        return
    request_data['image'] = url


def handle_page_image(image, request):
    if image:
        extension = get_file_extension(image.name)
        file_key = request.data.get('name') + extension
        upload_file_to_s3(image, file_key)
        add_page_image_to_request_data(file_key, request.data)
        return
    add_page_image_to_request_data('', request.data)
    


