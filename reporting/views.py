from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from projectmanagement.models import Project, Task
from resourcemanagement.models import ResourceAllocation  
from .serializers import ProjectReportSerializer, ResourceUsageSerializer
import csv
from django.http import HttpResponse
from io import StringIO
from reportlab.pdfgen import canvas
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse

class ProjectReportView(APIView):
    def get(self, request):
        projects = Project.objects.prefetch_related('tasks').all()
        serializer = ProjectReportSerializer(projects, many=True, context={'current_date': now()})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ResourceUsageReportView(APIView):
    def get(self, request):
        allocations = ResourceAllocation.objects.select_related('resource', 'project', 'task').all()
        serializer = ResourceUsageSerializer(allocations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportReportView(APIView):
    def get(self, request, format):
        # Debugging: Log the received format
        print(f"DEBUG: Export format received: {format}")

        # Validate the format parameter
        if format not in ['csv', 'pdf']:
            print("DEBUG: Invalid format received")  # Debugging
            return Response({'error': 'Invalid format. Use "csv" or "pdf".'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch projects and serialize them
        try:
            projects = Project.objects.prefetch_related('tasks').all()
            serializer = ProjectReportSerializer(projects, many=True, context={'current_date': now()})
            print(f"DEBUG: Serialized data: {serializer.data}")  # Debugging
        except Exception as e:
            print(f"DEBUG: Error fetching or serializing data: {e}")  # Debugging
            return Response({'error': 'Failed to fetch project data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Handle CSV or PDF export
        if format == 'csv':
            return self.export_csv(serializer.data)
        elif format == 'pdf':
            return self.export_pdf(serializer.data)

    def export_csv(self, data):
        try:
            print("DEBUG: Generating CSV file...")  # Debugging
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="project_report.csv"'

            writer = csv.writer(response)
            # Write CSV headers
            writer.writerow(['Project ID', 'Project Name', 'Start Date', 'End Date', 'Completed Tasks', 'Overdue Tasks'])

            # Write CSV rows
            for project in data:
                writer.writerow([project['id'], project['name'], project['start_date'], project['end_date'],
                                 project['completed_tasks'], project['overdue_tasks']])

            print("DEBUG: CSV file generated successfully.")  # Debugging
            return response
        except Exception as e:
            print(f"DEBUG: Error generating CSV: {e}")  # Debugging
            return Response({'error': 'Failed to generate CSV file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def export_pdf(self, data):
        try:
            print("DEBUG: Generating PDF file...")  # Debugging
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="project_report.pdf"'

            buffer = StringIO()
            pdf = canvas.Canvas(buffer)

            # Write PDF content
            pdf.drawString(100, 800, "Project Report")
            y = 750
            for project in data:
                pdf.drawString(50, y, f"Project: {project['name']}")
                pdf.drawString(50, y - 20, f"Start Date: {project['start_date']}, End Date: {project['end_date']}")
                pdf.drawString(50, y - 40, f"Completed Tasks: {project['completed_tasks']}, Overdue Tasks: {project['overdue_tasks']}")
                y -= 80

                # Prevent content from overflowing the page
                if y < 50:
                    pdf.showPage()
                    y = 750

            pdf.save()
            buffer.seek(0)
            response.write(buffer.getvalue())
            buffer.close()

            print("DEBUG: PDF file generated successfully.")  # Debugging
            return response
        except Exception as e:
            print(f"DEBUG: Error generating PDF: {e}")  # Debugging
            return Response({'error': 'Failed to generate PDF file.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DashboardMetricsView(APIView):
    def get(self, request):
        total_projects = Project.objects.count()
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='Completed').count()
        overdue_tasks = Task.objects.filter(status__in=['Not Started', 'In Progress'], due_date__lt=now()).count()

        metrics = {
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
        }
        return Response(metrics, status=status.HTTP_200_OK)