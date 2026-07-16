"""Employee views — single responsibility: employee search and display."""

import logging
from typing import Any, Dict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.esppa.models import Employee

logger = logging.getLogger(__name__)

EMPLOYEE_FIELD_NAMES = [
    'employee_id', 'name', 'department', 'job_title', 'age',
    'years_at_company', 'performance_score', 'monthly_salary',
    'monthly_salary_inr', 'hire_date', 'gender', 'education_level',
    'work_hours_per_week', 'projects_handled', 'overtime_hours',
    'sick_days', 'remote_work_frequency', 'team_size', 'training_hours',
    'promotions', 'employee_satisfaction_score', 'resigned',
]


def _employee_to_dict(emp: Employee) -> Dict[str, Any]:
    """Convert Employee model to a flat dict using data-driven field list."""
    return {name: getattr(emp, name, None) for name in EMPLOYEE_FIELD_NAMES}


@login_required
def employee_list_view(request):
    """Search for and display an employee by ID. Early return for empty search."""
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
