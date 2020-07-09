from django.contrib.auth import login
from rest_framework import views, status
from rest_framework.response import Response

from xauth import permissions
from xauth.serializers import AuthSerializer


class SignInView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = AuthSerializer

    def post(self, request, format=None):
        # authentication logic is by default handled by the auth-backend
        user = request.user
        login(request, user)
        user.update_or_create_access_log(force_create=True)
        serializer = self.serializer_class(user, context={'request': request}, )
        return Response(serializer.data, status=status.HTTP_200_OK)
