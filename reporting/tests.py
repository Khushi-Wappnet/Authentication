from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
from projectmanagement.models import Project, Task
from resourcemanagement.models import Resource, ResourceAllocation
from authflow.models import CustomUser, Role
from .views import ProjectReportView, ResourceUsageReportView, ExportReportView, DashboardMetricsView
from .serializers import ProjectReportSerializer, ResourceUsageSerializer

class ReportingTests(APITestCase):
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

        # Create test tasks
        self.completed_task = Task.objects.create(
            project=self.project,
            title='Completed Task',
            description='Completed Task Description',
            assignee=self.team_member,
            priority='High',
            due_date=timezone.now().date(),
            status='Completed'
        )

        self.overdue_task = Task.objects.create(
            project=self.project,
            title='Overdue Task',
            description='Overdue Task Description',
            assignee=self.team_member,
            priority='High',
            due_date=(timezone.now() - timedelta(days=1)).date(),
            status='In Progress'
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
            task=self.completed_task,
            allocated_quantity=5,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=7)).date()
        )

        # Set up API client
        self.client = APIClient()

    def test_project_report_view(self):
        """Test project report generation"""
        response = self.client.get('/api/reporting/projects/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One project
        project_data = response.data[0]
        self.assertEqual(project_data['name'], self.project.name)
        self.assertEqual(project_data['completed_tasks'], 1)
        self.assertEqual(project_data['overdue_tasks'], 1)

    def test_resource_usage_report_view(self):
        """Test resource usage report generation"""
        response = self.client.get('/api/reporting/resources/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # One resource allocation
        allocation_data = response.data[0]
        self.assertEqual(allocation_data['allocated_quantity'], 5)
        self.assertEqual(allocation_data['project'], self.project.id)
        self.assertEqual(allocation_data['task'], self.completed_task.id)

    def test_export_csv_report(self):
        """Test CSV report export"""
        response = self.client.get('/api/reporting/export/csv/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="project_report.csv"')
        
        # Verify CSV content
        content = response.content.decode('utf-8')
        self.assertIn('Project ID', content)
        self.assertIn('Project Name', content)
        self.assertIn('Test Project', content)

    def test_export_pdf_report(self):
        """Test PDF report export"""
        response = self.client.get('/api/reporting/export/pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="project_report.pdf"')

    def test_invalid_export_format(self):
        """Test invalid export format handling"""
        response = self.client.get('/api/reporting/export/invalid/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid format. Use "csv" or "pdf".')

    def test_dashboard_metrics_view(self):
        """Test dashboard metrics generation"""
        response = self.client.get('/api/reporting/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_projects'], 1)
        self.assertEqual(response.data['total_tasks'], 2)
        self.assertEqual(response.data['completed_tasks'], 1)
        self.assertEqual(response.data['overdue_tasks'], 1)

    def test_project_report_serializer(self):
        """Test project report serializer"""
        serializer = ProjectReportSerializer(
            self.project,
            context={'current_date': timezone.now()}
        )
        data = serializer.data
        
        self.assertEqual(data['name'], self.project.name)
        self.assertEqual(data['completed_tasks'], 1)
        self.assertEqual(data['overdue_tasks'], 1)

    def test_resource_usage_serializer(self):
        """Test resource usage serializer"""
        serializer = ResourceUsageSerializer(self.resource_allocation)
        data = serializer.data
        
        self.assertEqual(data['allocated_quantity'], 5)
        self.assertEqual(data['project'], self.project.id)
        self.assertEqual(data['task'], self.completed_task.id)
