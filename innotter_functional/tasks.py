from innotter.celery import app
from .aws_ses_conn import ses_send_email_about_post


@app.task()
def celery_send_mail_about_post(followers_list, page_name, post_url):
    ses_send_email_about_post(followers_list, page_name, post_url)
