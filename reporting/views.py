from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from projectmanagement.models import Project, Task
from resourcemanagement.models import ResourceAllocation  
from .serializers import ProjectReportSerializer, ResourceUsageSerializer
import csv
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
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
    def get(self, request, export_format):
        # Debugging: Log the received format
        print(f"DEBUG: Export format received: {export_format}")

        # Validate the format parameter
        if export_format not in ['csv', 'pdf']:
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
        if export_format == 'csv':
            return self.export_csv(serializer.data)
        elif export_format == 'pdf':
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

            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)

            # Write PDF content
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(1*inch, 10*inch, "Project Report")
            
            pdf.setFont("Helvetica", 12)
            y = 9*inch
            for project in data:
                # Project name
                pdf.drawString(1*inch, y, f"Project: {str(project['name'])}")
                y -= 0.5*inch
                
                # Dates
                pdf.drawString(1*inch, y, f"Start Date: {str(project['start_date'])}")
                pdf.drawString(4*inch, y, f"End Date: {str(project['end_date'])}")
                y -= 0.5*inch
                
                # Task counts
                pdf.drawString(1*inch, y, f"Completed Tasks: {str(project['completed_tasks'])}")
                pdf.drawString(4*inch, y, f"Overdue Tasks: {str(project['overdue_tasks'])}")
                y -= 1*inch

                # Add a new page if we're running out of space
                if y < 1*inch:
                    pdf.showPage()
                    y = 9*inch
                    pdf.setFont("Helvetica", 12)

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