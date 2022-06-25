import datetime

from rest_framework import serializers
from .models import Page


class PageModelUserSerializer(serializers.ModelSerializer):
    """ A page model serializer, works with default user(owner)"""
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(),)
    unblock_date = serializers.DateTimeField(default=None)

    class Meta:
        model = Page
        fields = ('name', 'description', 'image', 'uuid', 'tags', 'is_private', 'owner')


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
            print(validated_data['unblock_date'])
            instance.save()
            validated_data.pop('unblock_date')
        return super().update(instance, validated_data)
