from rest_framework import serializers
from .models import Resource, ResourceAllocation, Comment, FileAttachment

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'resource_type', 'total_quantity', 'description']

class ResourceAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceAllocation
        fields = ['id', 'resource', 'project', 'task', 'allocated_quantity', 'start_date', 'end_date']

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'project', 'task', 'user', 'content', 'parent', 'created_at', 'replies']

    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data

class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = ['id', 'project', 'task', 'user', 'file', 'uploaded_at']