import datetime
from rest_framework import serializers
from .models import Page, Post, Tag
from user.models import User


class PageModelUserSerializer(serializers.ModelSerializer):
    """ A page model serializer, works with default user(owner)"""
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(),)
    unblock_date = serializers.DateTimeField(default=None)

    class Meta:
        model = Page
        fields = ('name', 'description', 'image', 'uuid', 'tags', 'is_private', 'owner', 'followers', 'unblock_date')


class PageModelAdminOrModerSerializer(serializers.ModelSerializer):
    """ A page model serializer, works with default user(owner)"""
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(), )
    unblock_date = serializers.DateTimeField(default=None)

    class Meta:
        model = Page
        fields = '__all__'

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
        fields = "__all__"
        extra_kwargs = {
            'likes': {'read_only': True},
        }


class TagModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

