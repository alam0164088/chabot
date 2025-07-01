from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    """
    Stores a single chat message exchanged between a user and the AI chatbot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    user_query = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp'] # Order messages by time
        verbose_name_plural = "Chat Messages" # Better name in Django admin

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"