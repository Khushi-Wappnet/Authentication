from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from authflow.models import CustomUser, Role
from .models import Project, ProjectTeamMember, Milestone, Task

class ProjectTests(TestCase):
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

        # Create test project data
        self.project_data = {
            'name': 'Test Project',
            'description': 'Test Project Description',
            'start_date': timezone.now().date(),
            'end_date': (timezone.now() + timedelta(days=30)).date()
        }

    def test_project_creation(self):
        """Test creating a new project"""
        project = Project.objects.create(**self.project_data)
        self.assertEqual(project.name, self.project_data['name'])
        self.assertEqual(project.description, self.project_data['description'])
        self.assertEqual(project.start_date, self.project_data['start_date'])
        self.assertEqual(project.end_date, self.project_data['end_date'])

    def test_project_team_member_assignment(self):
        """Test assigning team members to a project"""
        project = Project.objects.create(**self.project_data)
        
        # Assign project manager
        pm_assignment = ProjectTeamMember.objects.create(
            project=project,
            user=self.project_manager,
            role=self.pm_role
        )
        self.assertEqual(pm_assignment.user, self.project_manager)
        self.assertEqual(pm_assignment.role, self.pm_role)
        
        # Assign team member
        member_assignment = ProjectTeamMember.objects.create(
            project=project,
            user=self.team_member,
            role=self.team_member_role
        )
        self.assertEqual(member_assignment.user, self.team_member)
        self.assertEqual(member_assignment.role, self.team_member_role)

    def test_project_team_member_uniqueness(self):
        """Test that a user can't be assigned to the same project twice"""
        project = Project.objects.create(**self.project_data)
        
        # First assignment should succeed
        ProjectTeamMember.objects.create(
            project=project,
            user=self.project_manager,
            role=self.pm_role
        )
        
        # Second assignment should fail
        with self.assertRaises(Exception):
            ProjectTeamMember.objects.create(
                project=project,
                user=self.project_manager,
                role=self.team_member_role  # Different role, same user and project
            )

    def test_project_team_member_different_projects(self):
        """Test that a user can be assigned to different projects"""
        project1 = Project.objects.create(**self.project_data)
        project2 = Project.objects.create(
            name='Test Project 2',
            description='Test Project 2 Description',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date()
        )
        
        # Assign to first project
        ProjectTeamMember.objects.create(
            project=project1,
            user=self.project_manager,
            role=self.pm_role
        )
        
        # Assign to second project (should succeed)
        ProjectTeamMember.objects.create(
            project=project2,
            user=self.project_manager,
            role=self.pm_role
        )
        
        self.assertEqual(ProjectTeamMember.objects.count(), 2)

class MilestoneTests(TestCase):
    def setUp(self):
        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date()
        )
        
        self.milestone_data = {
            'title': 'Test Milestone',
            'description': 'Test Milestone Description',
            'due_date': (timezone.now() + timedelta(days=15)).date()
        }

    def test_milestone_creation(self):
        """Test creating a new milestone"""
        milestone = Milestone.objects.create(
            project=self.project,
            **self.milestone_data
        )
        self.assertEqual(milestone.title, self.milestone_data['title'])
        self.assertEqual(milestone.description, self.milestone_data['description'])
        self.assertEqual(milestone.due_date, self.milestone_data['due_date'])
        self.assertEqual(milestone.project, self.project)

    def test_milestone_project_relationship(self):
        """Test milestone-project relationship"""
        milestone = Milestone.objects.create(
            project=self.project,
            **self.milestone_data
        )
        self.assertEqual(milestone.project, self.project)
        self.assertIn(milestone, self.project.milestones.all())

class TaskTests(TestCase):
    def setUp(self):
        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Project Description',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date()
        )
        
        # Create test user
        self.team_member_role = Role.objects.create(name='Team Member', description='Team Member')
        self.team_member = CustomUser.objects.create_user(
            username='member',
            email='member@example.com',
            password='member123',
            first_name='Team',
            last_name='Member',
            phone_number='0987654321',
            role=self.team_member_role
        )
        
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Task Description',
            'priority': 'High',
            'due_date': (timezone.now() + timedelta(days=7)).date(),
            'status': 'Not Started'
        }

    def test_task_creation(self):
        """Test creating a new task"""
        task = Task.objects.create(
            project=self.project,
            assignee=self.team_member,
            **self.task_data
        )
        self.assertEqual(task.title, self.task_data['title'])
        self.assertEqual(task.description, self.task_data['description'])
        self.assertEqual(task.priority, self.task_data['priority'])
        self.assertEqual(task.due_date, self.task_data['due_date'])
        self.assertEqual(task.status, self.task_data['status'])
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.assignee, self.team_member)

    def test_task_dependency(self):
        """Test task dependency validation"""
        # Create parent task
        parent_task = Task.objects.create(
            project=self.project,
            assignee=self.team_member,
            **self.task_data
        )
        
        # Create dependent task
        dependent_task = Task(
            project=self.project,
            assignee=self.team_member,
            title='Dependent Task',
            description='Dependent Task Description',
            priority='High',
            due_date=(timezone.now() + timedelta(days=10)).date(),
            status='Not Started',
            dependency=parent_task
        )
        
        # Try to save dependent task before parent is completed
        with self.assertRaises(ValidationError):
            dependent_task.full_clean()
            dependent_task.save()
        
        # Complete parent task
        parent_task.status = 'Completed'
        parent_task.save()
        
        # Now dependent task can be saved
        dependent_task.save()
        self.assertEqual(dependent_task.status, 'Not Started')

    def test_task_status_transitions(self):
        """Test valid task status transitions"""
        task = Task.objects.create(
            project=self.project,
            assignee=self.team_member,
            **self.task_data
        )
        
        # Test valid transitions
        task.status = 'In Progress'
        task.save()
        self.assertEqual(task.status, 'In Progress')
        
        task.status = 'Completed'
        task.save()
        self.assertEqual(task.status, 'Completed')
        
        # Test invalid status
        task.status = 'Invalid Status'
        with self.assertRaises(ValidationError):
            task.full_clean()
            task.save()

    def test_task_priority_validation(self):
        """Test task priority validation"""
        task = Task.objects.create(
            project=self.project,
            assignee=self.team_member,
            **self.task_data
        )
        
        # Test valid priorities
        for priority in ['Low', 'Medium', 'High']:
            task.priority = priority
            task.save()
            self.assertEqual(task.priority, priority)
        
        # Test invalid priority
        task.priority = 'Invalid Priority'
        with self.assertRaises(ValidationError):
            task.full_clean()
            task.save()
