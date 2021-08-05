from django.conf import settings
from django.urls import include, path
from django.utils.module_loading import import_string
from xently.core.loading import get_classes

from xauth.internal_settings import AUTH_APP_LABEL

(AccountViewSet, SecurityQuestionViewSet) = get_classes(
    f"{AUTH_APP_LABEL}.views", ["AccountViewSet", "SecurityQuestionViewSet"]
)

router = import_string(getattr(settings, "XAUTH_URL_ROUTER", "rest_framework.routers.SimpleRouter"))()
router.register(AUTH_APP_LABEL, AccountViewSet)
router.register("security-questions", SecurityQuestionViewSet)

urlpatterns = [path("", include(router.urls))]
