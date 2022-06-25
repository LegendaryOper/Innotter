from django.utils import timezone


def check_page_block(unblock_date):
    if timezone.now() < unblock_date:
        return False
    return True
