import boto3
from decouple import config
from django.conf import settings


client = boto3.client(
    'ses',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)


def ses_send_email_about_post(followers_list, page_name, post_url):
    client.send_email(
        Destination={
            "ToAddresses": followers_list
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": f"Hi! New post on following page:{page_name}\n"
                            f"{post_url}",
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "New Post!",
            },
        },
        Source=config('AWS_MAIL_SENDER')
    )
