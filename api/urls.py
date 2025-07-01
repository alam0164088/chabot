from django.urls import path
from .views import RegisterUserView, ChatbotView, ChatHistoryView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('chat/', ChatbotView.as_view(), name='chat'),
    path('chat/history/', ChatHistoryView.as_view(), name='chat_history'),
]
