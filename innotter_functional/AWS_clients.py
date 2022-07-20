import boto3
from django.conf import settings
from botocore.exceptions import ClientError


class ClientMeta(type):

    @property
    def client(cls):
        if not getattr(cls, '_client', None):
            service_name = getattr(cls, '_service_name')
            client = boto3.client(service_name, # noqa
                                       aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                       aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                       region_name=settings.AWS_REGION_NAME)
            setattr(cls, '_client', client)
        return getattr(cls, '_client')


class S3Client(metaclass=ClientMeta):

    _service_name = 's3'

    @classmethod
    def create_presigned_url(cls, object_name, expiration=25200, bucket_name=settings.AWS_STORAGE_BUCKET_NAME, ):
        # Generate a presigned URL for the S3 object
        try:
            response = cls.client.generate_presigned_url('get_object',
                                                         Params={
                                                              'Bucket': bucket_name,
                                                              'Key': object_name},
                                                         ExpiresIn=expiration)
        except ClientError:
            return None
        # The response contains the presigned URL
        return response

    @classmethod
    def upload_file(cls, file, object_name=None):
        try:
            cls.client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, object_name)
        except ClientError:
            return None


class SESClient(metaclass=ClientMeta):

    _service_name = 'ses'

    @classmethod
    def send_email_about_post(cls, followers_list, page_name, post_url):
        cls.client.send_email(
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
            Source=settings.AWS_MAIL_SENDER
        )

