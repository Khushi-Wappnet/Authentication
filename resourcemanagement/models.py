from django.db import models
from projectmanagement.models import Project, Task
from authflow.models import CustomUser

class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('Personnel', 'Personnel'),
        ('Budget', 'Budget'),
        ('Equipment', 'Equipment'),
    ]

    name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES)
    total_quantity = models.PositiveIntegerField()  # Total available quantity
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.resource_type})"

class ResourceAllocation(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='allocations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='resource_allocations')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='resource_allocations', null=True, blank=True)
    allocated_quantity = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.allocated_quantity} of {self.resource.name} for {self.project.name}"

    def clean(self):
        # Ensure allocated quantity does not exceed available quantity
        if self.allocated_quantity > self.resource.total_quantity:
            raise ValueError(f"Cannot allocate more than available quantity for {self.resource.name}.")
        
class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project or self.task}"

class FileAttachment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File by {self.user.username} for {self.project or self.task}"