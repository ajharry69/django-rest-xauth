from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        data={
            "security-questions": reverse("xauth:securityquestion-list", request=request, format=format),
            "signout": reverse("xauth:signout", request=request, format=format),
            "signin": reverse("xauth:signin", request=request, format=format),
            "signup": reverse("xauth:signup", request=request, format=format),
            "profile": reverse("xauth:profile", args=(1,), request=request, format=format),
            "verification-request": reverse("xauth:verification-request", request=request, format=format),
            "verification": reverse("xauth:verification-confirm", request=request, format=format),
            "password-reset-request": reverse("xauth:password-reset-request", request=request, format=format),
            "password-reset": reverse("xauth:password-reset-confirm", request=request, format=format),
            "account-activation-request": reverse("xauth:activation-request", request=request, format=format),
            "account-activation": reverse("xauth:activation-confirm", request=request, format=format),
            "security-question-add": reverse("xauth:security-question-add", request=request, format=format),
        },
        status=status.HTTP_200_OK,
    )
