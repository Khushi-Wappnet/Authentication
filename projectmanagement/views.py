from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, ProjectTeamMember, Milestone, Task
from .serializers import ProjectSerializer, ProjectTeamMemberSerializer, MilestoneSerializer, TaskSerializer,ScheduleSerializer
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from authflow.models import CustomUser  # Import CustomUser model

class ProjectView(APIView):
    @swagger_auto_schema(responses={200: ProjectSerializer(many=True)})
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProjectSerializer, responses={201: ProjectSerializer})
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the project'),
                'team_members': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='List of user IDs to assign as team members'
                ),
            },
            required=['project_id', 'team_members']
        ),
        responses={200: ProjectSerializer}
    )
    def patch(self, request):
        project_id = request.data.get('project_id')
        team_members = request.data.get('team_members')

        if not project_id or not team_members:
            return Response({'error': 'Project ID and team members are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Validate team members
        valid_team_members = CustomUser.objects.filter(id__in=team_members)
        if len(valid_team_members) != len(team_members):
            return Response({'error': 'One or more team members are invalid.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update team members
        project.team_members.set(valid_team_members)
        project.save()

        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class MilestoneView(APIView):
    @swagger_auto_schema(request_body=MilestoneSerializer, responses={201: MilestoneSerializer})
    def post(self, request):
        serializer = MilestoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskView(APIView):
    @swagger_auto_schema(request_body=TaskSerializer, responses={201: TaskSerializer})
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            try:
                task = serializer.save()
                # Validate dependency logic
                if task.dependency and task.dependency.status != 'Completed':
                    raise ValueError(
                        f"Task '{task.title}' cannot start until its dependency '{task.dependency.title}' is completed."
                    )
                # Send email notification to the assignee
                if task.assignee:
                    send_mail(
                        'New Task Assigned',
                        f"You have been assigned a new task: {task.title}",
                        'noreply@example.com',
                        [task.assignee.email]
                    )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=TaskSerializer, responses={200: TaskSerializer})
    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                updated_task = serializer.save()
                # Validate dependency logic
                if updated_task.dependency and updated_task.dependency.status != 'Completed':
                    raise ValueError(
                        f"Task '{updated_task.title}' cannot start until its dependency '{updated_task.dependency.title}' is completed."
                    )
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScheduleView(APIView):
    @swagger_auto_schema(responses={200: ScheduleSerializer(many=True)})
    def get(self, request):
        projects = Project.objects.prefetch_related('tasks', 'milestones').all()
        serializer = ScheduleSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)