from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Employee, Organization, OrganizationUserRelation
from .permission import IsCreator, IsCreatorOrUserAddToAccessToEdit
from .serializers import (AccessToEditSerializer, EmployeesSerializer,
                          OrganizationGetSerializer, OrganizationSerializer,
                          RegistrationSerializer)

User = get_user_model()


class RegistrationAPIView(APIView):

    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrganizationViewSet(ModelViewSet):
    serializer_class = OrganizationGetSerializer
    permission_classes = [IsCreatorOrUserAddToAccessToEdit]
    queryset = Organization.objects.all()

    def get_queryset(self):
        user = self.request.user
        result = self.queryset.filter(
            Q(access_to_edit=user) | Q(creator=user)
        ).distinct()
        return result

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrganizationGetSerializer
        else:
            return OrganizationSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(creator=user)


class EmployeeViewSet(ModelViewSet):
    serializer_class = EmployeesSerializer
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.all()


class AccessToEditView(APIView):
    permission_classes = [IsAuthenticated, IsCreator]
    serializer_class = AccessToEditSerializer

    def get(self, request, organization_id):
        organization = get_object_or_404(
            Organization,
            id=organization_id,
        )
        return JsonResponse(
            [user.email for user in organization.access_to_edit.all()],
            safe=False,
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Укажите email пользователей в формате списка",
                )
            },
        )
    )
    def post(self, request, organization_id):
        serializer = AccessToEditSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            organization = get_object_or_404(
                Organization,
                id=organization_id,
            )
            users = get_list_or_404(User, email__in=request.data["user"])
            for user in users:
                organization.access_to_edit.add(user)
                organization.save()
            return JsonResponse(
                organization.as_json(),
                safe=False,
                status=status.HTTP_200_OK,
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Укажите email пользователей в формате списка",
                )
            },
        )
    )
    def delete(self, request, organization_id):
        serializer = AccessToEditSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            organization = get_object_or_404(
                Organization,
                id=organization_id,
            )
            users = get_list_or_404(User, email__in=request.data["user"])
            for user in users:
                access_to_edit = get_object_or_404(
                    OrganizationUserRelation,
                    organization=organization,
                    user=user,
                )
                access_to_edit.delete()
            return JsonResponse(
                organization.as_json(),
                safe=False,
                status=status.HTTP_200_OK,
            )
