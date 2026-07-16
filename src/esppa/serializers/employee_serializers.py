"""
Employee serializers — single responsibility: Employee data serialization.
"""

from rest_framework import serializers

from esppa.models import Employee


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
