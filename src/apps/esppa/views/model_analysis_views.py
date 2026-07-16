"""Model analysis views — single responsibility: ML model performance comparison."""

import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.esppa.views import _get_ml_service, _load_ml_models, _safe_render

logger = logging.getLogger(__name__)


@login_required
def model_analysis_view(request):
    """Model performance comparison. Uses _safe_render for error boundary."""

    def _build_context() -> dict:
        _load_ml_models()
        performances = _get_ml_service().evaluate_persisted_models()
        return {
            'performances': {
                name: {
                    'r2_score': m.r2_score, 'mse': m.mse,
                    'rmse': m.rmse, 'mae': m.mae,
                }
                for name, m in performances.items()
            },
        }

    return _safe_render(
        request,
        'esppa/model_analysis.html',
        _build_context,
        error_message='Error loading model analysis.',
        log_message='Model analysis error',
    )
