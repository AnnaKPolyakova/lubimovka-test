from django.urls import include, path
from rest_framework.routers import DefaultRouter

from lubimovka.views import (AccessToEditView, EmployeeViewSet,
                             OrganizationViewSet, RegistrationAPIView)

router = DefaultRouter()

router.register(
    prefix="organizations",
    viewset=OrganizationViewSet,
    basename="organizations",
)

router.register(
    prefix="employees",
    viewset=EmployeeViewSet,
    basename="employees",
)

extra_patterns = [
    path("auth/users/", RegistrationAPIView.as_view()),
    path("", include(router.urls)),
    path(
        "organizations/<int:organization_id>/access_to_edit/",
        AccessToEditView.as_view(),
    ),
]

urlpatterns = [
    path("v1/", include(extra_patterns)),
]
