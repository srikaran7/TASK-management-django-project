from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Task
from .serializers import TaskSerializer
from .celery_tasks import send_task_notification



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Limt tasks to members in the project"""
        user = self.request.user
        return Task.objects.filter(project__members=user)
    
    def perform_create(self, serializer):
        task = serializer.save()
        if task.assigned_to.exists() and not task.assigned_to.filter(id__in=task.project.members.all()).exists():
            raise PermissionDenied("Assigned users must be project members.")
        
        # Notify assigned users asunchronously using celery
        for user in task.assigned_to.all():
            send_task_notification.delay(user.id, task.id, "A new task has been assigned to you.")

    
    def perform_update(self, serializer):
        """Allow only the project owner to edit tasks."""
        task = self.get_object()
        if task.project.owner != self.request.user:
            raise PermissionDenied('Only the project owner can edit tasks.')
        serializer.save()

        # Notify assigned users about task updates
        for user in task.assigned_to.all():
            send_task_notification.delay(user.id, task.id, "Your task has been updated.")

    
    def perform_destroy(self, instance):
        """Allow only the project owner to delete tasks."""
        if instance.project.owner != self.request.user:
            raise PermissionDenied('Only the project owner can delete tasks.')
        instance.delete()
        

