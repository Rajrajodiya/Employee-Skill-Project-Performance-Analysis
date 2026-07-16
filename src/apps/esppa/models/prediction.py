"""
Prediction model — single responsibility: storing ML model prediction results.
"""

from django.db import models
from django.contrib.auth.models import User


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
