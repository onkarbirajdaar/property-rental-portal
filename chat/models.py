from django.conf import settings
from django.db import models

from properties.models import Property


class Conversation(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="conversations",)
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_conversations",)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["property", "tenant"], name="unique_property_tenant_conversation",)]
        ordering = ["created_at"]

    def __str__(self):
        return f"Conversation: {self.property} - {self.tenant}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages",)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages",)
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["created_at"]
    def __str__(self):
        return f"{self.sender}: {self.body[:50]}"
