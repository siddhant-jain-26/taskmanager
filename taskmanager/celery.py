from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('celery.log'),
#         logging.StreamHandler()
#     ]
# )
app = Celery('taskmanager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')