"""
Main application views for ESPPA — dashboard, analysis, prediction, models, employees.
"""

import logging
from typing import Any, Dict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.esppa.models import Employee, Analysis as AnalysisModel, Prediction
from apps.esppa.forms import PredictionForm
from apps.esppa.services.config import PREDICTION_INPUT_FIELDS
from core.deps import get_data_service as _get_data_service, get_ml_service as _get_ml_service, get_employee_service as _get_employee_service, load_ml_models as _load_ml_models
from apps.esppa.views import _safe_render

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
#  Dashboard
# ═════════════════════════════════════════════════════════════════════════════

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
            'recent_analyses': AnalysisModel.objects.filter(
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


# ═════════════════════════════════════════════════════════════════════════════
#  Analysis
# ═════════════════════════════════════════════════════════════════════════════

@login_required
def analysis_view(request):
    """Render pre-built analytical charts."""

    def _build_chart_context() -> Dict[str, Any]:
        from apps.esppa.services.chart_service import ChartService
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


# ═════════════════════════════════════════════════════════════════════════════
#  Prediction
# ═════════════════════════════════════════════════════════════════════════════

def _build_input_dict(form) -> Dict[str, Any]:
    cd = form.cleaned_data
    return {name: cd[name] for name in PREDICTION_INPUT_FIELDS}


def _build_display_dict(form) -> Dict[str, Any]:
    d = _build_input_dict(form)
    d['monthly_salary_inr'] = round(d['monthly_salary'], 0)
    d['model_type'] = form.cleaned_data['model_type']
    return d


@login_required
def prediction_view(request):
    """Prediction form and processing."""
    _load_ml_models()

    if request.method != 'POST':
        return render(request, 'esppa/prediction.html', {'form': PredictionForm()})

    form = PredictionForm(request.POST)
    if not form.is_valid():
        return render(request, 'esppa/prediction.html', {'form': form})

    try:
        ml_service = _get_ml_service()
        input_data = _build_input_dict(form)
        result = ml_service.predict(
            model_type=form.cleaned_data['model_type'],
            input_data=input_data,
        )

        prediction = Prediction.objects.create(
            created_by=request.user,
            model_type=form.cleaned_data['model_type'],
            input_data=input_data,
            prediction_result=result.predicted_value,
            confidence_score=result.confidence,
            accuracy=result.accuracy,
            error_rate=result.error_rate,
        )

        return render(request, 'esppa/prediction_result.html', {
            'prediction': prediction,
            'input_data': _build_display_dict(form),
        })

    except ValueError as exc:
        logger.exception("Prediction input error")
        messages.error(request, f'Invalid input for prediction: {exc}')
    except (RuntimeError, ImportError) as exc:
        logger.exception("Prediction model error")
        messages.error(request, f'Model error during prediction: {exc}')

    return render(request, 'esppa/prediction.html', {'form': form})


# ═════════════════════════════════════════════════════════════════════════════
#  Model Analysis
# ═════════════════════════════════════════════════════════════════════════════

@login_required
def model_analysis_view(request):
    """Model performance comparison."""

    def _build_context() -> dict:
        _load_ml_models()
        performances = _get_ml_service().evaluate_persisted_models()
        return {
            'performances': {
                name: {
                    'r2_score': m.r2_score, 'mse': m.mse,
                    'rmse': m.rmse, 'mae': m.mae,
                }
                for name, m in performances.items()
            },
        }

    return _safe_render(
        request,
        'esppa/model_analysis.html',
        _build_context,
        error_message='Error loading model analysis.',
        log_message='Model analysis error',
    )


# ═════════════════════════════════════════════════════════════════════════════
#  Employees
# ═════════════════════════════════════════════════════════════════════════════

EMPLOYEE_FIELD_NAMES = [
    'employee_id', 'name', 'department', 'job_title', 'age',
    'years_at_company', 'performance_score', 'monthly_salary',
    'monthly_salary_inr', 'hire_date', 'gender', 'education_level',
    'work_hours_per_week', 'projects_handled', 'overtime_hours',
    'sick_days', 'remote_work_frequency', 'team_size', 'training_hours',
    'promotions', 'employee_satisfaction_score', 'resigned',
]


def _employee_to_dict(emp: Employee) -> Dict[str, Any]:
    return {name: getattr(emp, name, None) for name in EMPLOYEE_FIELD_NAMES}


@login_required
def employee_list_view(request):
    """Search for and display an employee by ID."""
    search_id = request.GET.get('search_id', '').strip()

    if not search_id:
        return render(request, 'esppa/employee_list.html', {
            'employees': [],
            'total_count': 0, 'avg_performance': 0, 'avg_salary_inr': 0, 'search_id': '',
        })

    try:
        emp_id = int(search_id)
    except ValueError:
        messages.error(request, 'Please enter a valid employee ID (numbers only)')
        return render(request, 'esppa/employee_list.html', {
            'employees': [], 'total_count': 0, 'avg_performance': 0,
            'avg_salary_inr': 0, 'search_id': search_id,
        })

    employee = Employee.objects.filter(employee_id=emp_id).first()
    if not employee:
        messages.warning(request, f'No employee found with ID: {search_id}')
        return render(request, 'esppa/employee_list.html', {
            'employees': [], 'total_count': 0, 'avg_performance': 0,
            'avg_salary_inr': 0, 'search_id': search_id,
        })

    messages.success(request, f'Found 1 employee with ID: {search_id}')
    return render(request, 'esppa/employee_list.html', {
        'employees': [_employee_to_dict(employee)],
        'total_count': 1,
        'avg_performance': round(employee.performance_score, 1),
        'avg_salary_inr': round(employee.monthly_salary_inr, 0),
        'search_id': search_id,
    })
