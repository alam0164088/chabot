import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

from google.api_core import exceptions as core_exceptions

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import UserSerializer, ChatMessageSerializer
from .models import ChatMessage
from rest_framework.views import APIView

load_dotenv()

logger = logging.getLogger(__name__)

# --- Configuration for Google Gemini API ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in .env file. Please set the environment variable.")
    raise ValueError("GOOGLE_API_KEY not found in .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# *** গুরুত্বপূর্ণ অংশ: উপলব্ধ Gemini মডেল চেক করা ***
# আপনার API Key এর জন্য কোন মডেলগুলো 'generateContent' সমর্থন করে তা দেখুন।
# টার্মিনাল আউটপুটে এই তালিকাটি দেখতে পাবেন।
print("\n--- Checking available Gemini models for 'generateContent' method ---")
available_gemini_models = []
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            available_gemini_models.append(m.name)
            print(f"- Found available model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
    print("Please ensure your GOOGLE_API_KEY is correct and you have an active internet connection.")

if not available_gemini_models:
    print("WARNING: No models found that support 'generateContent'. Your Gemini API might not work.")
    print("Please check your API key in Google AI Studio and ensure it's enabled for Gemini API.")

print("-------------------------------------------------------------------\n")

# আপনি যে মডেলটি ব্যবহার করতে চান, সেটির নাম এখানে লিখুন।
# আপনার লগে 'models/gemini-1.5-flash' এবং 'models/gemini-1.5-pro' এর মত মডেল দেখাচ্ছে।
# 'models/gemini-1.5-flash' সাধারণত দ্রুত কাজ করে এবং বর্তমান ব্যবহারের জন্য উপযুক্ত।
# যদি আপনি 'gemini-pro' ব্যবহার করতে চান, তাহলে নিশ্চিত করুন যে এটি আপনার উপলব্ধ মডেলের তালিকাতে আছে।
# আমি এখানে 'models/gemini-1.5-flash' ব্যবহার করছি, কারণ এটি আপনার লগে উপলব্ধ দেখা গেছে।
GEMINI_MODEL_NAME = 'models/gemini-1.5-flash' # <--- এই লাইনটি পরিবর্তন করা হয়েছে!

# আপনি যদি চান যে কোডটি স্বয়ংক্রিয়ভাবে প্রথম উপলব্ধ মডেলটি বেছে নিক, তাহলে নিচের অংশটি আনকমেন্ট করতে পারেন:
# if available_gemini_models:
#     GEMINI_MODEL_NAME = available_gemini_models[0]
#     print(f"Using first available model: {GEMINI_MODEL_NAME}")
# else:
#     print("No suitable Gemini model found. Falling back to default 'gemini-pro' which might not work.")


# নিশ্চিত করুন যে GEMINI_MODEL_NAME এ 'models/' প্রিফিক্সটি রয়েছে যদি মডেলের নাম সেটি দাবি করে
if not GEMINI_MODEL_NAME.startswith('models/'):
    GEMINI_MODEL_NAME = 'models/' + GEMINI_MODEL_NAME

GEMINI_MODEL = genai.GenerativeModel(GEMINI_MODEL_NAME)


# --- User Registration View ---
class RegisterUserView(generics.CreateAPIView):
    """
    API endpoint for user registration. Allows any user to register.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

# --- Updated Chatbot View for Gemini API ---
class ChatbotView(APIView):
    """
    API endpoint for interacting with the Google Gemini API. Requires authentication.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_query = request.data.get('query')
        if not user_query:
            return Response(
                {"error": "Query parameter is required in the request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            logger.info(f"Sending query to Gemini API: {user_query}")
            
            # Gemini মডেলের সাথে ইন্টারঅ্যাকশন
            response = GEMINI_MODEL.generate_content(user_query)
            
            # Gemini রেসপন্স থেকে টেক্সট এক্সট্র্যাক্ট করুন
            ai_response_text = response.text
            
            logger.debug(f"Raw Gemini API response: {ai_response_text}")

            # চ্যাট ইন্টারঅ্যাকশন ডেটাবেসে সংরক্ষণ করুন
            chat_message = ChatMessage.objects.create(
                user=request.user,
                user_query=user_query,
                bot_response=ai_response_text
            )
            serializer = ChatMessageSerializer(chat_message)
            logger.info(f"Chat interaction saved for user: {request.user.username}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        except genai.types.BlockedPromptException as e:
            # যদি প্রম্পট ব্লক করা হয় (যেমন, অনিরাপদ কন্টেন্ট)
            logger.error(f"Gemini API BlockedPromptException: {e.response.text}", exc_info=True)
            return Response(
                {"error": "Your query was blocked due to safety concerns. Please rephrase your query.",
                 "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except core_exceptions.GoogleAPICallError as e:
            # অন্যান্য Gemini API এরর (যেমন, 404 NotFound, 400 BadRequest, 403 Forbidden ইত্যাদি)
            logger.error(f"Gemini API Call Error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Gemini API Call Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # অন্য কোনো অপ্রত্যাশিত এরর
            logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# --- Chat History View ---
class ChatHistoryView(generics.ListAPIView):
    """
    API endpoint to retrieve the chat history for the authenticated user.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user).order_by('timestamp')