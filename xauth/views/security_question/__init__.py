from django.db.models import Q
from rest_framework import views, status
from rest_framework.response import Response

from xauth import permissions
from xauth.models import SecurityQuestion
from xauth.utils import valid_str, get_wrapped_response


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
        answer = data.get('answer', data.get('question_answer', None))
        question_id = data.get('question', data.get('id', data.get('question_id', None)))
        question = SecurityQuestion.objects.filter(Q(question=question_id) | Q(id=question_id)).first()
        if question and valid_str(answer):
            # question was found and answer is a valid string
            user.add_security_question(question, answer)
            data, status_code = {'success': 'security question added successfully'}, status.HTTP_200_OK
        else:
            data = {'error': f"invalid {'answer' if question else 'question'}"}
            data, status_code = data, status.HTTP_400_BAD_REQUEST
        response = Response(data, status=status_code if status_code else status.HTTP_200_OK)
        return get_wrapped_response(response)
