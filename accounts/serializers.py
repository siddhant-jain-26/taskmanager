# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterAPIViewSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')

    def validate_email(self, value):
        """
        Check that the email is valid.
        """
        if not value:
            raise serializers.ValidationError('This field is required.')
        if User.objects.filter(email=value):
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate(self, data):
        """
        Check that the passwords match.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        return data

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        validated_data.pop('password2')

        user = User(email=email)
        user.set_password(password)
        user.save()
        return user


class ProfileAPIViewSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)

        password = validated_data.get('password', '')
        if password:
            instance.set_password(password)

        instance.save()
        return instance
