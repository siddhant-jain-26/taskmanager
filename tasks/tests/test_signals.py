import os

from unittest.mock import patch
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.wsgi import get_wsgi_application
from django.test import TestCase
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from tasks.models import Task
from tasks.signals import schedule_notifications, revoke_scheduled_task

User = get_user_model()


class TaskCeleryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass')
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            status='pending',
            due_date=timezone.now() + timedelta(days=1),
            user=self.user,
        )

    @patch('tasks.utils.send_email_notification.apply_async')
    def test_schedule_notifications(self, mock_apply_async):
        mock_apply_async.return_value.id = 'mock_job_id'

        due_date_str = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        schedule_notifications(self.task.id, due_date_str)

        self.task.refresh_from_db()
        self.assertTrue(self.task.celery_job_ids)
        job_ids = self.task.celery_job_ids.split(',')

        self.assertEqual(len(job_ids), 2)

        self.assertEqual(job_ids[0], 'mock_job_id')
        self.assertEqual(job_ids[1], 'mock_job_id')

        self.assertEqual(mock_apply_async.call_count, 2)

        first_call_eta = mock_apply_async.call_args_list[0][1]['eta']
        second_call_eta = mock_apply_async.call_args_list[1][1]['eta']

        due_date = timezone.localtime(self.task.due_date)

        self.assertEqual(first_call_eta.date(), (due_date - timedelta(minutes=5)).date())
        self.assertAlmostEqual(second_call_eta.date(), (due_date - timedelta(minutes=10)).date())

    @patch('tasks.signals.AsyncResult')
    def test_revoke_scheduled_task(self, mock_async_result):
        job_id_1 = '12345'
        job_id_2 = '67890'
        self.task.celery_job_ids = f'{job_id_1},{job_id_2}'
        self.task.save()

        mock_result_instance = mock_async_result.return_value
        mock_result_instance.state = 'PENDING'

        revoke_scheduled_task(self.task)

        mock_async_result.assert_any_call(job_id_1)
        mock_async_result.assert_any_call(job_id_2)
        self.assertEqual(mock_result_instance.revoke.call_count, 2)

    @patch('tasks.signals.AsyncResult')
    def test_revoke_already_revoked_task(self, mock_async_result):
        job_id_1 = '12345'
        self.task.celery_job_ids = job_id_1
        self.task.save()

        mock_result_instance = mock_async_result.return_value
        mock_result_instance.state = 'REVOKED'

        revoke_scheduled_task(self.task)

        mock_async_result.assert_called_once_with(job_id_1)
        self.assertEqual(mock_result_instance.revoke.call_count, 0)
