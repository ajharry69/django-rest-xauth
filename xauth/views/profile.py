from django.contrib.auth import get_user_model
from rest_framework import generics

from xauth.permissions import IsOwnerOrSuperuserOrReadOnly
from xauth.serializers import profile
from xauth.utils.settings import USER_LOOKUP_FIELD


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = USER_LOOKUP_FIELD
    queryset = get_user_model().objects.all()
    # on provides (`dict`) data usable in `serializer_class_response`
    serializer_class = profile.request_serializer_class
    # does normal operations of `serializer_class` would it not have been used to provide data
    serializer_class_response = profile.response_serializer_class
    permission_classes = [IsOwnerOrSuperuserOrReadOnly, ]

    def get_serializer(self, *args, **kwargs):
        request_serializer = self.serializer_class(
            data=kwargs.get('data'),
            context=self.get_serializer_context(),
        )
        if request_serializer.is_valid(raise_exception=False):
            kwargs['data'] = request_serializer.data
        return super().get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        return self.serializer_class_response or super().get_serializer_class()
