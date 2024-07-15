from django.core.wsgi import get_wsgi_application
from django.urls import reverse, resolve
from django.test import TestCase
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from accounts.views import RegisterAPIView, ProfileAPIView


class TestRegisterAPIView(TestCase):

    def test_register_url(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, RegisterAPIView)

    def test_profile_url(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func.view_class, ProfileAPIView)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, TokenObtainPairView)
