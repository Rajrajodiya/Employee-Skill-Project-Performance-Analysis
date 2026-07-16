"""
Employee model — single responsibility: employee personal, work, and performance data.
"""

from django.db import models


class Employee(models.Model):
    """
    Represents an employee with work, performance, and personal data.

    This is the core data model used by all services for analysis and predictions.
    """
    employee_id = models.IntegerField(unique=True, verbose_name='Employee ID')
    name = models.CharField(max_length=200, verbose_name='Full Name')
    department = models.CharField(max_length=100, verbose_name='Department')
    job_title = models.CharField(max_length=100, verbose_name='Job Title')
    age = models.IntegerField(verbose_name='Age')
    years_at_company = models.IntegerField(verbose_name='Years at Company')
    performance_score = models.FloatField(verbose_name='Performance Score')
    monthly_salary = models.FloatField(verbose_name='Monthly Salary (USD)')
    monthly_salary_inr = models.IntegerField(verbose_name='Monthly Salary (INR)')
    hire_date = models.CharField(max_length=20, verbose_name='Hire Date')
    gender = models.CharField(max_length=10, verbose_name='Gender')
    education_level = models.CharField(max_length=50, verbose_name='Education Level')
    work_hours_per_week = models.IntegerField(verbose_name='Work Hours/Week')
    projects_handled = models.IntegerField(verbose_name='Projects Handled')
    overtime_hours = models.IntegerField(verbose_name='Overtime Hours')
    sick_days = models.IntegerField(verbose_name='Sick Days')
    remote_work_frequency = models.FloatField(verbose_name='Remote Work Frequency')
    team_size = models.IntegerField(verbose_name='Team Size')
    training_hours = models.IntegerField(verbose_name='Training Hours')
    promotions = models.IntegerField(verbose_name='Promotions')
    employee_satisfaction_score = models.FloatField(verbose_name='Satisfaction Score')
    resigned = models.BooleanField(verbose_name='Resigned', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        indexes = [
            models.Index(fields=['employee_id'], name='idx_employee_id'),
            models.Index(fields=['department'], name='idx_department'),
            models.Index(fields=['performance_score'], name='idx_performance'),
            models.Index(fields=['resigned'], name='idx_resigned'),
            models.Index(fields=['department', 'performance_score'], name='idx_dept_perf'),
        ]

    def __str__(self):
        return f'{self.name} (ID: {self.employee_id})'
