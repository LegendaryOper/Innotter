from innotter.celery import app
from .AWS_clients import SESClient


@app.task()
def celery_send_mail_about_post(followers_list, page_name, post_url):
    SESClient.send_email_about_post(followers_list, page_name, post_url)
