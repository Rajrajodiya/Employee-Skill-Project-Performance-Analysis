"""
Consolidated API serializers for ESPPA.
"""

from rest_framework import serializers
from django.contrib.auth.models import User

from apps.esppa.models import Analysis, Prediction, Employee, UserProfile
from apps.esppa.services.config import (
    GENDER_CHOICES, EDUCATION_CHOICES, DEPARTMENT_CHOICES, JOB_TITLE_CHOICES,
)


# ── User Serializers ────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'department', 'role',
                  'phone', 'profile_picture', 'created_at']
        read_only_fields = ['id', 'created_at']


# ── Employee Serializers ────────────────────────────────────────────────────

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employee_id', 'name', 'department', 'job_title',
                  'performance_score', 'monthly_salary_inr', 'resigned']


# ── Analysis Serializers ────────────────────────────────────────────────────

class AnalysisSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Analysis
        fields = ['id', 'analysis_type', 'chart_type', 'chart_data',
                  'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


# ── Prediction Serializers ──────────────────────────────────────────────────

class PredictionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    model_display = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = ['id', 'model_type', 'model_display', 'input_data',
                  'prediction_result', 'confidence_score', 'accuracy',
                  'error_rate', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at',
                            'prediction_result', 'confidence_score',
                            'accuracy', 'error_rate']

    def get_model_display(self, obj):
        return obj.get_model_type_display()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PredictionInputSerializer(serializers.Serializer):
    model_type = serializers.ChoiceField(choices=Prediction.MODEL_TYPES)
    age = serializers.IntegerField(min_value=18, max_value=70)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    education_level = serializers.ChoiceField(choices=EDUCATION_CHOICES)
    department = serializers.ChoiceField(choices=DEPARTMENT_CHOICES)
    job_title = serializers.ChoiceField(choices=JOB_TITLE_CHOICES)
    years_at_company = serializers.IntegerField(min_value=0)
    monthly_salary = serializers.IntegerField(min_value=0)
    work_hours_per_week = serializers.IntegerField(min_value=0, max_value=80)
    projects_handled = serializers.IntegerField(min_value=0)
    overtime_hours = serializers.IntegerField(min_value=0)
    sick_days = serializers.IntegerField(min_value=0, max_value=365)
    remote_work_frequency = serializers.IntegerField(min_value=0, max_value=100)
    team_size = serializers.IntegerField(min_value=1)
    training_hours = serializers.IntegerField(min_value=0)
    promotions = serializers.IntegerField(min_value=0)
    employee_satisfaction_score = serializers.FloatField(min_value=1.0, max_value=5.0)


# ── Dashboard Serializers ───────────────────────────────────────────────────

class DashboardMetricsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    avg_performance = serializers.FloatField()
    avg_salary_inr = serializers.FloatField()
    resignation_rate = serializers.FloatField()
    high_performers = serializers.IntegerField()
    medium_performers = serializers.IntegerField()
    low_performers = serializers.IntegerField()
