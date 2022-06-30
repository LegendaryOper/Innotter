from django.utils import timezone
from django.db.models import F


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
    request_data._mutable = True
    request_data['page'] = page_id
    request_data._mutable = False


def add_like_to_post(post):
    post.likes = F('likes') + 1
    post.save()


