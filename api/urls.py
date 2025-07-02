from django.urls import path
from .views import RegisterUserView, ChatbotView, ChatHistoryView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('chat/', ChatbotView.as_view(), name='chatbot'),
    path('chat/history/', ChatHistoryView.as_view(), name='chat_history'),
]