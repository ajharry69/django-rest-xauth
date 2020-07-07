from django.contrib.auth import get_user_model
from rest_framework import generics

from xauth.permissions import IsOwnerOrSuperuserOrReadOnly
from xauth.serializers import profile_serializer_class
from xauth.utils import get_204_wrapped_response, get_wrapped_response
from xauth.utils.settings import USER_LOOKUP_FIELD


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = USER_LOOKUP_FIELD
    queryset = get_user_model().objects.all()
    serializer_class = profile_serializer_class
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, ]

    def get(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().get(request, *args, **kwargs))

    def put(self, request, *args, **kwargs):
        return get_wrapped_response(super().put(request, *args, **kwargs))

    def patch(self, request, *args, **kwargs):
        return get_wrapped_response(super().patch(request, *args, **kwargs))

    def delete(self, request, *args, **kwargs):
        return get_204_wrapped_response(super().delete(request, *args, **kwargs))
