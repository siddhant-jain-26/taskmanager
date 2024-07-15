from rest_framework import serializers

from .models import Task


class TaskAPIViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'due_date')


class TasksAPIViewSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    due_date = serializers.CharField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'due_date')
