from django.db import models
from django.core.exceptions import ValidationError


class Conversation(models.Model):
    CONVERSATION_STATE_CHOICES = {
        "OPEN": "Open",
        "CLOSED": "Closed"
    }
    id = models.CharField(max_length=256, unique=True, blank=False, null=False, primary_key=True)
    state = models.CharField(choices=CONVERSATION_STATE_CHOICES, max_length=6)
    datetime = models.DateTimeField(blank=False, null=False)
    

class Message(models.Model):
    MESSAGE_DIRECTION_CHOICES = {
        "SENT": "Sent",
        "RECEIVED": "Received"
    }
    id = models.CharField(max_length=256, unique=True, blank=False, null=False, primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    datetime = models.DateTimeField(blank=False, null=False)
    direction = models.CharField(choices=MESSAGE_DIRECTION_CHOICES, max_length=8)
    content = models.TextField(blank=False, null=False)
    
    def save(self, **kwargs):
        if (self.conversation.state == "OPEN"):
            super().save(**kwargs)
        else:
            raise ValidationError("Cannot save message. Conversation is closed.")