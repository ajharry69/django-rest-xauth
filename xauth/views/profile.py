from django.contrib.auth import get_user_model
from rest_framework import generics

from xauth.permissions import IsOwnerOrSuperuserOrReadOnly
from xauth.serializers import profile
from xauth.utils.settings import USER_LOOKUP_FIELD


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = USER_LOOKUP_FIELD
    queryset = get_user_model().objects.all()
    serializer_class = profile.request_serializer_class
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, ]