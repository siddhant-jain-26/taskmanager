# Generated by Django 4.1.13 on 2024-07-14 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='celery_job_ids',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
