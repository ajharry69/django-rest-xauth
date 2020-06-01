from django.contrib.auth import get_user_model
from rest_framework import serializers

from xauth.models import SecurityQuestion


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:profile')

    # groups = serializers.HyperlinkedRelatedField(view_name='group-detail', many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = get_user_model().PUBLIC_READ_WRITE_FIELDS + ('url',)
        read_only_fields = get_user_model().READ_ONLY_FIELDS


class AuthTokenOnlySerializer(serializers.HyperlinkedModelSerializer):
    normal = serializers.CharField(source='token.tokens.normal', read_only=True, )
    encrypted = serializers.CharField(source='token.tokens.encrypted', read_only=True, )

    class Meta:
        model = get_user_model()
        fields = 'normal', 'encrypted',


class AuthSerializer(AuthTokenOnlySerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:profile')

    class Meta(AuthTokenOnlySerializer.Meta):
        fields = ProfileSerializer.Meta.fields + AuthTokenOnlySerializer.Meta.fields
        read_only_fields = ProfileSerializer.Meta.read_only_fields

    def validate(self, attrs):
        return super().validate(attrs)


class SignUpSerializer(AuthSerializer):
    password = serializers.CharField(write_only=True, allow_null=True, allow_blank=True,
                                     style={'input_type': 'password'})

    class Meta(AuthSerializer.Meta):
        fields = AuthSerializer.Meta.fields + get_user_model().WRITE_ONLY_FIELDS


class SecurityQuestionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Used by site **Admin/Superusers** to create and update list of security questions and only provide
    a public read access to available questions from which they could make a choice
    """
    url = serializers.HyperlinkedIdentityField(view_name='xauth:securityquestion-detail')
    date_added = serializers.DateTimeField(source='added_on', read_only=True, )
    usable = serializers.BooleanField(default=True, )

    class Meta:
        model = SecurityQuestion
        fields = ('url', 'id', 'question', 'usable', 'date_added',)
        read_only_fields = ('id',)


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
