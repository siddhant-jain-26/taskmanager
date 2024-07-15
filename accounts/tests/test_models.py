import os

from django.core.wsgi import get_wsgi_application
from django.test import TestCase
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

User = get_user_model()


class TestCustomUser(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(email='user@example.com', password='testpassword')

        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.date_joined)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(email='superuser@example.com', password='testpassword')

        self.assertEqual(superuser.email, 'superuser@example.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertIsNotNone(superuser.date_joined)

    def test_user_str_representation(self):
        user = User.objects.create_user(email='user@example.com', password='testpassword')

        self.assertEqual(str(user), 'user@example.com')
