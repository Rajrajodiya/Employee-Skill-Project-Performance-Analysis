from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return f'{self.name} (ID: {self.employee_id})'


class Analysis(models.Model):
    """Stores analysis results and generated chart data."""

    ANALYSIS_TYPES = [
        ('department', 'Department Analysis'),
        ('performance', 'Performance Analysis'),
        ('salary', 'Salary Analysis'),
        ('overtime', 'Overtime Analysis'),
        ('satisfaction', 'Satisfaction Analysis'),
        ('overall', 'Overall Analysis'),
    ]

    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    chart_type = models.CharField(max_length=50)
    chart_data = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analysis'
        verbose_name_plural = 'Analyses'

    def __str__(self):
        return f'{self.get_analysis_type_display()} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class Prediction(models.Model):
    """Stores ML model prediction results with confidence metrics."""

    MODEL_TYPES = [
        ('random_forest', 'Random Forest'),
        ('xgboost', 'XGBoost'),
        ('neural_network', 'Neural Network (MLP)'),
    ]

    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    input_data = models.JSONField()
    prediction_result = models.FloatField()
    confidence_score = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    error_rate = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'

    def __str__(self):
        return f'{self.get_model_type_display()} Prediction - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class UserProfile(models.Model):
    """Extended user profile with additional fields."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='esppa_profile')
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"
