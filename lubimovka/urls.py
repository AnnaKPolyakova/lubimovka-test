from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lubimovka.views import RegistrationAPIView, OrganizationViewSet

router = DefaultRouter()

router.register(
    prefix="organizations",
    viewset=OrganizationViewSet,
    basename="organizations",
)

extra_patterns = [
    path('auth/users/', RegistrationAPIView.as_view()),
    path("", include(router.urls)),
]

urlpatterns = [
    path("v1/", include(extra_patterns)),
]