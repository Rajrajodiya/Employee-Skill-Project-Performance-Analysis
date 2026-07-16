"""
Thin controller views for the ESPPA application.

Every view delegates business logic to the appropriate service module.
Views should never:
- Import pandas, sklearn, matplotlib, etc. directly
- Contain data transformation or ML logic
"""

import logging
import threading
from typing import Any, Dict

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages

from .models import Analysis, Prediction, Employee, UserProfile
from .forms import (
    UserRegistrationForm,
    UserProfileForm,
    PredictionForm,
    AnalysisForm,
)
from .services.data_service import DataService
from .services.ml_service import MLService
from .services.chart_service import ChartService
from .services.employee_service import EmployeeService

logger = logging.getLogger(__name__)

# ── Thread-safe service initialisation ──────────────────────────────────────
_service_lock = threading.Lock()
_services_initialised = False
_data_service: DataService = None  # type: ignore
_ml_service: MLService = None  # type: ignore
_employee_service: EmployeeService = None  # type: ignore


def _init_services() -> None:
    """Initialize all services exactly once (thread-safe)."""
    global _data_service, _ml_service, _employee_service, _services_initialised
    if _services_initialised:
        return
    with _service_lock:
        if _services_initialised:
            return
        _data_service = DataService()
        _ml_service = MLService(_data_service)
        _employee_service = EmployeeService()
        _services_initialised = True


def _get_data_service() -> DataService:
    _init_services()
    return _data_service


def _get_ml_service() -> MLService:
    _init_services()
    return _ml_service


def _get_employee_service() -> EmployeeService:
    _init_services()
    return _employee_service


def _load_ml_models() -> None:
    """Lazily initialise models (called once per process on first request)."""
    ml_service = _get_ml_service()
    if not ml_service.models:
        try:
            ml_service.load_or_train_models()
        except Exception as exc:
            logger.error("Failed to load models: %s", exc)


# ═════════════════════════════════════════════════════════════════════════════
#  Authentication Views
# ═════════════════════════════════════════════════════════════════════════════


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to ESPPA.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'esppa/register.html', {'form': form})


# ═════════════════════════════════════════════════════════════════════════════
#  Dashboard
# ═════════════════════════════════════════════════════════════════════════════


@login_required
def dashboard_view(request):
    """Dashboard with key metrics, department data, and recent activity."""
    try:
        data_service = _get_data_service()
        employee_service = _get_employee_service()
        df = data_service.load_csv()
        metrics = employee_service.build_dashboard_metrics(df)

        recent_predictions = Prediction.objects.filter(
            created_by=request.user,
        ).order_by('-created_at')[:5]

        recent_analyses = Analysis.objects.filter(
            created_by=request.user,
        ).order_by('-created_at')[:5]

        context: Dict[str, Any] = {
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
            'recent_predictions': recent_predictions,
            'recent_analyses': recent_analyses,
        }
        return render(request, 'esppa/dashboard.html', context)

    except FileNotFoundError as exc:
        logger.exception("Dashboard data not found")
        messages.error(request, 'Employee data file not found. Please ensure data is imported.')
        return render(request, 'esppa/dashboard.html', {})
    except (ValueError, KeyError) as exc:
        logger.exception("Dashboard data processing error")
        messages.error(request, f'Error processing dashboard data: {exc}')
        return render(request, 'esppa/dashboard.html', {})


# ═════════════════════════════════════════════════════════════════════════════
#  Analysis (Charts)
# ═════════════════════════════════════════════════════════════════════════════


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


# ═════════════════════════════════════════════════════════════════════════════
#  Predictions
# ═════════════════════════════════════════════════════════════════════════════


@login_required
def prediction_view(request):
    """Prediction form and processing."""
    _load_ml_models()

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            try:
                result = _get_ml_service().predict(
                    model_type=form.cleaned_data['model_type'],
                    input_data=_build_input_dict(form),
                )

                prediction = Prediction.objects.create(
                    created_by=request.user,
                    model_type=form.cleaned_data['model_type'],
                    input_data=_build_input_dict(form),
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
    else:
        form = PredictionForm()

    return render(request, 'esppa/prediction.html', {'form': form})


# ═════════════════════════════════════════════════════════════════════════════
#  Model Analysis
# ═════════════════════════════════════════════════════════════════════════════


@login_required
def model_analysis_view(request):
    """Model performance comparison."""
    try:
        _load_ml_models()
        performances = _get_ml_service().evaluate_all_models()
        return render(request, 'esppa/model_analysis.html', {
            'performances': {
                name: {
                    'r2_score': m.r2_score, 'mse': m.mse,
                    'rmse': m.rmse, 'mae': m.mae,
                }
                for name, m in performances.items()
            },
        })
    except (FileNotFoundError, ValueError) as exc:
        logger.exception("Model analysis data error")
        messages.error(request, f'Error loading model analysis: {exc}')
        return render(request, 'esppa/model_analysis.html', {})
    except (RuntimeError, ImportError) as exc:
        logger.exception("Model analysis ML error")
        messages.error(request, f'Model training error: {exc}')
        return render(request, 'esppa/model_analysis.html', {})


# ═════════════════════════════════════════════════════════════════════════════
#  Employee List / Search
# ═════════════════════════════════════════════════════════════════════════════


@login_required
def employee_list_view(request):
    """Search for and display an employee by ID."""
    search_id = request.GET.get('search_id', '').strip()
    employees = []
    total_count = 0
    avg_performance = 0
    avg_salary_inr = 0

    if search_id:
        try:
            emp_id = int(search_id)
            employee = Employee.objects.filter(employee_id=emp_id).first()
            if employee:
                employees.append(_employee_to_dict(employee))
                total_count = 1
                avg_performance = employee.performance_score
                avg_salary_inr = employee.monthly_salary_inr
                messages.success(request, f'Found 1 employee with ID: {search_id}')
            else:
                messages.warning(request, f'No employee found with ID: {search_id}')
        except ValueError:
            messages.error(request, 'Please enter a valid employee ID (numbers only)')

    return render(request, 'esppa/employee_list.html', {
        'employees': employees,
        'total_count': total_count,
        'avg_performance': round(avg_performance, 1),
        'avg_salary_inr': round(avg_salary_inr, 0),
        'search_id': search_id,
    })


# ═════════════════════════════════════════════════════════════════════════════
#  Profile
# ═════════════════════════════════════════════════════════════════════════════


@login_required
def profile_view(request):
    """User profile view and edit."""
    userprofile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=userprofile)

    return render(request, 'esppa/profile.html', {
        'form': form,
        'recent_predictions': Prediction.objects.filter(
            created_by=request.user).order_by('-created_at')[:10],
        'recent_analyses': Analysis.objects.filter(
            created_by=request.user).order_by('-created_at')[:10],
    })


# ═════════════════════════════════════════════════════════════════════════════
#  Private helpers
# ═════════════════════════════════════════════════════════════════════════════


def _build_input_dict(form) -> Dict[str, Any]:
    """Extract cleaned data from PredictionForm as a flat dict."""
    return {
        'age': form.cleaned_data['age'],
        'years_at_company': form.cleaned_data['years_at_company'],
        'monthly_salary': form.cleaned_data['monthly_salary'],
        'work_hours_per_week': form.cleaned_data['work_hours_per_week'],
        'projects_handled': form.cleaned_data['projects_handled'],
        'overtime_hours': form.cleaned_data['overtime_hours'],
        'sick_days': form.cleaned_data['sick_days'],
        'remote_work_frequency': form.cleaned_data['remote_work_frequency'],
        'team_size': form.cleaned_data['team_size'],
        'training_hours': form.cleaned_data['training_hours'],
        'promotions': form.cleaned_data['promotions'],
        'employee_satisfaction_score': form.cleaned_data['employee_satisfaction_score'],
        'department': form.cleaned_data['department'],
        'gender': form.cleaned_data['gender'],
        'job_title': form.cleaned_data['job_title'],
        'education_level': form.cleaned_data['education_level'],
    }


def _build_display_dict(form) -> Dict[str, Any]:
    d = _build_input_dict(form)
    d['monthly_salary_inr'] = round(d['monthly_salary'], 0)
    d['model_type'] = form.cleaned_data['model_type']
    return d


def _employee_to_dict(emp: Employee) -> Dict[str, Any]:
    return {
        'employee_id': emp.employee_id,
        'name': emp.name,
        'department': emp.department,
        'job_title': emp.job_title,
        'age': emp.age,
        'years_at_company': emp.years_at_company,
        'performance_score': emp.performance_score,
        'monthly_salary': emp.monthly_salary,
        'monthly_salary_inr': emp.monthly_salary_inr,
        'hire_date': emp.hire_date,
        'gender': emp.gender,
        'education_level': emp.education_level,
        'work_hours_per_week': emp.work_hours_per_week,
        'projects_handled': emp.projects_handled,
        'overtime_hours': emp.overtime_hours,
        'sick_days': emp.sick_days,
        'remote_work_frequency': emp.remote_work_frequency,
        'team_size': emp.team_size,
        'training_hours': emp.training_hours,
        'promotions': emp.promotions,
        'employee_satisfaction_score': emp.employee_satisfaction_score,
        'resigned': emp.resigned,
    }
