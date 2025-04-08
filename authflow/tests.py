from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Role, Permission, RolePermission, CustomUser

class RoleTests(TestCase):
    def setUp(self):
        self.role_data = {
            'name': 'Test Role',
            'description': 'Test Role Description'
        }

    def test_role_creation(self):
        """Test creating a new role"""
        role = Role.objects.create(**self.role_data)
        self.assertEqual(role.name, self.role_data['name'])
        self.assertEqual(role.description, self.role_data['description'])

    def test_role_unique_name(self):
        """Test that role names must be unique"""
        Role.objects.create(**self.role_data)
        with self.assertRaises(Exception):
            Role.objects.create(**self.role_data)

class PermissionTests(TestCase):
    def setUp(self):
        self.permission_data = {
            'name': 'test_permission',
            'description': 'Test Permission Description'
        }

    def test_permission_creation(self):
        """Test creating a new permission"""
        permission = Permission.objects.create(**self.permission_data)
        self.assertEqual(permission.name, self.permission_data['name'])
        self.assertEqual(permission.description, self.permission_data['description'])

    def test_permission_unique_name(self):
        """Test that permission names must be unique"""
        Permission.objects.create(**self.permission_data)
        with self.assertRaises(Exception):
            Permission.objects.create(**self.permission_data)

class RolePermissionTests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name='Test Role', description='Test Role Description')
        self.permission = Permission.objects.create(name='test_permission', description='Test Permission Description')

    def test_role_permission_assignment(self):
        """Test assigning a permission to a role"""
        role_permission = RolePermission.objects.create(role=self.role, permission=self.permission)
        self.assertEqual(role_permission.role, self.role)
        self.assertEqual(role_permission.permission, self.permission)

    def test_unique_role_permission_combination(self):
        """Test that role-permission combinations must be unique"""
        RolePermission.objects.create(role=self.role, permission=self.permission)
        with self.assertRaises(Exception):
            RolePermission.objects.create(role=self.role, permission=self.permission)

class CustomUserTests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(name='Test Role', description='Test Role Description')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'role': self.role
        }

    def test_create_user(self):
        """Test creating a regular user"""
        user = CustomUser.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            phone_number=self.user_data['phone_number'],
            role=self.user_data['role']
        )
        self.assertFalse(user.is_active)  # Default is False
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, self.role)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            phone_number='0987654321'
        )
        self.assertTrue(admin_user.is_active)  # Should be True for superusers
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_unique_fields(self):
        """Test that username, email, and phone_number must be unique"""
        CustomUser.objects.create_user(**self.user_data)
        
        # Test duplicate username
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(**self.user_data)
        
        # Test duplicate email
        self.user_data['username'] = 'testuser2'
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(**self.user_data)
        
        # Test duplicate phone number
        self.user_data['email'] = 'test2@example.com'
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(**self.user_data)

    def test_email_required(self):
        """Test that email is required"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='testuser',
                email='',
                password='testpass123'
            )

    def test_username_required(self):
        """Test that username is required"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123'
            )

    def test_required_fields_for_superuser(self):
        """Test that all required fields are provided for superuser"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_staff=False  # This should raise an error
            )

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890'
        }
        self.user = CustomUser.objects.create_user(**self.user_data)
        self.user.is_active = True  # Activate the user for testing authentication
        self.user.save()

    def test_user_authentication(self):
        """Test user authentication with correct credentials"""
        from django.contrib.auth import authenticate
        
        # Test with correct credentials
        authenticated_user = authenticate(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user, self.user)

        # Test with incorrect password
        authenticated_user = authenticate(
            username=self.user_data['username'],
            password='wrongpassword'
        )
        self.assertIsNone(authenticated_user)

        # Test with non-existent username
        authenticated_user = authenticate(
            username='nonexistent',
            password=self.user_data['password']
        )
        self.assertIsNone(authenticated_user)
