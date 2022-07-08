import boto3
from django.conf import settings
import urllib

session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
s3 = session.resource('s3')


def upload_file_to_s3(img, key):
    s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=key, Body=img)
    url = f'''https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{urllib.parse.quote(key, safe="~()*!.'")}'''
    return url


def delete_file_on_s3(img_link):
    # key =
    s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)