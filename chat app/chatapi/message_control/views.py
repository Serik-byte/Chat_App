from rest_framework.viewsets import ModelViewSet
from .serializers import GenericFileUpload, GenericFileUploadSerializer, Message, MessageAttachment,MessageSerializer
from ..chatapi.custom_methods import IsAuthenticatedCustom
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q


class GenericFileUploadView(ModelViewSet):
    queryset = GenericFileUpload.objects.all()
    serializer_class = GenericFileUploadSerializer


class MessageView(ModelViewSet):
    queryset = Message.objects.select_related(
        "sender", "receiver").prefetch_related("message_attachments")
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticatedCustom, )

    def get_queryset(self):
        data = self.request.query_params.dict()
        user_id = data.get("user_id", None)

        if user_id is None:
            raise Exception("Specify the user to get message for")

        active_user_id = self.request.user.id
        return self.queryset.filter(Q(sender_id=user_id, receiver_id=active_user_id) | Q(
            sender_id = active_user_id, receiver_id=user_id)).distinct()

    def create(self, request, *args, **kwargs):
        attachments = request.data.pop("attachments", None)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if attachments:
            MessageAttachment.objects.bulk_create([MessageAttachment(**attachment, message_id=serializer.data["id"]) for attachment in attachments])

            message_data = self.get_queryset().get(serializer.data["id"])
            return Response(self.serializer_class(message_data).data, status=201 )

        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        attachments = request.data.pop("attachments", None)
        instance = self.get_object()

        serializer = self.serializer_class(
            data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        MessageAttachment.objects.filter(message_id=instance.id).delete()

        if attachments:
            MessageAttachment.objects.bulk_create([MessageAttachment(
                **attachment, message_id=instance.id) for attachment in attachments])

            message_data = self.get_object()
            return Response(self.serializer_class(message_data).data, status=200)