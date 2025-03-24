from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser to handle user creation with email instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)  # Default to inactive
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Custom user model that uses email instead of username as the unique identifier.
    """
    username = None  # Remove the username field
    email = models.EmailField(unique=True)  # Use email as the unique identifier
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=False)  # Override default to False

    USERNAME_FIELD = 'email'  # Set email as the unique identifier
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']  # Fields required for superuser creation

    objects = CustomUserManager()  # Use the custom manager