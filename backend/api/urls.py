from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DetectionViewSet, ChatView, RegisterView, LoginView, UserView

router = DefaultRouter()
router.register(r'detections', DetectionViewSet, basename='detection')

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', ChatView.as_view(), name='chat'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/user/', UserView.as_view(), name='user'),
]