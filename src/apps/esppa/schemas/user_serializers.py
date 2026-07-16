"""
User serializers — single responsibility: User and UserProfile serialization.
"""

from rest_framework import serializers
from django.contrib.auth.models import User

from apps.esppa.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'department', 'role',
                  'phone', 'profile_picture', 'created_at']
        read_only_fields = ['id', 'created_at']
