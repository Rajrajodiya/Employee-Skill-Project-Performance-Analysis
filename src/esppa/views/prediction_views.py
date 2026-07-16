"""Prediction views — single responsibility: ML prediction form and results."""

import logging
from typing import Any, Dict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from esppa.models import Prediction
from esppa.forms import PredictionForm
from esppa.views import _get_ml_service, _load_ml_models

logger = logging.getLogger(__name__)


def _build_input_dict(form) -> Dict[str, Any]:
    """Extract cleaned data from PredictionForm as a flat dict."""
    return {
        'age': form.cleaned_data['age'],
        'years_at_company': form.cleaned_data['years_at_company'],
        'monthly_salary': form.cleaned_data['monthly_salary'],
        'work_hours_per_week': form.cleaned_data['work_hours_per_week'],
        'projects_handled': form.cleaned_data['projects_handled'],
        'overtime_hours': form.cleaned_data['overtime_hours'],
        'sick_days': form.cleaned_data['sick_days'],
        'remote_work_frequency': form.cleaned_data['remote_work_frequency'],
        'team_size': form.cleaned_data['team_size'],
        'training_hours': form.cleaned_data['training_hours'],
        'promotions': form.cleaned_data['promotions'],
        'employee_satisfaction_score': form.cleaned_data['employee_satisfaction_score'],
        'department': form.cleaned_data['department'],
        'gender': form.cleaned_data['gender'],
        'job_title': form.cleaned_data['job_title'],
        'education_level': form.cleaned_data['education_level'],
    }


def _build_display_dict(form) -> Dict[str, Any]:
    d = _build_input_dict(form)
    d['monthly_salary_inr'] = round(d['monthly_salary'], 0)
    d['model_type'] = form.cleaned_data['model_type']
    return d


@login_required
def prediction_view(request):
    """Prediction form and processing."""
    _load_ml_models()

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            try:
                result = _get_ml_service().predict(
                    model_type=form.cleaned_data['model_type'],
                    input_data=_build_input_dict(form),
                )

                prediction = Prediction.objects.create(
                    created_by=request.user,
                    model_type=form.cleaned_data['model_type'],
                    input_data=_build_input_dict(form),
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
    else:
        form = PredictionForm()

    return render(request, 'esppa/prediction.html', {'form': form})
