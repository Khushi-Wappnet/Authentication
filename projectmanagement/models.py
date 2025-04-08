from django.db import models
from django.core.exceptions import ValidationError
from authflow.models import CustomUser, Role

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    team_members = models.ManyToManyField(CustomUser, through='ProjectTeamMember')

    def __str__(self):
        return self.name

class ProjectTeamMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.role.name} in {self.project.name}"

class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.project.name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='tasks')
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    dependency = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_tasks')

    def clean(self):
        if self.dependency and self.dependency.status != 'Completed':
            raise ValidationError(f"Task '{self.title}' cannot start until its dependency '{self.dependency.title}' is completed.")
        
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError(f"Invalid status: {self.status}")
        
        if self.priority not in dict(self.PRIORITY_CHOICES):
            raise ValidationError(f"Invalid priority: {self.priority}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.project.name}"