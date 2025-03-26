from django.urls import path
from .views import ProjectView, MilestoneView, TaskView

urlpatterns = [
    path('projects/', ProjectView.as_view(), name='projects'),
    path('milestones/', MilestoneView.as_view(), name='milestones'),
    path('tasks/', TaskView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskView.as_view(), name='update_task'),
]