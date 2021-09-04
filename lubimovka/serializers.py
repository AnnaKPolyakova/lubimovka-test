from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from lubimovka.models import UnconfirmedUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'role', 'email')
        model = User


class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=100)

    def validate(self, data):
        user = get_object_or_404(UnconfirmedUser, email=data['email'])
        confirmation_code = data['confirmation_code']
        if confirmation_code == user.confirmation_code:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={'email': data['email']}
            )
            token = RefreshToken.for_user(user)
            return {
                'access': str(token.access_token),
                'refresh': str(token)
            }
