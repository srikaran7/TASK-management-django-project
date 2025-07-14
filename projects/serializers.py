from rest_framework import serializers
from .models import Project
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'members', 'created_at', 'task_count']
        read_only_fields = ['id', 'created_at']

    def get_task_count(self, obj):
        return Task.objects.filter(project_id=obj).count()

    def validate_members(self, value):
        if value is None:
            return []
        return value

class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return user