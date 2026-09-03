import uuid
from django.conf import settings
from django.db import models
from apps.customers.infrastructure.models import Customer

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, related_name="messages", on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class MessageReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, related_name="replies", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
