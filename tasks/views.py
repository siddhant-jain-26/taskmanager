from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .models import Task
from .permissions import IsOwner
from .serializers import TaskAPIViewSerializer, TasksAPIViewSerializer
from .signals import schedule_notifications, revoke_scheduled_task


class TasksAPIView(ListCreateAPIView):
    serializer_class = TaskAPIViewSerializer
    permission_classes = (IsAuthenticated, IsOwner)
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)

        if task.status in ["pending", "in_progress"]:
            schedule_notifications(task.id, task.due_date)


class TaskAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TasksAPIViewSerializer
    permission_classes = (IsAuthenticated, IsOwner)
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        try:
            task_instance = self.get_object()
            revoke_scheduled_task(task_instance)
            updated_task_instance = serializer.save(user=self.request.user)
            schedule_notifications(updated_task_instance.id, updated_task_instance.due_date)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, serializer):
        try:
            task_instance = self.get_object()
            revoke_scheduled_task(task_instance)
            task_instance.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
