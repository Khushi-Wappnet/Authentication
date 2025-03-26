from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, ProjectTeamMember, Milestone, Task
from .serializers import ProjectSerializer, ProjectTeamMemberSerializer, MilestoneSerializer, TaskSerializer
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema

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
            task = serializer.save()
            # Send email notification to the assignee
            if task.assignee:
                send_mail(
                    'New Task Assigned',
                    f"You have been assigned a new task: {task.title}",
                    'noreply@example.com',
                    [task.assignee.email]
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=TaskSerializer, responses={200: TaskSerializer})
    def patch(self, request, pk):
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)