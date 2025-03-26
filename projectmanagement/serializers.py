from rest_framework import serializers
from .models import Project, ProjectTeamMember, Milestone, Task
from authflow.models import CustomUser 

class ProjectSerializer(serializers.ModelSerializer):
    team_members = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),  # Allow assigning existing users
        many=True  # Accept multiple user IDs
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'team_members']

class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTeamMember
        fields = ['id', 'project', 'user', 'role']

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['id', 'project', 'title', 'description', 'due_date']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'project', 'title', 'description', 'assignee', 'priority', 'due_date', 'status']