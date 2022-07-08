import datetime
from rest_framework import serializers
from .models import Page, Post, Tag
from user.models import User
from .aws_s3_conn import create_presigned_url
from botocore.exceptions import ParamValidationError


class PageModelUserSerializer(serializers.ModelSerializer):
    """ A page model serializer, works with default user(owner)"""
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(),)
    unblock_date = serializers.DateTimeField(default=None)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ('id', 'name', 'description', 'image', 'uuid', 'tags',
                  'is_private', 'owner', 'followers', 'unblock_date', 'image_url')
        extra_kwargs = {
            'unblock_date': {'read_only': True},
            'owner': {'read_only': True},
            'followers': {'read_only': True},
        }

    def get_image_url(self, obj):
        try:
            url = create_presigned_url(object_name=obj.image)
        except ParamValidationError:
            url = ''
        return url


class PageModelAdminOrModerSerializer(serializers.ModelSerializer):
    """ A page model serializer, works with default user(owner)"""
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(), )
    unblock_date = serializers.DateTimeField(default=None)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ('id', 'name', 'description', 'image', 'uuid', 'tags',
                  'is_private', 'owner', 'followers', 'unblock_date', 'image_url')

    def get_image_url(self, obj):
        try:
            url = create_presigned_url(object_name=obj.image_s3_path)
        except ParamValidationError:
            url = ''
        return url

    def update(self, instance, validated_data):
        if validated_data['unblock_date']:
            instance.unblock_date = validated_data['unblock_date']
            instance.save()
            validated_data.pop('unblock_date')
        return super().update(instance, validated_data)


class PageModelFollowRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('follow_requests', 'followers')

    def update(self, instance, validated_data):
        if validated_data['followers_accept_ids']:
            instance.followers.add(*validated_data['followers_accept_ids'])
            if instance.follow_requests:
                instance.follow_requests.remove(*validated_data['follow_requests'])
            instance.save()
            return instance


class PostModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'page', 'content', 'reply_to', 'created_at', 'updated_at', 'likes')
        extra_kwargs = {
            'likes': {'read_only': True},
        }


class TagModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


