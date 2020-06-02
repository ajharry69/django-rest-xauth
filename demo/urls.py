from django.urls import include, path

from demo import views

urlpatterns = [
    path('', views.api_root, name='index'),
    path('xauth/', include('xauth.urls', namespace='xauth')),
    path('admin-auth/', include('rest_framework.urls', namespace='rest_framework')),  # should be at the end!
]
