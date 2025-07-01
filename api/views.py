import os
import openai
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import UserSerializer, ChatMessageSerializer
from .models import ChatMessage
from rest_framework.views import APIView

class RegisterUserView(generics.CreateAPIView):
    """
    API endpoint for user registration. Allows any user to register.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,) # No authentication required for registration

class ChatbotView(APIView):
    """
    API endpoint for interacting with the OpenAI chatbot. Requires authentication.
    """
    permission_classes = (IsAuthenticated,) # Only authenticated users can access this view

    def post(self, request, *args, **kwargs):
        user_query = request.data.get('query')
        if not user_query:
            return Response({"error": "Query parameter is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        # Get OpenAI API key from environment variables
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            return Response({"error": "OpenAI API key is not configured in environment variables."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Initialize OpenAI client with the retrieved API key
            client = openai.OpenAI(api_key=openai_api_key)

            # Make a request to the OpenAI Chat Completion API
            # Using gpt-3.5-turbo as it's widely available and cost-effective
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # You can change this to gpt-4 or other models if you have access
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for Sparktech Agency."},
                    {"role": "user", "content": user_query},
                ]
            )
            bot_response = response.choices[0].message.content

            # Save the chat interaction to the database
            chat_message = ChatMessage.objects.create(
                user=request.user, # The authenticated user
                user_query=user_query,
                bot_response=bot_response
            )
            serializer = ChatMessageSerializer(chat_message)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except openai.APIError as e:
            # Handle specific OpenAI API errors (e.g., invalid key, rate limits, server issues)
            print(f"OpenAI API Error details: {e.response.json()}") # For debugging
            return Response(
                {"error": f"OpenAI API Error: {e.status_code} - {e.response.json().get('error', {}).get('message', 'Unknown OpenAI error occurred.')}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred in ChatbotView: {e}") # For debugging
            return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatHistoryView(generics.ListAPIView):
    """
    API endpoint to retrieve the chat history for the authenticated user.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Filter chat messages by the currently authenticated user
        return ChatMessage.objects.filter(user=self.request.user).order_by('timestamp') # Order by timestamp for chronological history