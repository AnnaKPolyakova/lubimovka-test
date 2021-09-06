from django.shortcuts import get_object_or_404
from rest_framework import permissions

from lubimovka.models import Organization


class IsCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        organization = get_object_or_404(
            Organization,
            id=view.kwargs["organization_id"],
        )
        return organization.creator == request.user


class IsCreatorOrUserAddToAccessToEdit(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if obj.creator == request.user:
                return True
            if request.user in obj.access_to_edit.all():
                return True
        return False
