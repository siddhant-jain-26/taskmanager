import os
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.wsgi import get_wsgi_application
from django.test import TestCase
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from tasks.models import Task
from tasks.views import TasksAPIView, TaskAPIView

User = get_user_model()


class TasksAPIViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.task1 = Task.objects.create(title='Task 1', description='Description 1', status='pending',
                                         due_date=datetime.now() + timedelta(days=1), user=self.user)
        self.task2 = Task.objects.create(title='Task 2', description='Description 2', status='in_progress',
                                         due_date=datetime.now() + timedelta(days=2), user=self.user)
        self.factory = APIRequestFactory()

    def test_tasks_list(self):
        view = TasksAPIView.as_view()
        request = self.factory.get('/tasks/')
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Assuming it returns both tasks

    def test_task_create_success(self):
        view = TasksAPIView.as_view()
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        request = self.factory.post('/tasks/', data)
        force_authenticate(request, user=self.user)

        mock_schedule_task = Mock()

        with patch('tasks.views.schedule_notifications', mock_schedule_task):
            response = view(request)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(mock_schedule_task.called)
        scheduled_task_args = mock_schedule_task.call_args[0]
        task_id = scheduled_task_args[0]
        task = Task.objects.get(id=task_id)
        self.assertEqual(task.title, 'New Task')

    @patch('rest_framework.permissions.IsAuthenticated.has_permission')
    @patch('tasks.permissions.IsOwner.has_object_permission')
    def test_task_update(self, MockHasPermission, MockHasObjectPermission):
        MockHasPermission.return_value = True
        MockHasObjectPermission.return_value = True

        data = {
            'id': 1,
            'title': 'Updated Task',
            'description': 'New Description',
            'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }

        view = TaskAPIView.as_view()
        request = self.factory.put(f'/tasks/{self.task1.id}', data=data)
        force_authenticate(request, user=self.user)

        mock_schedule_task = Mock()
        mock_revoke_task = Mock()

        with patch('tasks.views.schedule_notifications', mock_schedule_task):
            with patch('tasks.views.revoke_scheduled_task', mock_revoke_task):
                response = view(request, pk=self.task1.id)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_revoke_task.assert_called_once()

        self.assertEqual(response.data['title'], 'Updated Task')

    @patch('rest_framework.permissions.IsAuthenticated.has_permission')
    @patch('tasks.permissions.IsOwner.has_object_permission')
    def test_task_delete(self, MockHasPermission, MockHasObjectPermission):
        MockHasPermission.return_value = True
        MockHasObjectPermission.return_value = True
        data = {
            'id': 1,
            'title': 'New Task',
            'description': 'New Description',
            'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        request = self.factory.post('/tasks/', data)
        force_authenticate(request, user=self.user)

        view = TaskAPIView.as_view()
        request = self.factory.delete(f'/tasks/{self.task1.id}')
        force_authenticate(request, user=self.user)

        mock_revoke_task = Mock()

        with patch('tasks.views.revoke_scheduled_task', mock_revoke_task):
            response = view(request, pk=self.task1.id)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        mock_revoke_task.assert_called_once()
        revoked_task_args = mock_revoke_task.call_args[0]
        self.assertEqual(revoked_task_args[0].title, 'Task 1')
