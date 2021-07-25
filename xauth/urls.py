from django.conf import settings
from django.urls import include, path
from django.utils.module_loading import import_string

from xauth.accounts.views import AccountViewSet

router = import_string(getattr(settings, "XAUTH_URL_ROUTER", "rest_framework.routers.SimpleRouter"))()
router.register("account", AccountViewSet, basename=AccountViewSet.url_name_basename)

urlpatterns = [path("", include(router.urls))]
