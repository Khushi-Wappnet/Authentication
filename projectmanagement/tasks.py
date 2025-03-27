# filepath: e:\Authentication\projectmanagement\tasks.py

from celery import shared_task  # Correct import
from django.utils.timezone import now, timedelta
from .models import Task
from django.core.mail import send_mail

@shared_task
def send_deadline_alerts():
    approaching_deadline = now() + timedelta(days=1)
    overdue_tasks = Task.objects.filter(due_date__lt=now(), status__in=['Not Started', 'In Progress'])
    upcoming_tasks = Task.objects.filter(due_date__lte=approaching_deadline, due_date__gte=now(), status__in=['Not Started', 'In Progress'])

    for task in overdue_tasks:
        send_mail(
            'Task Overdue',
            f"The task '{task.title}' is overdue.",
            'noreply@example.com',
            [task.assignee.email]
        )

    for task in upcoming_tasks:
        send_mail(
            'Task Deadline Approaching',
            f"The task '{task.title}' is due soon.",
            'noreply@example.com',
            [task.assignee.email]
        )