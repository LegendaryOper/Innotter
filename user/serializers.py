from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """ A user model serializer"""
    role = serializers.CharField(default='user')
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'title', 'image_s3_path', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            role='user',
            title=validated_data['title'],
            # image_s3_path=validated_data['image_s3_path']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
