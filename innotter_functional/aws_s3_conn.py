import boto3
from django.conf import settings
import urllib
from botocore.exceptions import ClientError

session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
s3 = session.resource('s3')


def create_presigned_url(object_name, expiration=25200, bucket_name=settings.AWS_STORAGE_BUCKET_NAME,):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name='us-east-1')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError:
        return None

    # The response contains the presigned URL
    return response


def upload_file_to_s3(file, key):
    s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=key, Body=file)


