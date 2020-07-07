# class AddSecurityQuestionSerializer(serializers.ModelSerializer):
#     """
#     Attaches users selected security question and the corresponding answer
#     """
#     __SECURITY_QUESTIONS = [(q.id, q.question) for q in SecurityQuestion.objects.filter(usable=True)]
#     question = serializers.ChoiceField(choices=__SECURITY_QUESTIONS, write_only=True)
#     answer = serializers.CharField(write_only=True, allow_null=True, allow_blank=True,
#                                    style={'input_type': 'password'}, )
#
#     class Meta:
#         model = Metadata
#         fields = ('question', 'answer',)
