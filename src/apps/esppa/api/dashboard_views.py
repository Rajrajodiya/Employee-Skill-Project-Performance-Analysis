"""Dashboard API views — single responsibility: dashboard KPI endpoints."""

import logging
from typing import Any, Dict, Optional

from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response

from apps.esppa.schemas import DashboardMetricsSerializer
from apps.esppa.api import _data_service, _employee_service

logger = logging.getLogger(__name__)


def _load_metrics() -> Optional[Dict[str, Any]]:
    """Load CSV data and build dashboard metrics. Returns None on known errors."""
    try:
        df = _data_service.load_csv()
        metrics = _employee_service.build_dashboard_metrics(df)
        return metrics
    except FileNotFoundError as exc:
        logger.warning("Dashboard data not found: %s", exc)
        return None


class DashboardViewSet(viewsets.ViewSet):
    """API endpoint for dashboard metrics and analysis."""
    permission_classes = [permissions.IsAuthenticated]

    def _apply_metrics(self, transform):
        """Load metrics and apply transform. Returns Response with data or error."""
        metrics = _load_metrics()
        if metrics is None:
            return Response(
                {'error': 'Data file not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            return Response(transform(metrics))
        except (ValueError, KeyError) as exc:
            logger.exception("Dashboard data processing error")
            return Response(
                {'error': f'Data processing error: {exc}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @decorators.action(detail=False, methods=['get'])
    def metrics(self, request):
        """Return all dashboard KPIs."""
        return self._apply_metrics(
            lambda m: DashboardMetricsSerializer({
                'total_employees': m.total_employees,
                'avg_performance': m.avg_performance,
                'avg_salary_inr': m.avg_salary_inr,
                'resignation_rate': m.resignation_rate,
                'high_performers': m.high_performers,
                'medium_performers': m.medium_performers,
                'low_performers': m.low_performers,
            }).data,
        )

    @decorators.action(detail=False, methods=['get'])
    def department_data(self, request):
        """Return department-wise analytics data."""
        return self._apply_metrics(
            lambda m: [{
                'name': d.name, 'count': d.count,
                'performance': d.performance,
                'performance_width': d.performance_width,
                'salary_inr': d.salary_inr,
            } for d in m.department_data],
        )

    @decorators.action(detail=False, methods=['get'])
    def demographics(self, request):
        """Return gender and education demographics."""
        return self._apply_metrics(
            lambda m: {
                'gender_counts': m.gender_counts,
                'education_counts': m.education_counts,
            },
        )
