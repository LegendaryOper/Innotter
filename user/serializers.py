from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """ A user model serializer"""
    role = serializers.CharField(default='user')
    # is_blocked = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'title', 'image_s3_path', 'role', 'is_blocked')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            role='user',
            title=validated_data['title'],
            is_blocked=False,
            # image_s3_path=validated_data['image_s3_path']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if validated_data.get('role') == 'admin':
            instance.is_staff = True
            instance.is_superuser = True
        if validated_data['password']:
            instance.set_password(validated_data['password'])
            instance.save()
            validated_data.pop('password')
        return super().update(instance, validated_data)
