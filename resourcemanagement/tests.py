from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from projectmanagement.models import Project, Task
from authflow.models import CustomUser, Role
from .models import Resource, ResourceAllocation, Comment, FileAttachment
from .serializers import ResourceSerializer, ResourceAllocationSerializer, CommentSerializer, FileAttachmentSerializer
import os
from django.core.files.uploadedfile import SimpleUploadedFile

class ResourceManagementTests(APITestCase):
    def setUp(self):
        # Create test roles
        self.pm_role = Role.objects.create(name='Project Manager', description='Project Manager')
        self.team_member_role = Role.objects.create(name='Team Member', description='Team Member')
        
        # Create test users
        self.project_manager = CustomUser.objects.create_user(
            username='pm',
            email='pm@example.com',
            password='pm123',
            first_name='Project',
            last_name='Manager',
            phone_number='1234567890',
            role=self.pm_role
        )
        self.team_member = CustomUser.objects.create_user(
            username='member',
            email='member@example.com',
            password='member123',
            first_name='Team',
            last_name='Member',
            phone_number='0987654321',
            role=self.team_member_role
        )

        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date()
        )

        # Create test task
        self.task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Test Task Description',
            assignee=self.team_member,
            priority='High',
            due_date=timezone.now().date(),
            status='Not Started'
        )

        # Create test resource
        self.resource = Resource.objects.create(
            name='Test Resource',
            resource_type='Equipment',
            total_quantity=10,
            description='Test Resource Description'
        )

        # Create test resource allocation
        self.resource_allocation = ResourceAllocation.objects.create(
            resource=self.resource,
            project=self.project,
            task=self.task,
            allocated_quantity=5,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=7)).date()
        )

        # Create test comment
        self.comment = Comment.objects.create(
            project=self.project,
            task=self.task,
            user=self.team_member,
            content='Test Comment'
        )

        # Create test file attachment
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            b"Test file content",
            content_type="text/plain"
        )
        self.file_attachment = FileAttachment.objects.create(
            project=self.project,
            task=self.task,
            user=self.team_member,
            file=self.test_file
        )

    def test_resource_creation(self):
        """Test resource creation and validation"""
        # Test valid resource creation
        resource_data = {
            'name': 'New Resource',
            'resource_type': 'Personnel',
            'total_quantity': 5,
            'description': 'New Resource Description'
        }
        response = self.client.post('/api/resource-management/resources/', resource_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.count(), 2)

        # Test invalid resource type
        invalid_data = {
            'name': 'Invalid Resource',
            'resource_type': 'Invalid',
            'total_quantity': 5,
            'description': 'Invalid Resource Description'
        }
        response = self.client.post('/api/resource-management/resources/', invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resource_allocation(self):
        """Test resource allocation and validation"""
        # Test valid allocation
        allocation_data = {
            'resource': self.resource.id,
            'project': self.project.id,
            'task': self.task.id,
            'allocated_quantity': 3,
            'start_date': timezone.now().date(),
            'end_date': (timezone.now() + timedelta(days=5)).date()
        }
        response = self.client.post('/api/resource-management/allocations/', allocation_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResourceAllocation.objects.count(), 2)

        # Test allocation exceeding available quantity
        invalid_allocation = {
            'resource': self.resource.id,
            'project': self.project.id,
            'task': self.task.id,
            'allocated_quantity': 15,  # More than total_quantity
            'start_date': timezone.now().date(),
            'end_date': (timezone.now() + timedelta(days=5)).date()
        }
        response = self.client.post('/api/resource-management/allocations/', invalid_allocation)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_creation(self):
        """Test comment creation and replies"""
        # Test comment creation
        comment_data = {
            'project': self.project.id,
            'task': self.task.id,
            'user': self.team_member.id,
            'content': 'New Comment'
        }
        response = self.client.post('/api/resource-management/comments/', comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

        # Test reply to comment
        reply_data = {
            'project': self.project.id,
            'task': self.task.id,
            'user': self.project_manager.id,
            'content': 'Reply to Comment',
            'parent': self.comment.id
        }
        response = self.client.post('/api/resource-management/comments/', reply_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.comment.replies.count(), 1)

    def test_file_attachment(self):
        """Test file attachment functionality"""
        # Test file upload
        test_file = SimpleUploadedFile(
            "new_file.txt",
            b"New file content",
            content_type="text/plain"
        )
        file_data = {
            'project': self.project.id,
            'task': self.task.id,
            'user': self.team_member.id,
            'file': test_file
        }
        response = self.client.post('/api/resource-management/attachments/', file_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FileAttachment.objects.count(), 2)

        # Test file retrieval
        response = self.client.get('/api/resource-management/attachments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_resource_list(self):
        """Test resource listing"""
        response = self.client.get('/api/resource-management/resources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.resource.name)

    def test_allocation_list(self):
        """Test resource allocation listing"""
        response = self.client.get('/api/resource-management/allocations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['allocated_quantity'], self.resource_allocation.allocated_quantity)

    def test_comment_list(self):
        """Test comment listing"""
        response = self.client.get('/api/resource-management/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], self.comment.content)

    def test_attachment_list(self):
        """Test file attachment listing"""
        response = self.client.get('/api/resource-management/attachments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.team_member.id)

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.file_attachment.file.path):
            os.remove(self.file_attachment.file.path)
