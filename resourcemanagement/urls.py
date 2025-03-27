from django.urls import path
from .views import ResourceView, ResourceAllocationView, CommentView, FileAttachmentView

urlpatterns = [
    path('resources/', ResourceView.as_view(), name='resources'),
    path('allocations/', ResourceAllocationView.as_view(), name='allocations'),
    path('comments/', CommentView.as_view(), name='comments'),
    path('attachments/', FileAttachmentView.as_view(), name='attachments'),
]