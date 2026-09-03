from rest_framework import serializers
from apps.messaging.infrastructure.models import Message, MessageReply
class MessageReplySerializer(serializers.ModelSerializer):
    sender_name=serializers.CharField(source="sender.username", read_only=True)
    class Meta:
        model=MessageReply; fields=["id","sender","sender_name","message_text","created_at"]; read_only_fields=["id","sender","sender_name","created_at"]
class MessageSerializer(serializers.ModelSerializer):
    replies=MessageReplySerializer(many=True, read_only=True)
    customer_name=serializers.CharField(source="customer.full_name", read_only=True)
    class Meta:
        model=Message; fields=["id","customer","customer_name","subject","message","is_closed","replies","created_at"]; read_only_fields=["id","customer","customer_name","replies","created_at"]
