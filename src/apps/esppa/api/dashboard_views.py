"""Dashboard API views — single responsibility: dashboard KPI endpoints."""

import logging

from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response

from apps.esppa.schemas import DashboardMetricsSerializer
from apps.esppa.api import _data_service, _employee_service

logger = logging.getLogger(__name__)


class DashboardViewSet(viewsets.ViewSet):
    """API endpoint for dashboard metrics and analysis."""
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def metrics(self, request):
        """Return all dashboard KPIs."""
        try:
            df = _data_service.load_csv()
            metrics = _employee_service.build_dashboard_metrics(df)
            return Response(DashboardMetricsSerializer({
                'total_employees': metrics.total_employees,
                'avg_performance': metrics.avg_performance,
                'avg_salary_inr': metrics.avg_salary_inr,
                'resignation_rate': metrics.resignation_rate,
                'high_performers': metrics.high_performers,
                'medium_performers': metrics.medium_performers,
                'low_performers': metrics.low_performers,
            }).data)
        except FileNotFoundError as exc:
            return Response({'error': f'Data file not found: {exc}'},
                            status=status.HTTP_404_NOT_FOUND)
        except (ValueError, KeyError) as exc:
            return Response({'error': f'Data processing error: {exc}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def department_data(self, request):
        """Return department-wise analytics data."""
        try:
            df = _data_service.load_csv()
            metrics = _employee_service.build_dashboard_metrics(df)
            return Response([{
                'name': d.name, 'count': d.count,
                'performance': d.performance,
                'performance_width': d.performance_width,
                'salary_inr': d.salary_inr,
            } for d in metrics.department_data])
        except FileNotFoundError as exc:
            return Response({'error': f'Data file not found: {exc}'},
                            status=status.HTTP_404_NOT_FOUND)
        except (ValueError, KeyError) as exc:
            return Response({'error': f'Data processing error: {exc}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def demographics(self, request):
        """Return gender and education demographics."""
        try:
            df = _data_service.load_csv()
            metrics = _employee_service.build_dashboard_metrics(df)
            return Response({
                'gender_counts': metrics.gender_counts,
                'education_counts': metrics.education_counts,
            })
        except FileNotFoundError as exc:
            return Response({'error': f'Data file not found: {exc}'},
                            status=status.HTTP_404_NOT_FOUND)
        except (ValueError, KeyError) as exc:
            return Response({'error': f'Data processing error: {exc}'},
                            status=status.HTTP_400_BAD_REQUEST)
