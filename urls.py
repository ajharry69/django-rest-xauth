from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api-admin/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include("xauth.urls")),
    path("admin/", admin.site.urls),
]
