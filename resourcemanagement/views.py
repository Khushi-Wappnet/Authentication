from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Resource, ResourceAllocation, Comment, FileAttachment
from .serializers import ResourceSerializer, ResourceAllocationSerializer, CommentSerializer, FileAttachmentSerializer

class ResourceView(APIView):
    @swagger_auto_schema(responses={200: ResourceSerializer(many=True)})
    def get(self, request):
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ResourceSerializer, responses={201: ResourceSerializer})
    def post(self, request):
        serializer = ResourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResourceAllocationView(APIView):
    @swagger_auto_schema(responses={200: ResourceAllocationSerializer(many=True)})
    def get(self, request):
        allocations = ResourceAllocation.objects.all()
        serializer = ResourceAllocationSerializer(allocations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ResourceAllocationSerializer, responses={201: ResourceAllocationSerializer})
    def post(self, request):
        serializer = ResourceAllocationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentView(APIView):
    @swagger_auto_schema(responses={200: CommentSerializer(many=True)})
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CommentSerializer, responses={201: CommentSerializer})
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# filepath: e:\Authentication\resourcemanagement\views.py


class FileAttachmentView(APIView):
    @swagger_auto_schema(responses={200: FileAttachmentSerializer(many=True)})
    def get(self, request):
        attachments = FileAttachment.objects.all()
        serializer = FileAttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the project (optional)'),
                'task': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the task (optional)'),
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user uploading the file'),
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='The file to upload'),
            },
            required=['user', 'file'],  # Specify required fields
        ),
        consumes=['multipart/form-data'],  # Specify content type for file uploads
        responses={201: FileAttachmentSerializer}
    )
    def post(self, request):
        serializer = FileAttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)