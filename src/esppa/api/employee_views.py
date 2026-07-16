"""Employee API views — single responsibility: employee endpoints with search."""

import logging

from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.db import models as django_models

from esppa.models import Employee
from esppa.serializers import EmployeeSerializer, EmployeeListSerializer

logger = logging.getLogger(__name__)


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API endpoint for Employee data."""
    queryset = Employee.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return EmployeeListSerializer if self.action == 'list' else EmployeeSerializer

    @decorators.action(detail=False, methods=['get'])
    def search(self, request):
        """Search for an employee by employee_id."""
        emp_id = request.query_params.get('id')
        if not emp_id:
            return Response({'error': 'Please provide an employee ID parameter (id=)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(employee_id=int(emp_id))
            return Response(EmployeeSerializer(employee).data)
        except Employee.DoesNotExist:
            return Response({'error': f'Employee with ID {emp_id} not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Employee ID must be a number'},
                            status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def department_summary(self, request):
        """Get department-wise employee counts."""
        dept_counts = (
            Employee.objects.values('department')
            .annotate(count=django_models.Count('id'))
            .order_by('-count')
        )
        return Response(list(dept_counts))
