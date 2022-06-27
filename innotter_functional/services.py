from django.utils import timezone


def check_page_block(unblock_date):
    if timezone.now() < unblock_date:
        return False
    return True


def add_follow_requests_to_request_data(request_data, follow_requests):
    follow_requests = list(follow_requests.values_list('pk', flat=True))
    request_data._mutable = True
    request_data.update({'follow_requests': follow_requests})
    request_data._mutable = False
    return request_data


def change_followers_data_from_str_to_list(request_data):
    request_data._mutable = True
    if request_data['followers']:
        followers = list(map(int, request_data['followers'].split(',')))
        request_data['followers'] = followers
    request_data._mutable = False
    return request_data


def check_user_in_page_followers(user, page):
    if page.followers.filter(id=user.pk).exists():
        return True
    return False


def check_user_in_page_follow_requests(user, page):
    if page.follow_requests.filter(id=user.pk).exists():
        return True
    return False


def add_user_to_page_follow_requests(user, page):
    page.follow_requests.add(user)


def add_user_to_page_followers(user, page):
    page.followers.add(user)


