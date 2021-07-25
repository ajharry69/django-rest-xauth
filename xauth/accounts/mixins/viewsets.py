from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

__all__ = ["ActivateAccountViewSetMixin", "ViewSetBasenameMixin"]


class ViewSetBasenameMixin:
    # See https://www.django-rest-framework.org/api-guide/routers/#usage
    url_name_basename = None

    def __init__(self, *args, **kwargs):
        # This can ease calling `view.reverse_action(...)`; where view is an instance of `ViewSet` created
        # using constructor e.g. `ViewSet(...)`
        kwargs.setdefault("basename", self.__class__._basename())
        super().__init__(*args, **kwargs)

    @classmethod
    def _basename(cls):
        return cls.url_name_basename or DefaultRouter().get_default_basename(cls)


class ActivateAccountViewSetMixin:
    @action(methods=["POST"], detail=True, url_path="activate-account")
    def activate_account(self, request, *args, **kwargs):
        return Response()
