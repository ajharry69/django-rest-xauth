from rest_framework import serializers


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, max_length=250, )
    password = serializers.CharField(write_only=True, max_length=1500, style={'input_type': 'password'}, )

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def create(self, validated_data):
        from xauth import authentication
        username, password = validated_data.get('username'), validated_data.get('password')
        auth = authentication.BasicTokenAuthentication()
        return auth.get_user_with_username_and_password(username, password)
