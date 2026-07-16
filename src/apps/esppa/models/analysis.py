"""
Analysis model — single responsibility: storing analysis results and chart data.
"""

from django.db import models
from django.contrib.auth.models import User


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
