"""ESPPA REST API — split by resource (user, employee, analysis, prediction, dashboard, models).

Shared service instances are accessed lazily via core.deps getter functions.
Services are NOT initialized at module level — this avoids loading heavy
ML dependencies (pandas, numpy, sklearn, xgboost) at import time.
"""

from core.deps import get_data_service, get_ml_service, get_employee_service


def _require_data():
    """Get DataService or raise RuntimeError if unavailable."""
    svc = get_data_service()
    if svc is None:
        raise RuntimeError("Data service is not available. Install pandas, numpy, scikit-learn.")
    return svc


def _require_ml():
    """Get MLService or raise RuntimeError if unavailable."""
    svc = get_ml_service()
    if svc is None:
        raise RuntimeError("ML service is not available. Install scikit-learn, xgboost.")
    return svc


def _require_employee():
    """Get EmployeeService or raise RuntimeError if unavailable."""
    svc = get_employee_service()
    if svc is None:
        raise RuntimeError("Employee service is not available. Install pandas.")
    return svc


# ── Re-export all ViewSets ─────────────────────────────────────────────────
from .user_views import UserViewSet, UserProfileViewSet               # noqa: E402, F401
from .employee_views import EmployeeViewSet                           # noqa: E402, F401
from .analysis_views import AnalysisViewSet                           # noqa: E402, F401
from .prediction_views import PredictionViewSet                       # noqa: E402, F401
from .dashboard_views import DashboardViewSet                         # noqa: E402, F401
from .model_views import ModelAnalysisViewSet                          # noqa: E402, F401

__all__ = [
    'UserViewSet', 'UserProfileViewSet', 'EmployeeViewSet',
    'AnalysisViewSet', 'PredictionViewSet', 'DashboardViewSet',
    'ModelAnalysisViewSet',
]
