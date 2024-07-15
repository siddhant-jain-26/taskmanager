import os

from django.core.wsgi import get_wsgi_application
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from tasks.models import Task, status_choices

User = get_user_model()


class TaskModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')

    def test_task_creation(self):
        task = Task.objects.create(
            title='Test Task',
            description='This is a test task description.',
            status='pending',
            due_date=timezone.now(),
            celery_job_ids='job123',
            user=self.user
        )

        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.user, self.user)

    def test_task_string_representation(self):
        task = Task.objects.create(
            title='Test Task',
            description='This is a test task description.',
            status='pending',
            due_date=timezone.now(),
            celery_job_ids='job123',
            user=self.user
        )

        self.assertEqual(str(task), 'Test Task')

    def test_task_status_choices(self):
        choices = dict(status_choices)
        for key, label in status_choices:
            self.assertIn(key, choices)
            self.assertEqual(choices[key], label)
