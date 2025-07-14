import uuid
from django.db import models
from django.conf import settings




class Project(models.Model):
    class Meta:
         # Ensure that each owner can only have one project with the same title
        unique_together = ('title', 'owner')
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null= True,
        related_name='projects'
        )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='project_members') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title