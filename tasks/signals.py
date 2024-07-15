import datetime
from datetime import datetime, timedelta
from celery import shared_task
from celery.result import AsyncResult
import logging
import pytz

from .utils import send_email_notification
from .models import Task

logger = logging.getLogger('taskmanager')


@shared_task
def schedule_notifications(task_id, due_date):
    try:
        task = Task.objects.get(id=task_id)

        if isinstance(due_date, str):
            timezone = pytz.timezone('Asia/Kolkata')
            due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
            due_date = timezone.localize(due_date)

        job_ids = [
            send_email_notification.apply_async((task_id,), eta=due_date - timedelta(minutes=5)).id,
            send_email_notification.apply_async((task_id,), eta=due_date - timedelta(minutes=10)).id
        ]

        task.celery_job_ids = ",".join(job_ids)
        task.save()
    except Task.DoesNotExist:
        logger.info("Task {} does not exist".format(task_id))


def revoke_scheduled_task(task):
    celery_job_ids = task.celery_job_ids.split(',')

    if isinstance(task, Task):
        for job_id in celery_job_ids:
            try:
                result = AsyncResult(job_id.strip())
                if result.state == 'REVOKED':
                    logger.info(f"Task {job_id} was already revoked")
                else:
                    result.revoke(terminate=True)
                    logger.info(f"Revoked task {job_id}")
            except Exception as e:
                logger.error(f"Error revoking task {job_id}: {e}")
    else:
        logger.warning("Invalid task object provided")
