from rest_framework.routers import DefaultRouter

__all__ = ["ViewSetBasenameMixin"]


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
