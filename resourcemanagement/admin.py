from django.contrib import admin
from .models import Resource, ResourceAllocation, Comment, FileAttachment

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'resource_type', 'total_quantity')
    search_fields = ('name', 'resource_type')
    list_filter = ('resource_type',)

@admin.register(ResourceAllocation)
class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ('resource', 'project', 'task', 'allocated_quantity', 'start_date', 'end_date')
    search_fields = ('resource__name', 'project__name', 'task__title')
    list_filter = ('start_date', 'end_date')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'task', 'content', 'created_at')
    search_fields = ('user__username', 'project__name', 'task__title', 'content')
    list_filter = ('created_at',)

@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'task', 'file', 'uploaded_at')
    search_fields = ('user__username', 'project__name', 'task__title')
    list_filter = ('uploaded_at',)