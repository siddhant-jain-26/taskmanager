from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

status_choices = (
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        )


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=status_choices, default='pending')
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    celery_job_ids = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


