"""Model analysis views — single responsibility: ML model performance comparison."""

import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from esppa.views import _get_ml_service, _load_ml_models

logger = logging.getLogger(__name__)


@login_required
def model_analysis_view(request):
    """Model performance comparison."""
    try:
        _load_ml_models()
        performances = _get_ml_service().evaluate_all_models()
        return render(request, 'esppa/model_analysis.html', {
            'performances': {
                name: {
                    'r2_score': m.r2_score, 'mse': m.mse,
                    'rmse': m.rmse, 'mae': m.mae,
                }
                for name, m in performances.items()
            },
        })
    except (FileNotFoundError, ValueError) as exc:
        logger.exception("Model analysis data error")
        messages.error(request, f'Error loading model analysis: {exc}')
        return render(request, 'esppa/model_analysis.html', {})
    except (RuntimeError, ImportError) as exc:
        logger.exception("Model analysis ML error")
        messages.error(request, f'Model training error: {exc}')
        return render(request, 'esppa/model_analysis.html', {})
