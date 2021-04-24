from rest_framework import viewsets

from xauth.apps.account.models import SecurityQuestion
from xauth.permissions import *  # noqa
from xauth.serializers.security_question.admin import SecurityQuestionSerializer


class SecurityQuestionView(viewsets.ModelViewSet):
    queryset = SecurityQuestion.objects.filter(usable=True)
    serializer_class = SecurityQuestionSerializer
    permission_classes = [
        IsSuperUserOrReadOnly,
    ]
