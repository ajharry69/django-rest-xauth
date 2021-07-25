from django.urls import path, include

urlpatterns = [
    path("admin/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include("xauth.urls")),
]
