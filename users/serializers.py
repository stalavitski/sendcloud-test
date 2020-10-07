from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['id', 'username', 'password']
        model = User

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create and save user object with encrypted password.

        :param validated_data: Dict of validated data in field:value format.
        :return: Saved User object with encrypted password.
        """
        password = validated_data.get('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
