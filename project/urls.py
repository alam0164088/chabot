from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', TemplateView.as_view(template_name='ai_api/index.html'), name='home'),
    path('index.html', TemplateView.as_view(template_name='ai_api/index.html'), name='index_html'),
    path('index.htm', TemplateView.as_view(template_name='ai_api/index.html'), name='index_htm'),
]