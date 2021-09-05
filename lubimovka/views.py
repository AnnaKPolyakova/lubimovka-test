import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Organization, Employee, OrganizationUserRelation
from .serializers import RegistrationSerializer, \
    OrganizationGetSerializer, OrganizationSerializer, AccessToEditSerializer, \
    ListUsersAccessToEditSerializer
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import JsonResponse

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


class OrganizationViewSet(ModelViewSet):
    serializer_class = OrganizationGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Organization.objects.all()

    def get_queryset(self):
        user = self.request.user
        result = self.queryset.filter(Q(access_to_edit=user) | Q(creator=user))
        return result

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrganizationGetSerializer
        else:
            return OrganizationSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(creator=user)

    @action(
        detail=False,
        methods=["post"],
        name="add_access_to_edit",
        permission_classes=[IsAuthenticated],
    )
    def add_access_to_edit(self, request):
        serializer = AccessToEditSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            organization = get_object_or_404(
                Organization, id=request.data["organization"],
                creator=request.user
            )
            users = get_list_or_404(
                User, email__in=request.data["user"]
            )
            for user in users:
                organization.access_to_edit.add(user)
                organization.save()
            return JsonResponse({"success": "Ok"},
                                status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["delete"],
        name="del_access_to_edit",
        permission_classes=[IsAuthenticated],
    )
    def del_access_to_edit(self, request):
        serializer = AccessToEditSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            organization = get_object_or_404(
                Organization,
                id=request.data["organization"],
                creator=request.user
            )
            users = get_list_or_404(
                User, email__in=request.data["user"]
            )
            for user in users:
                access_to_edit = get_object_or_404(
                    OrganizationUserRelation,
                    organization=organization,
                    user=user
                )
                access_to_edit.delete()
            return JsonResponse({"success": "Ok"},
                                status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        name="get_list_users_access_to_edit",
        permission_classes=[IsAuthenticated],
    )
    def get_list_users_access_to_edit(self, request):
        serializer = ListUsersAccessToEditSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            organization = get_object_or_404(
                Organization, id=request.data["organization"]
            )
            return JsonResponse({"success": "Ok"},
                                status=status.HTTP_200_OK)