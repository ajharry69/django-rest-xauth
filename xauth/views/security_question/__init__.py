from django.db.models import Q
from rest_framework import views, status
from rest_framework.response import Response

from xauth import permissions
from xauth.models import SecurityQuestion
from xauth.utils import valid_str


class AddSecurityQuestionView(views.APIView):
    """
    Attaches users selected security question and the corresponding answer
    """
    permission_classes = [permissions.IsAuthenticated, ]

    @staticmethod
    def post(request, format=None):
        user, data = request.user, request.data
        # question can be identified by the question text itself or it's id both of which are
        # expected to be unique
        answer = data.get('answer') or data.get('question_answer')
        question_id = data.get('question') or data.get('id') or data.get('question_id')
        question = SecurityQuestion.objects.filter(
            Q(question=question_id) | Q(id=question_id),
        ).first()
        if question and valid_str(answer):
            # question was found and answer is a valid string
            user.add_security_question(question, answer)
            data, status_code = {'success': 'security question added successfully'}, status.HTTP_200_OK
        else:
            data = {'error': f"invalid {'answer' if question else 'question'}"}
            data, status_code = data, status.HTTP_400_BAD_REQUEST
        return Response(data, status=status_code or status.HTTP_200_OK)
