from django.contrib.auth import get_user_model
from rest_framework import serializers

from xauth.models import SecurityQuestion
from xauth.utils import get_class
from xauth.utils.settings import USER_LOOKUP_FIELD, USER_PROFILE_SERIALIZER


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:profile', lookup_field=USER_LOOKUP_FIELD, )

    # groups = serializers.HyperlinkedRelatedField(view_name='group-detail', many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = tuple(get_user_model().PUBLIC_READ_WRITE_FIELDS) + ('url',)
        read_only_fields = tuple(get_user_model().READ_ONLY_FIELDS)


profile_serializer_class = get_class(USER_PROFILE_SERIALIZER, ProfileSerializer)


class AuthTokenOnlySerializer(serializers.HyperlinkedModelSerializer):
    normal = serializers.CharField(source='token.tokens.normal', read_only=True, )
    encrypted = serializers.CharField(source='token.tokens.encrypted', read_only=True, )

    class Meta:
        model = get_user_model()
        fields = 'normal', 'encrypted',


class AuthSerializer(profile_serializer_class):
    token = serializers.DictField(source='token.tokens', read_only=True, )

    class Meta(profile_serializer_class.Meta):
        fields = tuple(profile_serializer_class.Meta.fields) + ('token',)

    def validate(self, attrs):
        return super().validate(attrs)


class SignUpSerializer(AuthSerializer):
    password = serializers.CharField(write_only=True, allow_null=True, allow_blank=True,
                                     style={'input_type': 'password'})

    class Meta(AuthSerializer.Meta):
        fields = tuple(AuthSerializer.Meta.fields) + tuple(get_user_model().WRITE_ONLY_FIELDS)

    def create(self, validated_data):
        # saves password in plain text
        user = super().create(validated_data)
        if user.has_usable_password():
            # hash and re-save password
            user.password = user.get_hashed(user.password)
            user.save()
        return user


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
