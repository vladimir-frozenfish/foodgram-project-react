from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from recipes.models import User, Tag


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
                "email",
                "id",
                "username",
                "first_name",
                "last_name",
                "password",
                "is_subscribed"
            )
        model = User

    def get_is_subscribed(self, obj):
        """возвращает в поле is_subscribed True если текущий пользователь
        подписан на вызываемых в запросе GET"""
        request_user = self.context["request"].user
        if request_user.is_anonymous:
            return False
        following = [follower.following.username for follower in request_user.follower.all()]
        return obj.username in following

    def create(self, validated_data):
        """создание хэшируемого пароля"""
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag
