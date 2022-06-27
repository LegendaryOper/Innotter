import datetime
from .services import change_followers_data_from_str_to_list
from rest_framework import serializers
from .models import Page


class PageModelUserSerializer(serializers.ModelSerializer):
    """ A page model serializer, works with default user(owner)"""
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(),)
    unblock_date = serializers.DateTimeField(default=None)

    class Meta:
        model = Page
        fields = ('name', 'description', 'image', 'uuid', 'tags', 'is_private', 'owner', 'followers')


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
        validators = []

    def validate(self, data):
        if data['followers']:
            data = change_followers_data_from_str_to_list(data)
            return data
        raise serializers.ValidationError('Your data is not valid')

    def update(self, instance, validated_data):
        if validated_data['followers']:
            instance.followers.add(*validated_data['followers'])
            if instance.follow_requests:
                instance.follow_requests.remove(*validated_data['follow_requests'])
            instance.save()
            return instance

