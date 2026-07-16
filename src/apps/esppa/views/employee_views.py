"""Employee views — single responsibility: employee search and display."""

import logging
from typing import Any, Dict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.esppa.models import Employee

logger = logging.getLogger(__name__)


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
