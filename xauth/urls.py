from django.urls import include, path
from rest_framework.routers import SimpleRouter

from xauth.accounts.views import AccountViewSet

router = SimpleRouter()
router.register("account", AccountViewSet, basename=AccountViewSet.url_name_basename)

urlpatterns = [path("", include(router.urls))]
