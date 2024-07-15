import os
import logging
from datetime import datetime, timedelta

from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.core.wsgi import get_wsgi_application
from django.test import TestCase
from django.core import mail
from celery import Task as CeleryTask

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from tasks.models import Task
from tasks.utils import send_email_notification

User = get_user_model()

logger = logging.getLogger('taskmanager')


class TestSendEmailNotification(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpassword')
        self.task = Task.objects.create(title='Task 1', description='Description 1', status='pending',
                                        due_date=datetime.now() + timedelta(days=1), user=self.user)

    @patch.object(logger, 'info')
    @patch.object(logger, 'error')
    @patch('tasks.models.Task.objects.get')
    def test_send_email_notification_success(self, MockGetTask, MockLoggerError, MockLoggerInfo):
        MockGetTask.return_value = self.task

        send_email_notification(task_id=self.task.id)

        MockGetTask.assert_called_once_with(id=self.task.id)

        MockLoggerInfo.assert_called_once_with(f"Sending email for task {self.task.id} titled '{self.task.title}'")

        MockLoggerError.assert_not_called()

    @patch.object(logger, 'info')
    @patch.object(logger, 'error')
    @patch('tasks.utils.Task.objects.get')
    def test_send_email_notification_task_not_found(self, MockGetTask, MockLoggerError, MockLoggerInfo):
        MockGetTask.side_effect = Task.DoesNotExist

        send_email_notification(task_id=self.task.id)

        MockGetTask.assert_called_once_with(id=self.task.id)

        MockLoggerInfo.assert_not_called()

        MockLoggerError.assert_called_once_with(f"Task with ID {self.task.id} does not exist")
