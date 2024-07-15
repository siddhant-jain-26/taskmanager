from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from .views import RegisterAPIView, ProfileAPIView

urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('profile', ProfileAPIView.as_view(), name='profile'),
]