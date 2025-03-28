from rest_framework import serializers
from projectmanagement.models import Project, Task
from resourcemanagement.models import ResourceAllocation  

class ProjectReportSerializer(serializers.ModelSerializer):
    completed_tasks = serializers.SerializerMethodField()
    overdue_tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'start_date', 'end_date', 'completed_tasks', 'overdue_tasks']

    def get_completed_tasks(self, obj):
        return obj.tasks.filter(status='Completed').count()

    def get_overdue_tasks(self, obj):
        return obj.tasks.filter(status__in=['Not Started', 'In Progress'], due_date__lt=self.context['current_date']).count()

class ResourceUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceAllocation
        fields = ['id', 'resource', 'project', 'task', 'allocated_quantity', 'start_date', 'end_date']