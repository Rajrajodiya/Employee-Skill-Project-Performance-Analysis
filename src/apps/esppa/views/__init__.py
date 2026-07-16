"""ESPPA views — split by responsibility (auth, dashboard, analysis, prediction, models, employees, profile).

Shared service instances are imported from core.deps (FastAPI DI pattern).
Provides _safe_render helper for consistent error handling (boundary normalization).
"""

import logging
from typing import Any, Callable, Dict

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib import messages

# ── Re-export from core.deps with backward-compatible names ──────────────
from core.deps import get_data_service as _get_data_service        # noqa: F401
from core.deps import get_ml_service as _get_ml_service            # noqa: F401
from core.deps import get_employee_service as _get_employee_service  # noqa: F401
from core.deps import load_ml_models as _load_ml_models            # noqa: F401

logger = logging.getLogger(__name__)

# ── Normalization at Boundaries: shared error handler ───────────────────────


def _safe_render(
    request: HttpRequest,
    template: str,
    fn: Callable[[], Dict[str, Any]],
    error_message: str = 'An error occurred. Please try again.',
    log_message: str = 'View error',
) -> HttpResponse:
    """Execute fn() and render template, catching known errors at the boundary.

    Normalizes FileNotFoundError → user-facing 404 message
    Normalizes ValueError/KeyError/RuntimeError → user-facing 500 message
    Lets unexpected errors propagate (Fail Fast principle).
    """
    try:
        context = fn()
        return render(request, template, context)
    except FileNotFoundError:
        logger.exception(log_message)
        messages.error(request, 'Required data not found. Please ensure data is imported.')
    except (ValueError, KeyError, RuntimeError, ImportError, AttributeError, TypeError) as exc:
        logger.exception(log_message)
        messages.error(request, f'{error_message} Details: {exc}')
    return render(request, template, {})


# ── Re-export all view functions ──────────────────────────────────────────
from .auth_views import register_view                           # noqa: E402, F401
from .dashboard_views import dashboard_view                     # noqa: E402, F401
from .analysis_views import analysis_view                       # noqa: E402, F401
from .prediction_views import prediction_view                   # noqa: E402, F401
from .model_analysis_views import model_analysis_view           # noqa: E402, F401
from .employee_views import employee_list_view                  # noqa: E402, F401
from .profile_views import profile_view                         # noqa: E402, F401

__all__ = [
    'register_view', 'dashboard_view', 'analysis_view',
    'prediction_view', 'model_analysis_view', 'employee_list_view', 'profile_view',
    '_get_data_service', '_get_ml_service', '_get_employee_service', '_load_ml_models',
    '_safe_render',
]

