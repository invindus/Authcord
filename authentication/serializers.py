from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework import serializers

from api.models import Author
from django.contrib.auth import authenticate


class CreateAuthorUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, )
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        author_user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )

        Author.objects.create(
            user=author_user,
        )

        return author_user

    @staticmethod
    def validate_username(value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid Credentials")

        author = user.author

        if not author.is_approved:
            raise serializers.ValidationError("Author not approved by admin")

        attrs['user'] = user
        return attrs
