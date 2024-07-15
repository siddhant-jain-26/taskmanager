import logging
from celery import shared_task
from django.core.mail import send_mail

from .models import Task

logger = logging.getLogger('taskmanager')


@shared_task
def send_email_notification(task_id):
    try:
        task = Task.objects.get(id=task_id)
        logger.info(f"Sending email for task {task_id} titled '{task.title}'")
        send_mail(
            'Task Due Soon',
            f'Your task "{task.title}" is due soon.',
            'your-email@gmail.com',
            [task.user.email],
            fail_silently=False,
        )
    except Task.DoesNotExist:
        logger.error(f"Task with ID {task_id} does not exist")

