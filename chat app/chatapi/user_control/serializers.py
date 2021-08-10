from rest_framework import serializers
from.models import UserProfile, CustomUser
from ..message_control.serializers import GenericFileUploadSerializer
from django.db.models import Q


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '_all_'


class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomerUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    profile_picture = GenericFileUploadSerializer(read_only=True)
    profile_picture_id = serializers.IntegerField(write_only=True, required=False)
    message_count = serializers.SerializerMethodField("get_message_count")

    class Meta:
        model = UserProfile
        fields = '_all_'

    def get_message_count(self, obj):
        try:
            user_id = self.context["request"].user.id
        except Exception as e:
            user_id = None

        from ..message_control.models import Message
        message = Message.objects.filter(Q(sender_id=user_id, reciver_id=obj.user.id) |
                                         Q(sender_id=obj.user.id, reciver_id=user_id)).distinct()

        return message.count()

