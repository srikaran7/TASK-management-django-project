from rest_framework import serializers
from .models import Task
from projects.models import Project


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'project', 'title',
            'description', 'status', 'assigned_to',
            'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_assigned_to(self, value):
        """
        Ensure all assigned users are members of the project
        """
        if not value:
            return value  # Allow empty assignment
        
        if self.instance:  # If task already exists
            project = self.instance.project  # Get the existing project
        else:  # If it's a new task
            project_id = self.initial_data.get('project')

            if not project_id:
                raise serializers.ValidationError('Project is required.')

            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                raise serializers.ValidationError('Invalid project ID.')

        non_members = []  # Create an empty list to store invalid users

        for user in value:
            if user not in project.members.all():  # Check if the user is NOT in project members
                non_members.append(user)

        if non_members:  # If there are any invalid users
            raise serializers.ValidationError('Some assigned users are not members of the project.')

        return value  # If all users are valid, return value
