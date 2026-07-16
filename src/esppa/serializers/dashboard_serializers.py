"""
Dashboard serializers — single responsibility: dashboard KPI serialization.
"""

from rest_framework import serializers


class DashboardMetricsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    avg_performance = serializers.FloatField()
    avg_salary_inr = serializers.FloatField()
    resignation_rate = serializers.FloatField()
    high_performers = serializers.IntegerField()
    medium_performers = serializers.IntegerField()
    low_performers = serializers.IntegerField()
