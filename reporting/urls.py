from django.urls import path
from .views import ProjectReportView, ResourceUsageReportView, ExportReportView, DashboardMetricsView

urlpatterns = [
    path('projects/', ProjectReportView.as_view(), name='project_report'),
    path('resources/', ResourceUsageReportView.as_view(), name='resource_usage_report'),
    path('export/<str:format>/', ExportReportView.as_view(), name='export_report'),
    path('dashboard/', DashboardMetricsView.as_view(), name='dashboard_metrics'),
]