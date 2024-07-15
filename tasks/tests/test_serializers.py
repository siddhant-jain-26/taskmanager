import os

from django.core.wsgi import get_wsgi_application
from django.test import TestCase
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from tasks.serializers import TaskAPIViewSerializer, TasksAPIViewSerializer


class TestTaskAPIViewSerializer(TestCase):

    def setUp(self):
        self.task_data = {
            'title': 'Test Task',
            'description': 'This is a test task.',
            'status': 'pending',
            'due_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }

    def test_task_serializer_valid(self):
        serializer = TaskAPIViewSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())

    def test_task_serializer_save(self):
        serializer = TaskAPIViewSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()  # Save the task object
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.description, 'This is a test task.')

    def test_task_serializer_invalid_due_date_format(self):
        invalid_data = self.task_data.copy()
        invalid_data['due_date'] = 'Invalid Date Format'
        serializer = TaskAPIViewSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class TasksAPIViewSerializerTestCase(TestCase):

    def setUp(self):
        self.task_data = {
            'title': 'Test Task',
            'description': 'This is a test task.',
            'status': 'pending',
            'due_date': '2024-07-18T12:00:00Z'
        }

    def test_tasks_serializer_valid(self):
        serializer = TasksAPIViewSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())

    def test_tasks_serializer_save(self):
        serializer = TasksAPIViewSerializer(data=self.task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.description, 'This is a test task.')

    def test_tasks_serializer_missing_required_fields(self):
        incomplete_data = {
            'id': 1,
            'title': 'Test Task'
        }
        serializer = TasksAPIViewSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())

