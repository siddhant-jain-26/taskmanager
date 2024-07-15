import os
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.core.wsgi import get_wsgi_application
from django.test import TestCase

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory
from rest_framework.throttling import UserRateThrottle

from accounts.permissions import IsOwner

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from accounts.views import RegisterAPIView, ProfileAPIView

User = get_user_model()


class TestRegisterAPIViewSuccess(TestCase):

    def test_register_user(self):
        request = Mock()
        request.method = 'POST'
        request.data = {
            "email": "testuser@example.com",
            "password": "strongpassword",
            "password2": "strongpassword"
        }

        view = RegisterAPIView()
        response = view.post(request)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')


class TestRegisterAPIViewFailure(TestCase):

    def test_register_user_password_mismatch(self):
        request = Mock()
        request.method = 'POST'
        request.data = {
            "email": "testuser@example.com",
            "password": "",
            "password2": "strongpassword"
        }

        view = RegisterAPIView()
        response = view.post(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('accounts.views.UserRegisterAPIViewSerializer')
    @patch.object(User.objects, 'filter')
    def test_register_user_existing_email(self, MockFilter, MockSerializer):
        # Mock filter to simulate existing user with same email
        MockFilter.return_value.exists.return_value = True

        mock_serializer_instance = MockSerializer.return_value
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer_instance.errors = {'email': ['A user with that email already exists.']}

        request = Mock()
        request.method = 'POST'
        request.data = {
            "email": "existing@example.com",
            "password": "strongpassword",
            "password2": "strongpassword"
        }

        view = RegisterAPIView()
        response = view.post(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'A user with that email already exists.')

    @patch.object(User.objects, 'filter')
    def test_register_user_empty_email(self, MockFilter):
        MockFilter.return_value.exists.return_value = False

        request = Mock()
        request.method = 'POST'
        request.data = {
            "email": "",
            "password": "strongpassword",
            "password2": "strongpassword"
        }

        view = RegisterAPIView()
        response = view.post(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], 'This field may not be blank.')

    @patch.object(User.objects, 'filter')
    def test_register_user_empty_password(self, MockFilter):
        MockFilter.return_value.exists.return_value = False

        request = Mock()
        request.method = 'POST'
        request.data = {
            "email": "testuser@example.com",
            "password": "",
            "password2": ""
        }

        view = RegisterAPIView()
        response = view.post(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')


class TestProfileAPIView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')

    @patch.object(ProfileAPIView, 'get_object')
    def test_fetch_profile(self, MockGetObject):
        MockGetObject.return_value = self.user

        request = Mock()
        request.method = 'GET'
        request.user = self.user

        view = ProfileAPIView()
        view.request = request
        view.format_kwarg = None

        response = view.get(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    @patch.object(ProfileAPIView, 'get_object')
    def test_fetch_profile(self, MockGetObject):
        MockGetObject.return_value = self.user

        request = Mock()
        request.method = 'GET'
        request.user = self.user

        view = ProfileAPIView()
        view.request = request
        view.format_kwarg = None

        response = view.get(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    @patch.object(ProfileAPIView, 'get_object')
    def test_update_email(self, MockGetObject):
        MockGetObject.return_value = self.user

        request = Mock()
        request.method = 'PUT'
        request.data = {'email': 'newemail@example.com'}
        request.user = self.user

        view = ProfileAPIView()
        view.request = request
        view.format_kwarg = None

        response = view.put(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newemail@example.com')

    @patch.object(ProfileAPIView, 'get_object')
    def test_update_password(self, MockGetObject):
        MockGetObject.return_value = self.user

        request = Mock()
        request.method = 'PUT'
        request.data = {'password': 'newstrongpassword'}
        request.user = self.user

        view = ProfileAPIView()
        view.request = request
        view.format_kwarg = None

        response = view.put(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newstrongpassword'))

    @patch('rest_framework.permissions.IsAuthenticated.has_permission')
    @patch('accounts.permissions.IsOwner.has_object_permission')
    def test_unauthorized_user_fetch_profile(self, MockHasPermission, MockHasObjectPermission):
        MockHasPermission.return_value = False
        MockHasObjectPermission.return_value = False

        factory = APIRequestFactory()
        request = factory.get('/profile/')
        request.user = self.user

        view = ProfileAPIView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch.object(ProfileAPIView, 'get_object')
    @patch.object(UserRateThrottle, 'get_rate')
    @patch.object(IsAuthenticated, 'has_permission', return_value=True)
    @patch.object(IsOwner, 'has_object_permission', return_value=True)
    def test_throttling_exceeded(self, MockHasPermission, MockHasObjectPermission, MockGetRate, MockGetObject):
        MockGetRate.return_value = '1/minute'

        MockGetObject.return_value = self.user

        view = ProfileAPIView.as_view()
        factory = APIRequestFactory()

        request = factory.get('/profile/')
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request = factory.get('/profile/')
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch.object(ProfileAPIView, 'get_object')
    def test_delete_profile(self, MockGetObject):
        MockGetObject.return_value = self.user

        request = Mock()
        request.method = 'DELETE'
        request.user = self.user

        view = ProfileAPIView()
        view.request = request
        view.format_kwarg = None

        response = view.delete(request)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email=self.user.email).exists())
