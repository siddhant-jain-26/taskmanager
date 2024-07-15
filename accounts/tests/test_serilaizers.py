import os

from django.contrib.auth import get_user_model
from django.core.wsgi import get_wsgi_application
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

User = get_user_model()

from accounts.serializers import UserRegisterAPIViewSerializer, ProfileAPIViewSerializer


class TestUserRegisterAPIViewSerializer(APITestCase):

    def test_valid_registration(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'strongpassword',
            'password2': 'strongpassword'
        }
        serializer = UserRegisterAPIViewSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, data['email'])

    def test_email_already_exists(self):
        User.objects.create_user(email='testuser@example.com', password='testpassword')
        data = {
            'email': 'testuser@example.com',
            'password': 'strongpassword',
            'password2': 'strongpassword'
        }
        serializer = UserRegisterAPIViewSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('A user with that email already exists.', str(context.exception))

    def test_passwords_do_not_match(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'strongpassword',
            'password2': 'weakpassword'
        }
        serializer = UserRegisterAPIViewSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Passwords must match', str(context.exception))


class TestProfileAPIViewSerializer(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')

    def test_valid_profile_update(self):
        data = {
            'email': 'newemail@example.com',
            'password': 'newpassword'
        }
        serializer = ProfileAPIViewSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password']))

    def test_update_email_only(self):
        data = {
            'email': 'newemail@example.com'
        }
        serializer = ProfileAPIViewSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password('testpassword'))

    def test_update_password_only(self):
        data = {
            'password': 'newpassword'
        }
        serializer = ProfileAPIViewSerializer(instance=self.user, data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, self.user.email)
        self.assertTrue(user.check_password(data['password']))
