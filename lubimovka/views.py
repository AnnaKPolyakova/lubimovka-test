from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Organization
from .serializers import RegistrationSerializer, TokenSerializer, \
    OrganizationGetSerializer, OrganizationSerializer
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from .utils import get_tokens_for_user

User = get_user_model()


class RegistrationAPIView(APIView):
    """
    Разрешить всем пользователям (аутентифицированным и нет) доступ к данному эндпоинту.
    """
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        # user = request.data.get('user', {})

        # Паттерн создания сериализатора, валидации и сохранения - довольно
        # стандартный, и его можно часто увидеть в реальных проектах.
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TokenAPI(APIView):
    permission_classes = [AllowAny]
    serializer_class = TokenSerializer

    @action(detail=False, methods=["post"])
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token = get_tokens_for_user(user)
        return Response(token, status=status.HTTP_201_CREATED)


class OrganizationViewSet(ModelViewSet):
    serializer_class = OrganizationGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organization.objects.all()

    def get_queryset(self):
        user = self.request.user
        result = self.queryset.filter(access_to_edit=user)
        return result

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrganizationGetSerializer
        else:
            return OrganizationSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(access_to_edit=[user])
