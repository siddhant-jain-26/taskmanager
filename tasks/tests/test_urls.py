import os

from django.core.wsgi import get_wsgi_application
from django.urls import reverse, resolve
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
application = get_wsgi_application()
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from tasks.views import TasksAPIView, TaskAPIView


class TestRegisterAPIView(TestCase):

    def test_tasks_url(self):
        url = reverse('tasks')
        self.assertEqual(resolve(url).func.view_class, TasksAPIView)

    def test_task_url(self):
        url = reverse('task')
        self.assertEqual(resolve(url).func.view_class, TaskAPIView)

