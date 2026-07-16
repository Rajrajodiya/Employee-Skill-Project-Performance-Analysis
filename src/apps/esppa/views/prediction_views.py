"""Prediction views — single responsibility: ML prediction form and results."""

import logging
from typing import Any, Dict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.esppa.models import Prediction
from apps.esppa.forms import PredictionForm
from apps.esppa.views import _get_ml_service, _load_ml_models
from apps.esppa.services.config import PREDICTION_INPUT_FIELDS

logger = logging.getLogger(__name__)


def _build_input_dict(form) -> Dict[str, Any]:
    """Extract cleaned data from PredictionForm using data-driven field list."""
    cd = form.cleaned_data
    return {name: cd[name] for name in PREDICTION_INPUT_FIELDS}


def _build_display_dict(form) -> Dict[str, Any]:
    d = _build_input_dict(form)
    d['monthly_salary_inr'] = round(d['monthly_salary'], 0)
    d['model_type'] = form.cleaned_data['model_type']
    return d


@login_required
def prediction_view(request):
    """Prediction form and processing. Early return for GET."""
    _load_ml_models()

    if request.method != 'POST':
        return render(request, 'esppa/prediction.html', {'form': PredictionForm()})

    form = PredictionForm(request.POST)
    if not form.is_valid():
        return render(request, 'esppa/prediction.html', {'form': form})

    try:
        ml_service = _get_ml_service()
        input_data = _build_input_dict(form)
        result = ml_service.predict(
            model_type=form.cleaned_data['model_type'],
            input_data=input_data,
        )

        prediction = Prediction.objects.create(
            created_by=request.user,
            model_type=form.cleaned_data['model_type'],
            input_data=input_data,
            prediction_result=result.predicted_value,
            confidence_score=result.confidence,
            accuracy=result.accuracy,
            error_rate=result.error_rate,
        )

        return render(request, 'esppa/prediction_result.html', {
            'prediction': prediction,
            'input_data': _build_display_dict(form),
        })

    except ValueError as exc:
        logger.exception("Prediction input error")
        messages.error(request, f'Invalid input for prediction: {exc}')
    except (RuntimeError, ImportError) as exc:
        logger.exception("Prediction model error")
        messages.error(request, f'Model error during prediction: {exc}')

    return render(request, 'esppa/prediction.html', {'form': form})
