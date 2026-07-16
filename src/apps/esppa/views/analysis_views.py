"""Analysis views — single responsibility: rendering analytical charts."""

import logging
from typing import Dict, Any

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.esppa.services.chart_service import ChartService
from apps.esppa.views import _get_data_service, _safe_render

logger = logging.getLogger(__name__)


@login_required
def analysis_view(request):
    """Render pre-built analytical charts. Uses _safe_render for error boundary."""

    def _build_chart_context() -> Dict[str, Any]:
        df = _get_data_service().load_csv()
        return {
            'department_bar': ChartService.department_bar_chart(df),
            'department_pie': ChartService.department_pie_chart(df),
            'performance_hist': ChartService.performance_histogram(df),
            'salary_hist': ChartService.salary_histogram(df),
        }

    return _safe_render(
        request,
        'esppa/analysis_result.html',
        _build_chart_context,
        error_message='Error generating analysis.',
        log_message='Analysis generation error',
    )
