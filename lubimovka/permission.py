from rest_framework import permissions
from django.shortcuts import get_object_or_404
from lubimovka.models import Organization


class IsCreator(permissions.BasePermission):
    def has_permission(self, request, view):
        organization = get_object_or_404(
            Organization,
            id=view.kwargs['organization_id'],
        )
        return organization.creator == request.user
