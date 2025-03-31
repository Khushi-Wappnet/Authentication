from django.contrib import admin
from .models import Project, ProjectTeamMember, Milestone, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    list_filter = ('start_date', 'end_date')

@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role')
    search_fields = ('project__name', 'user__email', 'role__name')
    list_filter = ('role',)

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'due_date')
    search_fields = ('title', 'project__name')
    list_filter = ('due_date',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assignee', 'priority', 'status', 'due_date')
    search_fields = ('title', 'project__name', 'assignee__email')
    list_filter = ('priority', 'status', 'due_date')