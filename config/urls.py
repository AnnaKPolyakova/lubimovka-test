from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from lubimovka.serializers import EmailAuthSerializer
from lubimovka.views import send_confirmation_code

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/auth/email/', send_confirmation_code),
    path(
        'v1/token/',
        TokenObtainPairView.as_view(serializer_class=EmailAuthSerializer),
        name='token_obtain_pair'
    ),
    path(
        'v1/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]

