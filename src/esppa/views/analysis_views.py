"""Analysis views — single responsibility: rendering analytical charts."""

import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from esppa.services.chart_service import ChartService
from esppa.views import _get_data_service

logger = logging.getLogger(__name__)


@login_required
def analysis_view(request):
    """Render pre-built analytical charts."""
    try:
        df = _get_data_service().load_csv()
        context = {
            'department_bar': ChartService.department_bar_chart(df),
            'department_pie': ChartService.department_pie_chart(df),
            'performance_hist': ChartService.performance_histogram(df),
            'salary_hist': ChartService.salary_histogram(df),
        }
        return render(request, 'esppa/analysis_result.html', context)
    except FileNotFoundError as exc:
        logger.exception("Analysis data not found")
        messages.error(request, 'Employee data file not found. Please ensure data is imported.')
        return render(request, 'esppa/analysis_result.html', {})
    except (ValueError, KeyError, RuntimeError) as exc:
        logger.exception("Analysis generation error")
        messages.error(request, f'Error generating analysis: {exc}')
        return render(request, 'esppa/analysis_result.html', {})
