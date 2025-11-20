from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    """Model to store employee data"""
    employee_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    age = models.IntegerField()
    years_at_company = models.IntegerField()
    performance_score = models.FloatField()
    monthly_salary = models.FloatField()
    monthly_salary_inr = models.IntegerField()
    hire_date = models.CharField(max_length=20)  # Keeping as string for now
    gender = models.CharField(max_length=10)
    education_level = models.CharField(max_length=50)
    work_hours_per_week = models.IntegerField()
    projects_handled = models.IntegerField()
    overtime_hours = models.IntegerField()
    sick_days = models.IntegerField()
    remote_work_frequency = models.FloatField()
    team_size = models.IntegerField()
    training_hours = models.IntegerField()
    promotions = models.IntegerField()
    employee_satisfaction_score = models.FloatField()
    resigned = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.name} (ID: {self.employee_id})"

class Analysis(models.Model):
    """Model to store analysis results"""
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
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Prediction(models.Model):
    """Model to store prediction results"""
    MODEL_TYPES = [
        ('random_forest', 'Random Forest'),
        ('logistic_regression', 'Logistic Regression'),
        ('linear_regression', 'Linear Regression'),
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
    
    def __str__(self):
        return f"{self.get_model_type_display()} Prediction - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
