from django.urls import path

from .views import TasksAPIView, TaskAPIView

urlpatterns = [
    path('', TasksAPIView.as_view(), name='tasks'),
    path('<int:pk>', TaskAPIView.as_view(), name='task'),
]
