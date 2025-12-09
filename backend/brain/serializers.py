from rest_framework import serializers
from .models import AppUser

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = AppUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
