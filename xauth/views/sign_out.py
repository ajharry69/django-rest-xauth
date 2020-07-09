from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from rest_framework import views, status, permissions
from rest_framework.response import Response


class SignOutView(views.APIView):
    permission_classes = [permissions.AllowAny, ]

    @staticmethod
    def post(request, format=None):
        user = request.user
        if user and not isinstance(user, AnonymousUser):
            user.update_or_create_access_log()
        logout(request)
        return Response({'success': 'signed out'}, status=status.HTTP_200_OK)
