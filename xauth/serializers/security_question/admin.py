from rest_framework import serializers

from xauth.models import SecurityQuestion


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
