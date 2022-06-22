from rest_framework import serializers
from .models import Page


class PageSerializer(serializers.ModelSerializer):
    """ A user model serializer"""
    class Meta:
        model = Page
        # fields = ('username', 'password', 'email', 'title', 'image_s3_path', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Page(
            email=validated_data['email'],
            username=validated_data['username'],
            role=validated_data['role'],
            title=validated_data['title'],
            # image_s3_path=validated_data['image_s3_path']
        )
        user.save()
        return user