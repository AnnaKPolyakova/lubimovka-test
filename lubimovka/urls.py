from django.contrib import admin
from django.urls import path, include

from lubimovka.views import RegistrationAPIView

extra_patterns = [
    path('', admin.site.urls),

]

urlpatterns = [
    path('auth/users/', RegistrationAPIView.as_view()),
]
