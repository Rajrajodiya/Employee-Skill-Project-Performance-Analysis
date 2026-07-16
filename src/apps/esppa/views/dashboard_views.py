"""Dashboard views — single responsibility: rendering dashboard KPIs."""

import logging
from typing import Any, Dict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.esppa.models import Analysis, Prediction
from apps.esppa.views import _get_data_service, _get_employee_service, _safe_render

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """Dashboard with key metrics, department data, and recent activity."""

    def _build_context() -> Dict[str, Any]:
        data_service = _get_data_service()
        employee_service = _get_employee_service()
        df = data_service.load_csv()
        metrics = employee_service.build_dashboard_metrics(df)

        return {
            'total_employees': metrics.total_employees,
            'avg_performance': metrics.avg_performance,
            'avg_salary_inr': metrics.avg_salary_inr,
            'resignation_rate': metrics.resignation_rate,
            'department_data': [
                {
                    'name': d.name, 'count': d.count,
                    'performance': d.performance,
                    'performance_width': d.performance_width,
                    'salary_inr': d.salary_inr,
                }
                for d in metrics.department_data
            ],
            'gender_counts': metrics.gender_counts,
            'education_counts': metrics.education_counts,
            'high_performers': metrics.high_performers,
            'medium_performers': metrics.medium_performers,
            'low_performers': metrics.low_performers,
            'high_salary': metrics.high_salary,
            'medium_salary': metrics.medium_salary,
            'low_salary': metrics.low_salary,
            'recent_predictions': Prediction.objects.filter(
                created_by=request.user,
            ).order_by('-created_at')[:5],
            'recent_analyses': Analysis.objects.filter(
                created_by=request.user,
            ).order_by('-created_at')[:5],
        }

    return _safe_render(
        request,
        'esppa/dashboard.html',
        _build_context,
        error_message='Error processing dashboard data.',
        log_message='Dashboard generation error',
    )
